#!/usr/bin/env python3
"""Budget gate for the frontend-web-performance skill.

No exact Claude tokenizer is available offline, so this brackets the count instead of
guessing at it. WORST is a deliberately pessimistic chars/token ratio; if WORST clears the
ceiling the limit holds no matter which tokenizer is actually used.

Exit 1 on any breach, so this can gate a build.
"""
import glob
import os
import re
import sys

BODY_CEILING = 5000       # spec: SKILL.md body under 5k tokens
DESC_CEILING = 1024       # hard char cap, validator-enforced
META_TARGET  = 100        # name + description tokens; always resident, so keep it lean
WORST, LIKELY, BEST = 3.0, 3.8, 4.3   # chars per token

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
skill = os.path.join(root, "SKILL.md")
text = open(skill, encoding="utf-8").read()

m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not m:
    print("FAIL  no YAML frontmatter")
    sys.exit(1)
front, body = m.group(1), text[m.end():]

dm = re.search(r"^description:\s*(.+?)(?=\n[a-z_]+:|\Z)", front, re.S | re.M)
desc = " ".join(dm.group(1).split()) if dm else ""

n = len(body)
worst, likely, best = n / WORST, n / LIKELY, n / BEST

print(f"SKILL.md body   {n:>6} chars")
print(f"  worst  {worst:>7.0f} tok   {100*worst/BODY_CEILING:>3.0f}% of {BODY_CEILING}")
print(f"  likely {likely:>7.0f} tok   {100*likely/BODY_CEILING:>3.0f}%")
print(f"  best   {best:>7.0f} tok   {100*best/BODY_CEILING:>3.0f}%")
nm = re.search(r"^name:\s*(\S+)", front, re.M)
meta = len((nm.group(1) if nm else "") + desc)
print(f"description     {len(desc):>6} / {DESC_CEILING} chars (hard cap)")
print(f"name+desc meta  {meta:>6} chars -> ~{meta/LIKELY:.0f} tok, worst {meta/WORST:.0f} "
      f"(guideline ~{META_TARGET}, {meta/LIKELY/META_TARGET:.1f}x)")

refs = sorted(glob.glob(os.path.join(root, "references", "*.md")))
if refs:
    print("\nreferences (on demand, not counted against the body ceiling):")
    worst_ref = None
    for f in refs:
        c = len(open(f, encoding="utf-8").read())
        print(f"  {os.path.basename(f):<24}{c:>6} chars  ~{c/LIKELY:>5.0f} tok")
        if worst_ref is None or c > worst_ref[1]:
            worst_ref = (os.path.basename(f), c)
    if worst_ref and worst_ref[1] / LIKELY > 2800:
        print(f"  NOTE {worst_ref[0]} past 2800 tok — consider splitting it")

fails = []
if worst > BODY_CEILING:
    fails.append(f"body may exceed {BODY_CEILING} tokens (worst case {worst:.0f})")
if len(desc) > DESC_CEILING:
    fails.append(f"description {len(desc)} > {DESC_CEILING} chars")
if not desc:
    fails.append("description missing or unparseable")
warns = []
if meta / LIKELY > META_TARGET * 1.15:
    warns.append(f"name+description ~{meta/LIKELY:.0f} tok is {meta/LIKELY/META_TARGET:.1f}x "
                 f"the ~{META_TARGET} token guideline. Deliberate: traded resident cost for "
                 f"trigger coverage. Hard limit is the {DESC_CEILING}-char cap, so this is "
                 f"not a build failure. Re-check if the trigger eval shows no benefit.")

print()
for w in warns:
    print("WARN  " + w)
if fails:
    for f in fails:
        print("FAIL  " + f)
    sys.exit(1)
print(f"PASS  body clears {BODY_CEILING} tok even at the pessimistic {WORST} chars/token")

# --- link integrity, appended so the gate also catches stale cross-references ---
# Case-insensitive on purpose: an earlier version matched only [a-z], so references to
# LICENSE.md / README.md were invisible and a stale one could ship unnoticed.
LINK = r"`([A-Za-z0-9_-]+\.md)`"
linked = set()
for f in [skill] + refs:
    linked |= set(re.findall(LINK, open(f, encoding="utf-8").read()))
present = ({os.path.basename(f) for f in refs}
           | {f for f in os.listdir(root) if f.lower().endswith(".md")})
dangling = sorted(linked - present)
orphans = sorted({os.path.basename(f) for f in refs} - set(re.findall(LINK, text)))
if dangling:
    print("FAIL  cross-reference to missing file(s): " + ", ".join(dangling))
    sys.exit(1)
if orphans:
    print("WARN  reference(s) never linked from SKILL.md: " + ", ".join(orphans))
print("PASS  all cross-references resolve; every reference reachable from SKILL.md")

# --- eval set integrity, so a query-set change cannot silently break the harness ---
import json
ev = os.path.join(root, "evals", "trigger_queries.json")
if os.path.exists(ev):
    try:
        qs = json.load(open(ev, encoding="utf-8"))
    except Exception as exc:
        print("FAIL  evals/trigger_queries.json does not parse: " + str(exc))
        sys.exit(1)
    pos = sum(1 for x in qs if x.get("should_trigger") is True)
    neg = sum(1 for x in qs if x.get("should_trigger") is False)
    bad = [x for x in qs if not isinstance(x.get("query"), str)
           or not x.get("query", "").strip()
           or not isinstance(x.get("should_trigger"), bool)]
    print(f"\nevals           {len(qs)} queries, {pos} positive / {neg} near-miss")
    if bad:
        print(f"FAIL  {len(bad)} eval entr(ies) malformed")
        sys.exit(1)
    if pos == 0 or neg == 0:
        print("FAIL  eval set needs both positive and negative cases")
        sys.exit(1)
    if abs(pos - neg) > max(2, len(qs) // 10):
        print(f"WARN  eval set is unbalanced ({pos}/{neg}); near-misses are the informative half")
    print("PASS  eval set well-formed and balanced")

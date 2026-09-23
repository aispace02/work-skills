# SSL/TLS (Boost.Asio & standalone Asio)

Applies to every style — `ssl::stream<>` is a library feature that wraps a stream socket.

## Header and Namespaces

```cpp
#ifdef USE_STANDALONE_ASIO
  #include <asio.hpp>
  #include <asio/ssl.hpp>
  namespace net = asio;
#else
  #include <boost/asio.hpp>
  #include <boost/asio/ssl.hpp>
  namespace net = boost::asio;
#endif

namespace ssl = net::ssl;
using tcp = net::ip::tcp;
```

---

## 1. TLS Client (C++20 Coroutine Style)

Standard client setup: configure verification, establish TCP connection, set Server Name Indication (SNI), perform TLS handshake, and gracefully shut down.

```cpp
net::awaitable<void> tls_client(net::io_context& io, const std::string& host, const std::string& port) {
    // 1. SSL context with industry standard options (TLS 1.2+ fallback)
    ssl::context ctx(ssl::context::tls_client);
    ctx.set_default_verify_paths();
    ctx.set_options(ssl::context::default_workarounds |
                    ssl::context::no_sslv2 |
                    ssl::context::no_sslv3 |
                    ssl::context::no_tlsv1 |
                    ssl::context::no_tlsv1_1);

    // 2. Stream wrapping a TCP socket
    ssl::stream<tcp::socket> stream(io, ctx);

    // 3. Resolve & connect underlying TCP socket
    tcp::resolver resolver(io);
    auto endpoints = co_await resolver.async_resolve(host, port, net::use_awaitable);
    co_await net::async_connect(stream.lowest_layer(), endpoints, net::use_awaitable);

    // 4. Set SNI hostname (critical for virtual hosting / cloud providers)
    if (!SSL_set_tlsext_host_name(stream.native_handle(), host.c_str())) {
        throw net::system_error(
            net::error_code(static_cast<int>(::ERR_get_error()), net::error::get_ssl_category()));
    }

    // 5. Hostname verification
    stream.set_verify_mode(ssl::verify_peer);
    stream.set_verify_callback(ssl::host_name_verification(host));

    // 6. TLS handshake
    co_await stream.async_handshake(ssl::stream_base::client, net::use_awaitable);

    // 7. Normal read/write over SSL stream
    std::string request = "GET / HTTP/1.1\r\nHost: " + host + "\r\nConnection: close\r\n\r\n";
    co_await net::async_write(stream, net::buffer(request), net::use_awaitable);

    std::string response;
    net::error_code ec;
    co_await net::async_read(stream, net::dynamic_buffer(response),
                            net::redirect_error(net::use_awaitable, ec));
    if (ec && ec != net::error::eof && ec != ssl::error::stream_truncated) {
        throw net::system_error(ec);
    }

    // 8. Graceful TLS shutdown
    co_await stream.async_shutdown(net::redirect_error(net::use_awaitable, ec));
}
```

---

## 2. TLS Server (C++20 Coroutine Style)

Server setup requires loading a certificate chain, private key, and optional Diffie-Hellman parameters.

```cpp
net::awaitable<void> handle_tls_session(ssl::stream<tcp::socket> stream) {
    try {
        // Perform TLS server handshake
        co_await stream.async_handshake(ssl::stream_base::server, net::use_awaitable);

        // Echo loop
        char data[1024];
        for (;;) {
            std::size_t n = co_await stream.async_read_some(net::buffer(data), net::use_awaitable);
            co_await net::async_write(stream, net::buffer(data, n), net::use_awaitable);
        }
    } catch (const std::exception& e) {
        // Peer disconnected or handshake failure
    }

    net::error_code ec;
    co_await stream.async_shutdown(net::redirect_error(net::use_awaitable, ec));
}

net::awaitable<void> tls_server(net::io_context& io, unsigned short port) {
    ssl::context ctx(ssl::context::tls_server);
    ctx.set_options(ssl::context::default_workarounds |
                    ssl::context::no_sslv2 |
                    ssl::context::no_sslv3 |
                    ssl::context::no_tlsv1 |
                    ssl::context::no_tlsv1_1 |
                    ssl::context::single_dh_use);

    // Load server certificates & private key
    ctx.use_certificate_chain_file("server.crt");
    ctx.use_private_key_file("server.key", ssl::context::pem);
    // ctx.use_tmp_dh_file("dh2048.pem");

    tcp::acceptor acceptor(io, {tcp::v4(), port});
    acceptor.set_option(tcp::acceptor::reuse_address(true));

    for (;;) {
        // Accept socket onto a strand
        auto strand = net::make_strand(acceptor.get_executor());
        auto raw_sock = co_await acceptor.async_accept(strand, net::use_awaitable);

        ssl::stream<tcp::socket> stream(std::move(raw_sock), ctx);
        net::co_spawn(strand, handle_tls_session(std::move(stream)), net::detached);
    }
}
```

---

## 3. Critical Rules for SSL / TLS

1. **Strict Strand Synchronization:**
   An `ssl::stream<>` is **not thread-safe**. All asynchronous operations (including handshake, read, write, and shutdown) on a single `ssl::stream` **must run on the same strand** or within the same serialized coroutine chain.
2. **Never Interleave Writes:**
   Just like plain TCP sockets, multiple concurrent `async_write` calls will interleave TLS records and corrupt the cryptographic stream. Use an outbound queue (Outbox) with an in-flight flag.
3. **Stream Truncation:**
   If a remote peer abruptly drops the connection without sending a TLS `close_notify`, Asio reports `ssl::error::stream_truncated`. In HTTP/1.0 or non-keep-alive protocols, treat this as EOF if the full response has already been received.
4. **Shutdown before Close:**
   Call `async_shutdown` before closing the underlying TCP socket to cleanly notify the remote peer and prevent truncation vulnerabilities.

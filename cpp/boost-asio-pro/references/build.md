# Build Configuration

### Boost.Asio (Header-Only with Modern CMake)

Asio itself has been header-only since early Boost versions. Since Boost 1.69+, defining `BOOST_ERROR_CODE_HEADER_ONLY` makes `boost::system::error_code` header-only as well, eliminating the need to link `libboost_system`. In Boost 1.74+, `Boost::headers` is the recommended CMake target.

```cmake
cmake_minimum_required(VERSION 3.20)
project(myapp CXX)

find_package(Boost REQUIRED)
find_package(OpenSSL REQUIRED)          # if using SSL
find_package(Threads REQUIRED)

add_executable(myapp main.cpp)

target_link_libraries(myapp PRIVATE
    Boost::headers                       # header-only Asio
    OpenSSL::SSL OpenSSL::Crypto         # if using SSL
    Threads::Threads
)

target_compile_features(myapp PRIVATE cxx_std_20)

# REQUIRED for GCC coroutine support — build will fail without this
target_compile_options(myapp PRIVATE
    $<$<CXX_COMPILER_ID:GNU>:-fcoroutines>
)

# Header-only error_code (no Boost.System link needed)
target_compile_definitions(myapp PRIVATE BOOST_ERROR_CODE_HEADER_ONLY)

# Cross-platform: Windows requires Winsock libraries and Windows target version
if(WIN32)
    target_link_libraries(myapp PRIVATE ws2_32 mswsock)
    target_compile_definitions(myapp PRIVATE _WIN32_WINNT=0x0601) # Windows 7+ or 0x0A00 for Windows 10+
endif()
```

---

### Standalone Asio (Header-Only without Boost)

Standalone Asio does not depend on Boost and requires only standard C++ and system networking libraries.

```cmake
cmake_minimum_required(VERSION 3.20)
project(myapp CXX)

find_package(OpenSSL REQUIRED)          # if using SSL
find_package(Threads REQUIRED)

# If installed via package managers (brew / apt / vcpkg):
find_path(ASIO_INCLUDE_DIR asio.hpp HINTS /opt/homebrew/include /usr/include)

add_executable(myapp main.cpp)

target_include_directories(myapp PRIVATE ${ASIO_INCLUDE_DIR})
target_link_libraries(myapp PRIVATE
    OpenSSL::SSL OpenSSL::Crypto
    Threads::Threads
)
target_compile_features(myapp PRIVATE cxx_std_20)
target_compile_definitions(myapp PRIVATE ASIO_STANDALONE)

target_compile_options(myapp PRIVATE
    $<$<CXX_COMPILER_ID:GNU>:-fcoroutines>
)

if(WIN32)
    target_link_libraries(myapp PRIVATE ws2_32 mswsock)
    target_compile_definitions(myapp PRIVATE _WIN32_WINNT=0x0601)
endif()
```

---

### Dual-Mode CMake (Supports Both Boost and Standalone)

Allows switching between Boost.Asio and standalone Asio via `-DUSE_STANDALONE_ASIO=ON/OFF`.

```cmake
cmake_minimum_required(VERSION 3.20)
project(myapp CXX)

option(USE_STANDALONE_ASIO "Use standalone Asio instead of Boost.Asio" OFF)

find_package(OpenSSL REQUIRED)
find_package(Threads REQUIRED)

add_executable(myapp main.cpp)

if(USE_STANDALONE_ASIO)
    find_path(ASIO_INCLUDE_DIR asio.hpp HINTS /opt/homebrew/include /usr/include)
    target_include_directories(myapp PRIVATE ${ASIO_INCLUDE_DIR})
    target_compile_definitions(myapp PRIVATE USE_STANDALONE_ASIO ASIO_STANDALONE)
else()
    find_package(Boost REQUIRED)
    target_link_libraries(myapp PRIVATE Boost::headers)
    target_compile_definitions(myapp PRIVATE BOOST_ERROR_CODE_HEADER_ONLY)
endif()

target_link_libraries(myapp PRIVATE OpenSSL::SSL OpenSSL::Crypto Threads::Threads)
target_compile_features(myapp PRIVATE cxx_std_20)
target_compile_options(myapp PRIVATE $<$<CXX_COMPILER_ID:GNU>:-fcoroutines>)

if(WIN32)
    target_link_libraries(myapp PRIVATE ws2_32 mswsock)
    target_compile_definitions(myapp PRIVATE _WIN32_WINNT=0x0601)
endif()
```

---

## Macro and Header Management

1. **Define `BOOST_ERROR_CODE_HEADER_ONLY` in CMake, not source files:**
   Defining it via `target_compile_definitions` ensures consistent translation units and prevents `-Wmacro-redefined` compiler warnings.
2. **Windows Preprocessor Conflicts:**
   On Windows, include Asio headers before any file that includes `<windows.h>`, or define `WIN32_LEAN_AND_MEAN` and `NOMINMAX` in CMake to prevent Windows macro pollution (`min`, `max`, `ERROR`, etc.):
   ```cmake
   if(WIN32)
       target_compile_definitions(myapp PRIVATE WIN32_LEAN_AND_MEAN NOMINMAX)
   endif()
   ```
3. **Include Order:**
   ```cpp
   // Recommended clean include order
   #include <boost/asio.hpp>
   #include <boost/asio/ssl.hpp>
   #include <boost/asio/experimental/awaitable_operators.hpp>
   ```

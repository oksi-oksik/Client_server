cmake_minimum_required(VERSION 3.8)
project(102-cpp-protobuf)
set(CMAKE_CXX_STANDARD 17)

find_package(Protobuf REQUIRED)
include_directories(${CMAKE_SOURCE_DIR}/src ${CMAKE_BINARY_DIR}/src/protobuf)

add_subdirectory(src/protobuf)
add_subdirectory(src/async_server)

enable_testing()
add_subdirectory(tests)

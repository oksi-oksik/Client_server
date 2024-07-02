project(tests)

include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.13.0.zip
)

FetchContent_MakeAvailable(googletest)

add_executable(tests Test_DelimitedMessagesStreamParser.cpp Test_Helpers.cpp)
target_link_libraries(tests GTest::gtest_main ${Protobuf_LIBRARIES} protobuf)

include(GoogleTest)
gtest_discover_tests(tests)
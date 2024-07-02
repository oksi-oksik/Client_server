project(asioserver)
SET(Boost_USE_STATIC_LIBS ON)

find_package(Boost COMPONENTS log_setup log REQUIRED)
include_directories(${Boost_INCLUDE_DIR})
add_executable(asioserver main.cpp)
target_link_libraries(asioserver config++ ${Boost_LIBRARIES} ${Protobuf_LIBRARIES} protobuf)
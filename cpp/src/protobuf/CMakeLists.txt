project(protobuf)

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS message.proto)
add_library(protobuf ${PROTO_SRCS} ${PROTO_HDRS})


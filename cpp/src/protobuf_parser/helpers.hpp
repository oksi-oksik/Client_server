#include <iostream>
#include <fstream>
#include <message.pb.h>

#if GOOGLE_PROTOBUF_VERSION >= 3012004 
#define PROTOBUF_MESSAGE_BYTE_SIZE(message) ((message).ByteSizeLong()) 
#else 
#define PROTOBUF_MESSAGE_BYTE_SIZE(message) ((message).ByteSize()) 
#endif

template<typename Message>
std::shared_ptr<Message> parseDelimited(const void* data, size_t size, size_t* bytesConsumed = 0){
    google::protobuf::io::CodedInputStream coded_stream((const uint8_t*)data, size);

    uint32_t length;
    if (!coded_stream.ReadVarint32(&length)) {
        return nullptr;
    }

    if (length == 0) return nullptr;

    std::vector<uint8_t> bytes(length);
    if (!coded_stream.ReadRaw(bytes.data(), bytes.size())) {
        return nullptr;
    }
    
    std::shared_ptr<Message> message(new Message());
    if (!message->ParseFromArray(bytes.data(), bytes.size())) {
        throw std::runtime_error("Wrong data");
    }

    if (bytesConsumed) {
        *bytesConsumed = coded_stream.CurrentPosition();
    }

    return message;
};

typedef std::vector<char> Data; 
typedef std::shared_ptr<const Data> PointerToConstData; 
typedef std::shared_ptr<Data> PointerToData; 
template <typename Message> PointerToConstData serializeDelimited(const Message& msg) { 
    const size_t messageSize = PROTOBUF_MESSAGE_BYTE_SIZE(msg); 
    const size_t headerSize = google::protobuf::io::CodedOutputStream::VarintSize32(messageSize); 

    const PointerToData& result = std::make_shared<Data>(headerSize + messageSize); 
    google::protobuf::uint8* buffer = reinterpret_cast<google::protobuf::uint8*>(&*result->begin()); 

    google::protobuf::io::CodedOutputStream::WriteVarint32ToArray(messageSize, buffer); 
    msg.SerializeWithCachedSizesToArray(buffer + headerSize); 

    return result; 
}
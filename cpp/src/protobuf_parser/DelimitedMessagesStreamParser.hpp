#include "helpers.hpp"
#include <list>

template<typename MessageType>
class DelimitedMessagesStreamParser
{
public:
    typedef std::shared_ptr<const MessageType> PointerToConstValue;
    std::list<PointerToConstValue> parse(const std::string& data){
        std::list<PointerToConstValue> messages;
        m_buffer.insert(m_buffer.end(), data.begin(), data.end());
        size_t bytesConsumed;
        while (m_buffer.size() > 0) {
            auto message = parseDelimited<MessageType>(m_buffer.data(), m_buffer.size(), &bytesConsumed);
            if (message == nullptr) {
                break;
            }
            messages.push_back(message);
            m_buffer.erase(m_buffer.begin(), m_buffer.begin() + bytesConsumed);
        }
        return messages;
    };

private:
    std::vector<char> m_buffer;
};
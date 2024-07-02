#include <cstdlib>
#include <memory>
#include <utility>
#include <list>
#include <vector>
#include <typeinfo>
#include <boost/asio.hpp>
#include <google/protobuf/io/coded_stream.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>
#include <google/protobuf/io/zero_copy_stream.h>
#include "protobuf_parser/DelimitedMessagesStreamParser.hpp"

#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/utility/setup/file.hpp>
#include <boost/log/utility/setup/common_attributes.hpp>
namespace logging=boost::log;
namespace sinks = boost::log::sinks;
namespace keywords = boost::log::keywords;
namespace expr = boost::log::expressions;

#include <libconfig.h++>
using namespace libconfig;

#include <iomanip>
using namespace google::protobuf::io;

using boost::asio::ip::tcp;

#include <boost/date_time/posix_time/posix_time.hpp>
using namespace boost::posix_time;


google::protobuf::uint32 client_count = 0;

class session
    : public std::enable_shared_from_this<session>
{
public:
    session(tcp::socket socket)
        : socket_(std::move(socket))
    {
        client_count++;
        std::string sClientIp = socket_.remote_endpoint().address().to_string();
        unsigned short uiClientPort = socket_.remote_endpoint().port();
        BOOST_LOG_TRIVIAL(info) << "Connect with " << sClientIp << ' ' << uiClientPort << std::endl;
    }

    ~session(){
        client_count--;
        std::string sClientIp = socket_.remote_endpoint().address().to_string();
        unsigned short uiClientPort = socket_.remote_endpoint().port();
        BOOST_LOG_TRIVIAL(info) << "Disconnect with " << sClientIp << ' ' << uiClientPort << std::endl;
    }

    void start()
    {
        do_read();
    }

private:
    void do_read()
    {
        auto self(shared_from_this());
        socket_.async_read_some(boost::asio::buffer(data_, max_length),
            [this, self](boost::system::error_code ec, std::size_t length) 
            {   
                if (!ec)
                {

                    typedef DelimitedMessagesStreamParser<TestTask::Messages::WrapperMessage> Parser;
                    Parser parser;
                    typedef std::shared_ptr<const TestTask::Messages::WrapperMessage> PointerToConstValue;
                    int i = 0;
                    for(const char byte: data_)
                    {   
                        const std::list<PointerToConstValue>& parsedMessages = parser.parse(std::string(1, byte));
                        for(const PointerToConstValue& message: parsedMessages)
                        {
                            if (message->has_request_for_fast_response()) {
                                ptime t = microsec_clock::universal_time();
                                TestTask::Messages::WrapperMessage response;
                                response.mutable_fast_response()->set_current_date_time(to_iso_string(t));
                                do_write(response, length);
                            }
                            if (message->has_request_for_slow_response()) {
                                boost::asio::io_service io;
                                boost::asio::deadline_timer t(io, boost::posix_time::seconds(message->request_for_slow_response().time_in_seconds_to_sleep()));
                                t.async_wait([&](const boost::system::error_code& ec){
                                    if (!ec){
                                        TestTask::Messages::WrapperMessage response;
                                        response.mutable_slow_response()->set_connected_client_count(client_count);
                                        do_write(response, length);
                                    }
                                });
                                io.run();
                            }
                        }
                    }
                }
            });
    }

    void do_write(TestTask::Messages::WrapperMessage message, std::size_t length)
    {
        auto self(shared_from_this());

        auto data = serializeDelimited(message);

        boost::asio::async_write(socket_, boost::asio::buffer(data->data(), data->size()),
            [this, self](boost::system::error_code ec, std::size_t /*length*/)
            {
                if (!ec)
                {
                    
                    do_read();
                }
            });
    }

    tcp::socket socket_;
    enum { max_length = 1024 };
    char data_[max_length];
};

class server
{
public:
    boost::asio::ip::address_v4 addr;

    server(boost::asio::io_context& io_context, short port)
        : acceptor_(io_context, tcp::endpoint(addr.from_string("127.0.0.1"), port))
    {
        do_accept();
    }

private:
    void do_accept()
    {
        acceptor_.async_accept(
            [this](boost::system::error_code ec, tcp::socket socket)
            {
                if (!ec)
                {
                    std::make_shared<session>(std::move(socket))->start();
                }

                do_accept();
            });
    }

    tcp::acceptor acceptor_;
    bool flag = false;
};

void init_log()
{
    typedef boost::log::sinks::synchronous_sink< boost::log::sinks::text_file_backend > file_sink;
    boost::shared_ptr< file_sink > sink(new file_sink(
        boost::log::keywords::file_name = "../../../src/async_server/log_file.log",
        boost::log::keywords::rotation_size = 10 * 1024 * 1024,
        boost::log::keywords::time_based_rotation = boost::log::sinks::file::rotation_at_time_point(0, 0, 0),
        boost::log::keywords::auto_flush = true
    ));
    sink->set_formatter
    (
        expr::format("[%1%] <%2%> %3%")
            % expr::attr< boost::posix_time::ptime >("TimeStamp")
            % logging::trivial::severity
            % expr::smessage
    );

    logging::core::get()->add_sink(sink);
}

int main(int argc, char* argv[])
{   
    init_log();
    logging::add_common_attributes();

    Config cfg;
    int port;
    try{
        cfg.readFile("../../../src/async_server/config_file.cfg");
    }
    catch(const FileIOException &fioex){
        BOOST_LOG_TRIVIAL(error) << "I/O error while reading file.";
        return(EXIT_FAILURE);
    }
    catch(const ParseException &pex){
        BOOST_LOG_TRIVIAL(error) << "Parse error at " << pex.getFile() << ":" << pex.getLine() << " - " << pex.getError();
        return(EXIT_FAILURE);
    }
    try{
        port = cfg.lookup("port");
    }
    catch(const SettingNotFoundException &nfex){
        BOOST_LOG_TRIVIAL(error) << "No 'port' setting in configuration file.";
        return(EXIT_FAILURE);
    }
    
    try
    {
        boost::asio::io_context io_context;
        server s(io_context, port);

        io_context.run();
    }
    catch (std::exception& e)
    {
        BOOST_LOG_TRIVIAL(error) << "Exception: " << e.what();
    }

    return 0;
}
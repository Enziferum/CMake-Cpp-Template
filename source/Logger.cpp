#include <app/Logger.hpp>

#include <stdexcept>
#include <vector>

#include <spdlog/sinks/rotating_file_sink.h>
#include <spdlog/sinks/stdout_color_sinks.h>

namespace app {
    spdlog::level::level_enum Logger::toNative(LogLevel level) {
        switch(level) {
        case LogLevel::Trace: return spdlog::level::trace;
        case LogLevel::Debug: return spdlog::level::debug;
        case LogLevel::Info: return spdlog::level::info;
        case LogLevel::Warning: return spdlog::level::warn;
        case LogLevel::Error: return spdlog::level::err;
        case LogLevel::Critical: return spdlog::level::critical;
        case LogLevel::Off: return spdlog::level::off;
        }
        throw std::invalid_argument("Invalid log level");
    }

    Logger::Logger(std::string name, const LoggerConfig& config) {
        const auto nativeLevel = toNative(config.level);
        std::vector<spdlog::sink_ptr> sinks;
        if(config.console) {
            sinks.push_back(std::make_shared<spdlog::sinks::stdout_color_sink_mt>());
        }
        if(!config.filePath.empty()) {
            if(config.maxFileSize == 0 || config.maxFiles == 0) {
                throw std::invalid_argument("Log rotation limits must be positive");
            }
#ifdef _WIN32
            const auto filename = config.filePath.wstring();
#else
            const auto filename = config.filePath.string();
#endif
            sinks.push_back(std::make_shared<spdlog::sinks::rotating_file_sink_mt>(
                    filename, config.maxFileSize, config.maxFiles));
        }
        if(sinks.empty()) {
            throw std::invalid_argument("Logger requires a console or file sink");
        }
        m_logger = std::make_shared<spdlog::logger>(std::move(name), sinks.begin(), sinks.end());
        m_logger -> set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%n] [%^%l%$] [thread %t] %v");
        m_logger -> set_level(nativeLevel);
        m_logger -> flush_on(spdlog::level::err);
    }

    void Logger::setLevel(LogLevel level) {
        m_logger -> set_level(toNative(level));
    }

    LogLevel Logger::level() const {
        switch(m_logger -> level()) {
        case spdlog::level::trace: return LogLevel::Trace;
        case spdlog::level::debug: return LogLevel::Debug;
        case spdlog::level::info: return LogLevel::Info;
        case spdlog::level::warn: return LogLevel::Warning;
        case spdlog::level::err: return LogLevel::Error;
        case spdlog::level::critical: return LogLevel::Critical;
        case spdlog::level::off: return LogLevel::Off;
        default: throw std::logic_error("Unexpected backend log level");
        }
    }

    bool Logger::shouldLog(LogLevel level) const {
        const auto nativeLevel = toNative(level);
        return level != LogLevel::Off && m_logger -> should_log(nativeLevel);
    }

    void Logger::write(LogLevel level, std::string_view message) {
        if(shouldLog(level)) {
            m_logger -> log(toNative(level), spdlog::string_view_t(message.data(), message.size()));
        }
    }

    void Logger::flush() {
        m_logger -> flush();
    }
}

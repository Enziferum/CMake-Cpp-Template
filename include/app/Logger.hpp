#pragma once

#include <filesystem>
#include <memory>
#include <string>
#include <string_view>
#include <utility>

#include <spdlog/logger.h>

namespace app {
    enum class LogLevel {
        Trace,
        Debug,
        Info,
        Warning,
        Error,
        Critical,
        Off
    };

    struct LoggerConfig {
        LogLevel level = LogLevel::Info;
        bool console = true;
        std::filesystem::path filePath;
        std::size_t maxFileSize = 5 * 1024 * 1024;
        std::size_t maxFiles = 3;
    };

    // Synchronous, thread-safe output. Owns its backend without global registration.
    // Destroy only after all threads using this instance have finished.
    class Logger {
    public:
        explicit Logger(std::string name, const LoggerConfig& config = {});
        ~Logger() = default;

        Logger(const Logger&) = delete;
        Logger& operator=(const Logger&) = delete;

        void setLevel(LogLevel level);
        [[nodiscard]] LogLevel level() const;
        [[nodiscard]] bool shouldLog(LogLevel level) const;
        void flush();

        // Runtime text is always treated literally, including braces.
        void write(LogLevel level, std::string_view message);

        template<typename ... Args>
        void log(LogLevel level, spdlog::format_string_t<Args...> format, Args&&... args) {
            if(shouldLog(level)) {
                m_logger -> log(toNative(level), format, std::forward<Args>(args)...);
            }
        }

        template<typename ... Args>
        void trace(spdlog::format_string_t<Args...> format, Args&&... args) {
            log(LogLevel::Trace, format, std::forward<Args>(args)...);
        }

        template<typename ... Args>
        void debug(spdlog::format_string_t<Args...> format, Args&&... args) {
            log(LogLevel::Debug, format, std::forward<Args>(args)...);
        }

        template<typename ... Args>
        void info(spdlog::format_string_t<Args...> format, Args&&... args) {
            log(LogLevel::Info, format, std::forward<Args>(args)...);
        }

        template<typename ... Args>
        void warning(spdlog::format_string_t<Args...> format, Args&&... args) {
            log(LogLevel::Warning, format, std::forward<Args>(args)...);
        }

        template<typename ... Args>
        void error(spdlog::format_string_t<Args...> format, Args&&... args) {
            log(LogLevel::Error, format, std::forward<Args>(args)...);
        }

        template<typename ... Args>
        void critical(spdlog::format_string_t<Args...> format, Args&&... args) {
            log(LogLevel::Critical, format, std::forward<Args>(args)...);
        }

    private:
        static spdlog::level::level_enum toNative(LogLevel level);

        std::shared_ptr<spdlog::logger> m_logger;
    };
}

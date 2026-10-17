#include <app/Logger.hpp>

#include <atomic>
#include <chrono>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <thread>
#include <vector>

#include <gtest/gtest.h>

namespace {
    class LoggerTest : public testing::Test {
    protected:
        void SetUp() override {
            static std::atomic<unsigned> counter{0};
            const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
            directory = std::filesystem::temp_directory_path() /
                ("cpp-template-" + std::to_string(stamp) + "-" + std::to_string(counter++));
            std::filesystem::create_directory(directory);
            config.console = false;
            config.filePath = directory / std::filesystem::path(u8"журнал.log");
        }

        void TearDown() override {
            std::error_code error;
            std::filesystem::remove_all(directory, error);
        }

        std::string readLog() const {
            std::ifstream input(config.filePath, std::ios::binary);
            return {std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>()};
        }

        std::filesystem::path directory;
        app::LoggerConfig config;
    };
}

TEST_F(LoggerTest, FiltersLevelsAndSupportsRuntimeChanges) {
    app::Logger logger{"filter", config};
    logger.debug("hidden-debug");
    logger.info("visible-info {}", 42);
    logger.setLevel(app::LogLevel::Error);
    EXPECT_EQ(logger.level(), app::LogLevel::Error);
    logger.warning("hidden-warning");
    logger.error("visible-error");
    logger.setLevel(app::LogLevel::Off);
    logger.critical("hidden-critical");
    logger.write(app::LogLevel::Off, "hidden-off");
    logger.flush();
    const auto text = readLog();
    EXPECT_NE(text.find("visible-info 42"), std::string::npos);
    EXPECT_NE(text.find("visible-error"), std::string::npos);
    EXPECT_EQ(text.find("hidden-"), std::string::npos);
}

TEST_F(LoggerTest, PreservesLiteralRuntimeText) {
    app::Logger logger{"literal", config};
    logger.write(app::LogLevel::Info, "runtime {braces} and {} remain literal");
    logger.flush();
    EXPECT_NE(readLog().find("runtime {braces} and {} remain literal"), std::string::npos);
}

TEST_F(LoggerTest, InstancesHaveIndependentLevelsAndMayShareNames) {
    app::Logger first{"same-name", config};
    auto otherConfig = config;
    otherConfig.filePath = directory / "other.log";
    app::Logger second{"same-name", otherConfig};
    first.setLevel(app::LogLevel::Off);
    EXPECT_TRUE(second.shouldLog(app::LogLevel::Info));
    EXPECT_FALSE(first.shouldLog(app::LogLevel::Info));
}

TEST_F(LoggerTest, WritesFromMultipleThreads) {
    app::Logger logger{"workers", config};
    std::vector<std::jthread> workers;
    for(int worker = 0; worker < 4; ++worker) {
        workers.emplace_back([&logger, worker] {
            for(int item = 0; item < 40; ++item) {
                logger.info("message {}:{};", worker, item);
            }
        });
    }
    workers.clear();
    logger.flush();
    const auto text = readLog();
    for(int worker = 0; worker < 4; ++worker) {
        for(int item = 0; item < 40; ++item) {
            EXPECT_NE(text.find("message " + std::to_string(worker) + ":" +
                std::to_string(item) + ";"), std::string::npos);
        }
    }
}

TEST_F(LoggerTest, RotatesFiles) {
    config.maxFileSize = 256;
    config.maxFiles = 2;
    {
        app::Logger logger{"rotate", config};
        for(int index = 0; index < 30; ++index) {
            logger.info("rotation record {} with padding to fill the log", index);
        }
        logger.flush();
    }
    unsigned files = 0;
    for(const auto& entry : std::filesystem::directory_iterator(directory)) {
        if(entry.is_regular_file()) {
            ++files;
        }
    }
    EXPECT_EQ(files, 3u);
    EXPECT_NE(readLog().find("rotation record 29"), std::string::npos);
}

TEST(Logger, RejectsConfigurationWithoutSinks) {
    app::LoggerConfig config;
    config.console = false;
    EXPECT_THROW(app::Logger("invalid", config), std::invalid_argument);
}

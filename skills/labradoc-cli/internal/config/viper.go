package config

import (
	"fmt"
	"os"
	"strings"

	"github.com/spf13/viper"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

func InitConfig() {
	env := os.Getenv("ENVIRONMENT")
	if env == "" {
		env = "prod" // default
	}

	// Read base config first
	viper.SetConfigName("labrador")
	viper.SetConfigType("yaml")
	viper.AddConfigPath(".")
	viper.ReadInConfig() // ignore error, base file might not exist

	// Merge environment-specific config
	viper.SetConfigName(fmt.Sprintf("labrador.%s", env))
	viper.MergeInConfig() // Use MergeInConfig for override

	// Environment variables override everything
	viper.AutomaticEnv()
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

	if viper.GetBool("log.debug") {
		config := zap.NewDevelopmentConfig()
		config.Level = zap.NewAtomicLevelAt(zapcore.DebugLevel)
		logger, _ := config.Build()
		zap.ReplaceGlobals(logger)
	} else {
		config := zap.NewProductionConfig()
		logger, _ := config.Build()
		zap.ReplaceGlobals(logger)
	}
}

func InitTestConfig() {
	os.Setenv("ENVIRONMENT", "dev")
	InitConfig()
}

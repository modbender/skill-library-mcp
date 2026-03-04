package config

import (
	"fmt"
	"os"
)

const (
	BaseURL    = "https://api.caesar.xyz"
	EnvAPIKey  = "CAESAR_API_KEY"
)

func GetAPIKey() (string, error) {
	key := os.Getenv(EnvAPIKey)
	if key == "" {
		return "", fmt.Errorf("environment variable %s is not set", EnvAPIKey)
	}
	return key, nil
}

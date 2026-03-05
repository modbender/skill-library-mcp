package config

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

type SavedCookie struct {
	Name   string `json:"name"`
	Value  string `json:"value"`
	Domain string `json:"domain"`
	Path   string `json:"path"`
}

type Config struct {
	APIURL   string `json:"api_url"`
	Username string `json:"username"`
	Password string `json:"password"`
	// Saved session cookies (populated after successful login)
	Cookies []SavedCookie `json:"cookies,omitempty"`
}

func ConfigDir() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".canvas-cli")
}

func ConfigPath() string {
	return filepath.Join(ConfigDir(), "config.json")
}

func Load() (*Config, error) {
	data, err := os.ReadFile(ConfigPath())
	if err != nil {
		return nil, fmt.Errorf("not configured. Run: canvas-cli configure")
	}
	var cfg Config
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("corrupt config file: %w", err)
	}
	if cfg.APIURL == "" || cfg.Username == "" || cfg.Password == "" {
		return nil, fmt.Errorf("incomplete config. Run: canvas-cli configure")
	}
	return &cfg, nil
}

func Save(cfg *Config) error {
	if err := os.MkdirAll(ConfigDir(), 0700); err != nil {
		return err
	}
	data, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(ConfigPath(), data, 0600)
}

func RunSetup() (*Config, error) {
	reader := bufio.NewReader(os.Stdin)

	fmt.Println("=== Canvas CLI Configuration ===")
	fmt.Println()
	fmt.Println("Enter your Canvas login credentials.")
	fmt.Println("They will be stored locally in:", ConfigPath())
	fmt.Println()

	fmt.Print("Canvas URL (e.g. https://myschool.instructure.com): ")
	url, _ := reader.ReadString('\n')
	url = strings.TrimSpace(url)
	url = strings.TrimRight(url, "/")
	if !strings.HasPrefix(url, "https://") && !strings.HasPrefix(url, "http://") {
		url = "https://" + url
	}

	fmt.Print("Username / Email: ")
	username, _ := reader.ReadString('\n')
	username = strings.TrimSpace(username)

	fmt.Print("Password: ")
	password, _ := reader.ReadString('\n')
	password = strings.TrimSpace(password)

	if url == "" || username == "" || password == "" {
		return nil, fmt.Errorf("all fields are required")
	}

	cfg := &Config{
		APIURL:   url,
		Username: username,
		Password: password,
	}

	if err := Save(cfg); err != nil {
		return nil, fmt.Errorf("failed to save config: %w", err)
	}

	fmt.Println()
	fmt.Println("Configuration saved to", ConfigPath())
	return cfg, nil
}

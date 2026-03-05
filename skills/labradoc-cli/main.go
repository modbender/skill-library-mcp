package main

import (
	"github.com/zamedic/labradoc-cli/cmd"
	"github.com/zamedic/labradoc-cli/internal/config"
)

func main() {
	config.InitConfig()
	cmd.Execute()
}

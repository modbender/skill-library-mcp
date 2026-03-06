package cmd

import (
	"fmt"
	"os"

	"canvas-cli/internal/ui"
)

func runDebugLogin() {
	fmt.Println()
	ui.Header("Debug Login Flow")
	fmt.Println()

	client.Debug = true
	err := client.Login()
	if err != nil {
		fmt.Println()
		ui.Error(err.Error())
		os.Exit(1)
	}

	fmt.Println()
	ui.Success("Login successful! API access confirmed.")
	fmt.Println()
}

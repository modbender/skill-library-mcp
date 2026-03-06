package main

import (
	"os"

	"github.com/blanxlait/krocli/internal/cmd"
)

func main() {
	os.Exit(cmd.Execute())
}

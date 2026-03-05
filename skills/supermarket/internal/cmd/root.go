package cmd

import (
	"os"

	"github.com/alecthomas/kong"
	"github.com/blanxlait/krocli/internal/ui"
)

type RootFlags struct {
	JSON  bool `short:"j" help:"Output JSON to stdout."`
	Plain bool `short:"p" help:"Output plain/TSV to stdout."`
}

type CLI struct {
	RootFlags

	Auth      AuthCmd      `cmd:"" help:"Authentication commands."`
	Products  ProductsCmd  `cmd:"" help:"Product commands."`
	Locations LocationsCmd `cmd:"" help:"Location commands."`
	Cart      CartCmd      `cmd:"" help:"Cart commands."`
	Identity  IdentityCmd  `cmd:"" help:"Identity commands."`
}

func Execute() int {
	var cli CLI
	ctx := kong.Parse(&cli,
		kong.Name("krocli"),
		kong.Description("Kroger API CLI tool"),
		kong.UsageOnError(),
	)
	if err := ctx.Run(&cli.RootFlags); err != nil {
		ui.Error("%v", err)
		return 1
	}
	return 0
}

var fmtStderr = os.Stderr

package cmd

import (
	"errors"

	"github.com/blanxlait/krocli/internal/config"
	"github.com/blanxlait/krocli/internal/krogerapi"
	"github.com/blanxlait/krocli/internal/ui"
)

type CartCmd struct {
	Add CartAddCmd `cmd:"" help:"Add item to cart."`
}

type CartAddCmd struct {
	UPC string `required:"" help:"Product UPC." long:"upc"`
	Qty int    `help:"Quantity." default:"1" long:"qty"`
}

func (c *CartAddCmd) Run(flags *RootFlags) error {
	creds, err := config.LoadCredentials()
	if err != nil && !errors.Is(err, config.ErrNoCredentials) {
		return err
	}
	client := krogerapi.NewClient(creds)
	err = client.AddToCart([]krogerapi.CartItem{{UPC: c.UPC, Quantity: c.Qty}})
	if err != nil {
		return err
	}
	ui.Success("Added %s (qty %d) to cart.", c.UPC, c.Qty)
	return nil
}

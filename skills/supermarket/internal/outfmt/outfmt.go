package outfmt

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

func PrintJSON(v any) error {
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	return enc.Encode(v)
}

func PrintPlain(rows [][]string) {
	for _, row := range rows {
		fmt.Println(strings.Join(row, "\t"))
	}
}

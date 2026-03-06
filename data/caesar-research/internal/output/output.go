package output

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
)

// Stdout and Stderr are the writers used for output. Tests can replace these.
var (
	Stdout io.Writer = os.Stdout
	Stderr io.Writer = os.Stderr
)

// ExitFunc is called to exit the process. Tests can replace this.
var ExitFunc = os.Exit

// JSON prints v as indented JSON to Stdout.
func JSON(v any) {
	enc := json.NewEncoder(Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(v); err != nil {
		fmt.Fprintf(Stderr, "Error encoding output: %v\n", err)
	}
}

// Error prints an error message to Stderr and exits.
func Error(format string, args ...any) {
	fmt.Fprintf(Stderr, "Error: "+format+"\n", args...)
	ExitFunc(1)
}

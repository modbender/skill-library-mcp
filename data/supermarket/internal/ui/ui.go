package ui

import (
	"fmt"
	"os"

	"github.com/muesli/termenv"
)

var output = termenv.NewOutput(os.Stderr)

func Info(msg string, args ...any) {
	_, _ = fmt.Fprintln(os.Stderr, output.String(fmt.Sprintf(msg, args...)).Foreground(output.Color("12")).String())
}

func Success(msg string, args ...any) {
	_, _ = fmt.Fprintln(os.Stderr, output.String(fmt.Sprintf(msg, args...)).Foreground(output.Color("10")).String())
}

func Error(msg string, args ...any) {
	_, _ = fmt.Fprintln(os.Stderr, output.String(fmt.Sprintf(msg, args...)).Foreground(output.Color("9")).String())
}

func Warn(msg string, args ...any) {
	_, _ = fmt.Fprintln(os.Stderr, output.String(fmt.Sprintf(msg, args...)).Foreground(output.Color("11")).String())
}

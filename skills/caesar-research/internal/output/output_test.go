package output

import (
	"bytes"
	"os"
	"runtime"
	"strings"
	"testing"
)

func restoreDefaults() func() {
	origOut, origErr, origExit := Stdout, Stderr, ExitFunc
	return func() {
		Stdout = origOut
		Stderr = origErr
		ExitFunc = origExit
	}
}

func TestJSON_Struct(t *testing.T) {
	defer restoreDefaults()()
	var buf bytes.Buffer
	Stdout = &buf

	JSON(struct {
		Name string `json:"name"`
	}{Name: "test"})

	got := buf.String()
	if !strings.Contains(got, `"name": "test"`) {
		t.Errorf("JSON output = %q, want to contain %q", got, `"name": "test"`)
	}
}

func TestJSON_Nil(t *testing.T) {
	defer restoreDefaults()()
	var buf bytes.Buffer
	Stdout = &buf

	JSON(nil)

	got := strings.TrimSpace(buf.String())
	if got != "null" {
		t.Errorf("JSON(nil) = %q, want %q", got, "null")
	}
}

func TestJSON_Indented(t *testing.T) {
	defer restoreDefaults()()
	var buf bytes.Buffer
	Stdout = &buf

	JSON(map[string]int{"a": 1})

	got := buf.String()
	if !strings.Contains(got, "  ") {
		t.Errorf("JSON output should be indented, got %q", got)
	}
}

func TestError_WritesToStderr(t *testing.T) {
	defer restoreDefaults()()
	var buf bytes.Buffer
	Stderr = &buf
	ExitFunc = func(int) {} // prevent exit

	Error("something went %s", "wrong")

	got := buf.String()
	want := "Error: something went wrong\n"
	if got != want {
		t.Errorf("Error() wrote %q to stderr, want %q", got, want)
	}
}

func TestError_CallsExitWithOne(t *testing.T) {
	defer restoreDefaults()()
	Stderr = &bytes.Buffer{}

	var gotCode int
	var didExit bool

	ExitFunc = func(code int) {
		gotCode = code
		didExit = true
		// Use runtime.Goexit to stop execution like os.Exit would,
		// but in a way that's safe for tests.
		runtime.Goexit()
	}

	done := make(chan struct{})
	go func() {
		defer close(done)
		Error("fail")
	}()
	<-done

	if !didExit {
		t.Error("ExitFunc was not called")
	}
	if gotCode != 1 {
		t.Errorf("exit code = %d, want 1", gotCode)
	}
}

func TestJSON_EncodingError(t *testing.T) {
	defer restoreDefaults()()
	var stdoutBuf, stderrBuf bytes.Buffer
	Stdout = &stdoutBuf
	Stderr = &stderrBuf

	// Channels cannot be JSON-encoded.
	JSON(make(chan int))

	if stderrBuf.Len() == 0 {
		t.Error("expected error on stderr for non-encodable type")
	}
}

// Verify defaults point to the real os.Stdout/os.Stderr.
func TestDefaults(t *testing.T) {
	if Stdout != os.Stdout {
		t.Error("default Stdout should be os.Stdout")
	}
	if Stderr != os.Stderr {
		t.Error("default Stderr should be os.Stderr")
	}
}

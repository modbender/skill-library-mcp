package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

type Config struct {
	IntervalMinutes       int      `json:"interval_minutes"`
	OpenClawBin            string   `json:"openclaw_bin"`
	HealthCmd              []string `json:"health_cmd"`
	RestartCmd             []string `json:"restart_cmd"`
	InstallCmd             []string `json:"install_cmd"`
	StartCmd               []string `json:"start_cmd"`
	BootstrapCmd           []string `json:"bootstrap_cmd"`
	GatewayPlistPath       string   `json:"gateway_plist_path"`
	DoctorCmd              []string `json:"doctor_cmd"`
	StatusCmd              []string `json:"status_cmd"`
	HealthTimeoutSeconds   int      `json:"health_timeout_seconds"`
	RestartBackoffSeconds  int      `json:"restart_backoff_seconds"`
	MaxRestartAttempts     int      `json:"max_restart_attempts"`
	ConfigPath             string   `json:"config_path"`
	BackupDir              string   `json:"backup_dir"`
	StatePath              string   `json:"state_path"`
	AutoRollback           bool     `json:"auto_rollback"`
	LogPath                string   `json:"log_path"`
	LogToStdout            bool     `json:"log_to_stdout"`
	VerboseLogs            bool     `json:"verbose_logs"`
	LogHealthOk            bool     `json:"log_health_ok"`
}

type State struct {
	LastConfigHash string `json:"last_config_hash"`
	LastBackup     string `json:"last_backup"`
	LastGoodBackup string `json:"last_good_backup"`
}

func defaultConfig() Config {
	home, _ := os.UserHomeDir()
	base := filepath.Join(home, ".openclaw-guardian")
	return Config{
		IntervalMinutes:      3,
		OpenClawBin:           "openclaw",
		HealthCmd:             []string{"openclaw", "health", "--json"},
		RestartCmd:            []string{"openclaw", "gateway", "restart"},
		InstallCmd:            []string{"openclaw", "gateway", "install"},
		StartCmd:              []string{"openclaw", "gateway", "start"},
		GatewayPlistPath:       filepath.Join(home, "Library", "LaunchAgents", "ai.openclaw.gateway.plist"),
		DoctorCmd:             []string{"openclaw", "doctor", "--non-interactive"},
		StatusCmd:             []string{"openclaw", "status", "--deep"},
		HealthTimeoutSeconds:  20,
		RestartBackoffSeconds: 8,
		MaxRestartAttempts:    2,
		ConfigPath:            filepath.Join(home, ".openclaw", "openclaw.json"),
		BackupDir:             filepath.Join(base, "backups"),
		StatePath:             filepath.Join(base, "state.json"),
		AutoRollback:          true,
		LogPath:               filepath.Join(base, "guardian.log"),
		LogToStdout:           false,
		VerboseLogs:           false,
		LogHealthOk:           false,
	}
}

func ensureDir(path string) error {
	return os.MkdirAll(path, 0o755)
}

func loadConfig(path string) (Config, error) {
	cfg := defaultConfig()
	data, err := os.ReadFile(path)
	if err != nil {
		return cfg, err
	}
	if err := json.Unmarshal(data, &cfg); err != nil {
		return cfg, err
	}
	cfg = expandConfigPaths(cfg)
	cfg = normalizeCommands(cfg)
	return cfg, nil
}

func saveConfig(path string, cfg Config) error {
	if err := ensureDir(filepath.Dir(path)); err != nil {
		return err
	}
	cfg = normalizeCommands(cfg)
	data, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, data, 0o644)
}

func expandConfigPaths(cfg Config) Config {
	cfg.ConfigPath = expandPath(cfg.ConfigPath)
	cfg.BackupDir = expandPath(cfg.BackupDir)
	cfg.StatePath = expandPath(cfg.StatePath)
	cfg.LogPath = expandPath(cfg.LogPath)
	cfg.GatewayPlistPath = expandPath(cfg.GatewayPlistPath)
	return cfg
}

func expandPath(p string) string {
	if p == "" {
		return p
	}
	if strings.HasPrefix(p, "~") {
		home, _ := os.UserHomeDir()
		p = filepath.Join(home, strings.TrimPrefix(p, "~"))
	}
	return os.ExpandEnv(p)
}

func normalizeCommands(cfg Config) Config {
	if cfg.OpenClawBin == "" {
		return cfg
	}
	cfg.HealthCmd = normalizeCommand(cfg.HealthCmd, cfg.OpenClawBin)
	cfg.RestartCmd = normalizeCommand(cfg.RestartCmd, cfg.OpenClawBin)
	cfg.InstallCmd = normalizeCommand(cfg.InstallCmd, cfg.OpenClawBin)
	cfg.StartCmd = normalizeCommand(cfg.StartCmd, cfg.OpenClawBin)
	cfg.DoctorCmd = normalizeCommand(cfg.DoctorCmd, cfg.OpenClawBin)
	cfg.StatusCmd = normalizeCommand(cfg.StatusCmd, cfg.OpenClawBin)
	return cfg
}

func normalizeCommand(cmd []string, bin string) []string {
	if len(cmd) == 0 {
		return cmd
	}
	if cmd[0] == "openclaw" && bin != "" {
		cmd = append([]string{bin}, cmd[1:]...)
	}
	return cmd
}

func loadState(path string) (State, error) {
	var st State
	data, err := os.ReadFile(path)
	if err != nil {
		return st, err
	}
	if err := json.Unmarshal(data, &st); err != nil {
		return st, err
	}
	return st, nil
}

func saveState(path string, st State) error {
	if err := ensureDir(filepath.Dir(path)); err != nil {
		return err
	}
	data, err := json.MarshalIndent(st, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, data, 0o644)
}

type Logger struct {
	w io.Writer
}

func newLogger(path string, toStdout bool) (*Logger, error) {
	if err := ensureDir(filepath.Dir(path)); err != nil {
		return nil, err
	}
	f, err := os.OpenFile(path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil {
		return nil, err
	}
	if toStdout {
		return &Logger{w: io.MultiWriter(os.Stdout, f)}, nil
	}
	return &Logger{w: f}, nil
}

func (l *Logger) Printf(format string, args ...any) {
	ts := time.Now().Format("2006-01-02 15:04:05")
	fmt.Fprintf(l.w, "%s "+format+"\n", append([]any{ts}, args...)...)
}

func logCommand(log *Logger, label string, out, errOut string, code int, err error, verbose bool) {
	if verbose {
		log.Printf("%s (code=%d err=%v) stdout=%q stderr=%q", label, code, err, trim(out), trim(errOut))
		return
	}
	msg := shortMsg(out, errOut)
	if msg == "" {
		log.Printf("%s (code=%d err=%v)", label, code, err)
		return
	}
	log.Printf("%s (code=%d err=%v) msg=%q", label, code, err, msg)
}

func fileHash(path string) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer f.Close()
	h := sha256.New()
	if _, err := io.Copy(h, f); err != nil {
		return "", err
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}

func backupIfChanged(cfg Config, st State, log *Logger) (State, error) {
	_, err := os.Stat(cfg.ConfigPath)
	if err != nil {
		if errors.Is(err, fs.ErrNotExist) {
			return st, nil
		}
		return st, err
	}
	h, err := fileHash(cfg.ConfigPath)
	if err != nil {
		return st, err
	}
	if h == st.LastConfigHash {
		return st, nil
	}
	if err := ensureDir(cfg.BackupDir); err != nil {
		return st, err
	}
	timestamp := time.Now().Format("20060102-150405")
	backupName := fmt.Sprintf("openclaw.json.%s", timestamp)
	backupPath := filepath.Join(cfg.BackupDir, backupName)
	if err := copyFile(cfg.ConfigPath, backupPath); err != nil {
		return st, err
	}
	log.Printf("config changed; backed up to %s", backupPath)
	st.LastConfigHash = h
	st.LastBackup = backupPath
	return st, nil
}

func recordLastGood(cfg Config, st State, log *Logger) State {
	_, err := os.Stat(cfg.ConfigPath)
	if err != nil {
		return st
	}
	h, err := fileHash(cfg.ConfigPath)
	if err != nil {
		return st
	}
	if h == st.LastConfigHash && st.LastGoodBackup != "" {
		return st
	}
	if err := ensureDir(cfg.BackupDir); err != nil {
		return st
	}
	timestamp := time.Now().Format("20060102-150405")
	backupName := fmt.Sprintf("openclaw.good.%s", timestamp)
	backupPath := filepath.Join(cfg.BackupDir, backupName)
	if err := copyFile(cfg.ConfigPath, backupPath); err != nil {
		return st
	}
	log.Printf("recorded last-known-good config to %s", backupPath)
	st.LastGoodBackup = backupPath
	st.LastConfigHash = h
	return st
}

func copyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	if err := ensureDir(filepath.Dir(dst)); err != nil {
		return err
	}
	out, err := os.OpenFile(dst, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	defer out.Close()
	if _, err := io.Copy(out, in); err != nil {
		return err
	}
	return out.Close()
}

func runCommand(ctx context.Context, args []string) (string, string, int, error) {
	if len(args) == 0 {
		return "", "", -1, errors.New("empty command")
	}
	cmd := exec.CommandContext(ctx, args[0], args[1:]...)
	var stdout, stderr strings.Builder
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	err := cmd.Run()
	exitCode := 0
	if err != nil {
		if ee := new(exec.ExitError); errors.As(err, &ee) {
			exitCode = ee.ExitCode()
		} else {
			exitCode = -1
		}
	}
	return stdout.String(), stderr.String(), exitCode, err
}

type HealthResult struct {
	ok     bool
	stdout string
	stderr string
	code   int
	err    error
}

func healthCheck(cfg Config, log *Logger) HealthResult {
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(cfg.HealthTimeoutSeconds)*time.Second)
	defer cancel()
	out, errOut, code, err := runCommand(ctx, cfg.HealthCmd)
	if err == nil && code == 0 {
		return HealthResult{ok: true, stdout: out, stderr: errOut, code: code, err: err}
	}
	return HealthResult{ok: false, stdout: out, stderr: errOut, code: code, err: err}
}

func trim(s string) string {
	s = strings.TrimSpace(s)
	if len(s) > 800 {
		return s[:800] + "..."
	}
	return s
}

func shortMsg(out, errOut string) string {
	s := strings.TrimSpace(errOut)
	if s == "" {
		s = strings.TrimSpace(out)
	}
	if s == "" {
		return ""
	}
	first, _, _ := strings.Cut(s, "\n")
	if len(first) > 200 {
		return first[:200] + "..."
	}
	return first
}

func restart(cfg Config, log *Logger) {
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	out, errOut, code, err := runCommand(ctx, cfg.RestartCmd)
	logCommand(log, "restart", out, errOut, code, err, cfg.VerboseLogs)
	if requiresInstall(out, errOut) {
		handleServiceNotLoaded(cfg, log)
	}
}

func runDoctor(cfg Config, log *Logger) {
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()
	out, errOut, code, err := runCommand(ctx, cfg.DoctorCmd)
	logCommand(log, "doctor", out, errOut, code, err, cfg.VerboseLogs)
}

func runStatus(cfg Config, log *Logger) {
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()
	out, errOut, code, err := runCommand(ctx, cfg.StatusCmd)
	logCommand(log, "status", out, errOut, code, err, cfg.VerboseLogs)
}

func rollbackToPrevious(cfg Config, log *Logger) bool {
	paths := candidateBackups(cfg)
	if len(paths) == 0 {
		log.Printf("rollback: no candidate backups found")
		return false
	}
	prev := paths[0]
	if err := copyFile(prev, cfg.ConfigPath); err != nil {
		log.Printf("rollback: copy failed: %v", err)
		return false
	}
	log.Printf("rollback: restored %s to %s", prev, cfg.ConfigPath)
	return true
}

type backupEntry struct {
	path string
	mod  time.Time
}

func candidateBackups(cfg Config) []string {
	var entries []backupEntry
	addFile := func(p string) {
		info, err := os.Stat(p)
		if err != nil || info.IsDir() {
			return
		}
		entries = append(entries, backupEntry{path: p, mod: info.ModTime()})
	}

	// Guardian backups.
	if list, err := os.ReadDir(cfg.BackupDir); err == nil {
		for _, e := range list {
			if e.IsDir() {
				continue
			}
			addFile(filepath.Join(cfg.BackupDir, e.Name()))
		}
	}

	// OpenClaw native backups (openclaw.json.bak*, .bak.N, .bak-YYYY...).
	cfgDir := filepath.Dir(cfg.ConfigPath)
	if matches, err := filepath.Glob(filepath.Join(cfgDir, "openclaw.json.bak*")); err == nil {
		for _, m := range matches {
			addFile(m)
		}
	}
	addFile(filepath.Join(cfgDir, "openclaw.json.bak"))

	// Last known good snapshot, if present.
	if cfgDir != "" {
		addFile(filepath.Join(cfg.BackupDir, "openclaw.good.latest"))
	}

	if len(entries) == 0 {
		return nil
	}
	sort.Slice(entries, func(i, j int) bool {
		return entries[i].mod.After(entries[j].mod)
	})
	var paths []string
	for _, e := range entries {
		paths = append(paths, e.path)
	}
	return paths
}

func writeLatestGoodMarker(cfg Config, st State) {
	if st.LastGoodBackup == "" {
		return
	}
	_ = copyFile(st.LastGoodBackup, filepath.Join(cfg.BackupDir, "openclaw.good.latest"))
}

func rollbackToPreviousWithState(cfg Config, st State, log *Logger) bool {
	_ = st
	return rollbackToPrevious(cfg, log)
}

func requiresInstall(out, errOut string) bool {
	return strings.Contains(out, "Gateway service not loaded") ||
		strings.Contains(errOut, "Gateway service not loaded")
}

func installGateway(cfg Config, log *Logger) {
	if len(cfg.InstallCmd) == 0 {
		log.Printf("install skipped: missing install_cmd")
		return
	}
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()
	out, errOut, code, err := runCommand(ctx, cfg.InstallCmd)
	logCommand(log, "install", out, errOut, code, err, cfg.VerboseLogs)
}

func bootstrapGateway(cfg Config, log *Logger) {
	var cmd []string
	if len(cfg.BootstrapCmd) > 0 {
		cmd = cfg.BootstrapCmd
	} else if cfg.GatewayPlistPath != "" {
		cmd = []string{"launchctl", "bootstrap", fmt.Sprintf("gui/%d", os.Getuid()), cfg.GatewayPlistPath}
	} else {
		log.Printf("bootstrap skipped: missing gateway_plist_path and bootstrap_cmd")
		return
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	out, errOut, code, err := runCommand(ctx, cmd)
	logCommand(log, "bootstrap", out, errOut, code, err, cfg.VerboseLogs)
}

func shouldTryStart(res HealthResult) bool {
	msg := res.stderr
	return strings.Contains(msg, "gateway closed") ||
		strings.Contains(msg, "Connection refused") ||
		strings.Contains(msg, "ECONNREFUSED") ||
		strings.Contains(msg, "Gateway service not loaded")
}

func startGateway(cfg Config, log *Logger) bool {
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()
	out, errOut, code, err := runCommand(ctx, cfg.StartCmd)
	logCommand(log, "start", out, errOut, code, err, cfg.VerboseLogs)
	return requiresInstall(out, errOut)
}

func handleServiceNotLoaded(cfg Config, log *Logger) {
	if cfg.GatewayPlistPath != "" {
		if _, err := os.Stat(cfg.GatewayPlistPath); err == nil {
			log.Printf("service not loaded but plist exists; bootstrapping")
			bootstrapGateway(cfg, log)
			return
		}
	}
	log.Printf("service not loaded; installing gateway")
	installGateway(cfg, log)
	bootstrapGateway(cfg, log)
}

func main() {
	cfgPath := ""
	if len(os.Args) > 1 {
		cfgPath = os.Args[1]
	}
	if cfgPath == "" {
		home, _ := os.UserHomeDir()
		cfgPath = filepath.Join(home, ".openclaw-guardian", "config.json")
	}

	cfg, err := loadConfig(cfgPath)
	if err != nil {
		cfg = defaultConfig()
		_ = saveConfig(cfgPath, cfg)
	}

	log, err := newLogger(cfg.LogPath, cfg.LogToStdout)
	if err != nil {
		fmt.Fprintf(os.Stderr, "failed to open log: %v\n", err)
		os.Exit(1)
	}

	log.Printf("guardian started (interval=%d minutes)", cfg.IntervalMinutes)
	log.Printf("config: %s", cfg.ConfigPath)

	st, err := loadState(cfg.StatePath)
	if err != nil {
		st = State{}
	}

	tick := time.NewTicker(time.Duration(cfg.IntervalMinutes) * time.Minute)
	defer tick.Stop()

	lastHealthy := false
	for {
		st, _ = backupIfChanged(cfg, st, log)
		_ = saveState(cfg.StatePath, st)

		res := healthCheck(cfg, log)
		if res.ok {
			st = recordLastGood(cfg, st, log)
			writeLatestGoodMarker(cfg, st)
			_ = saveState(cfg.StatePath, st)
			if !lastHealthy && cfg.LogHealthOk {
				log.Printf("health ok")
			}
			lastHealthy = true
			<-tick.C
			continue
		}

		if lastHealthy {
			if cfg.VerboseLogs {
				logCommand(log, "health failed", res.stdout, res.stderr, res.code, res.err, true)
			} else {
				log.Printf("health failed: %s", shortMsg(res.stdout, res.stderr))
			}
		}
		lastHealthy = false

		if shouldTryStart(res) {
			log.Printf("gateway appears stopped; attempting start")
			if startGateway(cfg, log) {
				handleServiceNotLoaded(cfg, log)
				_ = startGateway(cfg, log)
			}
			time.Sleep(time.Duration(cfg.RestartBackoffSeconds) * time.Second)
			if healthCheck(cfg, log).ok {
				log.Printf("recovered after start")
				lastHealthy = true
				goto nextTick
			}
		}

		runStatus(cfg, log)

		for i := 0; i < cfg.MaxRestartAttempts; i++ {
			restart(cfg, log)
			time.Sleep(time.Duration(cfg.RestartBackoffSeconds) * time.Second)
			if healthCheck(cfg, log).ok {
				log.Printf("recovered after restart")
				lastHealthy = true
				goto nextTick
			}
		}

		runDoctor(cfg, log)

		if cfg.AutoRollback {
			if rollbackToPreviousWithState(cfg, st, log) {
				restart(cfg, log)
				time.Sleep(time.Duration(cfg.RestartBackoffSeconds) * time.Second)
				if healthCheck(cfg, log).ok {
					log.Printf("recovered after rollback")
					lastHealthy = true
					goto nextTick
				}
				log.Printf("rollback attempted but still unhealthy")
			}
		}

		nextTick:
		<-tick.C
	}
}

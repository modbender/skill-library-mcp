/**
 * @file logger.js
 * @author kelexine <https://github.com/kelexine>
 * @description Structured, leveled logger. Writes to stderr to keep stdout
 *              clean for tool output. Supports plain (TTY-colored) and JSON modes.
 */

const LEVELS = Object.freeze({ debug: 0, info: 1, warn: 2, error: 3, silent: 4 });

const ANSI = Object.freeze({
	debug: "\x1b[36m",  // cyan
	info:  "\x1b[32m",  // green
	warn:  "\x1b[33m",  // yellow
	error: "\x1b[31m",  // red
	reset: "\x1b[0m",
	dim:   "\x1b[2m",
	bold:  "\x1b[1m",
});

class Logger {
	/**
	 * @param {object}  opts
	 * @param {string}  opts.level    - Minimum level to emit
	 * @param {boolean} opts.json     - Emit newline-delimited JSON
	 * @param {string}  [opts.prefix] - Optional prefix / child label
	 */
	constructor({ level = "info", json = false, prefix = "" } = {}) {
		this.level  = LEVELS[level] ?? LEVELS.info;
		this.json   = json;
		this.prefix = prefix;
		this.isTTY  = process.stderr.isTTY ?? false;
	}

	_shouldLog(level) {
		return LEVELS[level] >= this.level;
	}

	_format(level, message, meta = {}) {
		const ts = new Date().toISOString();

		if (this.json) {
			const entry = { ts, level, message };
			if (this.prefix) entry.logger = this.prefix;
			if (Object.keys(meta).length) entry.meta = meta;
			return JSON.stringify(entry);
		}

		const c     = this.isTTY ? ANSI[level] : "";
		const reset = this.isTTY ? ANSI.reset   : "";
		const dim   = this.isTTY ? ANSI.dim      : "";
		const tag   = this.prefix ? ` [${this.prefix}]` : "";
		const metaStr = Object.keys(meta).length
			? `  ${dim}${JSON.stringify(meta)}${reset}`
			: "";

		return `${dim}${ts}${reset} ${c}${level.toUpperCase().padEnd(5)}${reset}${tag} ${message}${metaStr}`;
	}

	_emit(level, message, meta = {}) {
		if (!this._shouldLog(level)) return;
		process.stderr.write(this._format(level, message, meta) + "\n");
	}

	debug(message, meta) { this._emit("debug", message, meta); }
	info (message, meta) { this._emit("info",  message, meta); }
	warn (message, meta) { this._emit("warn",  message, meta); }
	error(message, meta) { this._emit("error", message, meta); }

	/** Create a child logger that inherits settings but adds a label. */
	child(prefix) {
		return new Logger({ level: Object.keys(LEVELS).find(k => LEVELS[k] === this.level), json: this.json, prefix });
	}
}

export const logger = new Logger({
	level: process.env.LOG_LEVEL ?? "info",
	json:  process.env.LOG_JSON  === "true",
});

#!/usr/bin/env node

/**
 * Session token manager — save, load, and check login status.
 *
 * Usage:
 *   node session-token.js save <sessionToken>   — persist the token
 *   node session-token.js load                  — print the saved token (exits 1 if none)
 *   node session-token.js check                 — print login status JSON
 *   node session-token.js clear                 — delete saved token (logout)
 *
 * The token is stored in .session_token in the same directory.
 */

const fs = require("fs")
const path = require("path")

const TOKEN_FILE = path.join(__dirname, ".session_token")

function saveToken(token) {
	fs.writeFileSync(TOKEN_FILE, token, "utf-8")
	process.stdout.write(JSON.stringify({ saved: true, sessionToken: token }))
}

function loadToken() {
	if (fs.existsSync(TOKEN_FILE)) {
		const token = fs.readFileSync(TOKEN_FILE, "utf-8").trim()
		if (token) {
			process.stdout.write(token)
			return
		}
	}
	process.stderr.write("No session token found. User is not logged in.\n")
	process.exit(1)
}

function checkLogin() {
	let loggedIn = false
	let token = null
	if (fs.existsSync(TOKEN_FILE)) {
		const stored = fs.readFileSync(TOKEN_FILE, "utf-8").trim()
		if (stored) {
			loggedIn = true
			token = stored
		}
	}
	process.stdout.write(JSON.stringify({ loggedIn, sessionToken: token }))
}

function clearToken() {
	if (fs.existsSync(TOKEN_FILE)) {
		fs.unlinkSync(TOKEN_FILE)
	}
	process.stdout.write(JSON.stringify({ cleared: true }))
}

// --- CLI ---
const [, , command, ...args] = process.argv

switch (command) {
	case "save":
		if (!args[0]) {
			process.stderr.write("Usage: node session-token.js save <token>\n")
			process.exit(1)
		}
		saveToken(args[0])
		break
	case "load":
		loadToken()
		break
	case "check":
		checkLogin()
		break
	case "clear":
		clearToken()
		break
	default:
		process.stderr.write("Commands: save <token> | load i | check | clear\n")
		process.exit(1)
}

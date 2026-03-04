#!/usr/bin/env node

/**
 * Generates a device ID based on the user's ID.
 * Format: openclaw_<userId>  (e.g. "openclaw_42")
 *
 * Usage:
 *   node generate-device-id.js <userId>
 *
 * Output: the device ID string
 */

function getDeviceId(userId) {
	return `openclaw_${userId}`
}

const userId = process.argv[2]
const deviceId = getDeviceId(userId)
process.stdout.write(deviceId)

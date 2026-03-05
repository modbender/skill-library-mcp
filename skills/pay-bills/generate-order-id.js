#!/usr/bin/env node

/**
 * Generates a unique order/transaction ID.
 * Usage: node generate-order-id.js
 * Output: a single ORDER_<timestamp36>_<random> string (uppercase)
 */

function generateTrxId() {
	const timestamp = Date.now().toString(36)
	const random = Math.random().toString(36).substring(2, 8)
	return `ORDER_${timestamp}_${random}`.toUpperCase()
}

const id = generateTrxId()
process.stdout.write(id)

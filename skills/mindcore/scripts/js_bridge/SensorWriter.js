/**
 * SensorWriter.js — Sensor State Updater (JS Side)
 * 
 * Safe utility to update Sensor_State.json and ShortTermMemory.json 
 * from the Node.js agent, allowing external events (like a user message)
 * to instantly alter the Python engine's environmental states.
 */

const fs = require('fs');
const path = require('path');

const DATA_DIR = path.resolve(__dirname, '../data');
const SENSOR_PATH = path.join(DATA_DIR, 'Sensor_State.json');
const MEMORY_PATH = path.join(DATA_DIR, 'ShortTermMemory.json');

class SensorWriter {
    /**
     * Safely load a JSON file, or return a fallback default if it fails.
     */
    _loadJson(filePath, fallback = {}) {
        try {
            if (fs.existsSync(filePath)) {
                const raw = fs.readFileSync(filePath, 'utf8');
                return JSON.parse(raw);
            }
        } catch (e) {
            console.warn(`[SensorWriter] Warning: Could not read ${filePath}: ${e.message}`);
        }
        return fallback;
    }

    /**
     * Safely save an object to a JSON file.
     */
    _saveJson(filePath, data) {
        try {
            // Write to a temporary file first, then rename to avoid corruption 
            // if the Python engine reads exactly while we are writing.
            const tempPath = `${filePath}.tmp`;
            fs.writeFileSync(tempPath, JSON.stringify(data, null, 4), 'utf8');
            fs.renameSync(tempPath, filePath);
            return true;
        } catch (e) {
            console.error(`[SensorWriter] Failed to write ${filePath}:`, e);
            return false;
        }
    }

    /**
     * Record that a user interaction just occurred.
     * This resets the 'ignored_long_time' need pressure in Layer 1.
     */
    recordUserInteraction() {
        const data = this._loadJson(SENSOR_PATH);
        if (!data.social) data.social = {};

        // Update interaction timestamp to now
        data.social.last_interaction_time = Date.now() / 1000.0;

        // Briefly activate "someone_online"
        data.social.someone_online = 1;

        // Optionally, tick 'deep_conversation' or 'small_talk' 
        // depending on the interaction type. We'll leave it generic here.

        this._saveJson(SENSOR_PATH, data);
        // console.log("[SensorWriter] 🟢 User interaction recorded. Loneliness reset.");
    }

    /**
     * Directly set any specific sensor value.
     * 
     * @param {string} category - "body", "environment", or "social"
     * @param {string} key - e.g. "late_night", "sleep_deprived"
     * @param {number|null} value - 1, 0, or timestamp
     */
    setSensor(category, key, value) {
        const data = this._loadJson(SENSOR_PATH);
        if (!data[category]) data[category] = {};
        data[category][key] = value;
        this._saveJson(SENSOR_PATH, data);
    }

    /**
     * Modify the mood_valence in ShortTermMemory.
     * 
     * @param {number} delta - e.g. -0.2 (more negative) or +0.1 (more positive)
     */
    shiftMood(delta) {
        const memory = this._loadJson(MEMORY_PATH);
        let currentMood = memory.mood_valence || 0.0;

        currentMood += delta;
        // Clamp between -1.0 and 1.0
        currentMood = Math.max(-1.0, Math.min(1.0, currentMood));

        memory.mood_valence = currentMood;
        this._saveJson(MEMORY_PATH, memory);
        // console.log(`[SensorWriter] 🧠 Mood shifted by ${delta} -> Now ${currentMood.toFixed(2)}`);
    }

    /**
     * Reset the "someone_online" flag when the user leaves/stops typing.
     */
    clearOnlineStatus() {
        this.setSensor("social", "someone_online", 0);
    }
}

module.exports = SensorWriter;

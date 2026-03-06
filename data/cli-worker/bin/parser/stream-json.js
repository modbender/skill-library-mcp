/**
 * Parse Kimi stream-json output: one JSON object per line.
 * Find last assistant message and extract last content part with type "text".
 */
function extractTextFromContent(content) {
    if (typeof content === "string")
        return content;
    if (!Array.isArray(content))
        return "";
    let text = "";
    for (const part of content) {
        if (part &&
            typeof part === "object" &&
            part.type === "text" &&
            typeof part.text === "string") {
            text = part.text;
        }
    }
    return text;
}
export function parseStreamJson(lines) {
    const raw = [];
    let lastAssistantText = "";
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed)
            continue;
        try {
            const obj = JSON.parse(trimmed);
            raw.push(obj);
            const msg = obj;
            if (msg.role === "assistant" && msg.content !== undefined) {
                lastAssistantText = extractTextFromContent(msg.content);
            }
        }
        catch {
            // skip non-JSON lines
        }
    }
    return { finalText: lastAssistantText, raw };
}
//# sourceMappingURL=stream-json.js.map
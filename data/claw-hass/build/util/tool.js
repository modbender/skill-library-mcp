import {} from '@mariozechner/pi-agent-core';
import { encode } from '@toon-format/toon';
export function toolResult(data, details) {
    return { content: [{ type: 'text', text: encode(data) }], details: details ?? {} };
}

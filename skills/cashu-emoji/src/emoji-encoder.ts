/*! emoji-encoder - Credit: Paul Butler https://github.com/paulgb/emoji-encoder */

// Variation selectors block https://unicode.org/charts/nameslist/n_FE00.html
// VS1..=VS16
const VARIATION_SELECTOR_START = 0xfe00;
const VARIATION_SELECTOR_END = 0xfe0f;

// Variation selectors supplement https://unicode.org/charts/nameslist/n_E0100.html
// VS17..=VS256
const VARIATION_SELECTOR_SUPPLEMENT_START = 0xe0100;
const VARIATION_SELECTOR_SUPPLEMENT_END = 0xe01ef;

export function toVariationSelector(byte: number): string | null {
  if (byte >= 0 && byte < 16) {
    return String.fromCodePoint(VARIATION_SELECTOR_START + byte);
  } else if (byte >= 16 && byte < 256) {
    return String.fromCodePoint(
      VARIATION_SELECTOR_SUPPLEMENT_START + byte - 16,
    );
  } else {
    return null;
  }
}

export function fromVariationSelector(codePoint: number): number | null {
  if (
    codePoint >= VARIATION_SELECTOR_START &&
    codePoint <= VARIATION_SELECTOR_END
  ) {
    return codePoint - VARIATION_SELECTOR_START;
  } else if (
    codePoint >= VARIATION_SELECTOR_SUPPLEMENT_START &&
    codePoint <= VARIATION_SELECTOR_SUPPLEMENT_END
  ) {
    return codePoint - VARIATION_SELECTOR_SUPPLEMENT_START + 16;
  } else {
    return null;
  }
}

/**
 * Encode UTF-8 text into variation selectors appended to the given emoji.
 */
export function encode(emoji: string, text: string): string {
  const bytes = new TextEncoder().encode(text);
  let encoded = emoji;

  for (const byte of bytes) {
    const vs = toVariationSelector(byte);
    if (!vs) throw new Error('byte out of range');
    encoded += vs;
  }

  return encoded;
}

/**
 * Decode UTF-8 text from a string that contains variation selectors.
 *
 * Behavior:
 * - Ignores characters until the first variation selector byte is found.
 * - Collects subsequent selector bytes.
 * - Stops when it hits a non-selector AFTER having collected bytes.
 */
export function decode(text: string): string {
  const decoded: number[] = [];
  const chars = Array.from(text);

  for (const char of chars) {
    const byte = fromVariationSelector(char.codePointAt(0)!);

    if (byte === null && decoded.length > 0) {
      break;
    } else if (byte === null) {
      continue;
    }

    decoded.push(byte);
  }

  return new TextDecoder().decode(new Uint8Array(decoded));
}

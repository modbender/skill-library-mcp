// 0x0://NUMBER/PIN
const URI_RE = /^0x0:\/\/(0x0-\d+-\d+-\d+)\/(.+)$/

export function parseUri(uri) {
  const m = URI_RE.exec(uri)
  if (!m) return null
  return { number: m[1], pin: m[2] }
}

export function buildUri(number, pin) {
  return `0x0://${number}/${pin}`
}

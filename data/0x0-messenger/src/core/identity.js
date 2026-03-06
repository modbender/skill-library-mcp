// 番号生成: 0x0-NNN-NNNN-NNNN

export function generateNumber() {
  const seg3 = String(Math.floor(Math.random() * 900) + 100)
  const seg4a = String(Math.floor(Math.random() * 9000) + 1000)
  const seg4b = String(Math.floor(Math.random() * 9000) + 1000)
  return `0x0-${seg3}-${seg4a}-${seg4b}`
}

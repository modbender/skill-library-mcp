export function gradeEmoji(grade) {
  const g = String(grade || "").toUpperCase();
  if (g.startsWith("A") || g.startsWith("B+")) return "🟢";
  if (g.startsWith("B") || g.startsWith("C+")) return "🟡";
  if (g.startsWith("C") || g.startsWith("D")) return "🔴";
  return "⚪";
}

export function riskEmoji(risk) {
  const r = String(risk || "").toLowerCase();
  if (r === "low") return "🟢";
  if (r === "medium") return "🟡";
  if (r === "high") return "🔴";
  return "⚪";
}

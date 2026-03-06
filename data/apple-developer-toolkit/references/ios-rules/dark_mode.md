---
description: "Implementation rules for dark mode"
---
# Dark Mode

DARK/LIGHT MODE:
- 3-way picker (system/light/dark) is the standard pattern:
  @AppStorage("appearance") private var appearance: String = "system"
  private var preferredColorScheme: ColorScheme? {
      switch appearance { case "light": return .light; case "dark": return .dark; default: return nil }
  }
  .preferredColorScheme(preferredColorScheme)    // on outermost container in @main app
- CRITICAL: .preferredColorScheme() MUST be in the root @main app, NOT just in the settings view.
- System option: .preferredColorScheme(nil) follows device setting.
- Settings screen: Picker with light/dark/system options writing to @AppStorage("appearance").

ADAPTIVE THEME COLORS (no color assets needed):
- Switch ALL AppTheme palette colors from plain Color(hex:) to Color(light:dark:) with TWO hex values:
  static let background = Color(light: Color(hex: "#F8F9FA"), dark: Color(hex: "#1C1C1E"))
  static let surface = Color(light: Color(hex: "#FFFFFF"), dark: Color(hex: "#2C2C2E"))
- Color(light:dark:) uses UIColor(dynamicProvider:) — reacts to .preferredColorScheme() automatically.
- YOU decide the dark palette based on app mood — user does not specify dark colors.
- Dark palette guidelines: darken backgrounds (#1C1C1E, #2C2C2E), lighten/brighten accents slightly, use Color.primary/Color.secondary for text.
- AppTheme MUST include the Color(light:dark:) extension (see shared constraints).

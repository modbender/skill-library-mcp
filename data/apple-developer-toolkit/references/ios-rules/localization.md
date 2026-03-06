---
description: "Implementation rules for localization"
---
# Localization

LOCALIZATION (.strings files + RTL/LTR + Language Switching):

FORBIDDEN PATTERNS (CRITICAL — violation = broken app):
- NEVER hardcode translations with if/else or switch on language code. Example of FORBIDDEN code:
  if appLanguage == "ar" { Text("الإعدادات") } else { Text("Settings") }
  switch language { case "ar": return "بحث" default: return "Search" }
- NEVER build a manual translation dictionary/map in code (e.g., let translations = ["en": "Settings", "ar": "الإعدادات"]).
- NEVER use ternary operators to pick translated strings: Text(isArabic ? "الإعدادات" : "Settings").
- These patterns bypass Apple's localization system, break when new languages are added, and ignore the environment locale.
- The ONLY correct approach: use string literals in views — Text("Settings"), Button("Save"), .navigationTitle("Dashboard") — and let Localizable.strings handle translations.
- The deployment pipeline generates .strings files automatically. Your code must ONLY contain English string literals.

.strings FILE GENERATION:
- When localization is requested, generate Resources/{lang}.lproj/Localizable.strings for EACH language.
- File format: standard Apple .strings — one "key" = "translation"; per line.
- KEYS MUST BE THE ENGLISH TEXT ITSELF. Example: "Settings" = "Settings"; (en), "Settings" = "الإعدادات"; (ar). NOT snake_case like "settings_title".
- This means Text("Settings") in code auto-localizes because the key IS the English text.
- English .strings: identity mapping (key = value). Other languages: key = translated value.
- ALL user-facing strings MUST have a key: Text(), Button(), Label(), Toggle(), navigationTitle(), Section(), alert titles/messages, ContentUnavailableView labels, placeholder text.

CRITICAL — localization key usage rules:

Rule 1 — String LITERALS in views are auto-localized:
  Text("settings_title"), .navigationTitle("dashboard_title"), Label("tab_workouts", systemImage: "icon")
  SwiftUI treats these as LocalizedStringKey and looks them up using the environment locale.

Rule 2 — String VARIABLES are NOT auto-localized:
  let key = "settings_title"; Text(key) — shows raw key text. This is the #1 localization bug.
  FIX: Text(LocalizedStringKey(key))

Rule 3 — Computed properties returning keys for display:
  If a switch/computed property returns a key as String (e.g. "metric_steps"), and you pass it to Text(label), it will NOT be localized.
  FIX: Return LocalizedStringKey instead of String from the computed property.

Rule 4 — NEVER use String(localized:) in view parameters:
  Text(String(localized: "key")) resolves against SYSTEM locale, NOT the environment locale. Runtime language switching breaks.

Rule 5 — EVERY key in code must exist in EVERY .strings file. Missing key = raw key shown to user.

- Sample data strings stay as plain String — they are demo content, not translatable.

CONFIG_CHANGES FOR LOCALIZATIONS:
- CONFIG_CHANGES MUST include "localizations": ["en", "ar", "es"] (list of all language codes).
- The client reads this to register knownRegions in the Xcode .pbxproj and create .lproj file references.

LANGUAGE SELECTION & SWITCHING:
- Root view: @AppStorage("appLanguage") private var appLanguage: String = "en"
- Root @main app MUST apply .id(appLanguage) on RootView AND set locale/layoutDirection:
  private var layoutDirection: LayoutDirection {
      ["ar", "he", "fa", "ur"].contains(appLanguage) ? .rightToLeft : .leftToRight
  }
  RootView()
      .id(appLanguage)    // MANDATORY: forces full view rebuild on language change
      .environment(\.locale, Locale(identifier: appLanguage))
      .environment(\.layoutDirection, layoutDirection)
- .id(appLanguage) is CRITICAL — without it, changing language causes mirrored/broken layouts because SwiftUI animates the layout direction change instead of rebuilding. With .id(), the entire view tree is destroyed and recreated cleanly.
- Setting locale ALONE does NOT flip layout to RTL. You MUST set layoutDirection explicitly.
- RTL languages: Arabic (ar), Hebrew (he), Persian/Farsi (fa), Urdu (ur).
- App restart NOT needed — .id(appLanguage) forces a full view rebuild when @AppStorage changes.
- Settings screen: add a language picker (Picker or List with checkmark) that writes to @AppStorage("appLanguage").
- Display language name: Locale(identifier: code).localizedString(forLanguageCode: code) ?? code

RTL / LTR LAYOUT DIRECTION:
- .environment(\.layoutDirection) MUST be set explicitly — .environment(\.locale) does NOT set it automatically.
- Use .leading/.trailing (never .left/.right) for alignment, padding, edges.
- Icons that represent direction (back arrows, chevrons, progress bars) MUST call .flipsForRightToLeftLayoutDirection(true).
- Decorative/universal icons (checkmarks, stars, hearts) must NOT flip.
- Text alignment: always use .leading — SwiftUI resolves it to left or right based on layoutDirection.
- Padding/spacing: always use .leading/.trailing edges, never .left/.right (Edge.Set).

LOCALE-AWARE FORMATTING:
- Dates: use .formatted(date:time:) or Text(date, format:) — automatically adapts to user's locale/calendar.
- Numbers: use .formatted() or Text(number, format: .number) — respects locale decimal/grouping separators.
- Currency: use .formatted(.currency(code:)) — locale-aware symbol placement and formatting.
- Measurements: use Measurement + MeasurementFormatter for locale-appropriate units.
- NEVER manually format dates/numbers with hardcoded separators or patterns.

TESTING RTL IN PREVIEWS:
- Add preview with RTL locale: .environment(\.locale, Locale(identifier: "ar")) and .environment(\.layoutDirection, .rightToLeft)
- Verify: text alignment flips, HStack order reverses, directional icons mirror, padding sides swap.

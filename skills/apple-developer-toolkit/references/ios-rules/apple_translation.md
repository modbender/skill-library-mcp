---
description: "Implementation rules for apple translation"
---
# Apple Translation

APPLE ON-DEVICE TRANSLATION (Translation framework):
FRAMEWORK: import Translation (iOS 17.4+, on-device, NO internet required, NO API key)

KEY DISTINCTION: Translation is for translating USER CONTENT on demand (e.g. translating a message from French to English). It is NOT for app localization (.strings files). Do not confuse the two.

MODIFIER APPROACH (simplest — shows system translation sheet):
  @State private var showTranslation = false
  Text(userContent)
      .translationPresentation(isPresented: $showTranslation, text: userContent)
  Button("Translate") { showTranslation = true }

PROGRAMMATIC TRANSLATION (TranslationSession):
  @State private var translatedText = ""

  func translateText(_ input: String) async {
      let config = TranslationSession.Configuration(source: .init(identifier: "fr"), target: .init(identifier: "en"))
      let session = TranslationSession(configuration: config)
      do {
          let response = try await session.translate(input)
          translatedText = response.targetText
      } catch {
          // Handle: language pair not supported on device, model not downloaded
      }
  }

  // Call with .task or Button:
  .task { await translateText(originalText) }

SUPPORTED LANGUAGES: Check Translation.supportedLanguages for the device's available language pairs.
AVAILABILITY: Some language pairs require a model download on first use.
NO ENTITLEMENTS NEEDED: Translation framework requires no special entitlements or Info.plist keys.

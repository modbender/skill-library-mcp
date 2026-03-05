# Setting Up ColorKit

Learn how to integrate the `ColorKit` package into your Swift project.

## Installation

### Swift Package Manager (Recommended)

1. In Xcode, go to **File > Add Package Dependency**.
2. Enter the package URL: `https://github.com/SzpakKamil/ColorKit.git`.
3. Select a version (e.g., `1.0.0` or later) or use the `main` branch.
4. Ensure your project uses Swift 5.9+ and targets compatible OS versions.
5. Import the module:
   ```swift
   import ColorKit
   ```

## Supported Platforms

- **iOS** 13.0+
- **macOS** 10.15+
- **tvOS** 13.0+
- **watchOS** 6.0+
- **visionOS** 1.0+

## Installing Agent Skill

You can install the ColorKit skill for your CLI agent to get expert guidance directly in your terminal:

```bash
npx skills add https://github.com/SzpakKamil/AgentSkills --skill ColorKit
```

## Example Integration

```swift
import SwiftUI
import ColorKit

struct ContentView: View {
    let accent = CKColor(hexString: "#FF5733")
    
    var body: some View {
        VStack {
            Text("Advanced Color")
                .font(.largeTitle)
                .foregroundStyle(accent)
            
            RoundedRectangle(cornerRadius: 12)
                .fill(accent.blended(with: .black, mode: .multiply))
                .frame(width: 200, height: 100)
        }
    }
}
```

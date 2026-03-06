---
name: HarmonyOS Developer Skills
description: 1. DevEco Studio → Build → Build Hap 2. Configure signing in
  Project Structure → Signing Configs 3. Requires .p12 certificate and .cer
  public key 4. Use debug signing for development, release for p...
---

# HarmonyOS Developer Skills

## Core Rules

- Use `.equals()` for string comparison, not `==`
- HarmonyOS uses ArkTS/TypeScript
- UI built with ArkUI framework
- App signing requires certificate configuration

---

## Development Environment

- **IDE**: DevEco Studio
- **Language**: ArkTS (TypeScript superset)
- **SDK**: HarmonyOS SDK
- **API**: HarmonyOS Next API

---

## ArkUI Basics

### Components

```typescript
// Basic component
@Entry
@Component
struct Index {
  @State message: string = 'Hello World'

  build() {
    Column() {
      Text(this.message)
        .fontSize(50)
        .fontWeight(FontWeight.Bold)
    }
    .alignItems(HorizontalAlign.Center)
    .width('100%')
    .height('100%')
  }
}
```

### State Management

```typescript
// @State - Component internal state
@State count: number = 0

// @Prop - Parent component prop
@Prop message: string

// @Link - Two-way binding
@Link childCount: number

// @Observed + @ObjectLink - Deep observation
@Observed
class Person {
  name: string = ''
  age: number = 0
}

@ObjectLink person: Person
```

### Lifecycle

```typescript
// Component lifecycle
aboutToAppear() {}    // About to display
onDidBuild() {}       // Build complete
aboutToDisappear() {} // About to destroy
```

---

## Common Components

- **Text** - Text display
- **Image** - Image display
- **Button** - Interactive button
- **Column/Row** - Layout containers
- **List** - Scrollable list
- **Grid** - Grid layout
- **Stack** - Stacked layout
- **Swiper** - Carousel
- **TabContent** - Tab pages

---

## Layouts

```typescript
// Linear layout
Column() { }  // Vertical
Row() { }     // Horizontal

// Flex layout
Flex() { 
  direction: FlexDirection.Row 
}

// Grid layout
Grid() { 
  columnsTemplate: '1fr 1fr 1fr' 
}

// Stack
Stack() { }
```

---

## Routing

```typescript
import router from '@ohos.router'

// Navigate
router.pushUrl('pages/Detail')

// Go back
router.back()

// With params
router.pushUrl({
  url: 'pages/Detail',
  params: { id: 123 }
})

// Get params
const params = router.getParams()
```

---

## Network Requests

```typescript
import http from '@ohos.net.http'

let httpRequest = http.createHttp()
httpRequest.request(
  'https://api.example.com/data',
  {
    method: http.RequestMethod.GET,
    header: { 'Content-Type': 'application/json' }
  },
  (err, data) => {
    if (!err) {
      console.log(JSON.stringify(data.result))
    }
  }
)
```

---

## Local Storage

```typescript
import preferences from '@ohos.data.preferences'

// Write
let preferences = await preferences.getPreferences(context, 'myPrefs')
await preferences.put('username', 'tom')
await preferences.flush()

// Read
let value = await preferences.get('username', 'default')
```

---

## Permissions

```typescript
import abilityAccessCtrl from '@ohos.abilityAccessCtrl'

// Declare in module.json5
// "requestPermissions": [
//   { "name": "ohos.permission.INTERNET" }
// ]

// Request at runtime
let atManager = abilityAccessCtrl.createAtManager()
atManager.requestPermissionsFromUser(context, ['ohos.permission.INTERNET'])
```

---

## Common Permissions

- `ohos.permission.INTERNET` - Network access
- `ohos.permission.GET_NETWORK_INFO` - Network status
- `ohos.permission.CAMERA` - Camera access
- `ohos.permission.WRITE_MEDIA` - Media write
- `ohos.permission.READ_MEDIA` - Media read

---

## Build & Signing

1. **DevEco Studio** → Build → Build Hap
2. Configure signing in `Project Structure` → Signing Configs
3. Requires `.p12` certificate and `.cer` public key
4. Use debug signing for development, release for production

---

## Quick Reference

| Need | Solution |
|------|----------|
| State management | @State, @Prop, @Link, @Observed |
| Lists | List + ListItem |
| Network | @ohos.net.http |
| Storage | @ohos.data.preferences |
| Routing | router.pushUrl() |
| Toast | promptAction.showToast() |
| Dialog | dialog.showDialog() |

---

## Learning Resources

- Official: https://developer.harmonyos.com/
- API Docs: https://docs.openharmony.cn/
- Samples: https://gitee.com/openharmony/app_samples

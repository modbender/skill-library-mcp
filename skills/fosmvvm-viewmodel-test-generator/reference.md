# FOSMVVM ViewModel Test Generator - Reference Templates

Complete file templates for generating ViewModel tests.

> **Conceptual context:** See [SKILL.md](SKILL.md) for when and why to use this skill.
> **Architecture context:** See [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md#testing-support) for testing overview.

## Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{Name}` | Feature or ViewModel name (PascalCase) | `Dashboard`, `Board` |
| `{Target}` | Your test target name | `FOSMVVM`, `ViewModels` |
| `{ResourceDir}` | YAML resource directory | `TestYAML`, `Resources` |

---

# Test File Templates

---

## Template 1: Basic ViewModel Test Suite

For testing one or more ViewModels with standard coverage.

**Location:** `Tests/{Target}Tests/Localization/{Name}ViewModelTests.swift`

```swift
// {Name}ViewModelTests.swift
//
// Copyright 2025 {Your Company}
//
// Licensed under the Apache License, Version 2.0 (the  License);
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import FOSFoundation
@testable import FOSMVVM
import FOSTesting
import Foundation
import Testing

@Suite("{Name} ViewModel Tests")
struct {Name}ViewModelTests: LocalizableTestCase {
    @Test func {name}ViewModel() throws {
        try expectFullViewModelTests({Name}ViewModel.self)
    }

    let locStore: LocalizationStore
    init() throws {
        self.locStore = try Self.loadLocalizationStore(
            bundle: Bundle.module,
            resourceDirectoryName: "{ResourceDir}"
        )
    }
}
```

---

## Template 2: Test Suite with Multiple ViewModels

For testing a feature area with multiple related ViewModels.

**Location:** `Tests/{Target}Tests/Localization/{Name}ViewModelTests.swift`

```swift
// {Name}ViewModelTests.swift

import FOSFoundation
@testable import FOSMVVM
import FOSTesting
import Foundation
import Testing

@Suite("{Name} ViewModel Tests")
struct {Name}ViewModelTests: LocalizableTestCase {
    // MARK: - Top-Level ViewModels

    @Test func {name}ViewModel() throws {
        try expectFullViewModelTests({Name}ViewModel.self)
    }

    // MARK: - Child ViewModels

    @Test func {childName}ViewModel() throws {
        try expectFullViewModelTests({ChildName}ViewModel.self)
    }

    @Test func {otherChildName}ViewModel() throws {
        try expectFullViewModelTests({OtherChildName}ViewModel.self)
    }

    // MARK: - Setup

    let locStore: LocalizationStore
    init() throws {
        self.locStore = try Self.loadLocalizationStore(
            bundle: Bundle.module,
            resourceDirectoryName: "{ResourceDir}"
        )
    }
}
```

---

## Template 3: Test Suite with Specific Behavior Verification

For testing ViewModels that have substitutions or specific formatting to verify.

**Location:** `Tests/{Target}Tests/Localization/{Name}ViewModelTests.swift`

```swift
// {Name}ViewModelTests.swift

import FOSFoundation
@testable import FOSMVVM
import FOSTesting
import Foundation
import Testing

@Suite("{Name} ViewModel Tests")
struct {Name}ViewModelTests: LocalizableTestCase {
    @Test func {name}ViewModel() throws {
        try expectFullViewModelTests({Name}ViewModel.self)
    }

    @Test func {name}Substitutions() throws {
        try expectFullViewModelTests({Name}ViewModel.self)

        // Verify specific substitution behavior
        let vm: {Name}ViewModel = try .stub()
            .toJSON(encoder: encoder(locale: en))
            .fromJSON()

        #expect(try vm.welcomeMessage.localizedString == "Welcome, {ExpectedValue}!")
        #expect(try vm.itemCount.localizedString == "{ExpectedCount} items")
    }

    let locStore: LocalizationStore
    init() throws {
        self.locStore = try Self.loadLocalizationStore(
            bundle: Bundle.module,
            resourceDirectoryName: "{ResourceDir}"
        )
    }
}
```

---

## Template 4: Test Suite with Embedded ViewModels

For testing parent ViewModels that contain child ViewModels.

**Location:** `Tests/{Target}Tests/Localization/{Name}ViewModelTests.swift`

```swift
// {Name}ViewModelTests.swift

import FOSFoundation
@testable import FOSMVVM
import FOSTesting
import Foundation
import Testing

@Suite("{Name} Embedded ViewModel Tests")
struct {Name}ViewModelTests: LocalizableTestCase {
    @Test func parentWithEmbeddedChildren() throws {
        try expectFullViewModelTests({Parent}ViewModel.self)
    }

    @Test func embeddedChildValues() throws {
        try expectFullViewModelTests({Parent}ViewModel.self)

        // Verify embedded child ViewModels have correct values
        let vm: {Parent}ViewModel = try .stub()
            .toJSON(encoder: encoder(locale: en))
            .fromJSON()

        #expect(try vm.children[0].title.localizedString == "Child Title")
        #expect(try vm.children[1].title.localizedString == "Child Title")
    }

    @Test func multipleChildrenOfSameType() throws {
        try expectFullViewModelTests({Parent}ViewModel.self)

        let vm: {Parent}ViewModel = try .stub()
            .toJSON(encoder: encoder(locale: en))
            .fromJSON()

        // Verify each child has its own substitution values (not shared)
        #expect(try vm.child1.value.localizedString == "Value: 1")
        #expect(try vm.child2.value.localizedString == "Value: 2")
    }

    let locStore: LocalizationStore
    init() throws {
        self.locStore = try Self.loadLocalizationStore(
            bundle: Bundle.module,
            resourceDirectoryName: "{ResourceDir}"
        )
    }
}
```

---

## Template 5: Test Suite with Private Test ViewModels

For testing specific scenarios using private ViewModel structs defined in the test file.

**Location:** `Tests/{Target}Tests/Localization/{Name}Tests.swift`

```swift
// {Name}Tests.swift

import FOSFoundation
@testable import FOSMVVM
import FOSTesting
import Foundation
import Testing

@Suite("{Name} Tests")
struct {Name}Tests: LocalizableTestCase {
    @Test func {scenarioName}() throws {
        try expectFullViewModelTests(Test{Name}ViewModel.self)
    }

    @Test func {anotherScenario}() throws {
        try expectFullViewModelTests(TestParentViewModel.self)

        let vm: TestParentViewModel = try .stub()
            .toJSON(encoder: encoder(locale: en))
            .fromJSON()

        #expect(try vm.child.label.localizedString == "Expected Label")
    }

    let locStore: LocalizationStore
    init() throws {
        self.locStore = try Self.loadLocalizationStore(
            bundle: Bundle.module,
            resourceDirectoryName: "{ResourceDir}"
        )
    }
}

// MARK: - Private Test ViewModels

private struct Test{Name}ViewModel: ViewModel {
    @LocalizedString var title

    var vmId: ViewModelId = .init()

    static func stub() -> Self {
        .init()
    }
}

private struct TestParentViewModel: ViewModel {
    @LocalizedString var parentTitle
    let child: TestChildViewModel

    var vmId: ViewModelId = .init()

    static func stub() -> Self {
        .init(child: .stub())
    }
}

private struct TestChildViewModel: ViewModel {
    @LocalizedString var label

    var vmId: ViewModelId = .init()

    static func stub() -> Self {
        .init()
    }
}
```

---

## Template 6: Test Suite with Custom Locales

For testing with additional locales beyond the default (en, es).

**Location:** `Tests/{Target}Tests/Localization/{Name}ViewModelTests.swift`

```swift
// {Name}ViewModelTests.swift

import FOSFoundation
@testable import FOSMVVM
import FOSTesting
import Foundation
import Testing

@Suite("{Name} ViewModel Tests")
struct {Name}ViewModelTests: LocalizableTestCase {
    // Override default locales
    var locales: Set<Locale> { [en, es, enGB, enUS] }

    @Test func {name}ViewModel() throws {
        // Tests all four locales
        try expectFullViewModelTests({Name}ViewModel.self)
    }

    @Test func {name}SpecificLocale() throws {
        // Test specific locale behavior
        let vmGB: {Name}ViewModel = try .stub()
            .toJSON(encoder: encoder(locale: enGB))
            .fromJSON()

        #expect(try vmGB.colorLabel.localizedString == "Colour")  // British spelling
    }

    let locStore: LocalizationStore
    init() throws {
        self.locStore = try Self.loadLocalizationStore(
            bundle: Bundle.module,
            resourceDirectoryName: "{ResourceDir}"
        )
    }
}
```

---

# YAML Templates

---

## Template 7: Basic ViewModel YAML

**Location:** `Tests/{Target}Tests/{ResourceDir}/{Name}ViewModel.yml`

```yaml
en:
  {Name}ViewModel:
    pageTitle: "Page Title"
    subtitle: "Subtitle text"
    emptyMessage: "No items found"
    buttonLabel: "Submit"

es:
  {Name}ViewModel:
    pageTitle: "Título de Página"
    subtitle: "Texto del subtítulo"
    emptyMessage: "No se encontraron elementos"
    buttonLabel: "Enviar"
```

---

## Template 8: ViewModel with Substitutions YAML

**Location:** `Tests/{Target}Tests/{ResourceDir}/{Name}ViewModel.yml`

```yaml
en:
  {Name}ViewModel:
    welcomeMessage: "Welcome, %{userName}!"
    itemCount: "%{count} items"
    lastUpdated: "Last updated: %{date}"

es:
  {Name}ViewModel:
    welcomeMessage: "Bienvenido, %{userName}!"
    itemCount: "%{count} elementos"
    lastUpdated: "Última actualización: %{date}"
```

---

## Template 9: Multiple ViewModels in One YAML File

**Location:** `Tests/{Target}Tests/{ResourceDir}/{Feature}ViewModels.yml`

```yaml
en:
  ParentViewModel:
    title: "Parent Title"
    description: "Parent description"

  ChildViewModel:
    label: "Child Label"
    value: "Value: %{number}"

  AnotherChildViewModel:
    name: "Another Child"

es:
  ParentViewModel:
    title: "Título del Padre"
    description: "Descripción del padre"

  ChildViewModel:
    label: "Etiqueta del Hijo"
    value: "Valor: %{number}"

  AnotherChildViewModel:
    name: "Otro Hijo"
```

---

## Template 10: Test-Only Private ViewModels YAML

**Location:** `Tests/{Target}Tests/{ResourceDir}/{TestName}Models.yml`

```yaml
en:
  Test{Name}ViewModel:
    title: "Test Title"

  TestParentViewModel:
    parentTitle: "Parent"

  TestChildViewModel:
    label: "Child Label"

es:
  Test{Name}ViewModel:
    title: "Título de Prueba"

  TestParentViewModel:
    parentTitle: "Padre"

  TestChildViewModel:
    label: "Etiqueta del Hijo"
```

---

# Checklists

## New ViewModel Test Checklist

- [ ] Test file created in `Tests/{Target}Tests/Localization/`
- [ ] Test suite conforms to `LocalizableTestCase`
- [ ] `locStore` initialized from bundle
- [ ] `@Test` method calls `expectFullViewModelTests()`
- [ ] YAML file exists with entries for all locales
- [ ] All `@LocalizedString` properties have YAML entries
- [ ] Child ViewModels have YAML entries
- [ ] Tests pass: `swift test --filter {TestSuiteName}`

## Embedded ViewModel Test Checklist

- [ ] Parent ViewModel has YAML entries
- [ ] All child ViewModel types have YAML entries
- [ ] `expectFullViewModelTests()` called on parent
- [ ] Optional: Specific child value assertions added

## Substitution Test Checklist

- [ ] YAML has `%{key}` substitution placeholders
- [ ] ViewModel has `@LocalizedSubs` property
- [ ] `subs` dictionary maps keys to values
- [ ] Test verifies substituted result matches expected

---

## Quick Reference

**Minimal test:**
```swift
@Test func myViewModel() throws {
    try expectFullViewModelTests(MyViewModel.self)
}
```

**With behavior verification:**
```swift
@Test func myViewModelBehavior() throws {
    try expectFullViewModelTests(MyViewModel.self)

    let vm: MyViewModel = try .stub()
        .toJSON(encoder: encoder(locale: en))
        .fromJSON()

    #expect(try vm.property.localizedString == "Expected")
}
```

**Minimal YAML:**
```yaml
en:
  MyViewModel:
    property: "Value"

es:
  MyViewModel:
    property: "Valor"
```

---
description: "Forms, text fields, pickers, and input validation patterns"
---
# SwiftUI Forms & Input Reference

## Form Basics

```swift
struct SettingsView: View {
    @State private var username = ""
    @State private var notificationsEnabled = true
    @State private var selectedColor = Color.blue

    var body: some View {
        Form {
            Section("Profile") {
                TextField("Username", text: $username)
                ColorPicker("Accent Color", selection: $selectedColor)
            }
            Section("Preferences") {
                Toggle("Notifications", isOn: $notificationsEnabled)
            }
        }
    }
}
```

## TextField Patterns

### Styled TextField

```swift
TextField("Email", text: $email)
    .textContentType(.emailAddress)
    .keyboardType(.emailAddress)
    .autocorrectionDisabled()
    .textInputAutocapitalization(.never)

SecureField("Password", text: $password)
    .textContentType(.password)
```

### TextField with Validation

```swift
@State private var email = ""

TextField("Email", text: $email)
    .onChange(of: email) { _, newValue in
        isEmailValid = newValue.contains("@")
    }
    .overlay(alignment: .trailing) {
        if !email.isEmpty {
            Image(systemName: isEmailValid ? "checkmark.circle.fill" : "xmark.circle.fill")
                .foregroundStyle(isEmailValid ? .green : .red)
        }
    }
```

## Picker Patterns

### Segmented Picker

```swift
@State private var selectedTab = 0

Picker("View", selection: $selectedTab) {
    Text("List").tag(0)
    Text("Grid").tag(1)
}
.pickerStyle(.segmented)
```

### Menu Picker

```swift
Picker("Sort By", selection: $sortOrder) {
    Text("Name").tag(SortOrder.name)
    Text("Date").tag(SortOrder.date)
    Text("Size").tag(SortOrder.size)
}
```

### DatePicker

```swift
DatePicker("Due Date", selection: $dueDate, displayedComponents: [.date])
    .datePickerStyle(.compact)
```

## Stepper and Slider

```swift
Stepper("Quantity: \(quantity)", value: $quantity, in: 1...99)

Slider(value: $volume, in: 0...100) {
    Text("Volume")
} minimumValueLabel: {
    Image(systemName: "speaker")
} maximumValueLabel: {
    Image(systemName: "speaker.wave.3")
}
```

## Form Submission

```swift
struct CreateItemView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var name = ""
    @State private var isSubmitting = false

    var body: some View {
        NavigationStack {
            Form {
                TextField("Name", text: $name)
            }
            .navigationTitle("New Item")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") {
                        Task { await submit() }
                    }
                    .disabled(name.isEmpty || isSubmitting)
                }
            }
        }
    }

    private func submit() async {
        isSubmitting = true
        // Save logic
        dismiss()
    }
}
```

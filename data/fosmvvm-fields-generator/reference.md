# FOSMVVM Fields Generator - Reference Templates

Complete file templates for generating Form Specifications.

> **Conceptual context:** See [SKILL.md](SKILL.md) for when and why to use this skill.
> **Architecture context:** See [FOSMVVMArchitecture.md](../../docs/FOSMVVMArchitecture.md) for full FOSMVVM understanding.

## Placeholders

| Placeholder | Replace With | Example |
|-------------|--------------|---------|
| `{Name}` | Form specification name (PascalCase) | `CreateIdea`, `User`, `LoginCredentials` |
| `{name}` | Same, but camelCase | `createIdea`, `user`, `loginCredentials` |
| `{ViewModelsTarget}` | Your ViewModels SPM target | `ViewModels`, `SharedViewModels` |
| `{ResourcesPath}` | Your localization resources path | `Sources/Resources` |

---

## File 1: {Name}Fields.swift

**Location:** `Sources/{ViewModelsTarget}/FieldModels/{Name}Fields.swift`

```swift
import FOSFoundation
import FOSMVVM
import Foundation

/// Form Specification for {describe the form purpose}.
///
/// This protocol defines:
/// - The user-editable fields
/// - Form presentation metadata (FormField definitions)
/// - Validation rules and localized error messages
///
/// Adopted by: RequestBody types, ViewModels, and optionally DataModels.
public protocol {Name}Fields: ValidatableModel, Codable, Sendable {
    // MARK: - Field Declarations

    // var fieldName: FieldType { get set }

    // MARK: - Validation Messages

    var {name}ValidationMessages: {Name}FieldsMessages { get }
}

// MARK: - Enums (if needed for constrained fields)

// public enum {Name}Status: String, CaseIterable, Equatable, Codable, Sendable {
//     case draft = "draft"
//     case published = "published"
// }

// MARK: - Field Definitions & Validation

public extension {Name}Fields {
    // MARK: Field Constraints

    // static var fieldNameRange: ClosedRange<Int> { 1...1024 }

    // MARK: FormField Definitions

    // static var fieldNameField: FormField<String?> { .init(
    //     fieldId: .init(id: "field_name"),
    //     title: .localized(for: {Name}FieldsMessages.self, propertyName: "fieldName", messageKey: "title"),
    //     placeholder: .localized(for: {Name}FieldsMessages.self, propertyName: "fieldName", messageKey: "placeholder"),
    //     type: .text(inputType: .text),
    //     options: [
    //         .required(value: true),
    //         .autocomplete(value: .off),
    //         .autocapitalize(value: .never)
    //     ] + FormInputOption.rangeLength(fieldNameRange)
    // ) }

    // MARK: Field Validation Methods

    // internal func validateFieldName(_ fields: [FormFieldBase]?) -> [ValidationResult]? {
    //     guard fields == nil || (fields?.contains(Self.fieldNameField) == true) else {
    //         return nil
    //     }
    //
    //     var result = [ValidationResult]()
    //
    //     if fieldName.isEmpty {
    //         result.append(.init(
    //             status: .error,
    //             field: Self.fieldNameField,
    //             message: {name}ValidationMessages.fieldNameRequiredMessage
    //         ))
    //     } else if !Self.fieldNameRange.contains(NSString(string: fieldName).length) {
    //         result.append(.init(
    //             status: .error,
    //             field: Self.fieldNameField,
    //             message: {name}ValidationMessages.fieldNameOutOfRangeMessage
    //         ))
    //     }
    //
    //     return result.isEmpty ? nil : result
    // }

    // MARK: ValidatableModel Implementation

    func {name}FieldsValidateModel(
        validations: Validations,
        fields: [FormFieldBase]?
    ) -> [ValidationResult]? {
        var result = [ValidationResult]()

        // Aggregate all field validations:
        // result += validateFieldName(fields)

        return result.isEmpty ? nil : result
    }

    func validate(fields: [FormFieldBase]?, validations: Validations) -> ValidationResult.Status? {
        let result = {name}FieldsValidateModel(validations: validations, fields: fields) ?? []

        if !result.isEmpty {
            validations.validations = result
        }

        return .init(for: result)
    }
}
```

---

## File 2: {Name}FieldsMessages.swift

**Location:** `Sources/{ViewModelsTarget}/FieldModels/{Name}FieldsMessages.swift`

```swift
import FOSFoundation
import FOSMVVM
import Foundation

/// Localized validation messages for {Name}Fields.
///
/// Each property maps to a key path in {Name}FieldsMessages.yml.
/// The @FieldValidationModel macro generates propertyNames() for localization binding.
@FieldValidationModel public struct {Name}FieldsMessages {
    // MARK: - Field Titles & Placeholders (used by FormField definitions)

    // Note: Titles and placeholders are referenced directly in FormField definitions
    // via .localized(for:propertyName:messageKey:) - no properties needed here.

    // MARK: - Validation Messages

    // @LocalizedString("fieldName", messageGroup: "validationMessages", messageKey: "required")
    // public var fieldNameRequiredMessage

    // @LocalizedString("fieldName", messageGroup: "validationMessages", messageKey: "outOfRange")
    // public var fieldNameOutOfRangeMessage

    public init() {}
}
```

---

## File 3: {Name}FieldsMessages.yml

**Location:** `{ResourcesPath}/FieldModels/{Name}FieldsMessages.yml`

```yaml
en:
  {Name}FieldsMessages:
    fieldName:
      title: "Field Display Name"
      placeholder: "Enter value..."
      validationMessages:
        required: "Field name is required"
        outOfRange: "Field name must be between X and Y characters"
```

---

## Complete Example: IdeaFields

A full implementation showing multiple fields, enums, and validation.

### IdeaFields.swift

```swift
import FOSFoundation
import FOSMVVM
import Foundation

/// Form Specification for Idea entities.
///
/// Defines the editable fields, validation rules, and localized messages
/// for creating and editing Ideas.
public protocol IdeaFields: ValidatableModel, Codable, Sendable {
    var id: ModelIdType? { get set }
    var content: String { get set }
    var department: Department { get set }
    var status: IdeaStatus { get set }
    var metadata: [String: String]? { get set }

    var ideaValidationMessages: IdeaFieldsMessages { get }
}

public enum Department: String, CaseIterable, Equatable, Codable, Sendable {
    case strategic
    case product
    case content
    case consulting
    case operations
}

public enum IdeaStatus: String, CaseIterable, Equatable, Codable, Sendable {
    case queued
    case exploring
    case parking
    case implementing
    case complete
    case discarded
}

public extension IdeaFields {
    // MARK: Field Constraints

    static var contentRange: ClosedRange<Int> { 1...10000 }

    // MARK: FormField Definitions

    static var contentField: FormField<String?> { .init(
        fieldId: .init(id: "content"),
        title: .localized(for: IdeaFieldsMessages.self, propertyName: "content", messageKey: "title"),
        placeholder: .localized(for: IdeaFieldsMessages.self, propertyName: "content", messageKey: "placeholder"),
        type: .textArea(inputType: .text),
        options: [
            .required(value: true)
        ] + FormInputOption.rangeLength(contentRange)
    ) }

    static var departmentField: FormField<String?> { .init(
        fieldId: .init(id: "department"),
        title: .localized(for: IdeaFieldsMessages.self, propertyName: "department", messageKey: "title"),
        type: .select,
        options: [.required(value: true)]
    ) }

    static var statusField: FormField<String?> { .init(
        fieldId: .init(id: "status"),
        title: .localized(for: IdeaFieldsMessages.self, propertyName: "status", messageKey: "title"),
        type: .select,
        options: [.required(value: true)]
    ) }

    // MARK: Validation Methods

    internal func validateContent(_ fields: [FormFieldBase]?) -> [ValidationResult]? {
        guard fields == nil || (fields?.contains(Self.contentField) == true) else {
            return nil
        }

        var result = [ValidationResult]()

        if content.isEmpty {
            result.append(.init(
                status: .error,
                field: Self.contentField,
                message: ideaValidationMessages.contentRequiredMessage
            ))
        } else if !Self.contentRange.contains(NSString(string: content).length) {
            result.append(.init(
                status: .error,
                field: Self.contentField,
                message: ideaValidationMessages.contentOutOfRangeMessage
            ))
        }

        return result.isEmpty ? nil : result
    }

    // MARK: ValidatableModel

    func ideaFieldsValidateModel(
        validations: Validations,
        fields: [FormFieldBase]?
    ) -> [ValidationResult]? {
        var result = [ValidationResult]()
        result += validateContent(fields)
        return result.isEmpty ? nil : result
    }

    func validate(fields: [FormFieldBase]?, validations: Validations) -> ValidationResult.Status? {
        let result = ideaFieldsValidateModel(validations: validations, fields: fields) ?? []
        if !result.isEmpty {
            validations.validations = result
        }
        return .init(for: result)
    }
}
```

### IdeaFieldsMessages.swift

```swift
import FOSFoundation
import FOSMVVM
import Foundation

@FieldValidationModel public struct IdeaFieldsMessages {
    @LocalizedString("content", messageGroup: "validationMessages", messageKey: "required")
    public var contentRequiredMessage

    @LocalizedString("content", messageGroup: "validationMessages", messageKey: "outOfRange")
    public var contentOutOfRangeMessage

    public init() {}
}
```

### IdeaFieldsMessages.yml

```yaml
en:
  IdeaFieldsMessages:
    content:
      title: "Idea Content"
      placeholder: "Describe your idea..."
      validationMessages:
        required: "Content is required"
        outOfRange: "Content must be between 1 and 10,000 characters"
    department:
      title: "Department"
    status:
      title: "Status"
```

---

## Adopting the Form Specification

### In a DataModel (Fluent)

```swift
final class Idea: DataModel, IdeaFields, Hashable, @unchecked Sendable {
    @ID(key: .id) var id: ModelIdType?
    @Field(key: "content") var content: String
    @Field(key: "department") var department: Department
    @Field(key: "status") var status: IdeaStatus
    @OptionalField(key: "metadata") var metadata: [String: String]?

    let ideaValidationMessages: IdeaFieldsMessages

    init() {
        self.ideaValidationMessages = .init()
    }
}
```

### In a RequestBody

```swift
public final class CreateIdeaRequest: CreateRequest, @unchecked Sendable {
    public struct RequestBody: IdeaFields, ServerRequestBody, Stubbable {
        public var id: ModelIdType? = nil
        public var content: String
        public var department: Department
        public var status: IdeaStatus = .queued
        public var metadata: [String: String]?

        public let ideaValidationMessages: IdeaFieldsMessages

        public init(content: String, department: Department) {
            self.content = content
            self.department = department
            self.ideaValidationMessages = .init()
        }

        public static func stub() -> Self {
            .init(content: "Stub idea", department: .product)
        }
    }
}
```

### In Tests

```swift
private struct TestIdea: IdeaFields {
    var id: ModelIdType?
    var content: String
    var department: Department
    var status: IdeaStatus
    var metadata: [String: String]?

    private(set) var ideaValidationMessages: IdeaFieldsMessages

    mutating func localizeMessages(encoder: JSONEncoder) throws {
        ideaValidationMessages = try IdeaFieldsMessages().toJSON(encoder: encoder).fromJSON()
    }

    init(
        id: ModelIdType? = .init(),
        content: String = "Test content",
        department: Department = .product,
        status: IdeaStatus = .queued,
        metadata: [String: String]? = nil
    ) {
        self.id = id
        self.content = content
        self.department = department
        self.status = status
        self.metadata = metadata
        self.ideaValidationMessages = .init()
    }
}
```

---

## Quick Reference: Naming Conventions

| Concept | Pattern | Example |
|---------|---------|---------|
| Protocol | `{Name}Fields` | `IdeaFields` |
| Messages struct | `{Name}FieldsMessages` | `IdeaFieldsMessages` |
| Messages property | `{name}ValidationMessages` | `ideaValidationMessages` |
| FormField definition | `{fieldName}Field` | `contentField` |
| Range constant | `{fieldName}Range` | `contentRange` |
| Validate method | `validate{FieldName}` | `validateContent` |
| Required message | `{fieldName}RequiredMessage` | `contentRequiredMessage` |
| OutOfRange message | `{fieldName}OutOfRangeMessage` | `contentOutOfRangeMessage` |

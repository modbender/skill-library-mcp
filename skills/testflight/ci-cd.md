# CI/CD Automation - TestFlight

## App Store Connect API Key Setup

### 1. Generate Key

1. [App Store Connect](https://appstoreconnect.apple.com) > Users and Access
2. Keys tab > App Store Connect API
3. Click + to generate new key
4. Role: "App Manager" (minimum for TestFlight)
5. Download the `.p8` file immediately (shown only once)

### 2. Store Securely

```bash
# Store in CI secrets, NOT in repo
APPSTORE_API_KEY_ID="XXXXXXXXXX"
APPSTORE_API_ISSUER_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
APPSTORE_API_KEY_CONTENT="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
```

### 3. Fastlane api_key.json

```json
{
  "key_id": "XXXXXXXXXX",
  "issuer_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "key": "-----BEGIN PRIVATE KEY-----\nMIGT...\n-----END PRIVATE KEY-----",
  "in_house": false
}
```

## GitHub Actions Example

```yaml
name: TestFlight

on:
  push:
    tags: ['v*']

jobs:
  deploy:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      
      - name: Install certificates
        env:
          P12_PASSWORD: ${{ secrets.P12_PASSWORD }}
          P12_BASE64: ${{ secrets.P12_BASE64 }}
          PROVISION_BASE64: ${{ secrets.PROVISION_BASE64 }}
        run: |
          # Create keychain
          security create-keychain -p "" build.keychain
          security default-keychain -s build.keychain
          security unlock-keychain -p "" build.keychain
          
          # Import certificate
          echo "$P12_BASE64" | base64 -d > cert.p12
          security import cert.p12 -k build.keychain -P "$P12_PASSWORD" -T /usr/bin/codesign
          security set-key-partition-list -S apple-tool:,apple: -s -k "" build.keychain
          
          # Install provisioning profile
          mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
          echo "$PROVISION_BASE64" | base64 -d > ~/Library/MobileDevice/Provisioning\ Profiles/profile.mobileprovision

      - name: Build and upload
        env:
          APPSTORE_API_KEY: ${{ secrets.APPSTORE_API_KEY }}
        run: |
          echo "$APPSTORE_API_KEY" > api_key.json
          fastlane beta
```

## GitLab CI Example

```yaml
deploy_testflight:
  stage: deploy
  tags: [macos]
  script:
    - bundle exec fastlane beta
  only:
    - tags
  variables:
    FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD: $APP_SPECIFIC_PASSWORD
```

## Fastlane Lanes

### Basic Upload

```ruby
lane :beta do
  increment_build_number(
    build_number: ENV["CI_PIPELINE_IID"] || Time.now.to_i
  )
  
  build_app(
    scheme: "MyApp",
    export_method: "app-store"
  )
  
  upload_to_testflight(
    api_key_path: "fastlane/api_key.json",
    skip_waiting_for_build_processing: true,
    distribute_external: false
  )
end
```

### With Changelog

```ruby
lane :beta do
  changelog = changelog_from_git_commits(
    commits_count: 10,
    pretty: "- %s"
  )
  
  build_app(scheme: "MyApp")
  
  upload_to_testflight(
    api_key_path: "fastlane/api_key.json",
    changelog: changelog,
    groups: ["Internal Testers"]
  )
end
```

### Distribute to External After Processing

```ruby
lane :distribute_external do
  upload_to_testflight(
    api_key_path: "fastlane/api_key.json",
    distribute_external: true,
    groups: ["Beta Testers"],
    submit_beta_review: true
  )
end
```

## Build Number Strategies

### Timestamp-based (Simple)

```ruby
increment_build_number(build_number: Time.now.strftime("%Y%m%d%H%M"))
# Result: 202602191530
```

### CI Pipeline ID (Recommended)

```ruby
# GitLab
increment_build_number(build_number: ENV["CI_PIPELINE_IID"])

# GitHub Actions
increment_build_number(build_number: ENV["GITHUB_RUN_NUMBER"])
```

### Version-based

```ruby
# 1.2.3 build 1 -> 10203001
version = get_version_number
parts = version.split('.').map(&:to_i)
build = (parts[0] * 10000) + (parts[1] * 100) + parts[2]
increment_build_number(build_number: "#{build}#{ENV['CI_PIPELINE_IID']}")
```

## Troubleshooting

### "No suitable application records found"

App not created in App Store Connect. Create it first with matching bundle ID.

### "The bundle version must be higher"

Build number already used. Always increment:

```ruby
latest = latest_testflight_build_number(api_key_path: "api_key.json")
increment_build_number(build_number: latest + 1)
```

### "Missing compliance information"

Add to Info.plist:

```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

Or for apps with encryption:

```xml
<key>ITSAppUsesNonExemptEncryption</key>
<true/>
<key>ITSEncryptionExportComplianceCode</key>
<string>YOUR_CODE</string>
```

### Processing stuck

Usually export compliance. Check App Store Connect > TestFlight > build status for required actions.

### "Could not find App Store Connect API key"

Verify:
- Key ID matches (10 characters)
- Issuer ID is UUID format
- .p8 content includes BEGIN/END markers
- Key has correct permissions

## Xcode Cloud Alternative

For teams preferring Apple-native CI:

1. Xcode > Product > Xcode Cloud > Create Workflow
2. Configure triggers (branch, tag, PR)
3. Select "Archive" action
4. Add "TestFlight Internal Testing" post-action
5. Signing managed automatically via cloud signing

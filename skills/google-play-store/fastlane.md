# Fastlane Automation — Google Play Store

## Setup

### Install Fastlane

```bash
# macOS (Homebrew)
brew install fastlane

# Ruby (any platform)
gem install fastlane

# Verify
fastlane --version
```

### Service Account Setup

Google Play API requires a service account.

1. **Google Cloud Console:**
   - Create project or use existing
   - Enable Google Play Developer API
   - Create service account
   - Download JSON key

2. **Play Console:**
   - Settings → API access
   - Link Google Cloud project
   - Grant service account access
   - Set permissions (Release manager for uploads)

3. **Project Setup:**
```bash
cd android-project
fastlane init
```

4. **Configure Key:**
```bash
# In Fastfile or supply
supply(
  json_key: "path/to/key.json"
)
```

## Common Commands

### Upload to Internal Track

```bash
# AAB (recommended)
fastlane supply --aab app-release.aab --track internal

# APK
fastlane supply --apk app-release.apk --track internal
```

### Upload to Closed Testing

```bash
fastlane supply --aab app-release.aab --track beta
```

### Upload to Production (Staged)

```bash
# 10% rollout
fastlane supply --aab app-release.aab --track production --rollout 0.1

# Increase to 50%
fastlane supply --track production --rollout 0.5

# Full rollout
fastlane supply --track production --rollout 1.0
```

### Promote Between Tracks

```bash
# Internal to beta
fastlane supply --track_promote_to beta --track internal

# Beta to production (10%)
fastlane supply --track_promote_to production --track beta --rollout 0.1
```

### Update Store Listing

```bash
# Sync metadata from fastlane/metadata/android/
fastlane supply --skip_upload_aab --skip_upload_apk
```

## Fastfile Examples

### Basic Upload Lane

```ruby
# fastlane/Fastfile
lane :internal do
  gradle(task: "bundleRelease")
  supply(
    track: "internal",
    aab: "app/build/outputs/bundle/release/app-release.aab"
  )
end
```

### Full Release Lane

```ruby
lane :release do |options|
  # Build
  gradle(
    task: "bundleRelease",
    properties: {
      "android.injected.signing.store.file" => ENV["KEYSTORE_PATH"],
      "android.injected.signing.store.password" => ENV["KEYSTORE_PASSWORD"],
      "android.injected.signing.key.alias" => ENV["KEY_ALIAS"],
      "android.injected.signing.key.password" => ENV["KEY_PASSWORD"]
    }
  )
  
  # Upload with staged rollout
  supply(
    track: "production",
    rollout: options[:rollout] || 0.1,
    aab: "app/build/outputs/bundle/release/app-release.aab",
    skip_upload_metadata: true,
    skip_upload_images: true,
    skip_upload_screenshots: true
  )
end

# Usage: fastlane release rollout:0.2
```

### Metadata Sync Lane

```ruby
lane :metadata do
  supply(
    skip_upload_aab: true,
    skip_upload_apk: true,
    skip_upload_changelogs: false
  )
end
```

## Metadata Structure

```
fastlane/metadata/android/
├── en-US/                 # Locale folder
│   ├── title.txt          # App title (30 chars)
│   ├── short_description.txt  # 80 chars
│   ├── full_description.txt   # 4000 chars
│   ├── changelogs/
│   │   └── 123.txt        # versionCode changelog
│   └── images/
│       ├── phoneScreenshots/
│       ├── tenInchScreenshots/
│       └── featureGraphic.png
├── es-ES/                 # Spanish locale
└── de-DE/                 # German locale
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Deploy to Play Store

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true
      
      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Decode Keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > keystore.jks
      
      - name: Decode Service Account
        run: echo "${{ secrets.PLAY_SERVICE_ACCOUNT }}" | base64 -d > service-account.json
      
      - name: Deploy to Internal
        env:
          KEYSTORE_PATH: keystore.jks
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: fastlane internal
```

### GitLab CI

```yaml
deploy_internal:
  stage: deploy
  image: cimg/android:2024.01
  script:
    - echo "$KEYSTORE_BASE64" | base64 -d > keystore.jks
    - echo "$PLAY_SERVICE_ACCOUNT" | base64 -d > service-account.json
    - gem install fastlane
    - fastlane internal
  only:
    - tags
```

## Troubleshooting

### Authentication Errors

```
Error: Google Api Error: forbidden
```

**Fixes:**
1. Check service account has correct permissions in Play Console
2. Verify JSON key path is correct
3. Check API is enabled in Google Cloud Console
4. Wait 24h after granting permissions

### Track Errors

```
Error: Cannot rollout to production before testing
```

**Fix:** Complete 20 testers + 14 days requirement first.

### Version Code Errors

```
Error: Version code already used
```

**Fix:** Increment versionCode. Cannot reuse even for rejected builds.

### Upload Timeouts

```
Error: Request timed out
```

**Fixes:**
1. Check file size (AAB should be < 150MB)
2. Check network connection
3. Try again (transient server issue)

## Best Practices

| Practice | Why |
|----------|-----|
| AAB over APK | Smaller downloads, Google manages signing |
| Semantic versioning | Easy to track releases |
| Automated changelogs | Consistent, error-free |
| Staged rollouts | Catch issues before full release |
| Store secrets in CI | Never commit keys |
| Separate lanes | internal vs production clarity |

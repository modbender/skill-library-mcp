# CI/CD & Automation

## Fastlane (Recommended)

### Why fastlane
- Single tool for both iOS and Android
- Handles screenshots, certificates, builds, uploads
- Active community, well-documented

### Key lanes

**iOS:**
```ruby
lane :beta do
  increment_build_number
  build_app(scheme: "MyApp")
  upload_to_testflight
end

lane :release do
  build_app(scheme: "MyApp")
  upload_to_app_store(
    submit_for_review: true,
    automatic_release: true
  )
end
```

**Android:**
```ruby
lane :beta do
  gradle(task: "bundleRelease")
  upload_to_play_store(track: "internal")
end

lane :release do
  gradle(task: "bundleRelease")
  upload_to_play_store(track: "production")
end
```

### Match (iOS signing)
- Stores certificates/profiles in git repo or cloud storage
- All team members use same signing identity
- `fastlane match appstore` to sync production certs
- `fastlane match adhoc` for TestFlight/internal builds

---

## App Store Connect API

### Setup
1. Create API key in App Store Connect (Users → Keys)
2. Download .p8 file (only downloadable once)
3. Note Issuer ID and Key ID

### Authentication
```bash
# Generate JWT (required for all requests)
JWT=$(generate_jwt --issuer $ISSUER_ID --key-id $KEY_ID --private-key key.p8)
curl -H "Authorization: Bearer $JWT" https://api.appstoreconnect.apple.com/v1/apps
```

### Common operations
- List apps: `GET /v1/apps`
- Get build status: `GET /v1/builds`
- Create version: `POST /v1/appStoreVersions`
- Submit for review: `POST /v1/appStoreVersionSubmissions`

### Rate limits
- 3600 requests per hour per key
- Use pagination, don't poll excessively

---

## Google Play Developer API

### Setup
1. Create service account in Google Cloud Console
2. Grant access in Play Console (Settings → API access)
3. Download JSON credentials

### Authentication
```python
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file(
    'service-account.json',
    scopes=['https://www.googleapis.com/auth/androidpublisher']
)
```

### Common operations
- Upload APK/AAB: `edits.bundles.upload`
- Update track: `edits.tracks.update`
- Get review status: `reviews.list`

### Workflow
1. Create edit: `edits.insert`
2. Upload bundle
3. Assign to track
4. Commit edit: `edits.commit`
5. (Edit = transaction, commit = publish)

---

## CI/CD Pipeline Tips

### Secrets management
- Never commit certificates, .p8 files, or JSON credentials
- Use CI secrets (GitHub Secrets, GitLab Variables)
- Match stores certs in encrypted git repo

### Build numbers
- iOS: Increment automatically per CI run
- Android: Use versionCode = CI build number or timestamp
- Both: Never reuse build numbers

### Caching
- Cache Pods/node_modules/Gradle dependencies
- iOS: Cache derived data for faster builds
- Android: Cache `.gradle` directory

### Typical workflow
```yaml
# Pseudo-workflow
on: push to main
jobs:
  build:
    - Checkout
    - Setup Ruby/Node/Java
    - Install dependencies
    - Run tests
    - Build release
    - Upload to TestFlight/Internal track
  
  release: # manual trigger
    - Download artifacts
    - Upload to App Store/Production
    - Tag release in git
```

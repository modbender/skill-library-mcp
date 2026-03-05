# App Store Connect CLI Reference

Complete reference for managing App Store Connect via the CLI tool.

## Installation

```bash
bash scripts/setup.sh
```

## Authentication

```bash
# Register API key
appstore auth login \
  --name "MyApp" \
  --key-id "ABC123" \
  --issuer-id "DEF456" \
  --private-key /path/to/AuthKey.p8

# With network validation
appstore auth login --network --name "MyApp" --key-id "ABC123" --issuer-id "DEF456" --private-key /path/to/AuthKey.p8

# Skip validation (CI)
appstore auth login --skip-validation --name "MyApp" --key-id "ABC123" --issuer-id "DEF456" --private-key /path/to/AuthKey.p8

# Switch profiles
appstore auth switch --name "ClientApp"

# Use profile for single command
appstore --profile "ClientApp" apps list

# Check auth status
appstore auth status
appstore auth status --verbose --validate

# Diagnose auth issues
appstore auth doctor
appstore auth doctor --fix --confirm

# Logout
appstore auth logout
appstore auth logout --all
appstore auth logout --name "MyApp"

# Init config
appstore auth init
appstore auth init --local
appstore auth init --open
```

### Environment Variables

| Variable | Purpose |
|----------|---------|
| `ASC_KEY_ID` | API key ID |
| `ASC_ISSUER_ID` | Issuer ID |
| `ASC_PRIVATE_KEY_PATH` | Path to .p8 key |
| `ASC_PRIVATE_KEY` | Raw key content |
| `ASC_PRIVATE_KEY_B64` | Base64 key content |
| `ASC_CONFIG_PATH` | Path to config.json |
| `ASC_PROFILE` | Default profile name |
| `ASC_APP_ID` | Default app ID |
| `ASC_VENDOR_NUMBER` | For sales/finance reports |
| `ASC_TIMEOUT` | Request timeout (e.g. 90s, 2m) |
| `ASC_DEFAULT_OUTPUT` | Default output format |
| `ASC_DEBUG` | Debug logging (1 or api) |

## Getting Started

```bash
# Initialize asc helper docs in current repo
appstore init
appstore init --path ./ASC.md
appstore init --force --link=false

# Access embedded documentation
appstore docs list
appstore docs show workflows
appstore docs init
appstore docs init --path ./ASC.md --force --link=false

# Install the asc skill pack
appstore install-skills

# Diagnose auth issues
appstore doctor
```

## Global Flags

| Flag | Purpose |
|------|---------|
| `--output table` | Human-readable table |
| `--output markdown` | Markdown format |
| `--paginate` | Fetch all pages |
| `--limit N` | Results per page |
| `--sort field` | Sort (prefix `-` for desc) |
| `--pretty` | Pretty-print JSON |
| `--profile "name"` | Use specific auth profile |
| `--debug` | Debug output |
| `--api-debug` | HTTP debug logging (redacts sensitive values) |
| `--report` | Report format for CI (e.g., junit) |
| `--report-file` | Path to write CI report file |
| `--retry-log` | Enable retry logging (overrides ASC_RETRY_LOG) |
| `--strict-auth` | Fail on multi-source credential resolution |

---

## Apps

```bash
appstore apps
appstore apps --sort name
appstore apps --paginate
```

## Builds

```bash
# List builds
appstore builds list --app "APP_ID"
appstore builds list --app "APP_ID" --sort -uploadedDate --paginate

# Build details
appstore builds info --build "BUILD_ID"

# Latest build
appstore builds latest --app "APP_ID"
appstore builds latest --app "APP_ID" --version "1.0.0" --platform IOS

# Upload build
appstore builds upload --app "APP_ID" --ipa "app.ipa"
appstore builds upload --app "APP_ID" --pkg "app.pkg" --version "1.0.0" --build-number "123"
appstore builds upload --app "APP_ID" --ipa "app.ipa" --concurrency 4 --checksum --wait
appstore builds upload --app "APP_ID" --ipa "app.ipa" --test-notes "Test login" --locale "en-US" --wait
appstore builds upload --app "APP_ID" --ipa "app.ipa" --dry-run

# Expire builds
appstore builds expire --build "BUILD_ID" --confirm
appstore builds expire-all --app "APP_ID" --older-than 90d --dry-run
appstore builds expire-all --app "APP_ID" --older-than 90d --confirm

# Build groups
appstore builds add-groups --build "BUILD_ID" --group "GROUP_ID"
appstore builds remove-groups --build "BUILD_ID" --group "GROUP_ID" --confirm

# Build testers
appstore builds individual-testers list --build "BUILD_ID"
appstore builds individual-testers add --build "BUILD_ID" --tester "TESTER_ID"
appstore builds individual-testers remove --build "BUILD_ID" --tester "TESTER_ID"

# Test notes
appstore builds test-notes list --build "BUILD_ID"
appstore builds test-notes create --build "BUILD_ID" --locale "en-US" --whats-new "Test the new login"
appstore builds test-notes update --id "LOC_ID" --whats-new "Updated notes"
appstore builds test-notes delete --id "LOC_ID" --confirm

# Build metrics
appstore builds metrics beta-usages --build "BUILD_ID"

# Upload management
appstore builds uploads list --app "APP_ID"
appstore builds uploads get --id "UPLOAD_ID"
appstore builds uploads delete --id "UPLOAD_ID" --confirm

# Build relationships
appstore builds app get --build "BUILD_ID"
appstore builds pre-release-version get --build "BUILD_ID"
appstore builds icons list --build "BUILD_ID"
```

## TestFlight

```bash
# Feedback
appstore feedback --app "APP_ID"
appstore feedback --app "APP_ID" --device-model "iPhone15,3" --os-version "17.2"
appstore feedback --app "APP_ID" --app-platform IOS --paginate

# Crashes
appstore crashes --app "APP_ID" --output table
appstore crashes --app "APP_ID" --sort -createdDate --limit 5 --paginate

# TestFlight apps
appstore testflight apps list
appstore testflight apps get --app "APP_ID"

# Sync config to YAML
appstore testflight sync pull --app "APP_ID" --output "./testflight.yaml"
appstore testflight sync pull --app "APP_ID" --output "./testflight.yaml" --include-builds --include-testers

# Review and submission
appstore testflight review get --app "APP_ID"
appstore testflight review submit --build "BUILD_ID" --confirm

# Beta details
appstore testflight beta-details get --build "BUILD_ID"
appstore testflight beta-details update --id "DETAIL_ID" --auto-notify

# Beta license agreements
appstore testflight beta-license-agreements list --app "APP_ID"
appstore testflight beta-license-agreements update --id "ID" --agreement-text "New terms"

# Beta notifications
appstore testflight beta-notifications create --build "BUILD_ID"

# Metrics
appstore testflight metrics public-link --group "GROUP_ID"
appstore testflight metrics beta-tester-usages --app "APP_ID"
```

## Beta Groups

```bash
appstore testflight beta-groups list --app "APP_ID"
appstore testflight beta-groups list --app "APP_ID" --internal
appstore testflight beta-groups list --app "APP_ID" --external --paginate
appstore testflight beta-groups create --app "APP_ID" --name "Beta Testers"
appstore testflight beta-groups create --app "APP_ID" --name "Internal" --internal
appstore testflight beta-groups get --id "GROUP_ID"
appstore testflight beta-groups update --id "GROUP_ID" --name "New Name"
appstore testflight beta-groups update --id "GROUP_ID" --public-link-enabled --feedback-enabled
appstore testflight beta-groups delete --id "GROUP_ID" --confirm
appstore testflight beta-groups add-testers --group "GROUP_ID" --tester "TESTER_ID"
appstore testflight beta-groups remove-testers --group "GROUP_ID" --tester "TESTER_ID"
appstore testflight beta-groups app get --group-id "GROUP_ID"
```

## Beta Testers

```bash
appstore testflight beta-testers list --app "APP_ID"
appstore testflight beta-testers list --app "APP_ID" --build "BUILD_ID"
appstore testflight beta-testers list --app "APP_ID" --group "Beta" --paginate
appstore testflight beta-testers get --id "TESTER_ID"
appstore testflight beta-testers add --app "APP_ID" --email "t@test.com" --group "Beta"
appstore testflight beta-testers remove --app "APP_ID" --email "t@test.com"
appstore testflight beta-testers invite --app "APP_ID" --email "t@test.com"
appstore testflight beta-testers add-groups --id "TESTER_ID" --group "GROUP_ID"
appstore testflight beta-testers remove-groups --id "TESTER_ID" --group "GROUP_ID"
appstore testflight beta-testers add-builds --id "TESTER_ID" --build "BUILD_ID"
appstore testflight beta-testers remove-builds --id "TESTER_ID" --build "BUILD_ID" --confirm
appstore testflight beta-testers metrics --tester-id "TESTER_ID" --app "APP_ID"
```

## Devices

```bash
appstore devices list
appstore devices list --platform IOS --status ENABLED --udid "UDID1,UDID2"
appstore devices list --name "My iPhone" --paginate
appstore devices get --id "DEVICE_ID"
appstore devices register --name "My iPhone" --udid "UDID" --platform IOS
appstore devices register --name "My Mac" --udid-from-system --platform MAC_OS
appstore devices update --id "DEVICE_ID" --name "New Name"
appstore devices update --id "DEVICE_ID" --status DISABLED
appstore devices local-udid
```

## Reviews

```bash
appstore reviews --app "APP_ID"
appstore reviews --app "APP_ID" --stars 1 --output table
appstore reviews --app "APP_ID" --territory US --sort -createdDate --paginate
appstore reviews get --id "REVIEW_ID"
appstore reviews ratings --app "APP_ID"
appstore reviews summarizations --app "APP_ID" --platform IOS --territory USA
appstore reviews respond --review-id "REVIEW_ID" --response "Thanks!"
appstore reviews response get --id "RESPONSE_ID"
appstore reviews response for-review --review-id "REVIEW_ID"
appstore reviews response delete --id "RESPONSE_ID" --confirm
```

## App Tags

```bash
appstore app-tags list --app "APP_ID"
appstore app-tags list --app "APP_ID" --visible-in-app-store true --sort -name
appstore app-tags get --app "APP_ID" --id "TAG_ID"
appstore app-tags update --id "TAG_ID" --visible-in-app-store=false --confirm
appstore app-tags territories --id "TAG_ID" --fields currency
appstore app-tags list --app "APP_ID" --paginate
```

## App Events

```bash
appstore app-events list --app "APP_ID"
appstore app-events localizations list --event-id "EVENT_ID"
appstore app-events localizations screenshots list --localization-id "LOC_ID"
appstore app-events localizations video-clips list --localization-id "LOC_ID"
```

## Alternative Distribution

```bash
appstore alternative-distribution domains list
appstore alternative-distribution domains create --domain "example.com" --reference-name "Example"
appstore alternative-distribution domains delete --domain-id "ID" --confirm
appstore alternative-distribution keys list
appstore alternative-distribution keys create --app "APP_ID" --public-key-path "./key.pem"
appstore alternative-distribution keys app --app "APP_ID"
appstore alternative-distribution packages create --app-store-version-id "VERSION_ID"
appstore alternative-distribution packages get --package-id "PKG_ID"
appstore alternative-distribution packages versions list --package-id "PKG_ID"
```

## Analytics & Sales

```bash
# Sales reports
appstore analytics sales --vendor "VENDOR" --type SALES --subtype SUMMARY --frequency DAILY --date "2024-01-20"
appstore analytics sales --vendor "VENDOR" --type SALES --subtype SUMMARY --frequency DAILY --date "2024-01-20" --decompress

# Analytics requests
appstore analytics request --app "APP_ID" --access-type ONGOING
appstore analytics requests --app "APP_ID" --paginate

# Get reports
appstore analytics get --request-id "REQ_ID"
appstore analytics get --request-id "REQ_ID" --date "2024-01-20"
appstore analytics get --request-id "REQ_ID" --include-segments

# Download
appstore analytics download --request-id "REQ_ID" --instance-id "INSTANCE_ID"
```

## Finance Reports

```bash
appstore finance reports --vendor "VENDOR" --report-type FINANCIAL --region "ZZ" --date "2025-12"
appstore finance reports --vendor "VENDOR" --report-type FINANCE_DETAIL --region "Z1" --date "2025-12" --decompress
appstore finance regions --output table
```

## Sandbox Testers

```bash
appstore sandbox list
appstore sandbox list --email "tester@test.com" --territory "USA" --paginate
appstore sandbox get --id "ID"
appstore sandbox get --email "tester@test.com"
appstore sandbox update --id "ID" --territory "USA"
appstore sandbox update --email "tester@test.com" --interrupt-purchases
appstore sandbox clear-history --id "ID" --confirm
```

## Xcode Cloud

```bash
# Workflows
appstore xcode-cloud workflows --app "APP_ID" --paginate
appstore xcode-cloud build-runs --workflow-id "WORKFLOW_ID" --paginate

# Trigger builds
appstore xcode-cloud run --app "APP_ID" --workflow "CI Build" --branch "main"
appstore xcode-cloud run --workflow-id "WORKFLOW_ID" --git-reference-id "REF_ID"
appstore xcode-cloud run --app "APP_ID" --workflow "Deploy" --branch "release/1.0" --wait
appstore xcode-cloud run --app "APP_ID" --workflow "CI" --branch "main" --wait --poll-interval 30s --timeout 1h

# Status
appstore xcode-cloud status --run-id "BUILD_RUN_ID" --output table
appstore xcode-cloud status --run-id "BUILD_RUN_ID" --wait

# Products
appstore xcode-cloud products --app "APP_ID"

# SCM
appstore xcode-cloud scm providers list
appstore xcode-cloud scm repositories list
appstore xcode-cloud scm repositories git-references --repo-id "REPO_ID"

# Artifacts
appstore xcode-cloud actions --run-id "BUILD_RUN_ID"
appstore xcode-cloud artifacts list --action-id "ACTION_ID"
appstore xcode-cloud artifacts download --id "ARTIFACT_ID" --path "./artifact.zip"

# Test results
appstore xcode-cloud test-results list --action-id "ACTION_ID"
appstore xcode-cloud issues list --action-id "ACTION_ID"

# Versions
appstore xcode-cloud macos-versions
appstore xcode-cloud xcode-versions
```

## Notarization

```bash
appstore notarization submit --file ./MyApp.zip
appstore notarization submit --file ./MyApp.zip --wait
appstore notarization submit --file ./MyApp.zip --wait --poll-interval 30s --timeout 1h
appstore notarization status --id "SUBMISSION_ID"
appstore notarization log --id "SUBMISSION_ID"
appstore notarization list --output table
```

## Game Center

```bash
# Achievements
appstore game-center achievements list --app "APP_ID"
appstore game-center achievements create --app "APP_ID" --reference-name "First Win" --vendor-id "com.example.firstwin" --points 10
appstore game-center achievements update --id "ID" --points 20
appstore game-center achievements delete --id "ID" --confirm
appstore game-center achievements localizations list --achievement-id "ID"
appstore game-center achievements localizations create --achievement-id "ID" --locale en-US --name "First Win" --before-earned-description "Win" --after-earned-description "Won!"
appstore game-center achievements images upload --localization-id "LOC_ID" --file "image.png"
appstore game-center achievements releases create --app "APP_ID" --achievement-id "ID"

# Leaderboards
appstore game-center leaderboards list --app "APP_ID"
appstore game-center leaderboards create --app "APP_ID" --reference-name "High Score" --vendor-id "com.example.highscore" --formatter INTEGER --sort DESC --submission-type BEST_SCORE
appstore game-center leaderboards localizations create --leaderboard-id "ID" --locale en-US --name "High Score"
appstore game-center leaderboards images upload --localization-id "LOC_ID" --file "image.png"

# Leaderboard Sets
appstore game-center leaderboard-sets list --app "APP_ID"
appstore game-center leaderboard-sets create --app "APP_ID" --reference-name "Season 1" --vendor-id "com.example.season1"
appstore game-center leaderboard-sets members set --set-id "SET_ID" --leaderboard-ids "id1,id2,id3"
```

## Signing

```bash
appstore signing fetch --bundle-id "com.example.app" --profile-type IOS_APP_STORE --output "./signing"
appstore signing fetch --bundle-id "com.example.app" --profile-type IOS_APP_DEVELOPMENT --device "DEVICE_ID" --create-missing
```

## Certificates

```bash
appstore certificates list
appstore certificates list --certificate-type "IOS_DISTRIBUTION,IOS_DEVELOPMENT" --paginate
appstore certificates get --id "CERT_ID"
appstore certificates create --certificate-type "IOS_DISTRIBUTION" --csr "./CertificateSigningRequest.certSigningRequest"
appstore certificates revoke --id "CERT_ID" --confirm
```

## Profiles

```bash
appstore profiles list
appstore profiles list --profile-type "IOS_APP_STORE,IOS_APP_DEVELOPMENT" --paginate
appstore profiles get --id "PROFILE_ID" --include "bundleId,certificates,devices"
appstore profiles create --name "My Profile" --profile-type IOS_APP_STORE --bundle "BUNDLE_ID" --certificate "CERT_ID"
appstore profiles create --name "Dev Profile" --profile-type IOS_APP_DEVELOPMENT --bundle "BUNDLE_ID" --certificate "CERT_ID" --device "DEVICE_ID1,DEVICE_ID2"
appstore profiles download --id "PROFILE_ID" --output "./profile.mobileprovision"
appstore profiles delete --id "PROFILE_ID" --confirm
```

## Bundle IDs

```bash
appstore bundle-ids list --paginate
appstore bundle-ids get --id "BUNDLE_ID"
appstore bundle-ids create --identifier "com.example.app" --name "My App" --platform IOS
appstore bundle-ids update --id "BUNDLE_ID" --name "New Name"
appstore bundle-ids delete --id "BUNDLE_ID" --confirm
appstore bundle-ids capabilities list --bundle "BUNDLE_ID"
appstore bundle-ids capabilities add --bundle "BUNDLE_ID" --capability IN_APP_PURCHASE
```

## Subscriptions

```bash
# Groups
appstore subscriptions groups list --app "APP_ID"
appstore subscriptions groups create --app "APP_ID" --reference-name "Premium"
appstore subscriptions groups update --id "GROUP_ID" --reference-name "Premium+"
appstore subscriptions groups delete --id "GROUP_ID" --confirm
appstore subscriptions groups submit --group-id "GROUP_ID" --confirm

# Group localizations
appstore subscriptions groups localizations list --group-id "GROUP_ID"
appstore subscriptions groups localizations create --group-id "GROUP_ID" --locale en-US --name "Premium"

# Subscriptions
appstore subscriptions list --group "GROUP_ID"
appstore subscriptions create --group "GROUP_ID" --ref-name "Monthly" --product-id "com.example.monthly" --subscription-period "ONE_MONTH"
appstore subscriptions get --id "SUB_ID"
appstore subscriptions update --id "SUB_ID" --ref-name "Monthly Premium"
appstore subscriptions delete --id "SUB_ID" --confirm
appstore subscriptions submit --subscription-id "SUB_ID" --confirm

# Pricing
appstore subscriptions pricing --app "APP_ID"
appstore subscriptions pricing --subscription-id "SUB_ID" --territory "USA"
appstore subscriptions prices list --id "SUB_ID"

# Availability
appstore subscriptions availability get --subscription-id "SUB_ID"
appstore subscriptions availability set --id "SUB_ID" --territory "USA,GBR,JPN"

# Offers
appstore subscriptions introductory-offers list --subscription-id "SUB_ID"
appstore subscriptions introductory-offers create --subscription-id "SUB_ID" --offer-duration "ONE_MONTH" --offer-mode "FREE_TRIAL" --number-of-periods 1
appstore subscriptions promotional-offers list --subscription-id "SUB_ID"
appstore subscriptions promotional-offers create --subscription-id "SUB_ID" --offer-code "PROMO1" --name "Holiday" --offer-duration "ONE_MONTH" --offer-mode "PAY_AS_YOU_GO" --number-of-periods 3

# Price points
appstore subscriptions price-points list --subscription-id "SUB_ID"
```

## In-App Purchases

```bash
appstore iap list --app "APP_ID" --paginate
appstore iap list --app "APP_ID" --legacy
appstore iap create --app "APP_ID" --type CONSUMABLE --ref-name "100 Coins" --product-id "com.example.coins100"
appstore iap update --id "IAP_ID" --ref-name "200 Coins"
appstore iap delete --id "IAP_ID" --confirm
appstore iap prices --app "APP_ID"
appstore iap submit --iap-id "IAP_ID" --confirm
appstore iap localizations list --iap-id "IAP_ID"
appstore iap localizations create --iap-id "IAP_ID" --locale en-US --name "100 Coins" --description "Buy 100 coins"
appstore iap availability get --iap-id "IAP_ID"
appstore iap availability set --iap-id "IAP_ID" --territories "USA,GBR,JPN"
appstore iap price-points list --iap-id "IAP_ID"
appstore iap price-schedules get --iap-id "IAP_ID"
```

## Offer Codes

```bash
appstore offer-codes list --offer-code "OFFER_CODE_ID" --paginate
appstore offer-codes get --offer-code-id "ID"
appstore offer-codes create --subscription-id "SUB_ID" --name "Holiday" --customer-eligibilities "NEW,EXISTING" --offer-eligibility "ONCE" --duration "ONE_MONTH" --offer-mode "PAY_AS_YOU_GO" --number-of-periods 3 --prices "USA:PRICE_POINT_ID"
appstore offer-codes update --offer-code-id "ID" --active false
appstore offer-codes generate --offer-code "ID" --quantity 10 --expiration-date "2026-02-01"
appstore offer-codes values --id "ID" --output "./offer-codes.txt"
appstore offer-codes custom-codes list --offer-code-id "ID"
appstore offer-codes custom-codes create --offer-code-id "ID" --custom-code "HOLIDAY2026"
```

## Performance

```bash
appstore performance metrics list --app "APP_ID"
appstore performance metrics list --app "APP_ID" --metric-type "LAUNCH,HANG" --platform IOS
appstore performance metrics get --build "BUILD_ID"
appstore performance diagnostics list --build "BUILD_ID" --diagnostic-type "DISK_WRITES,HANGS"
appstore performance diagnostics get --id "SIGNATURE_ID"
appstore performance download --app "APP_ID" --output "./metrics.json"
```

## Webhooks

```bash
appstore webhooks list --app "APP_ID"
appstore webhooks get --webhook-id "ID"
appstore webhooks create --app "APP_ID" --name "Build Notifications" --url "https://example.com/webhook" --secret "secret" --events "SUBSCRIPTION.CREATED,SUBSCRIPTION.UPDATED" --enabled true
appstore webhooks update --webhook-id "ID" --url "https://new-url.com/webhook" --enabled false
appstore webhooks delete --webhook-id "ID" --confirm
appstore webhooks deliveries --webhook-id "ID" --created-after "2025-01-01"
appstore webhooks deliveries relationships --webhook-id "ID"
appstore webhooks deliveries redeliver --delivery-id "ID"
appstore webhooks ping --webhook-id "ID"

# Local webhook receiver (testing/automation)
appstore webhooks serve --port 8787 --dir ./webhook-events
```

## Publish (End-to-End)

```bash
# TestFlight publish
appstore publish testflight --app "APP_ID" --ipa "app.ipa" --group "Beta Testers"
appstore publish testflight --app "APP_ID" --ipa "app.ipa" --group "Internal,External" --notify --wait
appstore publish testflight --app "APP_ID" --ipa "app.ipa" --group "Beta" --test-notes "Test login" --locale "en-US" --wait

# App Store publish
appstore publish appstore --app "APP_ID" --ipa "app.ipa" --submit --confirm --wait
```

## Versions

```bash
appstore versions list --app "APP_ID" --paginate
appstore versions get --version-id "VERSION_ID"
appstore versions create --app "APP_ID" --version "1.0.0"
appstore versions create --app "APP_ID" --version "2.0.0" --platform IOS --release-type MANUAL
appstore versions update --version-id "VERSION_ID" --version "1.0.1"
appstore versions delete --version-id "VERSION_ID" --confirm
appstore versions attach-build --version-id "VERSION_ID" --build "BUILD_ID"
appstore versions release --version-id "VERSION_ID" --confirm
appstore versions phased-release get --version-id "VERSION_ID"
appstore versions phased-release create --version-id "VERSION_ID"
appstore versions phased-release update --id "ID" --state PAUSED
```

## App Info

```bash
appstore app-info get --app "APP_ID"
appstore app-info get --app "APP_ID" --version "1.2.3" --platform IOS
appstore app-info get --app "APP_ID" --include "ageRatingDeclaration,territoryAgeRatings"
appstore app-info set --app "APP_ID" --locale "en-US" --whats-new "Bug fixes"
appstore app-info set --app "APP_ID" --locale "en-US" --description "My app" --keywords "app,tool" --support-url "https://example.com"
```

## App Setup

```bash
appstore app-setup info set --app "APP_ID" --primary-locale "en-US" --bundle-id "com.example.app"
appstore app-setup info set --app "APP_ID" --locale "en-US" --name "My App" --subtitle "Great app"
appstore app-setup categories set --app "APP_ID" --primary GAMES --secondary ENTERTAINMENT
appstore app-setup availability set --app "APP_ID" --territory "USA,GBR" --available true
appstore app-setup pricing set --app "APP_ID" --price-point "PRICE_POINT_ID" --base-territory "USA"
appstore app-setup localizations upload --version "VERSION_ID" --path "./localizations"
```

## Localizations

```bash
appstore localizations list --version "VERSION_ID" --paginate
appstore localizations list --app "APP_ID" --type app-info
appstore localizations download --version "VERSION_ID" --path "./localizations"
appstore localizations upload --version "VERSION_ID" --path "./localizations"
```

## Build Localizations

```bash
appstore build-localizations list --build "BUILD_ID" --paginate
appstore build-localizations create --build "BUILD_ID" --locale "en-US" --whats-new "Bug fixes"
appstore build-localizations update --id "LOC_ID" --whats-new "New features"
appstore build-localizations delete --id "LOC_ID" --confirm
```

## Pre-Release Versions

```bash
appstore pre-release-versions list --app "APP_ID" --paginate
appstore pre-release-versions list --app "APP_ID" --platform IOS --version "1.0.0"
appstore pre-release-versions get --id "PRERELEASE_ID"
```

## Screenshots & Video Previews

```bash
# Screenshots - App Store workflow
appstore screenshots list --version-localization "LOC_ID"
appstore screenshots sizes
appstore screenshots sizes --display-type "APP_IPHONE_69"
appstore screenshots upload --version-localization "LOC_ID" --path "./screenshots/" --device-type "IPHONE_69"
appstore screenshots download --version-localization "LOC_ID" --output-dir "./screenshots/downloaded"
appstore screenshots delete --id "SCREENSHOT_ID" --confirm

# Screenshots - Local workflow (experimental)
appstore screenshots run --plan .asc/screenshots.json
appstore screenshots capture --bundle-id "com.example.app" --name home
appstore screenshots frame --input "./screenshots/raw/home.png" --device iphone-air
appstore screenshots list-frame-devices --output json
appstore screenshots review-generate --framed-dir ./screenshots/framed
appstore screenshots review-open --output-dir ./screenshots/review
appstore screenshots review-approve --all-ready --output-dir ./screenshots/review

# Screenshot sets
appstore localizations screenshot-sets delete --set-id "SET_ID" --confirm

# Video previews
appstore video-previews list --version-localization "LOC_ID"
appstore video-previews upload --version-localization "LOC_ID" --path "./previews/" --device-type IPHONE_65
appstore video-previews delete --id "PREVIEW_ID" --confirm
```

## App Clips

```bash
appstore app-clips list --app "APP_ID"
appstore app-clips get --id "APP_CLIP_ID"
appstore app-clips default-experiences list --app-clip-id "ID"
appstore app-clips default-experiences create --app-clip-id "ID" --action OPEN
appstore app-clips advanced-experiences list --app-clip-id "ID"
appstore app-clips advanced-experiences create --app-clip-id "ID" --link "https://example.com/clip" --default-language en
appstore app-clips header-images create --localization-id "LOC_ID" --file "header.png"
appstore app-clips invocations list --build-bundle-id "BUNDLE_ID"
appstore app-clips domain-status cache --build-bundle-id "BUNDLE_ID"
```

## Encryption

```bash
appstore encryption declarations list --app "APP_ID"
appstore encryption declarations get --id "DECLARATION_ID"
appstore encryption declarations create --app "APP_ID" --app-description "Uses HTTPS only" --contains-proprietary-cryptography false --contains-third-party-cryptography false
appstore encryption declarations assign-builds --id "DECLARATION_ID" --build "BUILD_ID1,BUILD_ID2"
appstore encryption documents upload --declaration "DECLARATION_ID" --file "./encryption-doc.pdf"
```

## Background Assets

```bash
appstore background-assets list --app "APP_ID"
appstore background-assets create --app "APP_ID" --asset-pack-identifier "com.example.assets.pack1"
appstore background-assets update --id "ASSET_ID" --archived true
appstore background-assets versions list --background-asset-id "ASSET_ID"
appstore background-assets upload-files create --version-id "VERSION_ID" --file "./asset.bin" --asset-type ASSET
```

## Routing Coverage

```bash
appstore routing-coverage get --version-id "VERSION_ID"
appstore routing-coverage create --version-id "VERSION_ID" --file "./routing.geojson"
appstore routing-coverage delete --id "COVERAGE_ID" --confirm
```

## Workflow

```bash
appstore workflow validate
appstore workflow list
appstore workflow run --dry-run beta
appstore workflow run beta BUILD_ID:123456789 GROUP_ID:abcdef
```

## Categories

```bash
appstore categories list --output table
appstore categories set --app "APP_ID" --primary GAMES --secondary ENTERTAINMENT
```

## Validate (Pre-Submission)

```bash
# App Store version validation
appstore validate --app "APP_ID" --version-id "VERSION_ID"
appstore validate --app "APP_ID" --version-id "VERSION_ID" --platform IOS --output table
appstore validate --app "APP_ID" --version-id "VERSION_ID" --strict

# TestFlight build validation
appstore validate testflight --app "APP_ID" --build "BUILD_ID"

# In-App Purchase validation
appstore validate iap --app "APP_ID"

# Subscription validation
appstore validate subscriptions --app "APP_ID"
```

## Submit

```bash
appstore submit create --app "APP_ID" --version "1.0.0" --build "BUILD_ID" --confirm
appstore submit status --id "SUBMISSION_ID"
appstore submit status --version-id "VERSION_ID"
appstore submit cancel --id "SUBMISSION_ID" --confirm
```

## Migrate (Fastlane)

```bash
appstore migrate validate --fastlane-dir ./fastlane
appstore migrate import --app "APP_ID" --version-id "VERSION_ID" --fastlane-dir ./fastlane
appstore migrate import --dry-run
appstore migrate export --app "APP_ID" --version-id "VERSION_ID" --output-dir ./exported-metadata
```

## Notify

```bash
appstore notify slack --webhook "WEBHOOK_URL" --message "Build deployed!"
appstore notify slack --webhook "WEBHOOK_URL" --message "v1.0.0 live" --channel "#releases"

# Thread replies and release payload
appstore notify slack --webhook "WEBHOOK_URL" --message "Follow-up" --thread-ts "1234567890.123456"
appstore notify slack --webhook "WEBHOOK_URL" --release-payload --app "APP_ID" --version "1.2.3"
```

## Account

```bash
appstore account status
appstore account status --app "APP_ID"
appstore account status --output table
```

## Insights

```bash
# Weekly insights (this week vs last week)
appstore insights weekly --app "APP_ID" --source analytics --week "2026-02-16"
appstore insights weekly --app "APP_ID" --source sales --week "2026-02-16" --vendor "12345678"

# Daily insights (subscription renewal signals)
appstore insights daily --app "APP_ID" --vendor "12345678" --date "2026-02-20"
```

## Status (Release Pipeline Dashboard)

```bash
appstore status --app "APP_ID"
appstore status --app "APP_ID" --include builds,testflight,submission
appstore status --app "APP_ID" --output table
appstore status --app "APP_ID" --output markdown
```

## Release Notes

```bash
appstore release-notes generate --since-tag "v1.2.2"
appstore release-notes generate --since-tag "v1.2.2" --until-ref "HEAD" --output markdown
appstore release-notes generate --since-ref "origin/main" --until-ref "HEAD" --max-chars 4000
```

## Metadata (Deterministic File Workflows)

```bash
# Pull metadata from App Store Connect
appstore metadata pull --app "APP_ID" --version "1.2.3" --dir "./metadata"
appstore metadata pull --app "APP_ID" --version "1.2.3" --platform IOS --dir "./metadata"

# Push metadata changes
appstore metadata push --app "APP_ID" --version "1.2.3" --dir "./metadata"

# Validate offline
appstore metadata validate --dir "./metadata"
```

## Diff (Localization Comparison)

```bash
# Compare local files vs remote
appstore diff localizations --app "APP_ID" --path "./metadata/localizations" --version "VERSION_ID"

# Compare two remote versions
appstore diff localizations --app "APP_ID" --from-version "VERSION_ID_A" --to-version "VERSION_ID_B"
```

## Pricing

```bash
# Territories
appstore pricing territories list

# Price points
appstore pricing price-points --app "APP_ID"
appstore pricing price-points --app "APP_ID" --territory "USA"
appstore pricing price-points get --price-point "PRICE_POINT_ID"
appstore pricing price-points equalizations --price-point "PRICE_POINT_ID"

# Price schedule
appstore pricing schedule get --app "APP_ID"
appstore pricing schedule get --id "SCHEDULE_ID"
appstore pricing schedule create --app "APP_ID" --price-point "PRICE_POINT_ID" --base-territory "USA" --start-date "2024-03-01"
appstore pricing schedule manual-prices --schedule "SCHEDULE_ID"
appstore pricing schedule automatic-prices --schedule "SCHEDULE_ID"

# Availability
appstore pricing availability get --app "APP_ID"
appstore pricing availability get --id "AVAILABILITY_ID"
appstore pricing availability set --app "APP_ID" --territory "USA,GBR,DEU" --available true
appstore pricing availability territory-availabilities --availability "AVAILABILITY_ID"
```

## Pre-orders

```bash
appstore pre-orders get --app "APP_ID"
appstore pre-orders list --availability "AVAILABILITY_ID"
appstore pre-orders enable --app "APP_ID" --territory "USA,GBR" --release-date "2026-02-01"
appstore pre-orders update --territory-availability "TERRITORY_AVAILABILITY_ID" --release-date "2026-03-01"
appstore pre-orders disable --territory-availability "TERRITORY_AVAILABILITY_ID"
appstore pre-orders end --territory-availability "TA_1,TA_2"
```

## Accessibility

```bash
appstore accessibility list --app "APP_ID"
appstore accessibility get --id "DECLARATION_ID"
appstore accessibility create --app "APP_ID" --device-family IPHONE --supports-voiceover true
appstore accessibility update --id "DECLARATION_ID" --publish true
appstore accessibility delete --id "DECLARATION_ID" --confirm
```

## Nominations (Featuring)

```bash
appstore nominations list --status DRAFT
appstore nominations get --id "NOMINATION_ID"
appstore nominations create --app "APP_ID" --name "Launch" --type APP_LAUNCH --description "New launch" --submitted=false --publish-start-date "2026-02-01T08:00:00Z"
appstore nominations update --id "NOMINATION_ID" --notes "Updated notes"
appstore nominations delete --id "NOMINATION_ID" --confirm
```

## Product Pages

```bash
# Custom product pages
appstore product-pages custom-pages list --app "APP_ID"
appstore product-pages custom-pages create --app "APP_ID" --name "Summer Campaign"

# Product page experiments (A/B testing)
appstore product-pages experiments list --version-id "VERSION_ID"
appstore product-pages experiments create --version-id "VERSION_ID" --name "Icon Test" --traffic-proportion 25
```

## Win-back Offers

```bash
appstore win-back-offers list --subscription "SUB_ID"
appstore win-back-offers get --id "OFFER_ID"
appstore win-back-offers create --subscription "SUB_ID" --reference-name "spring-2026" --offer-id "OFFER-1" --duration ONE_MONTH --offer-mode PAY_AS_YOU_GO --period-count 1 --eligibility-paid-months 6 --eligibility-last-subscribed-min 3 --eligibility-last-subscribed-max 12 --start-date "2026-02-01" --priority HIGH --price "PRICE_ID"
appstore win-back-offers update --id "OFFER_ID" --priority NORMAL
appstore win-back-offers delete --id "OFFER_ID" --confirm
appstore win-back-offers prices --id "OFFER_ID"
appstore win-back-offers prices-relationships --id "OFFER_ID"
```

## Promoted Purchases

```bash
appstore promoted-purchases list --app "APP_ID"
appstore promoted-purchases get --promoted-purchase-id "PROMO_ID"
appstore promoted-purchases create --app "APP_ID" --product-id "PRODUCT_ID" --product-type SUBSCRIPTION --visible-for-all-users
appstore promoted-purchases update --promoted-purchase-id "PROMO_ID" --enabled false
appstore promoted-purchases delete --promoted-purchase-id "PROMO_ID" --confirm
appstore promoted-purchases link --app "APP_ID" --promoted-purchase-id "PROMO_ID"
```

## Marketplace

```bash
appstore marketplace search-details get --app "APP_ID"
appstore marketplace webhooks list
```

## Android-iOS Mapping

```bash
appstore android-ios-mapping list --app "APP_ID"
appstore android-ios-mapping get --mapping-id "MAPPING_ID"
appstore android-ios-mapping create --app "APP_ID" --android-package-name "com.example.android" --fingerprints "SHA1,SHA2"
appstore android-ios-mapping update --mapping-id "MAPPING_ID" --android-package-name "com.example.android.new"
appstore android-ios-mapping delete --mapping-id "MAPPING_ID" --confirm
```

## Agreements

```bash
appstore agreements territories list --id "EULA_ID"
```

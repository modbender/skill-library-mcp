# Common Workflows — App Store Connect

## Upload and Submit a Build

### 1. Upload via Xcode or Transporter

```bash
# Using xcrun altool (deprecated but still works)
xcrun altool --upload-app -f MyApp.ipa \
  --type ios \
  --apiKey YOUR_KEY_ID \
  --apiIssuer YOUR_ISSUER_ID

# Using Transporter CLI
/Applications/Transporter.app/Contents/itms/bin/iTMSTransporter \
  -m upload \
  -jwt "$JWT" \
  -f MyApp.ipa
```

### 2. Wait for Processing

```bash
# Check build status
curl -H "Authorization: Bearer $JWT" \
  "https://api.appstoreconnect.apple.com/v1/builds?filter[app]=APP_ID&sort=-uploadedDate&limit=1"
```

Wait until `processingState` is `VALID`.

### 3. Submit for Review

```bash
# Create app store version submission
curl -X POST -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  "https://api.appstoreconnect.apple.com/v1/appStoreVersionSubmissions" \
  -d '{
    "data": {
      "type": "appStoreVersionSubmissions",
      "relationships": {
        "appStoreVersion": {
          "data": { "type": "appStoreVersions", "id": "VERSION_ID" }
        }
      }
    }
  }'
```

## TestFlight Distribution

### Add Build to Internal Testing

Internal testers get access automatically after build processes.

```bash
# Get internal beta groups
curl -H "Authorization: Bearer $JWT" \
  "https://api.appstoreconnect.apple.com/v1/apps/APP_ID/betaGroups?filter[isInternalGroup]=true"
```

### Add Build to External Testing

```bash
# Add build to external beta group
curl -X POST -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  "https://api.appstoreconnect.apple.com/v1/betaGroups/GROUP_ID/relationships/builds" \
  -d '{
    "data": [{ "type": "builds", "id": "BUILD_ID" }]
  }'
```

First build of each version requires Beta App Review (usually 24-48h).

### Add External Testers

```bash
# Create beta tester
curl -X POST -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  "https://api.appstoreconnect.apple.com/v1/betaTesters" \
  -d '{
    "data": {
      "type": "betaTesters",
      "attributes": {
        "email": "tester@example.com",
        "firstName": "Test",
        "lastName": "User"
      },
      "relationships": {
        "betaGroups": {
          "data": [{ "type": "betaGroups", "id": "GROUP_ID" }]
        }
      }
    }
  }'
```

## Update App Metadata

### Update Description

```bash
# Get app store version localization ID
curl -H "Authorization: Bearer $JWT" \
  "https://api.appstoreconnect.apple.com/v1/appStoreVersions/VERSION_ID/appStoreVersionLocalizations"

# Update description
curl -X PATCH -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  "https://api.appstoreconnect.apple.com/v1/appStoreVersionLocalizations/LOCALIZATION_ID" \
  -d '{
    "data": {
      "type": "appStoreVersionLocalizations",
      "id": "LOCALIZATION_ID",
      "attributes": {
        "description": "Your new description here"
      }
    }
  }'
```

### Update Keywords

```bash
curl -X PATCH -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  "https://api.appstoreconnect.apple.com/v1/appStoreVersionLocalizations/LOCALIZATION_ID" \
  -d '{
    "data": {
      "type": "appStoreVersionLocalizations",
      "id": "LOCALIZATION_ID",
      "attributes": {
        "keywords": "keyword1,keyword2,keyword3"
      }
    }
  }'
```

## Download Sales Reports

```bash
# Get sales report
curl -H "Authorization: Bearer $JWT" \
  -H "Accept: application/a]gzip" \
  "https://api.appstoreconnect.apple.com/v1/salesReports?\
filter[reportType]=SALES&\
filter[reportSubType]=SUMMARY&\
filter[frequency]=DAILY&\
filter[vendorNumber]=YOUR_VENDOR_NUMBER&\
filter[reportDate]=2024-01-15" \
  --output report.csv.gz

gunzip report.csv.gz
```

## Check App Review Status

```bash
# Get app store version
curl -H "Authorization: Bearer $JWT" \
  "https://api.appstoreconnect.apple.com/v1/apps/APP_ID/appStoreVersions?filter[appStoreState]=PENDING_DEVELOPER_RELEASE,WAITING_FOR_REVIEW,IN_REVIEW"
```

### App Store States

| State | Meaning |
|-------|---------|
| PREPARE_FOR_SUBMISSION | Editable, not submitted |
| WAITING_FOR_REVIEW | Submitted, in queue |
| IN_REVIEW | Being reviewed |
| PENDING_DEVELOPER_RELEASE | Approved, waiting for manual release |
| READY_FOR_SALE | Live on App Store |
| REJECTED | Review failed |

## Create New App

```bash
# Register new bundle ID first
curl -X POST -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  "https://api.appstoreconnect.apple.com/v1/bundleIds" \
  -d '{
    "data": {
      "type": "bundleIds",
      "attributes": {
        "identifier": "com.company.newapp",
        "name": "New App Bundle",
        "platform": "IOS"
      }
    }
  }'

# Create app
curl -X POST -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  "https://api.appstoreconnect.apple.com/v1/apps" \
  -d '{
    "data": {
      "type": "apps",
      "attributes": {
        "name": "My New App",
        "primaryLocale": "en-US",
        "sku": "MYAPP001"
      },
      "relationships": {
        "bundleId": {
          "data": { "type": "bundleIds", "id": "BUNDLE_ID" }
        }
      }
    }
  }'
```

## Release Management

### Enable Phased Release

```bash
curl -X PATCH -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  "https://api.appstoreconnect.apple.com/v1/appStoreVersionPhasedReleases/PHASED_RELEASE_ID" \
  -d '{
    "data": {
      "type": "appStoreVersionPhasedReleases",
      "id": "PHASED_RELEASE_ID",
      "attributes": {
        "phasedReleaseState": "ACTIVE"
      }
    }
  }'
```

### Manual Release After Approval

```bash
curl -X PATCH -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  "https://api.appstoreconnect.apple.com/v1/appStoreVersions/VERSION_ID" \
  -d '{
    "data": {
      "type": "appStoreVersions",
      "id": "VERSION_ID",
      "attributes": {
        "releaseType": "MANUAL"
      }
    }
  }'
```

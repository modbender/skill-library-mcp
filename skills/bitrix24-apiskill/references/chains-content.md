# Chains: content

## 1) Upload file to process folder

1. `disk.storage.getlist`
2. `disk.folder.getchildren`
3. `disk.folder.uploadfile`
4. Store resulting file ID in CRM/task entity

## 2) Versioned replacement flow

1. `disk.file.get`
2. `disk.file.uploadversion`
3. Keep previous version reference for rollback

## 3) Move-and-archive pattern

1. `disk.file.moveto`
2. `disk.file.copyto` for backup
3. `disk.file.delete` only with explicit destructive confirmation

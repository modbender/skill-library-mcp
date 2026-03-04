# Chains: collab

## 1) Workgroup provisioning

1. `sonet_group.create`
2. `sonet_group.update`
3. Persist group mapping in your app store

## 2) Feed post lifecycle

1. `log.blogpost.add`
2. `log.blogcomment.add`
3. `log.blogpost.update` when status changes

## 3) Controlled cleanup

1. `sonet_group.get` and dependency checks
2. `sonet_group.delete` only with explicit destructive confirmation

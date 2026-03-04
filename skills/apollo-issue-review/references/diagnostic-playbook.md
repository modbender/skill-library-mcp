# Diagnostic Playbook

Use this file when the issue asks for concrete troubleshooting directions.

## 1) Portal page slow after upgrade

Goal: determine whether slowdown is in portal aggregation, adminservice, DB, auth dependency, or network.

1. Browser-side check
- Capture top 3 slow requests by total time and TTFB.
- Prioritize `GET /apps/{appId}/navtree` and namespace-related requests.

2. Portal-side tracing (Arthas)
```bash
trace com.ctrip.framework.apollo.portal.controller.AppController nav -n 5
trace com.ctrip.framework.apollo.portal.service.AppService createEnvNavNode -n 5
trace com.ctrip.framework.apollo.portal.service.ClusterService findClusters -n 5
```

3. Adminservice-side tracing (Arthas)
```bash
trace com.ctrip.framework.apollo.adminservice.controller.ClusterController find -n 5
trace com.ctrip.framework.apollo.biz.service.ClusterService findParentClusters -n 5
```

4. Database checks
- Enable slow SQL logs.
- Focus on cluster/appnamespace/namespace related queries.
- Run `EXPLAIN` for slow statements and verify index usage.

5. Dependency and network checks
- Measure SSO/LDAP/Keycloak/user-info dependency latency.
- Verify portal -> adminservice route (same zone or cross-zone/region).

## 2) Decide regression vs environment difference

Mark `likely-regression` only when both conditions hold:
- Controlled A/B: same data and topology, version changed.
- Hot-path code change exists between versions.

Otherwise classify as:
- `known-limit-or-unoptimized`, or
- `environment-or-dependency`.

## 3) Useful Git checks

```bash
# Compare same file across versions
git show v1.9.2:apollo-portal/src/main/java/.../AppController.java
git show v2.4.0:apollo-portal/src/main/java/.../AppController.java

# Find PR commit and check whether release tag contains it
git log --oneline --grep '#5518' -n 5
git merge-base --is-ancestor v2.4.0 <commit_sha> && echo included || echo not-included
```

## 4) Roadmap/testing-asset ask (non-regression issue)

Goal: answer "plan vs assets" directly, then provide a runnable validation baseline.

1. Clarify primary ask
- Keep either-or ask explicit, e.g. "official Spring Boot 3 plan" OR "official/near-official validation assets".
- Do not over-focus on incidental version deltas unless they change the conclusion.

2. Verify what exists today
- Check root/version facts from `pom.xml` and release tags.
- Check existing tests/docs/attachments that can be reused as validation input.
- Check linked issues/comments for maintainers' explicit support boundary statements.

3. Provide minimal SB3 self-upgrade regression checklist
- Config read: `GET /configs/{appId}/{cluster}/{namespace}`.
- Notification long polling: `GET /notifications/v2`.
- Publish flow: `POST /apps/{appId}/clusters/{cluster}/namespaces/{namespace}/releases`.
- Portal core path: `GET /apps/{appId}/navtree` and auth/login path in your deployment.

4. Include non-code verification
- DB: slow SQL and `EXPLAIN` on hot statements.
- Auth dependency: SSO/OIDC/LDAP callback and permission chain.
- Network/infra: portal -> adminservice -> configservice latency and timeout/retry policy.

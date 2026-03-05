# Deploy Guide

## Pre-deploy Checklist
- Run full test suite
- Check CI pipeline is green
- Review open PRs for conflicts
- Verify staging environment matches production

## Deploy Steps
1. Merge to main branch
2. CI builds and runs tests
3. Deploy to staging
4. Run smoke tests on staging
5. Promote staging to production
6. Monitor error rates for 15 minutes

## Rollback Procedure
If errors spike after deploy:
1. Revert the last merge commit
2. Push the revert to main
3. CI auto-deploys the revert
4. Notify the team in #incidents
5. Post-mortem within 24 hours

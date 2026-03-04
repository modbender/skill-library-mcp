#!/usr/bin/env bash
set -euo pipefail

cd "$1"

git init
git config user.email "bench@agentbench.local"
git config user.name "AgentBench"

mkdir -p skills

cat > skills/lint-code.md << 'SKILL'
# Lint Code

## Description

Run static analysis and linting checks on the source code to catch style
violations, potential bugs, and code quality issues early in the pipeline.
This step ensures code meets team standards before any further processing.

## Steps

1. Install linting dependencies (eslint, pylint, or language-appropriate linter)
2. Run the linter against all source files in the repository
3. Parse linter output and categorize issues by severity (error, warning, info)
4. Fail the pipeline if any error-level issues are found
5. Generate a lint report artifact for review
SKILL

cat > skills/build-artifacts.md << 'SKILL'
# Build Artifacts

## Description

Compile source code, resolve dependencies, and produce deployable artifacts.
This includes building container images, bundling assets, and creating
versioned release packages ready for testing and deployment.

## Steps

1. Resolve and install all project dependencies
2. Compile source code (transpile, bundle, or build as appropriate)
3. Build container image with proper tagging (git SHA + semantic version)
4. Run build-time validations (type checking, asset optimization)
5. Push artifacts to the artifact registry
SKILL

cat > skills/run-tests.md << 'SKILL'
# Run Tests

## Description

Execute the full test suite including unit tests, integration tests, and
contract tests against the built artifacts. Verify that the application
behaves correctly before it proceeds to any deployment environment.

## Steps

1. Pull the built artifacts from the artifact registry
2. Start required test infrastructure (databases, mock services)
3. Run unit tests with coverage measurement
4. Run integration tests against the built container
5. Generate test report and coverage summary
6. Fail the pipeline if coverage drops below threshold or tests fail
SKILL

cat > skills/deploy-staging.md << 'SKILL'
# Deploy to Staging

## Description

Deploy the tested artifacts to the staging environment for final validation.
The staging environment mirrors production configuration to catch
environment-specific issues before they reach real users.

## Steps

1. Provision or update staging infrastructure to match production spec
2. Deploy the container image to the staging cluster
3. Run database migrations if applicable
4. Execute smoke tests against the staging endpoint
5. Monitor error rates and latency for a 10-minute stabilization window
6. Mark the staging deployment as healthy or trigger an alert
SKILL

cat > skills/promote-production.md << 'SKILL'
# Promote to Production

## Description

Promote the staging-validated artifacts to the production environment using
a blue-green or canary deployment strategy. This is the final step that
makes the new version available to end users.

## Steps

1. Create a new production deployment with the validated artifact version
2. Route a small percentage of traffic to the new version (canary)
3. Monitor key metrics (error rate, latency p99, throughput) during canary
4. Gradually increase traffic to the new version if metrics are healthy
5. Complete cutover and drain the old version
6. Update deployment records and notify stakeholders
SKILL

git add skills/
git commit -m "Initial commit: add CI/CD pipeline skill files"

# CI/CD Integration Examples

## GitHub Actions

### Basic Workflow

```yaml
# .github/workflows/api-tests.yml
name: API Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Newman
        run: npm install -g newman newman-reporter-htmlextra
      
      - name: Run API Tests
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
        run: |
          newman run collections/api-tests.json \
            -e environments/staging.json \
            --reporters cli,htmlextra,junit \
            --reporter-htmlextra-export ./test-results/newman.html \
            --reporter-junit-export ./test-results/newman.xml \
            --bail
      
      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: newman-reports
          path: test-results/
      
      - name: Publish Test Report
        if: always()
        uses: dorny/test-reporter@v1
        with:
          name: Newman Tests
          path: test-results/newman.xml
          reporter: java-junit
```

### Multi-Environment

```yaml
# .github/workflows/api-tests-matrix.yml
name: API Tests (Multi-Env)

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, production]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Newman
        run: npm install -g newman
      
      - name: Run Tests - ${{ matrix.environment }}
        env:
          API_KEY: ${{ secrets[format('{0}_API_KEY', matrix.environment)] }}
        run: |
          newman run collections/api-tests.json \
            -e environments/${{ matrix.environment }}.json \
            --reporters cli,json \
            --reporter-json-export ./results-${{ matrix.environment }}.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: test-results-${{ matrix.environment }}
          path: results-${{ matrix.environment }}.json
```

## GitLab CI

### Basic Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - test

api_tests:
  stage: test
  image: node:18-alpine
  
  before_script:
    - npm install -g newman
  
  script:
    - |
      newman run collections/api-tests.json \
        -e environments/staging.json \
        --env-var "API_KEY=$API_KEY" \
        --reporters cli,junit \
        --reporter-junit-export newman-report.xml
  
  artifacts:
    when: always
    reports:
      junit: newman-report.xml
    paths:
      - newman-report.xml
    expire_in: 30 days
  
  variables:
    API_KEY: $CI_API_KEY
  
  only:
    - merge_requests
    - main
```

### Scheduled Tests

```yaml
# .gitlab-ci.yml
scheduled_smoke_tests:
  stage: test
  image: node:18-alpine
  
  before_script:
    - npm install -g newman newman-reporter-htmlextra
  
  script:
    - |
      newman run collections/smoke-tests.json \
        -e environments/production.json \
        --env-var "API_KEY=$PROD_API_KEY" \
        --reporters cli,htmlextra \
        --reporter-htmlextra-export smoke-test-report.html
  
  artifacts:
    paths:
      - smoke-test-report.html
    expire_in: 7 days
  
  only:
    - schedules
```

## Jenkins

### Declarative Pipeline

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        API_KEY = credentials('api-key')
        DB_PASSWORD = credentials('db-password')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'npm install -g newman newman-reporter-htmlextra'
            }
        }
        
        stage('API Tests') {
            steps {
                sh '''
                    newman run collections/api-tests.json \
                        -e environments/staging.json \
                        --env-var "API_KEY=$API_KEY" \
                        --env-var "DB_PASSWORD=$DB_PASSWORD" \
                        --reporters cli,htmlextra,junit \
                        --reporter-htmlextra-export ./reports/newman.html \
                        --reporter-junit-export ./reports/newman.xml \
                        --bail
                '''
            }
        }
    }
    
    post {
        always {
            junit 'reports/newman.xml'
            publishHTML([
                reportDir: 'reports',
                reportFiles: 'newman.html',
                reportName: 'Newman Test Report'
            ])
        }
        failure {
            emailext(
                subject: "API Tests Failed - ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Check console output at ${env.BUILD_URL}",
                to: 'team@example.com'
            )
        }
    }
}
```

### Scripted Pipeline with Parallel Execution

```groovy
// Jenkinsfile
node {
    stage('Checkout') {
        checkout scm
    }
    
    stage('Setup') {
        sh 'npm install -g newman'
    }
    
    stage('API Tests') {
        parallel(
            'Auth Tests': {
                sh 'newman run collections/auth-tests.json -e environments/staging.json'
            },
            'User Tests': {
                sh 'newman run collections/user-tests.json -e environments/staging.json'
            },
            'Payment Tests': {
                sh 'newman run collections/payment-tests.json -e environments/staging.json'
            }
        )
    }
    
    stage('Report') {
        publishHTML([
            reportDir: 'reports',
            reportFiles: '*.html',
            reportName: 'Newman Reports'
        ])
    }
}
```

## Docker

### Standalone Container

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install Newman and reporters
RUN npm install -g newman newman-reporter-htmlextra

# Copy collections and environments
COPY collections/ ./collections/
COPY environments/ ./environments/

# Entry point
ENTRYPOINT ["newman"]
CMD ["run", "collections/api-tests.json", "-e", "environments/staging.json"]
```

**Build and run:**
```bash
docker build -t api-tests .
docker run --rm -e API_KEY="secret" api-tests
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api-tests:
    image: node:18-alpine
    working_dir: /app
    volumes:
      - ./collections:/app/collections
      - ./environments:/app/environments
      - ./reports:/app/reports
    environment:
      - API_KEY=${API_KEY}
      - DB_PASSWORD=${DB_PASSWORD}
    command: >
      sh -c "npm install -g newman newman-reporter-htmlextra &&
             newman run collections/api-tests.json
             -e environments/staging.json
             --reporters cli,htmlextra
             --reporter-htmlextra-export /app/reports/newman.html"
```

**Run:**
```bash
docker-compose run --rm api-tests
```

## Bitbucket Pipelines

```yaml
# bitbucket-pipelines.yml
image: node:18

pipelines:
  default:
    - step:
        name: API Tests
        caches:
          - node
        script:
          - npm install -g newman
          - |
            newman run collections/api-tests.json \
              -e environments/staging.json \
              --env-var "API_KEY=$API_KEY" \
              --reporters cli,junit \
              --reporter-junit-export test-results/newman.xml
        artifacts:
          - test-results/**
  
  branches:
    main:
      - step:
          name: Production Smoke Tests
          deployment: production
          script:
            - npm install -g newman
            - |
              newman run collections/smoke-tests.json \
                -e environments/production.json \
                --env-var "API_KEY=$PROD_API_KEY" \
                --bail
```

## CircleCI

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  api-tests:
    docker:
      - image: cimg/node:18.0
    
    steps:
      - checkout
      
      - run:
          name: Install Newman
          command: npm install -g newman newman-reporter-htmlextra
      
      - run:
          name: Run API Tests
          command: |
            newman run collections/api-tests.json \
              -e environments/staging.json \
              --env-var "API_KEY=$API_KEY" \
              --reporters cli,htmlextra,junit \
              --reporter-htmlextra-export ./test-results/newman.html \
              --reporter-junit-export ./test-results/newman.xml
      
      - store_test_results:
          path: test-results
      
      - store_artifacts:
          path: test-results

workflows:
  version: 2
  test:
    jobs:
      - api-tests:
          context: api-credentials
```

## Best Practices for CI/CD

1. **Secret Management**: Use CI platform secrets, never commit
2. **Fail Fast**: Use `--bail` to stop on first failure
3. **Parallel Execution**: Split collections for faster feedback
4. **Artifacts**: Always save reports (even on failure)
5. **Notifications**: Alert team on failures
6. **Caching**: Cache Newman install to speed up runs
7. **Matrix Testing**: Test multiple environments in parallel
8. **Timeouts**: Set appropriate timeout values for CI
9. **Version Pinning**: Pin Newman version for consistency
10. **Smoke Tests**: Run critical tests on every deploy

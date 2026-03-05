# Reference: 06 - DevOps, CI/CD, and Version Control

DevOps is the culture and practice of automating the processes between software development and IT teams, in order that they can build, test, and release software faster and more reliably.

## 1. Version Control: Git Discipline

Version control is the backbone of a reliable development process, especially in AI-assisted workflows where frequent rollbacks may be necessary.

- **Branching Strategy**: Use **GitHub Flow**:
    1.  Create a new branch from `main` for every new feature or bugfix.
    2.  Commit your changes to that branch.
    3.  Open a Pull Request (PR) when you are ready for feedback.
    4.  After the PR is reviewed and approved, merge it into `main`.
    5.  The `main` branch is always deployable.
- **Commit Messages**: Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification (e.g., `feat: add user registration endpoint`, `fix: correct score calculation logic`).
- **Frequent Commits**: In AI-assisted development, commit after every successful, validated chunk of work. This creates frequent "save points" that you can roll back to if the AI introduces a regression in a later step. Think of it as a "Ctrl+S" for your entire project state.
- **Rollback Strategy**: Before asking the AI to make a large or risky change, always create a new branch or tag the current commit. If the change goes wrong, you can instantly revert to the known-good state.

## 2. Continuous Integration (CI)

CI is the practice of automatically building and testing your code every time a change is committed.

- **Automate Everything**: Your CI pipeline (e.g., using GitHub Actions, GitLab CI) should automatically:
    1.  Install dependencies.
    2.  Run linters to check code style.
    3.  Run all unit and integration tests.
    4.  Run security scans (dependency audit, SAST).
    5.  Build the application (e.g., create a Docker image).
- **Fail Fast**: If any step fails, the build should be marked as broken. Merging to `main` should be blocked if the CI pipeline fails.

## 3. Continuous Deployment (CD)

CD is the practice of automatically deploying your application to production after it has passed all the tests in the CI pipeline.

- **Infrastructure as Code (IaC)**: Define and manage your infrastructure using code (e.g., Terraform, Pulumi, or Docker Compose). This makes your infrastructure reproducible and version-controlled.
- **Containerization**: Package your application into a container using Docker. This ensures consistency across environments.
- **Blue-Green or Canary Deployments**: Use advanced deployment strategies to release new versions with zero downtime and the ability to quickly roll back.

## 4. Monitoring & Observability (OpenTelemetry)

Once your application is in production, you need to know what it is doing. The modern standard for observability is **OpenTelemetry** [1], which provides a unified framework for collecting three types of telemetry data:

| Pillar | Description | Tool Example |
| :--- | :--- | :--- |
| **Traces** | Track a single request as it flows through all services in your system. | Jaeger, Zipkin |
| **Metrics** | Numerical measurements of your system's health (e.g., request latency, error rate, CPU usage). | Prometheus + Grafana |
| **Logs** | Detailed, structured records of events within your application. Refer to `references/07-error-handling.md`. | ELK Stack, Datadog |

- **Health Checks**: Expose a `/health` endpoint that your deployment environment can use to check if your application is running correctly.
- **Alerting**: Set up alerts to notify you immediately if a critical metric crosses a threshold (e.g., if the error rate exceeds 5%).

---

### References

[1] OpenTelemetry. (2025). *OpenTelemetry Documentation*. opentelemetry.io.

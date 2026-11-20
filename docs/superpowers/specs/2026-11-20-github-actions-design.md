# GitHub-hosted CI/CD design

## Purpose and constraints

Extend the existing Flask and Nginx Terraform project to demonstrate all five final-project requirements. Keep the application small, retain the existing tests and local Docker workflow, and keep project files on D:. The deployment is a temporary demonstration on a GitHub-hosted Linux runner, not a persistent public service. No AWS account, self-hosted runner, or deployment secrets are needed.

## Approaches

- GitHub-hosted Linux runner (chosen): runs Docker, Terraform, and tests in a fresh disposable environment; straightforward and independent of the student's computer, but the service only exists during the job.
- Self-hosted runner: deploys to the student's Docker Desktop and can leave the service running, but requires an online machine and additional care with a public repository.

## Workflow

A workflow under .github/workflows runs automatically on pushes and can also be started manually. It checks out the repository, installs Python dependencies and a compatible Terraform version, runs application tests, then initializes, formats and validates Terraform. Terraform builds the Flask image from the existing Dockerfile and applies the existing Docker configuration noninteractively. The workflow confirms the two containers and network, verifies the HTTP health response and the existing integration tests, and checks a second Terraform plan for changes. Bounded readiness checks will allow services time to start. Tests and Terraform failures must fail the job. Cleanup runs even after a failure when initialization succeeded, while preserving the original failure status. Runner disposal is an additional cleanup boundary.

## Regression and evidence

Keep fast Flask tests separate from Docker integration tests. Add or adjust tests only where necessary to cover the pipeline's meaningful behavior; verify failures are surfaced and run the existing tests on the hosted runner. Workflow logs should clearly show the push trigger, image build and Terraform apply, running containers, successful HTTP and integration checks, no-change plan, and destroy. Capture actual GitHub Actions screenshots or relevant logs for the report; do not present recreated output as screenshots. Avoid exposing secrets, Terraform state, or credentials.

## Deliverables and acceptance

Update the concise README with local and CI instructions and explain the temporary GitHub-hosted environment. Push the workflow and show a successful run triggered by a push, including deployment and application verification. Prepare an individual report with the repository link, actual evidence and a clear explanation of the deployment setup; obtain the student's first and last name rather than guessing. Review Git status before committing so unrelated local files are not included. A successful result covers all five grading categories, even though only four are required.

## Implementation choices

The implementer may choose maintained compatible action versions and exact test commands. Existing local deployment behavior should be preserved unless a specific compatibility issue requires a documented change. GitHub-hosted runner availability and Actions permissions must be verified in the actual repository; do not claim success without a completed run.

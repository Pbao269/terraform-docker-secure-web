# GitHub-hosted CI/CD Implementation Plan

> Implement the approved design using the existing local Docker project.

**Goal:** Automatically build, deploy, test, and destroy the application on GitHub-hosted runners.
**Architecture:** A GitHub Actions job checks out source, runs unit tests, uses Terraform to build the image and deploy both containers, runs live verification and a no-change plan, and cleans up. Logs provide submission evidence.
**Tech stack:** GitHub Actions, Python/pytest, Terraform, Docker.
**Spec:** docs/superpowers/specs/2026-11-20-github-actions-design.md

## Constraints and review focus

Keep local deployment and tests working; no state or secrets in the repository; fail on unavailable service, failing tests, infrastructure drift, or failed deployment; clean up after failures; do not include the existing local submission document. Use Kris To in the final report.

## Task 1: Workflow and regression verification

Files: create `.github/workflows/ci.yml`; retain `tests/test_app.py` and `tests/test_deployment.py`.

- [ ] Confirm existing tests and deployment inputs and establish a failing check for the absent automated workflow.
- [ ] Add a push and manual-triggered Linux workflow with checkout, Python and Terraform setup, unit tests, Terraform init/fmt/validate/apply, bounded readiness, container and HTTP output, integration tests, no-change plan and always-run cleanup.
- [ ] Check workflow syntax and run the existing fast tests locally; run deployment and integration checks when Docker is available.

## Task 2: Documentation and published verification

Files: modify `README.md`; create this plan and approved design.

- [ ] Document the runner, transient deployment, CI logs and existing local commands.
- [ ] Inspect the diff and repository status; commit only intended project files and push to the existing repository.
- [ ] Inspect the push-triggered run through completion and resolve failures; verify the build, apply and application checks in its logs.
- [ ] Prepare a concise report with Kris To, repository URL, setup, and genuine run evidence if the necessary tools and run are available.

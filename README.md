# Terraform Secure Web Application

**Option 1: Secure Web Application.** Terraform manages an Nginx reverse proxy and a Flask application on a private Docker network. Only Nginx is published, on `127.0.0.1:8080`. Nginx uses the container name `secure-web-app` to reach Flask and adds the `X-Content-Type-Options: nosniff` security header. Its configuration is mounted read-only. This is a small learning example, not a production security configuration.

## Prerequisites

Docker Desktop with its engine running, Terraform 1.5 or newer, and Python with Flask and pytest installed for testing. Docker must be able to access the project directory for the bind mount. Ports and container names must be available. The first apply downloads container images and Python packages.

## Deploy and verify

Run from this directory (PowerShell; use `curl` instead of `curl.exe` on other systems):

```powershell
terraform version
docker version
docker ps
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
docker ps
docker network inspect secure-web-network
curl.exe -i http://localhost:8080/health
python -m pytest -q
python -m pytest -o addopts= -m integration -q
terraform plan
```

The health request should return `{"status":"healthy"}` with the `X-Content-Type-Options: nosniff` header. The first test command checks Flask without containers. The second exercises the deployed proxy and verifies the network and port bindings. The final plan should say `No changes`.

Capture the requested screenshots or terminal output before cleanup, including communication, the no-change plan, and the subsequent destroy output. Then run:

```powershell
terraform destroy
```

For development tests, install `requirements.txt` and pytest in your Python environment. Re-run both test commands after making changes; integration tests require a running deployment.

## GitHub Actions

A push to GitHub automatically starts the **Build, deploy, and verify** workflow; it can also be started manually from the Actions tab. A GitHub-hosted Linux runner builds the Flask image with Terraform, deploys both containers to its own Docker engine, runs the application and deployment tests, checks for Terraform drift, and destroys the resources. The deployment is temporary and exists only during the job. Open the workflow run to see the Terraform output, container status, health response, and test results. No self-hosted runner or deployment credentials are required.

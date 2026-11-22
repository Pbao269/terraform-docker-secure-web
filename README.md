# Weather Lookup with Terraform and Docker

A small Flask weather app behind an Nginx reverse proxy. Search for a city to see current model-based weather, humidity, and wind. Weather data and location search are provided by [Open-Meteo](https://open-meteo.com/). An internet connection is needed for weather lookups; no API key is required for this noncommercial project.

Terraform builds the Flask image and manages both containers on a private Docker network. Nginx forwards requests to Flask by container name and is the only service exposed to the host, at `127.0.0.1:8080`. The Nginx configuration is mounted read-only. This is a learning project, not a production security configuration.

## Deploy and test locally

Install Docker Desktop, Terraform 1.5 or newer, Python, and the dependencies in `requirements.txt` plus pytest. Start Docker Desktop and run from the project directory:

```sh
terraform init
terraform fmt -check
terraform validate
terraform apply
```

Open http://localhost:8080 and search for a city. Include the region or country to narrow ambiguous results. The health endpoint at http://localhost:8080/health does not depend on the weather service.

```sh
python -m pytest -q
python -m pytest -o addopts= -m integration -q
terraform plan
```

The first test command uses controlled weather-service responses; the second checks the deployed application and Docker networking. The final plan should report no changes. To remove the containers and network when finished, run `terraform destroy`.

## GitHub Actions

A push automatically starts the **Build, deploy, and verify** workflow; it can also be started manually from the Actions tab. A GitHub-hosted Linux runner builds the Flask image with Terraform, deploys both containers to its own Docker engine, runs the application and deployment tests, checks for Terraform drift, and destroys the resources. The deployment is temporary and exists only during the job. The run logs show the Terraform output, container status, health response, and test results. No self-hosted runner or deployment credentials are required.

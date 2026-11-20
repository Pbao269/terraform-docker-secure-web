terraform {
  required_version = ">= 1.5.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_network" "app" {
  name = "secure-web-network"
}

resource "docker_image" "app" {
  name = "secure-web-app:local"
  build {
    context = abspath(path.module)
  }
  triggers = {
    app          = filesha256("${path.module}/app.py")
    dockerfile   = filesha256("${path.module}/Dockerfile")
    requirements = filesha256("${path.module}/requirements.txt")
  }
}

resource "docker_image" "nginx" {
  name = "nginx:1.27-alpine"
}

resource "docker_container" "app" {
  name  = "secure-web-app"
  image = docker_image.app.image_id
  networks_advanced {
    name = docker_network.app.name
  }
}

resource "docker_container" "proxy" {
  name  = "secure-web-proxy"
  image = docker_image.nginx.image_id
  networks_advanced {
    name = docker_network.app.name
  }
  ports {
    internal = 80
    external = 8080
    ip       = "127.0.0.1"
  }
  mounts {
    type      = "bind"
    source    = abspath("${path.module}/nginx.conf")
    target    = "/etc/nginx/conf.d/default.conf"
    read_only = true
  }
  depends_on = [docker_container.app]
}

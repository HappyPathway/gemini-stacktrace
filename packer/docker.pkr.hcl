packer {
  required_plugins {
    docker = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/docker"
    }
  }
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "dockerhub_password" {
  type    = string
}

variable "dockerhub_user" {
  type    = string
}


variable "docker_repo" {
  type    = string
  default = "happypathway/gemini-stacktrace"
}

source "docker" "python" {
  image  = "python:3.11-slim"
  commit = true
  changes = [
    "WORKDIR /app",
    "ENTRYPOINT [\"gemini-stacktrace\"]",
    "CMD []"
  ]
}

build {
  name = "gemini-stacktrace"
  
  sources = [
    "source.docker.python"
  ]
  
  provisioner "shell" {
    inline = [
      "apt-get update",
      "apt-get install -y --no-install-recommends git curl build-essential",
      "apt-get clean",
      "rm -rf /var/lib/apt/lists/*"
    ]
  }
  
  provisioner "file" {
    source      = "../"
    destination = "/app"
  }
  
  provisioner "shell" {
    inline = [
      "cd /app",
      "pip install --no-cache-dir -r requirements.txt",
      "pip install --no-cache-dir -e .",
      "rm -rf .git .github .devcontainer tests examples docs"
    ]
  }
  
  post-processors {
    post-processor "docker-tag" {
      repository = "${var.dockerhub_user}/gemini-stacktrace"
      tags       = [var.image_tag, "latest"]
    }
    
    post-processor "docker-tag" {
      repository = "${var.dockerhub_user}/gemini-stacktrace"
      tags       = ["${var.image_tag}-${timestamp()}"]
      only       = ["docker.python"]
    }
    
    post-processor "docker-push" {
      login          = true
      login_username = var.dockerhub_user
      login_password = var.dockerhub_password
    }
  }
}

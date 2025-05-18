# Building Docker Images with Packer

This directory contains Packer configurations for building Docker images for the Gemini Stack Trace tool.

## Prerequisites

1. Install [Packer](https://developer.hashicorp.com/packer/downloads)
2. Docker installed and configured
3. Docker Hub account (if you want to push the image)

## Building the Docker Image

To build the Docker image:

```bash
cd /path/to/gemini-stacktrace
packer init packer/docker.pkr.hcl  # Initialize Packer plugins
packer validate packer/docker.pkr.hcl  # Validate the configuration
```

### Building with default settings:

```bash
packer build packer/docker.pkr.hcl
```

This will build an image tagged as `happypathway/gemini-stacktrace:latest`.

### Specifying a version:

```bash
packer build -var "version=1.0.0" packer/docker.pkr.hcl
```

### Pushing to a different Docker repository:

```bash
packer build -var "docker_repo=yourusername/gemini-stacktrace" packer/docker.pkr.hcl
```

### Pushing to Docker Hub

To push the image to Docker Hub, make sure you're logged in:

```bash
docker login
```

Then set the environment variables for Docker Hub and run the build:

```bash
export DOCKER_USERNAME=yourusername
export DOCKER_PASSWORD=yourpassword
packer build packer/docker.pkr.hcl
```

## Using the Docker Image

Once built, you can use the image:

```bash
docker run --rm -it -v $(pwd):/workspace happypathway/gemini-stacktrace:latest --help
```

To analyze a stack trace:

```bash
docker run --rm -it \
  -v $(pwd):/workspace \
  -e GEMINI_API_KEY=your_api_key \
  happypathway/gemini-stacktrace:latest \
  /path/to/stacktrace.txt
```

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Download Terraform

- Ubuntu / Debian / AMD64

https://developer.hashicorp.com/terraform/install

- Rename to `terraform_linux_amd64.zip`

terraform_1.14.3_linux_amd64.zip

-----

-----

## Use Terraform to Build Docker Container for Debian Bookworm

Steps:

- Create `main.tf`
- Run `terraform`
- Run `docker` to start container

### Save the following as `main.tf`

```terraform
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

# Pull Debian Bookworm image
resource "docker_image" "debian_bookworm" {
  name         = "debian:bookworm"
  keep_locally = true
}

# Create a container
resource "docker_container" "bookworm" {
  name  = "debian-bookworm"
  image = docker_image.debian_bookworm.image_id

  # Keep it running (Debian exits immediately otherwise)
  command = ["sleep", "infinity"]

  # Install packages on startup (simple)
  # Add to docker_container:
  #command = ["bash", "-lc", "apt-get update && apt-get install -y curl ca-certificates && sleep infinity"]

  # Optional: set a hostname
  hostname = "bookworm"

  # Optional: environment variables
  env = [
    "DEBIAN_FRONTEND=noninteractive"
  ]

  # Optional: port mapping example (uncomment if you run a service)
  # ports {
  #   internal = 8080
  #   external = 8080
  # }

  # Optional: mount a host directory into the container
  # volumes {
  #   host_path      = "${path.module}/data"
  #   container_path = "/data"
  #   read_only      = false
  # }
}

output "container_name" {
  value = docker_container.bookworm.name
}

output "container_id" {
  value = docker_container.bookworm.id
}
```

### Save the following as `run-terraform.sh`

```bash
#!/bin/bash
# set -x
# trap read debug

terraform init
terraform apply
```

### Save the following as `run-docker.sh`

```bash
#!/bin/bash
# set -x
# trap read debug

# run script as root

docker exec -it debian-bookworm bash
```
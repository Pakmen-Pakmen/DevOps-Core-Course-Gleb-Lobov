1. Cloud Provider & Infrastructure
Cloud Provider Chosen

I selected Yandex Cloud because:

It provides a free tier suitable for this lab

No credit card required initially

Good documentation

Accessible from Russia

Instance Type & Configuration

Free-tier compatible configuration:

Platform: standard-v2

vCPU: 2 cores (20% core_fraction)

RAM: 1 GB

Boot disk: 10 GB

OS: Ubuntu 24.04 LTS

Zone: ru-central1-a

Estimated cost: $0 (free tier)

Resources Created
Infrastructure Components

VPC Network

Subnet

Security Group (Firewall rules)

Compute Instance (VM)

Public IP (NAT enabled)

Firewall Rules

SSH (22) — restricted to my IP

HTTP (80) — open

Custom port 5000 — open (for future app deployment)

2. Terraform Implementation
Project Structure
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars (gitignored)
├── .gitignore


Sensitive files ignored:

*.tfstate
*.tfstate.*
.terraform/
terraform.tfvars
*.json
*.pem
*.key

Provider Configuration

Used official Yandex provider:

terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}


Authentication via service account key (not committed to Git).

Key Decisions

Used variables for zone and instance name

Used outputs to expose public IP

Used SSH key injection via metadata

Restricted SSH access to my IP only

Terraform Workflow

terraform init


Result:

Provider downloaded

Backend initialized

terraform plan


Plan showed:

Plan: 4 to add, 0 to change, 0 to destroy.


Resources:

yandex_vpc_network

yandex_vpc_subnet

yandex_vpc_security_group

yandex_compute_instance

terraform apply


Result:

Apply complete! Resources: 4 added, 0 changed, 0 destroyed.


Output:

public_ip = "93.77.180.162"

SSH Access Proof
ssh -i ~/.ssh/id_ed25519 ubuntu@93.77.180.162


Successful login:

Welcome to Ubuntu 24.04 LTS

Terraform Destroy

Before starting Pulumi:

terraform destroy


Result:

Destroy complete! Resources: 4 destroyed.


Verified in Yandex Cloud console that no resources remained.

Challenges Encountered

Incorrect SSH key format

Metadata misconfiguration

Understanding Terraform state file importance

3. Pulumi Implementation
Language Chosen

Python

Reason:

Full programming language

Familiar syntax

Better flexibility compared to HCL

Project Structure
pulumi/
├── __main__.py
├── requirements.txt
├── Pulumi.yaml
├── Pulumi.dev.yaml (gitignored)
├── venv/

Setup
pulumi new python
pulumi login file://.
pulumi stack init dev
pip install pulumi pulumi-yandex

pulumi preview
pulumi preview


Output:

+ 4 resources to create

pulumi up
pulumi up


Result:

Resources:
    + 4 created


Output:

external_ip: "84.xxx.xxx.xxx"

SSH Access Proof
ssh -i ~/.ssh/id_ed25519 ubuntu@84.xxx.xxx.xxx


Successful login confirmed.

Differences from Terraform

Terraform:

resource "yandex_compute_instance" "vm" { ... }


Pulumi:

instance = yandex.ComputeInstance("vm", ...)


Terraform is declarative.
Pulumi is imperative.

Pulumi allows:

Loops

Functions

Conditional logic

Native language tooling

Challenges Encountered

PATH issue with Pulumi in VS Code

Organization configuration error

Understanding stack management

4. Terraform vs Pulumi Comparison
Ease of Learning

Terraform was easier initially because HCL is simpler and documentation is very extensive. Pulumi required understanding stacks and Python SDK.

Winner: Terraform (for beginners)

Code Readability

Terraform is more readable for simple infrastructure.

Pulumi becomes more readable when logic grows complex.

Winner: Terraform (for simple projects)

Debugging

Pulumi was easier to debug because Python errors are clearer than Terraform error messages.

Winner: Pulumi

Documentation

Terraform has larger ecosystem and more examples.

Winner: Terraform

Use Cases

I would use:

Terraform:

Standard infrastructure provisioning

Team environments

Enterprise environments

Pulumi:

Complex infrastructure logic

When strong programming features are required

When integrating infrastructure with application logic

5. Lab 5 Preparation & Cleanup
VM for Lab 5

I am keeping:

Pulumi-created VM

Reason:

Already tested

Clean setup

Ready for Ansible provisioning

Cleanup Status

Terraform infrastructure: Destroyed

Pulumi infrastructure: Active

VM is currently running and accessible via SSH.
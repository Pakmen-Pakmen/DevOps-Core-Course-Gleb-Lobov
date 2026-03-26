In this lab I enhanced the Ansible infrastructure automation created in previous labs.  
The main goal was to introduce more advanced automation patterns used in real DevOps environments.

Technologies used:

- Ansible 2.16
- Docker
- Docker Compose
- GitHub Actions
- Jinja2 Templates
- Ansible Vault

Main improvements implemented in this lab:

- Refactoring roles using **blocks**
- Selective execution using **tags**
- Migration from `docker run` to **Docker Compose**
- **Role dependencies**
- Safe **wipe logic**
- Full **CI/CD automation using GitHub Actions**

Task 1: Blocks & Tags

Blocks usage

Blocks were implemented to group logically related tasks and simplify configuration.

Example from `roles/common/tasks/main.yml`:

```yaml
- name: Install base packages
  block:

    - name: Update apt cache
      apt:
        update_cache: yes

    - name: Install packages
      apt:
        name:
          - git
          - curl
          - python3-pip
        state: present

  rescue:

    - name: Fix apt cache
      command: apt-get update --fix-missing

  always:

    - name: Log completion
      file:
        path: /tmp/common_role_done
        state: touch

  become: true
  tags:
    - packages

This block ensures that package installation is grouped, errors are handled, and completion is logged.

Tags Strategy

Tags allow selective playbook execution.

Tags used in the project:

Tag	Purpose
packages	package installation
users	user management
docker_install	docker installation
docker_config	docker configuration
app_deploy	application deployment
compose	docker compose tasks
web_app_wipe	application cleanup

Example usage:

Run only docker tasks:

ansible-playbook provision.yml --tags docker

Run only package installation:

ansible-playbook provision.yml --tags packages

List available tags:

ansible-playbook provision.yml --list-tags
Research Answers
What happens if rescue block also fails?

If both the main block and the rescue block fail, Ansible stops execution and marks the task as failed.

Can you have nested blocks?

Yes. Blocks can be nested inside other blocks to create more complex error-handling logic.

How do tags inherit to tasks within blocks?

Tags defined on a block are automatically inherited by all tasks inside that block.

Task 2: Docker Compose Migration

Previously the application was deployed using docker run.

In this lab the deployment was migrated to Docker Compose for better maintainability.

Advantages of Docker Compose:

Declarative configuration

Multi-container support

Environment variable management

Easier updates

Reproducible deployments

Docker Compose Template

File:

roles/web_app/templates/docker-compose.yml.j2

Example template:

version: '3.8'

services:
  {{ app_name }}:
    image: {{ docker_image }}:{{ docker_tag }}
    container_name: {{ app_name }}
    ports:
      - "{{ app_port }}:{{ app_internal_port }}"
    restart: unless-stopped

Variables used:

Variable	Purpose
app_name	container name
docker_image	docker image
docker_tag	image version
app_port	host port
app_internal_port	container port
Role Dependencies

File:

roles/web_app/meta/main.yml
dependencies:
  - role: docker

This ensures that Docker is installed automatically before deploying the application.

Deployment Tasks

Application deployment uses Docker Compose.

Example:

- name: Deploy application
  block:

    - name: Create application directory
      file:
        path: "/opt/{{ app_name }}"
        state: directory

    - name: Copy docker-compose file
      template:
        src: docker-compose.yml.j2
        dest: "/opt/{{ app_name }}/docker-compose.yml"

    - name: Start application
      command: docker compose up -d
      args:
        chdir: "/opt/{{ app_name }}"

  tags:
    - app_deploy
    - compose
Idempotency Verification

Playbook executed twice:

First run:

changed=3

Second run:

changed=0

This confirms the deployment is idempotent.

Task 3: Wipe Logic

Wipe logic allows safe removal of deployed applications.

The wipe is protected by two safety mechanisms:

Variable: web_app_wipe

Tag: web_app_wipe

Default value:

web_app_wipe: false
Wipe Implementation

File:

roles/web_app/tasks/wipe.yml

Example:

- name: Remove container
  community.docker.docker_container:
    name: "{{ app_name }}"
    state: absent
  ignore_errors: true

- name: Remove application directory
  file:
    path: "/opt/{{ app_name }}"
    state: absent
Wipe Scenarios
Scenario 1 – Normal deployment
ansible-playbook deploy.yml

Result: deployment runs normally.

Scenario 2 – Wipe only
ansible-playbook deploy.yml -e "web_app_wipe=true" --tags web_app_wipe

Result: application removed.

Scenario 3 – Clean reinstall
ansible-playbook deploy.yml -e "web_app_wipe=true"

Process:

Old application removed

Fresh deployment executed

Scenario 4 – Safety test
ansible-playbook deploy.yml --tags web_app_wipe

Result: wipe skipped because variable is false.

Research Answers
Why use both variable and tag?

This creates double protection against accidental deletion of the application.

Difference between never tag and this approach?

The never tag completely disables tasks unless explicitly invoked, while variable + tag allows more flexible control.

Why must wipe logic come before deployment?

This allows clean reinstall scenarios where the old application is removed before deploying the new one.

Task 4: CI/CD with GitHub Actions

A CI/CD pipeline was created to automate deployment.

Workflow file:

.github/workflows/ansible-deploy.yml

Pipeline steps:

Checkout repository

Install Python

Install Ansible

Run ansible-lint

Execute Ansible playbook

Verify deployment using curl

Example Workflow
name: Ansible Deployment

on:
  push:
    branches: [ main ]
    paths:
      - 'ansible/**'

jobs:

  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: pip install ansible ansible-lint

      - name: Run ansible-lint
        run: ansible-lint ansible/

  deploy:

    needs: lint
    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v4

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa

      - name: Deploy
        run: |
          cd ansible
          echo "${{ secrets.ANSIBLE_VAULT_PASSWORD }}" > /tmp/vault
          ansible-playbook deploy.yml --vault-password-file /tmp/vault
GitHub Secrets Used
Secret	Purpose
ANSIBLE_VAULT_PASSWORD	decrypt vault secrets
SSH_PRIVATE_KEY	SSH access to VM
VM_HOST	target server
VM_USER	SSH username
Deployment Verification

After deployment the workflow verifies the application:

curl http://VM_IP:8000

If the request fails the workflow stops with an error.

Task 5: Documentation

This document (LAB06.md) provides a full explanation of the implementation including:

architecture decisions

configuration details

test scenarios

research answers

All Ansible files were also documented with comments.

Challenges & Solutions
Docker compose module issues

Initially the docker_compose module produced errors due to missing dependencies.

Solution:

Installed docker-compose-plugin

Switched to running docker compose command directly.

Docker connection error

Error:

Not supported URL scheme http+docker

Solution:

Removed conflicting docker python package.

SSH key issues in CI

GitHub runner required proper SSH configuration.

Solution:

Configured SSH key using GitHub Secrets and added known_hosts.

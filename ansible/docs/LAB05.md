# DevOps Lab 05 – Automated Docker Deployment with Ansible

## Objective

The goal of this lab is to automate:

- Server provisioning
- Docker installation
- Application deployment from DockerHub
- Secure credential management using Ansible Vault
- Firewall configuration
- Idempotent infrastructure setup

---

## Architecture

Control Node (WSL Ubuntu)
        ↓
Ansible
        ↓
Remote VM (Docker Host)
        ↓
Docker Container (Python Application)

---

## Project Structure


devops-lab05/
├── LAB05.md
├── ansible/
│ ├── inventory.ini
│ ├── site.yml
│ ├── provision.yml
│ ├── deploy.yml
│ ├── group_vars/
│ │ ├── all.yml
│ │ └── vault.yml (encrypted, not committed)
│ └── roles/
│ ├── common/
│ │ └── tasks/main.yml
│ └── app_deploy/
│ └── tasks/main.yml


---

## Roles

### common

Responsible for base server configuration:

- Update apt cache
- Install docker.io
- Install python3-pip
- Install ufw
- Install Docker SDK for Python
- Enable and start Docker service
- Open ports 22 (SSH) and 5000 (application)
- Enable firewall

### app_deploy

Responsible for application deployment:

- Docker login
- Pull image from DockerHub
- Run container with restart policy `always`

---

## Ansible Vault

Sensitive data is stored in:


ansible/group_vars/vault.yml


Encrypted using:


ansible-vault create group_vars/vault.yml


Playbook execution:


ansible-playbook site.yml --ask-vault-pass


---

## Deployment

Full provisioning and deployment:


ansible-playbook site.yml --ask-vault-pass


Provision only:


ansible-playbook provision.yml


Deploy only:


ansible-playbook deploy.yml --ask-vault-pass


---

## Idempotency

Re-running the playbook:


ansible-playbook site.yml --ask-vault-pass


Produces:


changed=0


This confirms idempotent configuration.

---

## Application Access

The application is available at:


http://<VM_IP>:5000


---

## Cleanup

Remove container:


docker rm -f python_app


Remove Docker:


sudo apt remove docker.io -y


After cleanup, infrastructure can be redeployed using Ansible.

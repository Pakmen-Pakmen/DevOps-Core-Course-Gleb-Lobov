terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  service_account_key_file = var.service_account_key_file
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
  zone      = var.zone
}

resource "yandex_vpc_network" "network" {
  name = "devops-network"
}

resource "yandex_vpc_subnet" "subnet" {
  name           = "devops-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.network.id
  v4_cidr_blocks = ["10.5.0.0/24"]
}

resource "yandex_compute_instance" "vm" {
  name        = "devops-vm"
  platform_id = "standard-v1"

  resources {
    cores  = 2
    memory = 2
  }

  boot_disk {
    initialize_params {
      image_id = "fd80qm01ah03dkqb14lc"
      size     = 30
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet.id
    nat       = true
  }

  metadata = {
    ssh-keys = "ubuntu:${file("C:/Users/79524/.ssh/id_ed25519.pub")}"
  }
}

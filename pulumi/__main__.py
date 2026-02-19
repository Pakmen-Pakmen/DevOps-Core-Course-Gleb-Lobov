import pulumi
import pulumi_yandex as yandex
import os

network = yandex.VpcNetwork("devops-network")

subnet = yandex.VpcSubnet(
    "devops-subnet",
    zone="ru-central1-a",
    network_id=network.id,
    v4_cidr_blocks=["10.6.0.0/24"],
)

with open(os.path.expanduser("C:/Users/79524/.ssh/id_ed25519.pub")) as f:
    ssh_key = f.read().strip()
    print(ssh_key)

instance = yandex.ComputeInstance(
    "devops-vm",
    platform_id="standard-v1",
    resources=yandex.ComputeInstanceResourcesArgs(
        cores=2,
        memory=2,
    ),
    boot_disk=yandex.ComputeInstanceBootDiskArgs(
        initialize_params=yandex.ComputeInstanceBootDiskInitializeParamsArgs(
            image_id="fd80qm01ah03dkqb14lc",
            size=30,
        )
    ),
    network_interfaces=[
        yandex.ComputeInstanceNetworkInterfaceArgs(
            subnet_id=subnet.id,
            nat=True,
        )
    ],
    metadata={
        "ssh-keys": f"ubuntu:{ssh_key}"
    }
)

pulumi.export("external_ip", instance.network_interfaces[0].nat_ip_address)

from math import ceil


def required_regional_vcpu_quota(vm_count: int, batch_size: int = 4) -> int:
    """
    Compute the regional vCPU quota requirements given the number of VMs to be scanned.

    Args:
        vm_count: Number of VMs to be scanned
        batch_size: Number of VMs to be scanned in each batch
    """
    vcpu_per_vm = 2 / batch_size
    return ceil(vm_count * vcpu_per_vm)


def required_regional_public_ip_quota(vm_count: int, use_nat_gateway: bool, batch_size: int = 4) -> int:
    """
    Compute the regional public IP quota requirements given the number of VMs to be scanned.

    Args:
        vm_count: Number of VMs to be scanned
        use_nat_gateway: Whether to use NAT Gateway
        batch_size: Number of VMs to be scanned in each batch
    """
    if use_nat_gateway:
        return 1
    return ceil(vm_count / batch_size)

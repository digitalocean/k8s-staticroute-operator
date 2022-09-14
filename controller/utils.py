import ipaddress


# checks for both standard IP address, and CIDR notation
def valid_ip_address(address):
    try:
        ip_object = ipaddress.ip_network(address)
    except ValueError:
        return False

    return True

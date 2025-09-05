import uuid

def get_mac_address() -> str:
    """Obtém o MAC address do dispositivo atual."""
    mac = uuid.getnode()
    return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

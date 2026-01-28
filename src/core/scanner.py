import subprocess
import plistlib
import sys
from typing import List, Dict, Any, Union

def get_usb_registry() -> Union[Dict[str, Any], List[Any]]:
    """
    Retrieves the full USB plane from the macOS I/O Registry as a parsed dictionary.

    Returns:
        A dictionary (or list of dictionaries) representing the root of the IOUSB plane.

    Raises:
        subprocess.CalledProcessError: If the ioreg command fails.
        plistlib.InvalidFileException: If the output cannot be parsed as XML.
    """
    # -a: Archive (XML output)
    # -p IOUSB: Restrict to USB plane
    # -l: Load all properties (includes IDs)
    cmd = ["ioreg", "-p", "IOUSB", "-a", "-l"]

    output = subprocess.check_output(cmd)
    return plistlib.loads(output)

def _extract_device_data(node: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts relevant metadata from a raw IORegistry node.

    Args:
        node: A dictionary representing a single IORegistry entry.

    Returns:
        A dictionary containing standardized device info (name, vid, pid).
    """
    # IORegistry keys can vary; check common variants
    name = node.get("USB Product Name", node.get("kUSBProductString", "Unknown Device"))
    vendor_id = node.get("idVendor", 0)
    product_id = node.get("idProduct", 0)
    location_id = node.get("locationID", 0)

    return {
        "name": name,
        "vendor_id": vendor_id,
        "product_id": product_id,
        "location_id": location_id
    }

def traverse_registry(node: Dict[str, Any], device_list: List[Dict[str, Any]]) -> None:
    """
    Recursively traverses the IORegistry tree to identify valid USB devices.

    Populates device_list with devices that possess valid Vendor and Product IDs.

    Args:
        node: Current node in the registry tree.
        device_list: Accumulator list for found devices.
    """
    # Filter for nodes that act as devices (must have VID/PID)
    if "idVendor" in node and "idProduct" in node:
        device_data = _extract_device_data(node)
        device_list.append(device_data)

    # Recurse into children (Hubs/Docks)
    # Key 'IORegistryEntryChildren' contains the list of child nodes
    children = node.get("IORegistryEntryChildren", [])
    for child in children:
        traverse_registry(child, device_list)

def scan_devices() -> List[Dict[str, Any]]:
    """
    Main entry point for USB discovery.

    Orchestrates the retrieval and traversal of the registry.

    Returns:
        A list of dictionaries, each representing a connected USB device.
    """
    try:
        registry_root = get_usb_registry()
    except Exception as e:
        print(f"Error querying system registry: {e}", file=sys.stderr)
        return []

    found_devices = []

    # The registry root can be a single dict or a list of controllers
    if isinstance(registry_root, list):
        for root in registry_root:
            traverse_registry(root, found_devices)
    elif isinstance(registry_root, dict):
        traverse_registry(registry_root, found_devices)

    return found_devices

def print_report(devices: List[Dict[str, Any]]) -> None:
    """
    Formats and prints the device list to stdout in a tabular format.
    """
    print(f"\n{'VENDOR ID':<12} | {'PRODUCT ID':<12} | {'DEVICE NAME'}")
    print("-" * 65)

    for dev in devices:
        v_dec, p_dec = dev['vendor_id'], dev['product_id']
        v_hex, p_hex = f"0x{v_dec:04x}", f"0x{p_dec:04x}"

        print(f"{v_hex} ({v_dec:<4}) | {p_hex} ({p_dec:<4}) | {dev['name']}")

if __name__ == "__main__":
    devices = scan_devices()
    print_report(devices)

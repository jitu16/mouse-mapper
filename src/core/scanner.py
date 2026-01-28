# This is a test to check if the program can scan hardware correctly!

import subprocess
import json
import re

def get_usb_chain():
    """
    Calls the native macOS system_profiler to get the raw USB tree.
    Returns: List of USB controllers/hubs.
    """
    cmd = ["system_profiler", "SPUSBDataType", "-json"]

    try:
        output = subprocess.check_output(cmd)
        data = json.loads(output)
        return data.get("SPUSBDataType", [])
    except subprocess.CalledProcessError as e:
        print(f"Error calling system_profiler: {e}")
        return []
    except json.JSONDecodeError:
        print("Error: Could not parse system_profiler output.")
        return []

def extract_device_info(node, device_list):
    """
    Recursively traverses the USB tree to flatten it into a list of devices.
    """
    # 1. Capture the current device if it has valid IDs
    if "vendor_id" in node and "product_id" in node:
        name = node.get("_name", "Unknown Device")
        # IDs often come as "0x1234 (Company)", so we clean them
        v_id_raw = node.get("vendor_id", "0x0000")
        p_id_raw = node.get("product_id", "0x0000")

        # Helper to strip text and keep just the hex/int
        v_id = re.search(r'0x[0-9a-fA-F]+', v_id_raw)
        p_id = re.search(r'0x[0-9a-fA-F]+', p_id_raw)

        if v_id and p_id:
            device_list.append({
                "name": name,
                "vendor_id": int(v_id.group(0), 16),
                "product_id": int(p_id.group(0), 16),
                "manufacturer": node.get("manufacturer", "Unknown")
            })

    # 2. Recursively dive into children (hubs usually have an inner list)
    # The key is often "_items" or sometimes just nested dicts
    if "_items" in node:
        for child in node["_items"]:
            extract_device_info(child, device_list)

def scan():
    """
    Main entry point: Scans and prints all connected devices.
    """
    print("🔍 Scanning for USB devices via system_profiler...")
    raw_data = get_usb_chain()
    devices = []

    for controller in raw_data:
        # Start recursion from the root controllers
        if "_items" in controller:
            for item in controller["_items"]:
                extract_device_info(item, devices)
        else:
            extract_device_info(controller, devices)

    print(f"✅ Found {len(devices)} devices.\n")

    # Print in a format easy to copy-paste into config.json
    print(f"{'DEVICE NAME':<40} | {'VENDOR':<10} | {'PRODUCT':<10}")
    print("-" * 66)
    for dev in devices:
        print(f"{dev['name']:<40} | {hex(dev['vendor_id']):<10} | {hex(dev['product_id']):<10}")

    return devices

if __name__ == "__main__":
    scan()

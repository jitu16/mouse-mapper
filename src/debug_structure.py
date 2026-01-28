import subprocess
import json
import sys

def get_raw_usb_data():
    """Calls system_profiler and returns the raw JSON list."""
    cmd = ["system_profiler", "SPUSBDataType", "-json"]
    try:
        output = subprocess.check_output(cmd)
        data = json.loads(output)
        return data.get("SPUSBDataType", [])
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

def print_node(node, depth=0):
    """
    Recursively prints a node and its children with indentation.
    This mimics the 'tree' command for your USB ports.
    """
    indent = "    " * depth
    name = node.get("_name", "Unknown Device")

    # Extract IDs raw (so we see exactly what Python sees)
    vid = node.get("vendor_id", "N/A")
    pid = node.get("product_id", "N/A")

    # Print the current node
    print(f"{indent}├── 📦 {name}")
    if vid != "N/A":
        print(f"{indent}│    └── IDs: {vid} / {pid}")

    # CRITICAL: Check for children (hubs usually have '_items')
    # Some devices might use 'items' or other keys, let's check keys.
    if "_items" in node:
        for child in node["_items"]:
            print_node(child, depth + 1)

    # DEBUG: Check if there are other list-type keys we missed?
    # This helps us catch if macOS uses a different key for this specific dock.
    elif "items" in node:
        print(f"{indent}│    ⚠️ FOUND 'items' key instead of '_items'!")
        for child in node["items"]:
            print_node(child, depth + 1)

if __name__ == "__main__":
    print("🔍 VISUALIZING USB HIERARCHY\n")
    roots = get_raw_usb_data()

    for root in roots:
        print_node(root)
        print("\n" + "="*40 + "\n")

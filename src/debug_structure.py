import subprocess
import re

def scan_ioreg():
    """
    Uses the raw 'ioreg' command to find USB devices.
    This bypasses the simplified system_profiler view.
    """
    print("🔍 Deep Scanning via I/O Kit Registry...")

    # -p IOUSB runs a scan strictly on the USB plane
    # -l shows all properties (where IDs live)
    # -w0 prevents line truncation
    cmd = ["ioreg", "-p", "IOUSB", "-l", "-w0"]

    try:
        output = subprocess.check_output(cmd).decode("utf-8")
    except Exception as e:
        print(f"❌ Error running ioreg: {e}")
        return

    # We are looking for the block that contains your known Product ID (14373)
    # The output format is messy, so we split by device blocks
    devices = output.split("+-o")

    for dev in devices:
        # Check if our target Product ID is in this block
        # ioreg usually lists it as "idProduct" = 14373
        if "14373" in dev:
            print("\n✅ TARGET FOUND IN REGISTRY!")

            # Extract Name
            name_match = re.search(r'"USB Product Name" = "([^"]+)"', dev)
            name = name_match.group(1) if name_match else "Unknown Name"

            # Extract Vendor ID
            # Look for "idVendor" = 1234
            vendor_match = re.search(r'"idVendor" = (\d+)', dev)
            if vendor_match:
                vid = int(vendor_match.group(1))
                print(f"   Name:      {name}")
                print(f"   Vendor ID: {vid} (0x{vid:04x})")
                print(f"   Product ID: 14373 (0x3825)")
                print("-" * 40)
                print("👉 This is the OFFICIAL hardware ID.")
                return vid
            else:
                print("⚠️ Found the device, but Vendor ID is missing in IORegistry.")

    print("\n❌ Device 14373 not found in IOUSB plane.")

if __name__ == "__main__":
    vid = scan_ioreg()
    if vid:
        print(f"\nFinal Config Value -> vendor_id: {vid}")

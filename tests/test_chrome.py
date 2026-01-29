import sys
import os
import json

# Add the parent directory to sys.path so we can import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import ButtonConfig, ButtonBehavior, Action, compile_rule, _add_app_condition

def test_chrome_binding():
    print("🧪 TEST: Generating Chrome-Specific Rule for '1' -> 'Cmd+W'")

    # 1. Define the Action (Close Tab)
    # Note: The side buttons on Naga usually send "1", "2", etc.
    # We are mapping Physical Key "1" to "Cmd + W"
    chrome_action = ButtonConfig(
        button_id="1",                 # The physical key code from the mouse
        behavior=ButtonBehavior.CLICK,
        tap_action=Action(key_code="w", modifiers=["left_command"])
    )

    # 2. Compile the Base Rule (Device Restricted)
    # We use a dummy Vendor ID (0x1532) for the test
    rule = compile_rule(chrome_action, vendor_id=0x68e, product_id=0xb5)

    # 3. Apply the App Restriction (The Magic Step)
    # This Bundle ID regex matches Google Chrome
    _add_app_condition(rule, app_id="^com\\.google\\.Chrome$")

    # 4. Output the Result
    print("\n📜 GENERATED JSON:")
    print(json.dumps(rule, indent=2))

    # 5. Validation Logic
    conditions = rule.get("conditions", [])
    has_app_check = any(c['type'] == 'frontmost_application_if' for c in conditions)
    has_device_check = any(c['type'] == 'device_if' for c in conditions)

    if has_app_check and has_device_check:
        print("\n✅ SUCCESS: Rule contains both DEVICE and APP conditions.")
    else:
        print("\n❌ FAILURE: Missing conditions.")

if __name__ == "__main__":
    test_chrome_binding()

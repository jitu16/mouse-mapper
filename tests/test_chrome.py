import sys
import os
import json

# Ensure we can import the src module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import compile_rule, add_app_restriction, ButtonConfig, ButtonBehavior, Action

# --- HARDWARE CONSTANTS ---
# Verbatim/Naga Device IDs
TARGET_VENDOR_ID = 0x68e
TARGET_PRODUCT_ID = 0xb5

# --- APP CONSTANTS ---
CHROME_BUNDLE_ID = "^com\\.google\\.Chrome$"

def create_scroll_manipulator(layer_var: str, direction: str, action_key: str, modifiers: list) -> dict:
    """
    Constructs a manipulator that triggers an action when scrolling while a layer is active.

    Args:
        layer_var: The name of the variable that must be 1 to enable this scroll.
        direction: 'up' or 'down'.
        action_key: The key code to output.
        modifiers: List of modifier keys to include.

    Returns:
        A dictionary representing the Karabiner manipulator.
    """
    # Vertical wheel: -1 is typically UP, 1 is typically DOWN on macOS natural scrolling
    wheel_value = -1 if direction == "up" else 1

    return {
        "type": "basic",
        "from": {
            "mouse_key": {"vertical_wheel": wheel_value},
            "modifiers": {"optional": ["any"]}
        },
        "to": [
            {
                "key_code": action_key,
                "modifiers": modifiers
            }
        ],
        "conditions": [
            {
                "type": "device_if",
                "identifiers": [
                    {
                        "vendor_id": TARGET_VENDOR_ID,
                        "product_id": TARGET_PRODUCT_ID
                    }
                ]
            },
            {
                "type": "variable_if",
                "name": layer_var,
                "value": 1
            }
        ]
    }

def generate_feature_test():
    """
    Generates a Karabiner profile implementing:
    1. Button 1 Tap -> Mission Control
    2. Button 1 Hold + Scroll -> Switch Spaces (Ctrl+Arrows)
    3. Button 2 Tap -> Close Tab (Chrome Only)
    4. Button 2 Hold + Scroll -> History Navigation (Cmd+Arrows)
    """
    print(f"Generating test profile for Device {hex(TARGET_VENDOR_ID)}:{hex(TARGET_PRODUCT_ID)}...")

    rules = []

    # ==============================================================================
    # FEATURE SET A: BUTTON 1 (Mission Control & Spaces)
    # ==============================================================================

    # 1. Define Button 1 Logic (Tap=Mission Control, Hold=Layer Variable)
    btn1_config = ButtonConfig(
        button_id="1",
        behavior=ButtonBehavior.DUAL,
        tap_action=Action(key_code="mission_control"),
        layer_variable="layer_mission_mode",
        threshold_ms=200
    )
    rules.append(compile_rule(btn1_config, TARGET_VENDOR_ID, TARGET_PRODUCT_ID))

    # 2. Define Scroll Actions for Layer 1
    # Scroll Up -> Move Left a Space (Ctrl + Left Arrow)
    rules.append(create_scroll_manipulator(
        layer_var="layer_mission_mode",
        direction="up",
        action_key="left_arrow",
        modifiers=["left_control"]
    ))

    # Scroll Down -> Move Right a Space (Ctrl + Right Arrow)
    rules.append(create_scroll_manipulator(
        layer_var="layer_mission_mode",
        direction="down",
        action_key="right_arrow",
        modifiers=["left_control"]
    ))

    # ==============================================================================
    # FEATURE SET B: BUTTON 2 (Chrome Tab & History)
    # ==============================================================================

    # 1. Define Button 2 Logic (Tap=Close Tab, Hold=Layer Variable)
    # Note: We configure the 'tap_action' here. App restriction is applied after.
    btn2_config = ButtonConfig(
        button_id="2",
        behavior=ButtonBehavior.DUAL,
        tap_action=Action(key_code="w", modifiers=["left_command"]),
        layer_variable="layer_chrome_mode",
        threshold_ms=200
    )

    # Compile the rule
    btn2_rule = compile_rule(btn2_config, TARGET_VENDOR_ID, TARGET_PRODUCT_ID)

    # Apply Chrome Restriction to the entire button behavior to prevent
    # accidental triggering in other apps.
    add_app_restriction(btn2_rule, CHROME_BUNDLE_ID)
    rules.append(btn2_rule)

    # 2. Define Scroll Actions for Layer 2 (History)
    # Scroll Up -> Back (Cmd + Left Arrow)
    scroll_back = create_scroll_manipulator(
        layer_var="layer_chrome_mode",
        direction="up",
        action_key="left_arrow",
        modifiers=["left_command"]
    )
    add_app_restriction(scroll_back, CHROME_BUNDLE_ID)
    rules.append(scroll_back)

    # Scroll Down -> Forward (Cmd + Right Arrow)
    scroll_fwd = create_scroll_manipulator(
        layer_var="layer_chrome_mode",
        direction="down",
        action_key="right_arrow",
        modifiers=["left_command"]
    )
    add_app_restriction(scroll_fwd, CHROME_BUNDLE_ID)
    rules.append(scroll_fwd)

    # ==============================================================================
    # OUTPUT
    # ==============================================================================

    profile = {
        "title": "MouseMapper: Complex Gesture Test",
        "rules": [
            {
                "description": "Generated by MouseMapper Test Script",
                "manipulators": rules
            }
        ]
    }

    print(json.dumps(profile, indent=2))

if __name__ == "__main__":
    generate_feature_test()

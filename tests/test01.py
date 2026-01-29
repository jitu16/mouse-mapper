import sys
import os
import json

# Add parent directory to path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import (
    compile_rule,
    compile_scroll_rule,
    add_app_restriction,
    ButtonConfig,
    ButtonBehavior,
    Action
)

# --- CONSTANTS ---
VID = 0x68e
PID = 0xb5
CHROME_ID = "^com\\.google\\.Chrome$"

def generate_full_test():
    print(f"Building Full Profile for Verbatim (0x68e/0xb5)...")

    rules = []

    # ==============================================================================
    # 1. BUTTON 1: Mission Control + Desktop Swipe
    # ==============================================================================

    # Rule A: The Button Logic
    # FIXED: Tap Action is now 'mission_control', not '1'
    btn1 = ButtonConfig(
        button_id="1",
        behavior=ButtonBehavior.DUAL,
        tap_action=Action(key_code="mission_control"),
        layer_variable="mode_desktop",
        threshold_ms=200
    )
    rules.append(compile_rule(btn1, VID, PID))

    # Rule B: Scroll Up -> Move Space Left (Ctrl + Left Arrow)
    rules.append(compile_scroll_rule(
        vendor_id=VID, product_id=PID,
        layer_name="mode_desktop",
        scroll_direction="up",
        target_action=Action(key_code="left_arrow", modifiers=["left_control"])
    ))

    # Rule C: Scroll Down -> Move Space Right (Ctrl + Right Arrow)
    rules.append(compile_scroll_rule(
        vendor_id=VID, product_id=PID,
        layer_name="mode_desktop",
        scroll_direction="down",
        target_action=Action(key_code="right_arrow", modifiers=["left_control"])
    ))

    # ==============================================================================
    # 2. BUTTON 2: Chrome Close Tab + History Nav
    # ==============================================================================

    # Rule D: The Button Logic (Chrome Only)
    # Tap -> Cmd+W (Close Tab)
    btn2 = ButtonConfig(
        button_id="2",
        behavior=ButtonBehavior.DUAL,
        tap_action=Action(key_code="w", modifiers=["left_command"]),
        layer_variable="mode_chrome",
        threshold_ms=200
    )

    # Compile AND Apply App Restriction
    rule_btn2 = compile_rule(btn2, VID, PID)
    add_app_restriction(rule_btn2, CHROME_ID)
    rules.append(rule_btn2)

    # Rule E: Scroll Up -> History Back (Cmd + Left Arrow)
    scroll_back = compile_scroll_rule(
        vendor_id=VID, product_id=PID,
        layer_name="mode_chrome",
        scroll_direction="up",
        target_action=Action(key_code="left_arrow", modifiers=["left_command"])
    )
    add_app_restriction(scroll_back, CHROME_ID)
    rules.append(scroll_back)

    # Rule F: Scroll Down -> History Forward (Cmd + Right Arrow)
    scroll_fwd = compile_scroll_rule(
        vendor_id=VID, product_id=PID,
        layer_name="mode_chrome",
        scroll_direction="down",
        target_action=Action(key_code="right_arrow", modifiers=["left_command"])
    )
    add_app_restriction(scroll_fwd, CHROME_ID)
    rules.append(scroll_fwd)

    # ==============================================================================
    # OUTPUT
    # ==============================================================================
    print(json.dumps({"title": "MouseMapper Full Test", "rules": [{"description": "Full Feature Set", "manipulators": rules}]}, indent=2))

if __name__ == "__main__":
    generate_full_test()

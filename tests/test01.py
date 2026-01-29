import sys
import os
import json

# Add parent directory to path to import src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import (
    compile_rule,
    add_app_restriction,
    add_layer_condition,
    ButtonConfig,
    ButtonBehavior,
    Action
)

# --- CONFIGURATION ---
VID = 1678  # 0x68e
PID = 181   # 0xb5
LAYER_NAME = "naga_nav_mode"

def generate_master_json():
    print(f"🔨 Recreating 'Naga Master' Profile for Device {VID}/{PID}...")

    rules = []

    # ==========================================================================
    # 1. THE MODIFIER: Scroll Wheel Click (Button 3)
    # ==========================================================================
    # Behavior: Hold to enable 'naga_nav_mode'. Tap to Middle Click (preserved).
    mod_btn = ButtonConfig(
        button_id="button3",
        behavior=ButtonBehavior.MODIFIER,
        layer_variable=LAYER_NAME,
        threshold_ms=200
    )
    rules.append(compile_rule(mod_btn, VID, PID))

    # ==========================================================================
    # 2. LAYER ACTIONS: What happens when Modifier is HELD?
    # ==========================================================================

    # Action A: Hold Modifier + Press '1' -> Left Arrow (Move Space Left)
    layer_action_1 = ButtonConfig(
        button_id="1",
        behavior=ButtonBehavior.CLICK,
        tap_action=Action(key_code="left_arrow", modifiers=["left_control"])
    )
    rule_layer_1 = compile_rule(layer_action_1, VID, PID)

    # INJECT the Layer Condition (Must hold button3)
    add_layer_condition(rule_layer_1, LAYER_NAME, 1)

    # OPTIONAL: Allow other modifiers (like holding Command) while doing this
    rule_layer_1["from"]["modifiers"] = {"optional": ["any"]}

    rules.append(rule_layer_1)

    # Action B: Hold Modifier + Press '2' -> Right Arrow (Move Space Right)
    layer_action_2 = ButtonConfig(
        button_id="2",
        behavior=ButtonBehavior.CLICK,
        tap_action=Action(key_code="right_arrow", modifiers=["left_control"])
    )
    rule_layer_2 = compile_rule(layer_action_2, VID, PID)
    add_layer_condition(rule_layer_2, LAYER_NAME, 1)
    rule_layer_2["from"]["modifiers"] = {"optional": ["any"]}
    rules.append(rule_layer_2)

    # ==========================================================================
    # 3. DEFAULT ACTIONS: What happens normally?
    # ==========================================================================

    # Action C: Tap '1' -> Mission Control
    default_1 = ButtonConfig(
        button_id="1",
        behavior=ButtonBehavior.CLICK,
        tap_action=Action(key_code="mission_control")
    )
    rules.append(compile_rule(default_1, VID, PID))

    # Action D: Tap '2' -> Close Tab (Chrome Only)
    default_2 = ButtonConfig(
        button_id="2",
        behavior=ButtonBehavior.CLICK,
        tap_action=Action(key_code="w", modifiers=["left_command"])
    )
    rule_default_2 = compile_rule(default_2, VID, PID)
    add_app_restriction(rule_default_2, "^com\\.google\\.Chrome$")
    rules.append(rule_default_2)

    # ==========================================================================
    # OUTPUT
    # ==========================================================================
    final_json = {
        "title": "MouseMapper: Naga Master Profile (Generated)",
        "rules": [
            {
                "description": "Generated via src/core.py",
                "manipulators": rules
            }
        ]
    }

    print(json.dumps(final_json, indent=2))

if __name__ == "__main__":
    generate_master_json()

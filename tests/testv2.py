import sys
import os
import json

# Add parent directory to path
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
VID = 1678
PID = 181
LAYER_HYPER = "naga_hyper_mode"
APP_EMACS  = "^org\\.gnu\\.Emacs$"

manipulators = []

# 1. ANCHOR: Scroll Wheel (Button 3) -> Hyper Mode
hyper_btn = ButtonConfig(
    button_id="button3",
    behavior=ButtonBehavior.MODIFIER,
    layer_variable=LAYER_HYPER,
    threshold_ms=200
)
manipulators.append(compile_rule(hyper_btn, VID, PID))

# 2. GLOBAL: Button 1 -> Mission Control
btn1_tap = ButtonConfig(
    button_id="1",
    behavior=ButtonBehavior.CLICK,
    tap_action=Action(key_code="mission_control")
)
manipulators.append(compile_rule(btn1_tap, VID, PID))

# 3. LAYER: Hyper + Button 1/2 -> Navigation
# Hyper + 1 -> Space Left
btn1_hyper = ButtonConfig(
    button_id="1",
    behavior=ButtonBehavior.CLICK,
    tap_action=Action(key_code="left_arrow", modifiers=["left_control"])
)
rule1_hyper = compile_rule(btn1_hyper, VID, PID)
add_layer_condition(rule1_hyper, LAYER_HYPER, 1)
rule1_hyper["from"]["modifiers"] = {"optional": ["any"]}
manipulators.append(rule1_hyper)

# Hyper + 2 -> Space Right
btn2_hyper = ButtonConfig(
    button_id="2",
    behavior=ButtonBehavior.CLICK,
    tap_action=Action(key_code="right_arrow", modifiers=["left_control"])
)
rule2_hyper = compile_rule(btn2_hyper, VID, PID)
add_layer_condition(rule2_hyper, LAYER_HYPER, 1)
rule2_hyper["from"]["modifiers"] = {"optional": ["any"]}
manipulators.append(rule2_hyper)

# 4. MACRO: Tap Button 2 (Emacs) -> SPC g g
btn2_emacs = ButtonConfig(
    button_id="2",
    behavior=ButtonBehavior.CLICK,
    tap_action=Action(key_code=["spacebar", "g", "g"])
)
rule2_emacs = compile_rule(btn2_emacs, VID, PID)
add_app_restriction(rule2_emacs, APP_EMACS)
manipulators.append(rule2_emacs)

# OUTPUT: Full Container Format
profile_json = {
    "title": "MouseMapper Test Profile",
    "rules": [
        {
            "description": "MouseMapper: Simple Test (Nav + Macro)",
            "manipulators": manipulators
        }
    ]
}

print(json.dumps(profile_json, indent=2))

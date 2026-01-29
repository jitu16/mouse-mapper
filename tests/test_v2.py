import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import (
    compile_rule,
    add_app_restriction,
    add_layer_condition,
    ButtonConfig,
    ButtonBehavior,
    Action
)

VID = 1678
PID = 181
LAYER_HYPER = "naga_hyper_mode"
APP_EMACS  = "^org\\.gnu\\.Emacs$"

def generate_naga_v2_profile():
    """
    Generates the Naga V2 profile ensuring correct priority order for rule evaluation.

    Priority Hierarchy:
    1. Modifiers (Define the Layer Variable)
    2. Layer Rules (Check for Variable)
    3. App-Specific Rules (Check for App ID)
    4. Global Defaults (Fall-through)
    """
    manipulators = []

    # 1. MODIFIER DEFINITION
    hyper_btn = ButtonConfig(
        button_id="button3",
        behavior=ButtonBehavior.MODIFIER,
        layer_variable=LAYER_HYPER,
        threshold_ms=200
    )
    manipulators.append(compile_rule(hyper_btn, VID, PID))

    # 2. HYPER LAYER RULES
    btn1_hyper = ButtonConfig(
        button_id="1",
        behavior=ButtonBehavior.CLICK,
        tap_action=Action(key_code="left_arrow", modifiers=["left_control"])
    )
    rule1_hyper = compile_rule(btn1_hyper, VID, PID)
    add_layer_condition(rule1_hyper, LAYER_HYPER, 1)
    rule1_hyper["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(rule1_hyper)

    btn2_hyper = ButtonConfig(
        button_id="2",
        behavior=ButtonBehavior.CLICK,
        tap_action=Action(key_code="right_arrow", modifiers=["left_control"])
    )
    rule2_hyper = compile_rule(btn2_hyper, VID, PID)
    add_layer_condition(rule2_hyper, LAYER_HYPER, 1)
    rule2_hyper["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(rule2_hyper)

    # 3. APP SPECIFIC RULES
    btn2_emacs = ButtonConfig(
        button_id="2",
        behavior=ButtonBehavior.CLICK,
        tap_action=Action(key_code=["spacebar", "g", "g"])
    )
    rule2_emacs = compile_rule(btn2_emacs, VID, PID)
    add_app_restriction(rule2_emacs, APP_EMACS)
    manipulators.append(rule2_emacs)

    # 4. GLOBAL DEFAULT RULES
    btn1_tap = ButtonConfig(
        button_id="1",
        behavior=ButtonBehavior.CLICK,
        tap_action=Action(key_code="mission_control")
    )
    manipulators.append(compile_rule(btn1_tap, VID, PID))

    # OUTPUT: PROFILE CONTAINER FORMAT
    profile_json = {
        "title": "MouseMapper Test Profile",
        "rules": [
            {
                "description": "MouseMapper: Test V2.0 (Nav + Macro)",
                "manipulators": manipulators
            }
        ]
    }

    print(json.dumps(profile_json, indent=2))

if __name__ == "__main__":
    generate_naga_v2_profile()

import sys
import os
import json

# Adjust path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core import (
    compile_rule,
    add_app_restriction,
    add_layer_condition,
    make_seq,
    ButtonConfig,
    ButtonBehavior,
    Action,
    ActionEvent
)

# ==============================================================================
# CONFIGURATION
# ==============================================================================

VID = 1678
PID = 181

LAYER_HYPER = "naga_hyper_wheel"
LAYER_RMB   = "naga_hyper_rmb" # Button 2 (Context/App Layer)
LAYER_LMB   = "naga_hyper_lmb" # Button 1 (Media/Seek Layer)

APP_CHROME  = r"^com\.google\.Chrome$"
APP_NOTES   = r"^com\.apple\.Notes$"
APP_SUBLIME = r"^com\.sublimetext\.4$"
APP_EMACS   = r"^org\.gnu\.Emacs$"


def generate_leisure_profile():
    """
    Generates the MouseMapper V3.8 'YouTube Seek' Profile.

    Structure:
    1. Layer Triggers (Wheel, RMB=Btn2, LMB=Btn1).
    2. Layer Actions (Hyper, RMB-Context, LMB-Media).
    3. Global Actions (Tap defaults).
    """
    manipulators = []

    # ==========================================================================
    # 1. LAYER DEFINITIONS
    # ==========================================================================

    # Hyper: Scroll Wheel (Button 3)
    manipulators.append(compile_rule(
        ButtonConfig("button3", ButtonBehavior.DUAL, tap_action=Action("button3"), layer_variable=LAYER_HYPER, threshold_ms=200),
        VID, PID
    ))

    # Context Layer: Right Click (Button 2)
    r_rmb = compile_rule(
        ButtonConfig("button2", ButtonBehavior.DUAL, tap_action=Action("button2"), layer_variable=LAYER_RMB, threshold_ms=150),
        VID, PID
    )
    r_rmb["conditions"] = [{
        "type": "frontmost_application_if",
        "bundle_identifiers": [APP_CHROME, APP_NOTES, APP_SUBLIME, APP_EMACS]
    }]
    manipulators.append(r_rmb)

    # Media Layer: Left Click (Button 1) - Chrome Only
    r_lmb = compile_rule(
        ButtonConfig("button1", ButtonBehavior.DUAL, tap_action=Action("button1"), layer_variable=LAYER_LMB, threshold_ms=150),
        VID, PID
    )
    r_lmb["conditions"] = [{
        "type": "frontmost_application_if",
        "bundle_identifiers": [APP_CHROME]
    }]
    manipulators.append(r_lmb)


    # ==========================================================================
    # 2. ROW 1: NAVIGATION & FILES
    # ==========================================================================

    # --- Button 1: Left / Back ---

    r_b1_hyp = compile_rule(ButtonConfig("1", ButtonBehavior.CLICK, Action("1", ["left_option", "left_shift"])), VID, PID)
    add_layer_condition(r_b1_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b1_hyp)

    # NEW: YouTube Seek Backward (LMB + 1)
    r_b1_seek = compile_rule(ButtonConfig("1", ButtonBehavior.CLICK, Action("left_arrow")), VID, PID)
    add_layer_condition(r_b1_seek, LAYER_LMB, 1)
    add_app_restriction(r_b1_seek, APP_CHROME)
    manipulators.append(r_b1_seek)

    r_b1_emacs = compile_rule(ButtonConfig("1", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("f"), ActionEvent("r")
    ])), VID, PID)
    add_layer_condition(r_b1_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b1_emacs, APP_EMACS)
    manipulators.append(r_b1_emacs)

    r_b1_rmb = compile_rule(ButtonConfig("1", ButtonBehavior.CLICK, Action("open_bracket", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b1_rmb, LAYER_RMB, 1)
    add_app_restriction(r_b1_rmb, r"^(com\.google\.Chrome|com\.apple\.Notes|com\.sublimetext\.4)$")
    manipulators.append(r_b1_rmb)

    manipulators.append(compile_rule(ButtonConfig("1", ButtonBehavior.CLICK, Action("left_arrow", ["left_control"])), VID, PID))


    # --- Button 2: Center / Overview ---

    r_b2_hyp = compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, Action("2", ["left_option", "left_shift"])), VID, PID)
    add_layer_condition(r_b2_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b2_hyp)

    r_b2_emacs = compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("f"), ActionEvent("d")
    ])), VID, PID)
    add_layer_condition(r_b2_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b2_emacs, APP_EMACS)
    manipulators.append(r_b2_emacs)

    r_b2_chrome = compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, Action("t", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b2_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b2_chrome, APP_CHROME)
    manipulators.append(r_b2_chrome)

    r_b2_subl = compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, Action("s", ["left_command"])), VID, PID)
    add_layer_condition(r_b2_subl, LAYER_RMB, 1)
    add_app_restriction(r_b2_subl, APP_SUBLIME)
    manipulators.append(r_b2_subl)

    r_b2_notes = compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, Action("s", ["left_command", "left_option"])), VID, PID)
    add_layer_condition(r_b2_notes, LAYER_RMB, 1)
    add_app_restriction(r_b2_notes, APP_NOTES)
    manipulators.append(r_b2_notes)

    manipulators.append(compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, Action("up_arrow", ["left_control"])), VID, PID))


    # --- Button 3: Right / Forward ---

    r_b3_hyp = compile_rule(ButtonConfig("3", ButtonBehavior.CLICK, Action("return_or_enter", ["left_control", "left_option", "left_shift"])), VID, PID)
    add_layer_condition(r_b3_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b3_hyp)

    # NEW: YouTube Seek Forward (LMB + 3)
    r_b3_seek = compile_rule(ButtonConfig("3", ButtonBehavior.CLICK, Action("right_arrow")), VID, PID)
    add_layer_condition(r_b3_seek, LAYER_LMB, 1)
    add_app_restriction(r_b3_seek, APP_CHROME)
    manipulators.append(r_b3_seek)

    r_b3_emacs = compile_rule(ButtonConfig("3", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("f"), ActionEvent("f")
    ])), VID, PID)
    add_layer_condition(r_b3_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b3_emacs, APP_EMACS)
    manipulators.append(r_b3_emacs)

    r_b3_rmb = compile_rule(ButtonConfig("3", ButtonBehavior.CLICK, Action("close_bracket", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b3_rmb, LAYER_RMB, 1)
    add_app_restriction(r_b3_rmb, r"^(com\.google\.Chrome|com\.apple\.Notes|com\.sublimetext\.4)$")
    manipulators.append(r_b3_rmb)

    manipulators.append(compile_rule(ButtonConfig("3", ButtonBehavior.CLICK, Action("right_arrow", ["left_control"])), VID, PID))


    # ==========================================================================
    # 3. ROW 2: ACTION & EDITING
    # ==========================================================================

    # --- Button 4: Copy / Pull ---

    r_b4_hyp = compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, Action("x", ["left_command"])), VID, PID)
    add_layer_condition(r_b4_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b4_hyp)

    r_b4_emacs = compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, make_seq([
        ActionEvent("f", ["left_shift"]),
        ActionEvent("p")
    ])), VID, PID)
    add_layer_condition(r_b4_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b4_emacs, APP_EMACS)
    manipulators.append(r_b4_emacs)

    r_b4_chrome = compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, Action(["l", "c", "escape"], ["left_command"])), VID, PID)
    add_layer_condition(r_b4_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b4_chrome, APP_CHROME)
    manipulators.append(r_b4_chrome)

    r_b4_subl = compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, Action("d", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b4_subl, LAYER_RMB, 1)
    add_app_restriction(r_b4_subl, APP_SUBLIME)
    manipulators.append(r_b4_subl)

    r_b4_notes = compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, Action("l", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b4_notes, LAYER_RMB, 1)
    add_app_restriction(r_b4_notes, APP_NOTES)
    manipulators.append(r_b4_notes)

    manipulators.append(compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, Action("c", ["left_command"])), VID, PID))


    # --- Button 5: Undo / Cycle ---

    r_b5_hyp = compile_rule(ButtonConfig("5", ButtonBehavior.CLICK, make_seq([
        ActionEvent("left_arrow", ["left_command", "left_shift"]),
        ActionEvent("right_arrow", ["left_command", "left_shift"])
    ])), VID, PID)
    add_layer_condition(r_b5_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b5_hyp)

    r_b5_emacs = compile_rule(ButtonConfig("5", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("w"), ActionEvent("w")
    ])), VID, PID)
    add_layer_condition(r_b5_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b5_emacs, APP_EMACS)
    manipulators.append(r_b5_emacs)

    r_b5_rmb = compile_rule(ButtonConfig("5", ButtonBehavior.CLICK, Action("escape")), VID, PID)
    add_layer_condition(r_b5_rmb, LAYER_RMB, 1)
    add_app_restriction(r_b5_rmb, r"^(com\.google\.Chrome|com\.apple\.Notes|com\.sublimetext\.4)$")
    manipulators.append(r_b5_rmb)

    manipulators.append(compile_rule(ButtonConfig("5", ButtonBehavior.CLICK, Action("z", ["left_command"])), VID, PID))


    # --- Button 6: Paste / Commit ---

    r_b6_hyp = compile_rule(ButtonConfig("6", ButtonBehavior.CLICK, Action("v", ["left_option", "left_shift", "left_command"])), VID, PID)
    add_layer_condition(r_b6_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b6_hyp)

    r_b6_emacs = compile_rule(ButtonConfig("6", ButtonBehavior.CLICK, make_seq([
        ActionEvent("c"), ActionEvent("c")
    ])), VID, PID)
    add_layer_condition(r_b6_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b6_emacs, APP_EMACS)
    manipulators.append(r_b6_emacs)

    r_b6_rmb = compile_rule(ButtonConfig("6", ButtonBehavior.CLICK, Action("v", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b6_rmb, LAYER_RMB, 1)
    add_app_restriction(r_b6_rmb, r"^(com\.google\.Chrome|com\.apple\.Notes|com\.sublimetext\.4)$")
    manipulators.append(r_b6_rmb)

    manipulators.append(compile_rule(ButtonConfig("6", ButtonBehavior.CLICK, Action("v", ["left_command"])), VID, PID))


    # ==========================================================================
    # 4. ROW 3: LIFECYCLE
    # ==========================================================================

    # --- Button 7: Start / New ---

    r_b7_hyp = compile_rule(ButtonConfig("7", ButtonBehavior.CLICK, Action("n", ["left_command"])), VID, PID)
    add_layer_condition(r_b7_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b7_hyp)

    r_b7_emacs = compile_rule(ButtonConfig("7", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("q"), ActionEvent("r")
    ])), VID, PID)
    add_layer_condition(r_b7_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b7_emacs, APP_EMACS)
    manipulators.append(r_b7_emacs)

    r_b7_chrome = compile_rule(ButtonConfig("7", ButtonBehavior.CLICK, Action("n", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b7_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b7_chrome, APP_CHROME)
    manipulators.append(r_b7_chrome)

    r_b7_new = compile_rule(ButtonConfig("7", ButtonBehavior.CLICK, Action("n", ["left_command"])), VID, PID)
    add_layer_condition(r_b7_new, LAYER_RMB, 1)
    add_app_restriction(r_b7_new, r"^(com\.sublimetext\.4|com\.apple\.Notes)$")
    manipulators.append(r_b7_new)

    manipulators.append(compile_rule(ButtonConfig("7", ButtonBehavior.CLICK, Action("play_or_pause")), VID, PID))


    # --- Button 8: Enter / Status ---

    r_b8_hyp = compile_rule(ButtonConfig("8", ButtonBehavior.CLICK, Action("r", ["left_command"])), VID, PID)
    add_layer_condition(r_b8_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b8_hyp)

    r_b8_emacs = compile_rule(ButtonConfig("8", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("g"), ActionEvent("g")
    ])), VID, PID)
    add_layer_condition(r_b8_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b8_emacs, APP_EMACS)
    manipulators.append(r_b8_emacs)

    r_b8_chrome = compile_rule(ButtonConfig("8", ButtonBehavior.CLICK, Action("r", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b8_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b8_chrome, APP_CHROME)
    manipulators.append(r_b8_chrome)

    r_b8_subl = compile_rule(ButtonConfig("8", ButtonBehavior.CLICK, Action("p", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b8_subl, LAYER_RMB, 1)
    add_app_restriction(r_b8_subl, APP_SUBLIME)
    manipulators.append(r_b8_subl)

    r_b8_notes = compile_rule(ButtonConfig("8", ButtonBehavior.CLICK, Action("3", ["left_command"])), VID, PID)
    add_layer_condition(r_b8_notes, LAYER_RMB, 1)
    add_app_restriction(r_b8_notes, APP_NOTES)
    manipulators.append(r_b8_notes)

    manipulators.append(compile_rule(ButtonConfig("8", ButtonBehavior.CLICK, Action("return_or_enter")), VID, PID))


    # --- Button 9: Close / Quit ---

    r_b9_hyp = compile_rule(ButtonConfig("9", ButtonBehavior.CLICK, Action("escape", ["left_command", "left_option"])), VID, PID)
    add_layer_condition(r_b9_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b9_hyp)

    r_b9_emacs = compile_rule(ButtonConfig("9", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("q"), ActionEvent("q")
    ])), VID, PID)
    add_layer_condition(r_b9_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b9_emacs, APP_EMACS)
    manipulators.append(r_b9_emacs)

    r_b9_rmb = compile_rule(ButtonConfig("9", ButtonBehavior.CLICK, Action("w", ["left_command"])), VID, PID)
    add_layer_condition(r_b9_rmb, LAYER_RMB, 1)
    add_app_restriction(r_b9_rmb, r"^(com\.google\.Chrome|com\.apple\.Notes|com\.sublimetext\.4)$")
    manipulators.append(r_b9_rmb)

    manipulators.append(compile_rule(ButtonConfig("9", ButtonBehavior.CLICK, Action("w", ["left_command"])), VID, PID))


    # ==========================================================================
    # 5. ROW 4: TOOLS & REMOTE
    # ==========================================================================

    # --- Button 10: Find / Search ---

    r_b10_hyp = compile_rule(ButtonConfig("0", ButtonBehavior.CLICK, Action("f", ["left_command"])), VID, PID)
    add_layer_condition(r_b10_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b10_hyp)

    r_b10_emacs = compile_rule(ButtonConfig("0", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("slash")
    ])), VID, PID)
    add_layer_condition(r_b10_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b10_emacs, APP_EMACS)
    manipulators.append(r_b10_emacs)

    r_b10_chrome = compile_rule(ButtonConfig("0", ButtonBehavior.CLICK, make_seq([
        ActionEvent("c", ["left_command"]),
        ActionEvent("t", ["left_command"]),
        ActionEvent("v", ["left_command"]),
        ActionEvent("return_or_enter")
    ])), VID, PID)
    add_layer_condition(r_b10_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b10_chrome, APP_CHROME)
    manipulators.append(r_b10_chrome)

    r_b10_subl = compile_rule(ButtonConfig("0", ButtonBehavior.CLICK, Action("o", ["left_command"])), VID, PID)
    add_layer_condition(r_b10_subl, LAYER_RMB, 1)
    add_app_restriction(r_b10_subl, APP_SUBLIME)
    manipulators.append(r_b10_subl)

    r_b10_notes = compile_rule(ButtonConfig("0", ButtonBehavior.CLICK, Action("f", ["left_command", "left_option"])), VID, PID)
    add_layer_condition(r_b10_notes, LAYER_RMB, 1)
    add_app_restriction(r_b10_notes, APP_NOTES)
    manipulators.append(r_b10_notes)

    manipulators.append(compile_rule(ButtonConfig("0", ButtonBehavior.CLICK, make_seq([
        ActionEvent("c", ["left_command"]),
        ActionEvent("f", ["left_command"]),
        ActionEvent("v", ["left_command"]),
        ActionEvent("return_or_enter", hold_down_milliseconds=20)
    ])), VID, PID))


    # --- Button 11: Vol Down / Switch ---

    r_b11_hyp = compile_rule(ButtonConfig("hyphen", ButtonBehavior.CLICK, Action("display_brightness_decrement")), VID, PID)
    add_layer_condition(r_b11_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b11_hyp)

    r_b11_emacs = compile_rule(ButtonConfig("hyphen", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("b"), ActionEvent("b")
    ])), VID, PID)
    add_layer_condition(r_b11_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b11_emacs, APP_EMACS)
    manipulators.append(r_b11_emacs)

    r_b11_chrome = compile_rule(ButtonConfig("hyphen", ButtonBehavior.CLICK, Action("d", ["left_command"])), VID, PID)
    add_layer_condition(r_b11_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b11_chrome, APP_CHROME)
    manipulators.append(r_b11_chrome)

    r_b11_subl = compile_rule(ButtonConfig("hyphen", ButtonBehavior.CLICK, Action("slash", ["left_command"])), VID, PID)
    add_layer_condition(r_b11_subl, LAYER_RMB, 1)
    add_app_restriction(r_b11_subl, APP_SUBLIME)
    manipulators.append(r_b11_subl)

    r_b11_notes = compile_rule(ButtonConfig("hyphen", ButtonBehavior.CLICK, Action("k", ["left_command"])), VID, PID)
    add_layer_condition(r_b11_notes, LAYER_RMB, 1)
    add_app_restriction(r_b11_notes, APP_NOTES)
    manipulators.append(r_b11_notes)

    manipulators.append(compile_rule(ButtonConfig("hyphen", ButtonBehavior.CLICK, Action("volume_decrement")), VID, PID))


    # --- Button 12: Vol Up / Ship It ---

    r_b12_hyp = compile_rule(ButtonConfig("equal_sign", ButtonBehavior.CLICK, Action("display_brightness_increment")), VID, PID)
    add_layer_condition(r_b12_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b12_hyp)

    r_b12_chrome = compile_rule(ButtonConfig("equal_sign", ButtonBehavior.CLICK, Action("n", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b12_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b12_chrome, APP_CHROME)
    manipulators.append(r_b12_chrome)

    r_b12_emacs = compile_rule(ButtonConfig("equal_sign", ButtonBehavior.CLICK, make_seq([
        ActionEvent("p", ["left_shift"]),
        ActionEvent("p")
    ])), VID, PID)
    add_layer_condition(r_b12_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b12_emacs, APP_EMACS)
    manipulators.append(r_b12_emacs)

    r_b12_subl = compile_rule(ButtonConfig("equal_sign", ButtonBehavior.CLICK, Action("a", ["left_command"])), VID, PID)
    add_layer_condition(r_b12_subl, LAYER_RMB, 1)
    add_app_restriction(r_b12_subl, APP_SUBLIME)
    manipulators.append(r_b12_subl)

    manipulators.append(compile_rule(ButtonConfig("equal_sign", ButtonBehavior.CLICK, Action("volume_increment")), VID, PID))


    # ==========================================================================
    # OUTPUT
    # ==========================================================================
    profile_json = {
        "title": "test v3.0",
        "rules": [
            {
                "description": "MouseMapper V3.8 (YouTube Seek)",
                "manipulators": manipulators
            }
        ]
    }

    print(json.dumps(profile_json, indent=2))


if __name__ == "__main__":
    generate_leisure_profile()

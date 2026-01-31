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
LAYER_RMB   = "naga_hyper_rmb"

# App Identifiers
APP_CHROME  = r"^com\.google\.Chrome$"
APP_NOTES   = r"^com\.apple\.Notes$"
APP_SUBLIME = r"^com\.sublimetext\.4$"
APP_EMACS   = r"^org\.gnu\.Emacs$"


def generate_leisure_profile():
    """
    Generates the MouseMapper V3.2 'Emacs Expanded' Profile.
    """
    manipulators = []

    # ==========================================================================
    # 1. LAYER DEFINITIONS
    # ==========================================================================

    # Global Hyper: Scroll Wheel (Button 3)
    manipulators.append(compile_rule(
        ButtonConfig("button3", ButtonBehavior.MODIFIER, layer_variable=LAYER_HYPER, threshold_ms=200),
        VID, PID
    ))

    # App-Specific Hyper: Right Click (Button 2)
    r_rmb = compile_rule(
        ButtonConfig("button2", ButtonBehavior.DUAL, tap_action=Action("button2"), layer_variable=LAYER_RMB, threshold_ms=150),
        VID, PID
    )
    r_rmb["conditions"] = [{
        "type": "frontmost_application_if",
        "bundle_identifiers": [APP_CHROME, APP_NOTES, APP_SUBLIME, APP_EMACS]
    }]
    manipulators.append(r_rmb)


    # ==========================================================================
    # 2. ROW 1: NAVIGATION & FILES
    # ==========================================================================

    # --- Button 1: Left / Back ---
    # Tap: Space Left
    manipulators.append(compile_rule(ButtonConfig("1", ButtonBehavior.CLICK, Action("left_arrow", ["left_control"])), VID, PID))

    # RMB (Chrome/Notes/Sublime): Tab Left
    r_b1_rmb = compile_rule(ButtonConfig("1", ButtonBehavior.CLICK, Action("open_bracket", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b1_rmb, LAYER_RMB, 1)
    # Fixed: Added r prefix
    add_app_restriction(r_b1_rmb, r"^(com\.google\.Chrome|com\.apple\.Notes|com\.sublimetext\.4)$")
    manipulators.append(r_b1_rmb)

    # RMB (Emacs): Recent Files (SPC f r)
    r_b1_emacs = compile_rule(ButtonConfig("1", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("f"), ActionEvent("r")
    ])), VID, PID)
    add_layer_condition(r_b1_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b1_emacs, APP_EMACS)
    manipulators.append(r_b1_emacs)

    # Hyper: Throw Screen 1
    r_b1_hyp = compile_rule(ButtonConfig("1", ButtonBehavior.CLICK, Action("1", ["left_option", "left_shift"])), VID, PID)
    add_layer_condition(r_b1_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b1_hyp)


    # --- Button 2: Center / Overview ---
    # Tap: Mission Control
    manipulators.append(compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, Action("up_arrow", ["left_control"])), VID, PID))

    # RMB (Chrome): Reopen Closed Tab
    r_b2_rmb_chrome = compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, Action("t", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b2_rmb_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b2_rmb_chrome, APP_CHROME)
    manipulators.append(r_b2_rmb_chrome)

    # RMB (Sublime/Notes): Save
    r_b2_rmb_save = compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, Action("s", ["left_command"])), VID, PID)
    add_layer_condition(r_b2_rmb_save, LAYER_RMB, 1)
    r_b2_rmb_save["conditions"].append({"type": "frontmost_application_if", "bundle_identifiers": [APP_SUBLIME, APP_NOTES]})
    manipulators.append(r_b2_rmb_save)

    # RMB (Emacs): Dired (SPC f d)
    r_b2_emacs = compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("f"), ActionEvent("d")
    ])), VID, PID)
    add_layer_condition(r_b2_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b2_emacs, APP_EMACS)
    manipulators.append(r_b2_emacs)

    # Hyper: Throw Screen 2
    r_b2_hyp = compile_rule(ButtonConfig("2", ButtonBehavior.CLICK, Action("2", ["left_option", "left_shift"])), VID, PID)
    add_layer_condition(r_b2_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b2_hyp)


    # --- Button 3: Right / Forward ---
    # Tap: Space Right
    manipulators.append(compile_rule(ButtonConfig("3", ButtonBehavior.CLICK, Action("right_arrow", ["left_control"])), VID, PID))

    # RMB (Chrome/Notes): Tab Right
    r_b3_rmb = compile_rule(ButtonConfig("3", ButtonBehavior.CLICK, Action("close_bracket", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b3_rmb, LAYER_RMB, 1)
    # Fixed: Added r prefix
    add_app_restriction(r_b3_rmb, r"^(com\.google\.Chrome|com\.apple\.Notes|com\.sublimetext\.4)$")
    manipulators.append(r_b3_rmb)

    # RMB (Emacs): Find File (SPC f f)
    r_b3_emacs = compile_rule(ButtonConfig("3", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("f"), ActionEvent("f")
    ])), VID, PID)
    add_layer_condition(r_b3_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b3_emacs, APP_EMACS)
    manipulators.append(r_b3_emacs)

    # Hyper: Swap Main Window
    r_b3_hyp = compile_rule(ButtonConfig("3", ButtonBehavior.CLICK, Action("return_or_enter", ["left_control", "left_option", "left_shift"])), VID, PID)
    add_layer_condition(r_b3_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b3_hyp)


    # ==========================================================================
    # 3. ROW 2: ACTION & GIT
    # ==========================================================================

    # --- Button 4: Copy / Pull ---
    # Tap: Copy
    manipulators.append(compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, Action("c", ["left_command"])), VID, PID))

    # RMB (Chrome): Copy URL
    r_b4_chrome = compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, Action(["l", "c", "escape"], ["left_command"])), VID, PID)
    add_layer_condition(r_b4_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b4_chrome, APP_CHROME)
    manipulators.append(r_b4_chrome)

    # RMB (Sublime): Duplicate Line
    r_b4_subl = compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, Action("d", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b4_subl, LAYER_RMB, 1)
    add_app_restriction(r_b4_subl, APP_SUBLIME)
    manipulators.append(r_b4_subl)

    # RMB (Emacs): Pull (F p)
    r_b4_emacs = compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, make_seq([
        ActionEvent("f", ["left_shift"]), # Capital F
        ActionEvent("p")
    ])), VID, PID)
    add_layer_condition(r_b4_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b4_emacs, APP_EMACS)
    manipulators.append(r_b4_emacs)

    # Hyper: Cut
    r_b4_hyp = compile_rule(ButtonConfig("4", ButtonBehavior.CLICK, Action("x", ["left_command"])), VID, PID)
    add_layer_condition(r_b4_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b4_hyp)


    # --- Button 5: Undo / Cycle ---
    # Tap: Undo
    manipulators.append(compile_rule(ButtonConfig("5", ButtonBehavior.CLICK, Action("z", ["left_command"])), VID, PID))

    # RMB (General): Escape
    r_b5_rmb = compile_rule(ButtonConfig("5", ButtonBehavior.CLICK, Action("escape")), VID, PID)
    add_layer_condition(r_b5_rmb, LAYER_RMB, 1)
    # Fixed: Added r prefix
    add_app_restriction(r_b5_rmb, r"^(com\.google\.Chrome|com\.apple\.Notes|com\.sublimetext\.4)$")
    manipulators.append(r_b5_rmb)

    # RMB (Emacs): Other Window (SPC w w)
    r_b5_emacs = compile_rule(ButtonConfig("5", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("w"), ActionEvent("w")
    ])), VID, PID)
    add_layer_condition(r_b5_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b5_emacs, APP_EMACS)
    manipulators.append(r_b5_emacs)

    # Hyper: Select Whole Line
    r_b5_hyp = compile_rule(ButtonConfig("5", ButtonBehavior.CLICK, make_seq([
        ActionEvent("left_arrow", ["left_command", "left_shift"]),
        ActionEvent("right_arrow", ["left_command", "left_shift"])
    ])), VID, PID)
    add_layer_condition(r_b5_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b5_hyp)


    # --- Button 6: Paste / Commit ---
    # Tap: Paste
    manipulators.append(compile_rule(ButtonConfig("6", ButtonBehavior.CLICK, Action("v", ["left_command"])), VID, PID))

    # RMB (Chrome): Paste & Go
    r_b6_rmb = compile_rule(ButtonConfig("6", ButtonBehavior.CLICK, Action("v", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b6_rmb, LAYER_RMB, 1)
    # Fixed: Added r prefix
    add_app_restriction(r_b6_rmb, r"^(com\.google\.Chrome|com\.apple\.Notes|com\.sublimetext\.4)$")
    manipulators.append(r_b6_rmb)

    # RMB (Emacs): Commit (c c)
    r_b6_emacs = compile_rule(ButtonConfig("6", ButtonBehavior.CLICK, make_seq([
        ActionEvent("c"), ActionEvent("c")
    ])), VID, PID)
    add_layer_condition(r_b6_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b6_emacs, APP_EMACS)
    manipulators.append(r_b6_emacs)

    # Hyper: Paste Match Style
    r_b6_hyp = compile_rule(ButtonConfig("6", ButtonBehavior.CLICK, Action("v", ["left_option", "left_shift", "left_command"])), VID, PID)
    add_layer_condition(r_b6_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b6_hyp)


    # ==========================================================================
    # 4. ROW 3: LIFECYCLE
    # ==========================================================================

    # --- Button 7: Start / New ---
    # Tap: Media Play
    manipulators.append(compile_rule(ButtonConfig("7", ButtonBehavior.CLICK, Action("play_or_pause")), VID, PID))

    # RMB (Chrome): Incognito
    r_b7_chrome = compile_rule(ButtonConfig("7", ButtonBehavior.CLICK, Action("n", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b7_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b7_chrome, APP_CHROME)
    manipulators.append(r_b7_chrome)

    # RMB (Emacs): Restart (SPC q r)
    r_b7_emacs = compile_rule(ButtonConfig("7", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("q"), ActionEvent("r")
    ])), VID, PID)
    add_layer_condition(r_b7_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b7_emacs, APP_EMACS)
    manipulators.append(r_b7_emacs)

    # Hyper: New Window
    r_b7_hyp = compile_rule(ButtonConfig("7", ButtonBehavior.CLICK, Action("n", ["left_command"])), VID, PID)
    add_layer_condition(r_b7_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b7_hyp)


    # --- Button 8: Enter / Status ---
    # Tap: Enter
    manipulators.append(compile_rule(ButtonConfig("8", ButtonBehavior.CLICK, Action("return_or_enter")), VID, PID))

    # RMB (Chrome): Hard Reload
    r_b8_chrome = compile_rule(ButtonConfig("8", ButtonBehavior.CLICK, Action("r", ["left_command", "left_shift"])), VID, PID)
    add_layer_condition(r_b8_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b8_chrome, APP_CHROME)
    manipulators.append(r_b8_chrome)

    # RMB (Emacs): Magit Status (SPC g g)
    r_b8_emacs = compile_rule(ButtonConfig("8", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("g"), ActionEvent("g")
    ])), VID, PID)
    add_layer_condition(r_b8_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b8_emacs, APP_EMACS)
    manipulators.append(r_b8_emacs)

    # Hyper: Refresh Page
    r_b8_hyp = compile_rule(ButtonConfig("8", ButtonBehavior.CLICK, Action("r", ["left_command"])), VID, PID)
    add_layer_condition(r_b8_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b8_hyp)


    # --- Button 9: Close / Quit ---
    # Tap: Close Window
    manipulators.append(compile_rule(ButtonConfig("9", ButtonBehavior.CLICK, Action("w", ["left_command"])), VID, PID))

    # RMB (General): Close Tab
    r_b9_rmb = compile_rule(ButtonConfig("9", ButtonBehavior.CLICK, Action("w", ["left_command"])), VID, PID)
    add_layer_condition(r_b9_rmb, LAYER_RMB, 1)
    # Fixed: Added r prefix
    add_app_restriction(r_b9_rmb, r"^(com\.google\.Chrome|com\.apple\.Notes|com\.sublimetext\.4)$")
    manipulators.append(r_b9_rmb)

    # RMB (Emacs): Quit (SPC q q)
    r_b9_emacs = compile_rule(ButtonConfig("9", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("q"), ActionEvent("q")
    ])), VID, PID)
    add_layer_condition(r_b9_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b9_emacs, APP_EMACS)
    manipulators.append(r_b9_emacs)

    # Hyper: Force Quit
    r_b9_hyp = compile_rule(ButtonConfig("9", ButtonBehavior.CLICK, Action("escape", ["left_command", "left_option"])), VID, PID)
    add_layer_condition(r_b9_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b9_hyp)


    # ==========================================================================
    # 5. ROW 4: LAZY TOOLS
    # ==========================================================================

    # --- Button 10: Find / Search ---
    # Tap: Find Selection
    manipulators.append(compile_rule(ButtonConfig("0", ButtonBehavior.CLICK, make_seq([
        ActionEvent("c", ["left_command"]),
        ActionEvent("f", ["left_command"]),
        ActionEvent("v", ["left_command"]),
        ActionEvent("return_or_enter", hold_down_milliseconds=20)
    ])), VID, PID))

    # RMB (Chrome): Super Search
    r_b10_chrome = compile_rule(ButtonConfig("0", ButtonBehavior.CLICK, make_seq([
        ActionEvent("c", ["left_command"]),
        ActionEvent("t", ["left_command"]),
        ActionEvent("v", ["left_command"]),
        ActionEvent("return_or_enter")
    ])), VID, PID)
    add_layer_condition(r_b10_chrome, LAYER_RMB, 1)
    add_app_restriction(r_b10_chrome, APP_CHROME)
    manipulators.append(r_b10_chrome)

    # RMB (Emacs): Search Project (SPC /)
    r_b10_emacs = compile_rule(ButtonConfig("0", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("slash")
    ])), VID, PID)
    add_layer_condition(r_b10_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b10_emacs, APP_EMACS)
    manipulators.append(r_b10_emacs)

    # Hyper: Manual Find
    r_b10_hyp = compile_rule(ButtonConfig("0", ButtonBehavior.CLICK, Action("f", ["left_command"])), VID, PID)
    add_layer_condition(r_b10_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b10_hyp)


    # --- Button 11: Vol Down / Switch ---
    # Tap: Volume Down
    manipulators.append(compile_rule(ButtonConfig("hyphen", ButtonBehavior.CLICK, Action("volume_decrement")), VID, PID))

    # RMB (Notes): Add Link
    r_b11_notes = compile_rule(ButtonConfig("hyphen", ButtonBehavior.CLICK, Action("k", ["left_command"])), VID, PID)
    add_layer_condition(r_b11_notes, LAYER_RMB, 1)
    add_app_restriction(r_b11_notes, APP_NOTES)
    manipulators.append(r_b11_notes)

    # RMB (Emacs): Switch Buffer (SPC b b)
    r_b11_emacs = compile_rule(ButtonConfig("hyphen", ButtonBehavior.CLICK, make_seq([
        ActionEvent("spacebar"), ActionEvent("b"), ActionEvent("b")
    ])), VID, PID)
    add_layer_condition(r_b11_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b11_emacs, APP_EMACS)
    manipulators.append(r_b11_emacs)

    # Hyper: Brightness Down
    r_b11_hyp = compile_rule(ButtonConfig("hyphen", ButtonBehavior.CLICK, Action("display_brightness_decrement")), VID, PID)
    add_layer_condition(r_b11_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b11_hyp)


    # --- Button 12: Vol Up / Ship It ---
    # Tap: Volume Up
    manipulators.append(compile_rule(ButtonConfig("equal_sign", ButtonBehavior.CLICK, Action("volume_increment")), VID, PID))

    # RMB (Emacs): SHIP IT! (Push: P p)
    # Workflow: 8(Status) -> s(Stage) -> 6(Commit) -> 12(Push)
    r_b12_emacs = compile_rule(ButtonConfig("equal_sign", ButtonBehavior.CLICK, make_seq([
        ActionEvent("p", ["left_shift"]), # P
        ActionEvent("p")                  # p
    ])), VID, PID)
    add_layer_condition(r_b12_emacs, LAYER_RMB, 1)
    add_app_restriction(r_b12_emacs, APP_EMACS)
    manipulators.append(r_b12_emacs)

    # Hyper: Brightness Up
    r_b12_hyp = compile_rule(ButtonConfig("equal_sign", ButtonBehavior.CLICK, Action("display_brightness_increment")), VID, PID)
    add_layer_condition(r_b12_hyp, LAYER_HYPER, 1)
    manipulators.append(r_b12_hyp)


    # ==========================================================================
    # OUTPUT
    # ==========================================================================
    profile_json = {
        "title": "test v3.0",
        "rules": [
            {
                "description": "MouseMapper V3.2 (Emacs Expanded)",
                "manipulators": manipulators
            }
        ]
    }

    print(json.dumps(profile_json, indent=2))


if __name__ == "__main__":
    generate_leisure_profile()

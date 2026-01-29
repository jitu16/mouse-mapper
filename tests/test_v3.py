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

APP_CHROME = "^com\\.google\\.Chrome$"
APP_NOTES  = "^com\\.apple\\.Notes$"
APP_EMACS  = "^org\\.gnu\\.Emacs$"

def generate_naga_v3_profile():
    """
    Generates the MouseMapper V2.4 Master Profile (Naga V3).

    Structure:
    1. Modifier Definition (Button 3)
    2. Hyper Layer Rules (Priority High)
    3. App-Specific Rules (Priority Medium)
    4. Global Default Rules (Priority Low)
    """
    manipulators = []

    # ==========================================================================
    # 1. MODIFIER DEFINITION
    # ==========================================================================
    hyper_btn = ButtonConfig(
        button_id="button3",
        behavior=ButtonBehavior.MODIFIER,
        layer_variable=LAYER_HYPER,
        threshold_ms=200
    )
    manipulators.append(compile_rule(hyper_btn, VID, PID))

    # ==========================================================================
    # 2. HYPER LAYER RULES (HOLD BUTTON 3)
    # ==========================================================================

    # --- Row 1: Window Management (Amethyst) ---
    # Hyper 1 -> Throw to Screen 1 (LO + LS + 1)
    h1 = ButtonConfig("1", ButtonBehavior.CLICK, Action("1", ["left_option", "left_shift"]))
    r_h1 = compile_rule(h1, VID, PID)
    add_layer_condition(r_h1, LAYER_HYPER, 1)
    r_h1["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h1)

    # Hyper 2 -> Throw to Screen 2 (LO + LS + 2)
    h2 = ButtonConfig("2", ButtonBehavior.CLICK, Action("2", ["left_option", "left_shift"]))
    r_h2 = compile_rule(h2, VID, PID)
    add_layer_condition(r_h2, LAYER_HYPER, 1)
    r_h2["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h2)

    # Hyper 3 -> Swap Main (LCt + LO + LS + Enter)
    h3 = ButtonConfig("3", ButtonBehavior.CLICK, Action("return_or_enter", ["left_control", "left_option", "left_shift"]))
    r_h3 = compile_rule(h3, VID, PID)
    add_layer_condition(r_h3, LAYER_HYPER, 1)
    r_h3["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h3)

    # --- Row 2: Advanced Editing ---
    # Hyper 4 -> Cut (Cmd + X)
    h4 = ButtonConfig("4", ButtonBehavior.CLICK, Action("x", ["left_command"]))
    r_h4 = compile_rule(h4, VID, PID)
    add_layer_condition(r_h4, LAYER_HYPER, 1)
    r_h4["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h4)

    # Hyper 5 -> Select Line (Cmd+Left -> Shift+Cmd+Right)
    action_select_line = Action(key_code=["left_arrow", "right_arrow"], modifiers=["left_command"])
    # Note: Complex macros with changing modifiers need careful Action handling or splitting.
    # Current core Action applies modifiers to ALL keys.
    # For "Cmd+Left then Shift+Cmd+Right", we need separate Actions if we stick to the core strictly.
    # However, for simplicity in this version, we will assume standard "Select Line" behavior via Shift+Cmd+Right from start?
    # No, that misses the start. Let's use the core list support but we might need to manually craft the event if modifiers change.
    # To keep it safe: Just Cmd+L (Select Line in many editors) or purely Shift+Cmd+Right (Select to End).
    # Let's map it to "Select to End of Line" (Shift+Cmd+Right) for stability.
    h5 = ButtonConfig("5", ButtonBehavior.CLICK, Action("right_arrow", ["left_command", "left_shift"]))
    r_h5 = compile_rule(h5, VID, PID)
    add_layer_condition(r_h5, LAYER_HYPER, 1)
    r_h5["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h5)

    # Hyper 6 -> Paste Match Style (Cmd + Opt + Shift + V)
    h6 = ButtonConfig("6", ButtonBehavior.CLICK, Action("v", ["left_command", "left_option", "left_shift"]))
    r_h6 = compile_rule(h6, VID, PID)
    add_layer_condition(r_h6, LAYER_HYPER, 1)
    r_h6["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h6)

    # --- Row 3: Hyper Apps ---
    # Hyper 7 (Chrome) -> Incognito
    h7_chrome = ButtonConfig("7", ButtonBehavior.CLICK, Action("n", ["left_command", "left_shift"]))
    r_h7c = compile_rule(h7_chrome, VID, PID)
    add_layer_condition(r_h7c, LAYER_HYPER, 1)
    add_app_restriction(r_h7c, APP_CHROME)
    r_h7c["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h7c)

    # Hyper 8 (Chrome) -> Reopen Closed Tab
    h8_chrome = ButtonConfig("8", ButtonBehavior.CLICK, Action("t", ["left_command", "left_shift"]))
    r_h8c = compile_rule(h8_chrome, VID, PID)
    add_layer_condition(r_h8c, LAYER_HYPER, 1)
    add_app_restriction(r_h8c, APP_CHROME)
    r_h8c["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h8c)

    # Hyper 8 (Notes) -> Indent (Cmd + ])
    h8_notes = ButtonConfig("8", ButtonBehavior.CLICK, Action("close_bracket", ["left_command"]))
    r_h8n = compile_rule(h8_notes, VID, PID)
    add_layer_condition(r_h8n, LAYER_HYPER, 1)
    add_app_restriction(r_h8n, APP_NOTES)
    r_h8n["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h8n)

    # Hyper 9 (Notes) -> Outdent (Cmd + [)
    h9_notes = ButtonConfig("9", ButtonBehavior.CLICK, Action("open_bracket", ["left_command"]))
    r_h9n = compile_rule(h9_notes, VID, PID)
    add_layer_condition(r_h9n, LAYER_HYPER, 1)
    add_app_restriction(r_h9n, APP_NOTES)
    r_h9n["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h9n)

    # Hyper 9 (Chrome) -> Reload (Cmd + r)
    h9_chrome = ButtonConfig("9", ButtonBehavior.CLICK, Action("r", ["left_command"]))
    r_h9c = compile_rule(h9_chrome, VID, PID)
    add_layer_condition(r_h9c, LAYER_HYPER, 1)
    add_app_restriction(r_h9c, APP_CHROME)
    r_h9c["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h9c)

    # --- Row 4: Hyper Search ---
    # Hyper 10 (Chrome) -> Google Selection (Cmd+C -> Cmd+T -> Cmd+V -> Enter)
    # We cheat slightly: Since modifiers apply to all, we rely on the fact Cmd is held for C, T, V.
    # Enter does not need Cmd, but Cmd+Enter usually submits anyway in Chrome URL bar.
    h10_chrome = ButtonConfig("0", ButtonBehavior.CLICK, Action(["c", "t", "v", "return_or_enter"], ["left_command"]))
    r_h10c = compile_rule(h10_chrome, VID, PID)
    add_layer_condition(r_h10c, LAYER_HYPER, 1)
    add_app_restriction(r_h10c, APP_CHROME)
    r_h10c["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h10c)

    # Hyper 10 (Notes) -> Global Search Selection (Cmd+C -> Cmd+Opt+F -> Cmd+V)
    # This requires mixed modifiers (Cmd vs Cmd+Opt).
    # For now, we simplify to just "Search All" (Cmd+Opt+F) so user can paste manually.
    h10_notes = ButtonConfig("0", ButtonBehavior.CLICK, Action("f", ["left_command", "left_option"]))
    r_h10n = compile_rule(h10_notes, VID, PID)
    add_layer_condition(r_h10n, LAYER_HYPER, 1)
    add_app_restriction(r_h10n, APP_NOTES)
    r_h10n["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h10n)

    # Hyper 11 (Notes) -> Add Link (Cmd+K)
    h11_notes = ButtonConfig("hyphen", ButtonBehavior.CLICK, Action("k", ["left_command"]))
    r_h11n = compile_rule(h11_notes, VID, PID)
    add_layer_condition(r_h11n, LAYER_HYPER, 1)
    add_app_restriction(r_h11n, APP_NOTES)
    r_h11n["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h11n)

    # Hyper 11 (Chrome) -> DevTools (Cmd+Opt+I)
    h11_chrome = ButtonConfig("hyphen", ButtonBehavior.CLICK, Action("i", ["left_command", "left_option"]))
    r_h11c = compile_rule(h11_chrome, VID, PID)
    add_layer_condition(r_h11c, LAYER_HYPER, 1)
    add_app_restriction(r_h11c, APP_CHROME)
    r_h11c["from"]["modifiers"] = {"optional": ["any"]}
    manipulators.append(r_h11c)


    # ==========================================================================
    # 3. APP SPECIFIC RULES (TAP)
    # ==========================================================================

    # --- Chrome Taps ---
    # 7: New Tab
    c7 = ButtonConfig("7", ButtonBehavior.CLICK, Action("t", ["left_command"]))
    r_c7 = compile_rule(c7, VID, PID)
    add_app_restriction(r_c7, APP_CHROME)
    manipulators.append(r_c7)

    # 8: Copy URL (Cmd+L -> Cmd+C -> Esc)
    c8 = ButtonConfig("8", ButtonBehavior.CLICK, Action(["l", "c", "escape"], ["left_command"]))
    r_c8 = compile_rule(c8, VID, PID)
    add_app_restriction(r_c8, APP_CHROME)
    manipulators.append(r_c8)

    # 9: Close Tab
    c9 = ButtonConfig("9", ButtonBehavior.CLICK, Action("w", ["left_command"]))
    r_c9 = compile_rule(c9, VID, PID)
    add_app_restriction(r_c9, APP_CHROME)
    manipulators.append(r_c9)

    # 10: Find
    c10 = ButtonConfig("0", ButtonBehavior.CLICK, Action("f", ["left_command"]))
    r_c10 = compile_rule(c10, VID, PID)
    add_app_restriction(r_c10, APP_CHROME)
    manipulators.append(r_c10)

    # 11: Find Selection (Copy -> Find -> Paste -> Enter)
    c11 = ButtonConfig("hyphen", ButtonBehavior.CLICK, Action(["c", "f", "v", "return_or_enter"], ["left_command"]))
    r_c11 = compile_rule(c11, VID, PID)
    add_app_restriction(r_c11, APP_CHROME)
    manipulators.append(r_c11)

    # 12: Downloads
    c12 = ButtonConfig("equal_sign", ButtonBehavior.CLICK, Action("j", ["left_command", "left_shift"]))
    r_c12 = compile_rule(c12, VID, PID)
    add_app_restriction(r_c12, APP_CHROME)
    manipulators.append(r_c12)


    # --- Notes Taps ---
    # 7: Title (Cmd+Shift+T)
    n7 = ButtonConfig("7", ButtonBehavior.CLICK, Action("t", ["left_command", "left_shift"]))
    r_n7 = compile_rule(n7, VID, PID)
    add_app_restriction(r_n7, APP_NOTES)
    manipulators.append(r_n7)

    # 8: Checklist (Cmd+Shift+L)
    n8 = ButtonConfig("8", ButtonBehavior.CLICK, Action("l", ["left_command", "left_shift"]))
    r_n8 = compile_rule(n8, VID, PID)
    add_app_restriction(r_n8, APP_NOTES)
    manipulators.append(r_n8)

    # 9: Code Block (Cmd+Shift+M) - Note: M might vary, checking generic mapping
    # Assuming Cmd+Shift+M is user's bind for Monospace/Code.
    n9 = ButtonConfig("9", ButtonBehavior.CLICK, Action("m", ["left_command", "left_shift"]))
    r_n9 = compile_rule(n9, VID, PID)
    add_app_restriction(r_n9, APP_NOTES)
    manipulators.append(r_n9)

    # 10: Search All (Cmd+Opt+F)
    n10 = ButtonConfig("0", ButtonBehavior.CLICK, Action("f", ["left_command", "left_option"]))
    r_n10 = compile_rule(n10, VID, PID)
    add_app_restriction(r_n10, APP_NOTES)
    manipulators.append(r_n10)

    # 11: Find Selection (Same as Chrome)
    n11 = ButtonConfig("hyphen", ButtonBehavior.CLICK, Action(["c", "f", "v", "return_or_enter"], ["left_command"]))
    r_n11 = compile_rule(n11, VID, PID)
    add_app_restriction(r_n11, APP_NOTES)
    manipulators.append(r_n11)

    # 12: New Note
    n12 = ButtonConfig("equal_sign", ButtonBehavior.CLICK, Action("n", ["left_command"]))
    r_n12 = compile_rule(n12, VID, PID)
    add_app_restriction(r_n12, APP_NOTES)
    manipulators.append(r_n12)


    # --- Emacs Taps ---
    # 7: Magit Status (Space g g)
    e7 = ButtonConfig("7", ButtonBehavior.CLICK, Action(["spacebar", "g", "g"]))
    r_e7 = compile_rule(e7, VID, PID)
    add_app_restriction(r_e7, APP_EMACS)
    manipulators.append(r_e7)

    # 8: Commit (c c)
    e8 = ButtonConfig("8", ButtonBehavior.CLICK, Action(["c", "c"]))
    r_e8 = compile_rule(e8, VID, PID)
    add_app_restriction(r_e8, APP_EMACS)
    manipulators.append(r_e8)

    # 9: Ship It (C-c C-c -> p -> p)
    # Using modifier on first Action item (C-c C-c), then plain p p.
    # Current Action structure applies modifiers to ALL keys in list.
    # Workaround: Use simple 'C-c' repeated twice? No, we need sequences.
    # We will map it to: Control+C, Control+C, p, p.
    # Since our core helper is simple, we will map 9 to a complex chain by just doing the Commit part (C-c C-c)
    # and letting user press P, OR we assume the user configured C-c C-c P p as a key chord in Emacs?
    # Better: Just send C-c C-c. User can press p. Or we send p p without modifiers?
    # Our simplified Core applies modifiers to the whole list.
    # Compromise: Map to C-c C-c only.
    e9 = ButtonConfig("9", ButtonBehavior.CLICK, Action(["c", "c"], ["left_control"]))
    r_e9 = compile_rule(e9, VID, PID)
    add_app_restriction(r_e9, APP_EMACS)
    manipulators.append(r_e9)

    # 10: Find File (Space f f)
    e10 = ButtonConfig("0", ButtonBehavior.CLICK, Action(["spacebar", "f", "f"]))
    r_e10 = compile_rule(e10, VID, PID)
    add_app_restriction(r_e10, APP_EMACS)
    manipulators.append(r_e10)

    # 11: Switch Buffer (Space b b)
    e11 = ButtonConfig("hyphen", ButtonBehavior.CLICK, Action(["spacebar", "b", "b"]))
    r_e11 = compile_rule(e11, VID, PID)
    add_app_restriction(r_e11, APP_EMACS)
    manipulators.append(r_e11)

    # 12: Toggle Shell (Option+t)
    e12 = ButtonConfig("equal_sign", ButtonBehavior.CLICK, Action("t", ["left_option"]))
    r_e12 = compile_rule(e12, VID, PID)
    add_app_restriction(r_e12, APP_EMACS)
    manipulators.append(r_e12)


    # ==========================================================================
    # 4. GLOBAL DEFAULT RULES
    # ==========================================================================

    # 1: Space Left
    g1 = ButtonConfig("1", ButtonBehavior.CLICK, Action("left_arrow", ["left_control"]))
    manipulators.append(compile_rule(g1, VID, PID))

    # 2: Mission Control
    g2 = ButtonConfig("2", ButtonBehavior.CLICK, Action("mission_control"))
    manipulators.append(compile_rule(g2, VID, PID))

    # 3: Space Right
    g3 = ButtonConfig("3", ButtonBehavior.CLICK, Action("right_arrow", ["left_control"]))
    manipulators.append(compile_rule(g3, VID, PID))

    # 4: Copy
    g4 = ButtonConfig("4", ButtonBehavior.CLICK, Action("c", ["left_command"]))
    manipulators.append(compile_rule(g4, VID, PID))

    # 5: Undo
    g5 = ButtonConfig("5", ButtonBehavior.CLICK, Action("z", ["left_command"]))
    manipulators.append(compile_rule(g5, VID, PID))

    # 6: Paste
    g6 = ButtonConfig("6", ButtonBehavior.CLICK, Action("v", ["left_command"]))
    manipulators.append(compile_rule(g6, VID, PID))


    # --- OUTPUT ---
    profile_json = {
        "title": "MouseMapper V2.4 Profile",
        "rules": [
            {
                "description": "MouseMapper V2.4 (Naga HyperSpeed)",
                "manipulators": manipulators
            }
        ]
    }

    print(json.dumps(profile_json, indent=2))

if __name__ == "__main__":
    generate_naga_v3_profile()

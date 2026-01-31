"""
Core V3: Karabiner-Elements JSON Generator.

This module provides a functional API and data structures to generate complex
Karabiner-Elements rules.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from enum import Enum

# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass
class ActionEvent:
    """
    Represents a single, atomic event within an action sequence.

    Attributes:
        key_code: The key or button identifier (e.g., 'a', 'left_command', 'button1').
        modifiers: List of modifier keys to hold during this event.
        shell_command: A raw shell command to execute.
        hold_down_milliseconds: Duration to hold the input.
    """
    key_code: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    shell_command: Optional[str] = None
    hold_down_milliseconds: int = 0


@dataclass
class Action:
    """
    Container for output commands.

    Attributes:
        key_code: Single key/button string or list of strings (Simple Mode).
        modifiers: Modifiers applied globally to the key_code inputs.
        shell_command: Raw shell command string.
        events: List of ActionEvents for complex sequences (Complex Mode).
    """
    key_code: Optional[Union[str, List[str]]] = None
    modifiers: List[str] = field(default_factory=list)
    shell_command: Optional[str] = None
    events: List[ActionEvent] = field(default_factory=list)


class ButtonBehavior(Enum):
    """
    Enumeration of interaction archetypes.
    """
    CLICK = "click"
    MODIFIER = "modifier"
    DUAL = "dual"
    VIRTUAL = "virtual"
    SIMULTANEOUS = "simultaneous"


@dataclass
class ButtonConfig:
    """
    Configuration blueprint for a physical input rule.

    Attributes:
        button_id: Input identifier(s). String for single input, List for simultaneous.
        behavior: The interaction archetype (CLICK, DUAL, etc).
        tap_action: The Action to execute on a tap event.
        layer_variable: The variable name to toggle for modifier layers.
        threshold_ms: Input latency threshold for dual-role triggers.
        mandatory_modifiers: Hardware modifiers required to trigger this rule.
        simultaneous_threshold_ms: Time window for simultaneous detection.
    """
    button_id: Union[str, List[str]]
    behavior: ButtonBehavior
    tap_action: Optional[Action] = None
    layer_variable: Optional[str] = None
    threshold_ms: int = 200
    mandatory_modifiers: List[str] = field(default_factory=list)
    simultaneous_threshold_ms: int = 50


# ==============================================================================
# FACTORY FUNCTIONS
# ==============================================================================

def make_seq(events: List[ActionEvent]) -> Action:
    """
    Factory function to create a complex Action sequence.

    Args:
        events: A list of ActionEvent objects.

    Returns:
        An Action object configured for complex execution.
    """
    return Action(events=events)


def add_app_restriction(manipulator: Dict[str, Any], app_id: Optional[str]) -> None:
    """
    Injects a 'frontmost_application_if' condition into a manipulator.

    Args:
        manipulator: The rule dictionary to modify.
        app_id: The regex string for the application bundle identifier.
    """
    if not app_id:
        return
    condition = {"type": "frontmost_application_if", "bundle_identifiers": [app_id]}
    manipulator.setdefault("conditions", []).append(condition)


def add_layer_condition(manipulator: Dict[str, Any], layer_name: str, value: int = 1) -> None:
    """
    Injects a 'variable_if' condition into a manipulator.

    Args:
        manipulator: The rule dictionary to modify.
        layer_name: The name of the variable to check.
        value: The required value (1 or 0).
    """
    condition = {"type": "variable_if", "name": layer_name, "value": value}
    manipulator.setdefault("conditions", []).append(condition)


# ==============================================================================
# INTERNAL LOGIC
# ==============================================================================

def _create_event_payload(key_or_btn: str) -> Dict[str, Any]:
    """
    Creates the correct JSON payload key based on the input string.

    Args:
        key_or_btn: The input string (e.g., "return_or_enter" or "button1").

    Returns:
        A dictionary with either "pointing_button" or "key_code".
    """
    if key_or_btn.startswith("button"):
        return {"pointing_button": key_or_btn}
    return {"key_code": key_or_btn}


def _action_to_json(action: Action) -> List[Dict[str, Any]]:
    """
    Serializes an Action object into a list of Karabiner 'to' events.

    Args:
        action: The Action object to serialize.

    Returns:
        A list of dictionaries representing the 'to' block in JSON.
    """
    if action.shell_command:
        return [{"shell_command": action.shell_command}]

    json_events: List[Dict[str, Any]] = []

    if action.events:
        for event in action.events:
            if event.shell_command:
                json_events.append({"shell_command": event.shell_command})
                continue

            if not event.key_code:
                continue

            payload = _create_event_payload(event.key_code)

            if event.modifiers:
                payload["modifiers"] = event.modifiers
            if event.hold_down_milliseconds > 0:
                payload["hold_down_milliseconds"] = event.hold_down_milliseconds
            json_events.append(payload)
        return json_events

    keys = []
    if isinstance(action.key_code, str):
        keys.append(action.key_code)
    elif isinstance(action.key_code, list):
        keys = action.key_code

    for k in keys:
        payload = _create_event_payload(k)

        if action.modifiers:
            payload["modifiers"] = action.modifiers
        if len(keys) > 1:
             payload["hold_down_milliseconds"] = 20
        json_events.append(payload)

    return json_events


def _create_from_block(config: ButtonConfig) -> Dict[str, Any]:
    """
    Generates the 'from' block for a manipulator.

    Args:
        config: The ButtonConfig object.

    Returns:
        A dictionary representing the 'from' block in JSON.
    """
    from_block = {}

    if config.behavior == ButtonBehavior.SIMULTANEOUS:
        if not isinstance(config.button_id, list):
            raise ValueError("Simultaneous behavior requires a list of button_ids")

        simul_events = []
        for b in config.button_id:
            if b.startswith("button"):
                simul_events.append({"pointing_button": b})
            else:
                simul_events.append({"key_code": b})

        from_block["simultaneous"] = simul_events
        from_block["simultaneous_options"] = {
            "key_down_order": "insensitive",
            "detect_key_down_uninterruptedly": True
        }
    else:
        if isinstance(config.button_id, str):
            if config.button_id.startswith("button"):
                from_block["pointing_button"] = config.button_id
            else:
                from_block["key_code"] = config.button_id

    if config.mandatory_modifiers:
        from_block["modifiers"] = {"mandatory": config.mandatory_modifiers}

    return from_block


def _create_base_manipulator(config: ButtonConfig, vid: int, pid: int) -> Dict[str, Any]:
    """
    Creates the base dictionary structure for a Karabiner manipulator.

    Args:
        config: The ButtonConfig object.
        vid: The Vendor ID.
        pid: The Product ID.

    Returns:
        A dictionary containing 'type', 'from', and 'conditions'.
    """
    rule = {
        "type": "basic",
        "from": _create_from_block(config),
    }

    if vid and pid:
        rule["conditions"] = [
            {
                "type": "device_if",
                "identifiers": [{"vendor_id": vid, "product_id": pid}]
            }
        ]

    return rule


# ==============================================================================
# COMPILERS
# ==============================================================================

def compile_click_rule(config: ButtonConfig, vid: int, pid: int) -> Dict[str, Any]:
    """
    Compiles a rule for standard click or simultaneous input.

    Args:
        config: The ButtonConfig object.
        vid: The Vendor ID.
        pid: The Product ID.

    Returns:
        The complete manipulator dictionary.
    """
    rule = _create_base_manipulator(config, vid, pid)
    if config.tap_action:
        rule["to"] = _action_to_json(config.tap_action)
    return rule


def compile_dual_rule(config: ButtonConfig, vid: int, pid: int) -> Dict[str, Any]:
    """
    Compiles a dual-role rule (Tap for Action, Hold for Layer Variable).

    Args:
        config: The ButtonConfig object.
        vid: The Vendor ID.
        pid: The Product ID.

    Returns:
        The complete manipulator dictionary.
    """
    rule = _create_base_manipulator(config, vid, pid)

    if not config.layer_variable:
        raise ValueError(f"Button {config.button_id} configured as dual/modifier but missing layer_variable.")

    rule["to"] = [{"set_variable": {"name": config.layer_variable, "value": 1}}]
    rule["to_after_key_up"] = [{"set_variable": {"name": config.layer_variable, "value": 0}}]

    if config.tap_action:
        rule["to_if_alone"] = _action_to_json(config.tap_action)

    rule["parameters"] = {
        "basic.to_if_alone_timeout_milliseconds": config.threshold_ms
    }
    return rule


def compile_virtual_modifier_rule(config: ButtonConfig, vid: int, pid: int) -> Dict[str, Any]:
    """
    Compiles a rule turning a standard key into a virtual modifier variable.

    Args:
        config: The ButtonConfig object.
        vid: The Vendor ID.
        pid: The Product ID.

    Returns:
        The complete manipulator dictionary.
    """
    rule = _create_base_manipulator(config, vid, pid)

    if not config.layer_variable:
        raise ValueError(f"Button {config.button_id} configured as virtual modifier but missing layer_variable.")

    rule["to"] = [{"set_variable": {"name": config.layer_variable, "value": 1}}]
    rule["to_after_key_up"] = [{"set_variable": {"name": config.layer_variable, "value": 0}}]

    if config.tap_action:
        rule["to_if_alone"] = _action_to_json(config.tap_action)

    rule["parameters"] = {
        "basic.to_if_alone_timeout_milliseconds": config.threshold_ms
    }
    return rule


def compile_rule(config: ButtonConfig, vid: int = 0, pid: int = 0) -> Dict[str, Any]:
    """
    Main dispatch function to compile a ButtonConfig into a Karabiner manipulator.

    Args:
        config: The ButtonConfig object.
        vid: The Vendor ID.
        pid: The Product ID.

    Returns:
        The complete manipulator dictionary.
    """
    if config.behavior == ButtonBehavior.CLICK:
        return compile_click_rule(config, vid, pid)
    elif config.behavior in [ButtonBehavior.MODIFIER, ButtonBehavior.DUAL]:
        return compile_dual_rule(config, vid, pid)
    elif config.behavior == ButtonBehavior.VIRTUAL:
        return compile_virtual_modifier_rule(config, vid, pid)
    elif config.behavior == ButtonBehavior.SIMULTANEOUS:
        return compile_click_rule(config, vid, pid)
    return {}

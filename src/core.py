from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class ButtonBehavior(Enum):
    """
    Defines the interaction archetypes for button configuration.
    """
    CLICK = "click"           # Standard single-action button
    MODIFIER = "modifier"     # Active only while held (Shift-style)
    TOGGLE = "toggle"         # Tap to activate, Tap to deactivate (Caps-style)
    DUAL = "dual"             # Tap for Action A, Hold for Modifier Layer

@dataclass
class Action:
    """
    Represents a single executable command in macOS.

    Attributes:
        key_code: The target key to simulate (e.g., 't', 'mission_control').
        modifiers: A list of mandatory modifiers (e.g., ['left_command']).
        shell_command: A raw terminal command to execute.
    """
    key_code: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    shell_command: Optional[str] = None

@dataclass
class ButtonConfig:
    """
    The Input Blueprint: Defines how a physical button should behave.

    Attributes:
        button_id: The physical button identifier (e.g., 'button3', '1').
        behavior: The interaction archetype (CLICK, MODIFIER, TOGGLE, DUAL).
        tap_action: The action to execute on a standard click (required for CLICK and DUAL).
        layer_variable: The name of the variable to manipulate (required for MODIFIER, TOGGLE, DUAL).
        threshold_ms: Time in milliseconds to distinguish tap from hold (required for DUAL).
    """
    button_id: str
    behavior: ButtonBehavior
    tap_action: Optional[Action] = None
    layer_variable: Optional[str] = None
    threshold_ms: int = 200

def add_app_restriction(manipulator: Dict[str, Any], app_id: Optional[str]) -> None:
    """
    Injects the 'frontmost_application_if' condition into a rule.

    Args:
        manipulator: The dictionary representing the Karabiner rule.
        app_id: The Bundle ID regex of the target application.
    """
    if not app_id:
        return

    app_condition = {
        "type": "frontmost_application_if",
        "bundle_identifiers": [app_id]
    }

    if "conditions" not in manipulator:
        manipulator["conditions"] = []

    manipulator["conditions"].append(app_condition)

def add_layer_condition(manipulator: Dict[str, Any], layer_name: str, value: int = 1) -> None:
    """
    Injects a 'variable_if' condition into a rule to check if a modifier layer is active.

    Args:
        manipulator: The dictionary representing the Karabiner rule.
        layer_name: The name of the variable to check.
        value: The value the variable must match (default 1).
    """
    layer_condition = {
        "type": "variable_if",
        "name": layer_name,
        "value": value
    }

    if "conditions" not in manipulator:
        manipulator["conditions"] = []

    manipulator["conditions"].append(layer_condition)

def _create_basic_manipulator(from_button: str, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    Generates the skeleton of a Karabiner manipulator with hardware enforcement.
    Automatically detects if the input is a Mouse Button (starts with 'button') or a Key Code.

    Args:
        from_button: The physical button ID (e.g., 'button3' or '1').
        vendor_id: The target USB Vendor ID.
        product_id: The target USB Product ID.

    Returns:
        A dictionary containing the 'type', 'from', and 'conditions' keys.
    """
    # Determine if input is a Pointing Button or a Key Code
    if from_button.startswith("button"):
        from_event = {"pointing_button": from_button}
    else:
        from_event = {"key_code": from_button}

    return {
        "type": "basic",
        "from": from_event,
        "conditions": [
            {
                "type": "device_if",
                "identifiers": [{
                    "vendor_id": vendor_id,
                    "product_id": product_id
                }]
            }
        ]
    }

def _convert_action_to_json(action: Action) -> Dict[str, Any]:
    """
    Serializes an Action object into a Karabiner 'to' event.

    Args:
        action: The Action object to convert.

    Returns:
        A dictionary compatible with Karabiner's 'to' array.
    """
    if action.shell_command:
        return {"shell_command": action.shell_command}

    payload = {"key_code": action.key_code}
    if action.modifiers:
        payload["modifiers"] = action.modifiers
    return payload

def compile_click_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    Compiles a Standard Click rule.

    Args:
        config: The button configuration.
        vendor_id: The target USB Vendor ID.
        product_id: The target USB Product ID.

    Returns:
        A complete Karabiner manipulator dictionary.
    """
    rule = _create_basic_manipulator(config.button_id, vendor_id, product_id)
    rule["to"] = [_convert_action_to_json(config.tap_action)]
    return rule

def compile_modifier_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    Compiles a Pure Modifier rule (active only while held).

    Args:
        config: The button configuration.
        vendor_id: The target USB Vendor ID.
        product_id: The target USB Product ID.

    Returns:
        A complete Karabiner manipulator dictionary.
    """
    rule = _create_basic_manipulator(config.button_id, vendor_id, product_id)

    # Set variable to 1 on Key Down, 0 on Key Up
    rule["to"] = [{"set_variable": {"name": config.layer_variable, "value": 1}}]
    rule["to_after_key_up"] = [{"set_variable": {"name": config.layer_variable, "value": 0}}]

    # If using a mouse button as modifier, preserve its original click if tapped alone
    if config.button_id.startswith("button"):
        rule["to_if_alone"] = [{"pointing_button": config.button_id}]
        rule["parameters"] = {"basic.to_if_alone_timeout_milliseconds": config.threshold_ms}

    return rule

def compile_dual_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    Compiles a Dual Role rule (Tap for Action, Hold for Layer).

    Args:
        config: The button configuration.
        vendor_id: The target USB Vendor ID.
        product_id: The target USB Product ID.

    Returns:
        A complete Karabiner manipulator dictionary.
    """
    rule = _create_basic_manipulator(config.button_id, vendor_id, product_id)

    rule["to"] = [{"set_variable": {"name": config.layer_variable, "value": 1}}]
    rule["to_after_key_up"] = [{"set_variable": {"name": config.layer_variable, "value": 0}}]
    rule["to_if_alone"] = [_convert_action_to_json(config.tap_action)]
    rule["parameters"] = {"basic.to_if_alone_timeout_milliseconds": config.threshold_ms}

    return rule

def compile_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    The Main Dispatcher.

    Args:
        config: The high-level button configuration.
        vendor_id: The specific USB Vendor ID to target.
        product_id: The specific USB Product ID to target.

    Returns:
        A complete Karabiner manipulator dictionary.
    """
    if config.behavior == ButtonBehavior.CLICK:
        if not config.tap_action:
            raise ValueError(f"Button {config.button_id} (CLICK) missing tap_action.")
        return compile_click_rule(config, vendor_id, product_id)

    elif config.behavior == ButtonBehavior.MODIFIER:
        if not config.layer_variable:
            raise ValueError(f"Button {config.button_id} (MODIFIER) missing layer_variable.")
        return compile_modifier_rule(config, vendor_id, product_id)

    elif config.behavior == ButtonBehavior.DUAL:
        if not config.tap_action or not config.layer_variable:
            raise ValueError(f"Button {config.button_id} (DUAL) missing tap_action or layer_variable.")
        return compile_dual_rule(config, vendor_id, product_id)

    return {}

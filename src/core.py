from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from enum import Enum

class ButtonBehavior(Enum):
    """
    Defines the interaction archetypes for button configuration.
    """
    CLICK = "click"
    MODIFIER = "modifier"
    TOGGLE = "toggle"
    DUAL = "dual"

@dataclass
class Action:
    """
    Represents a command or sequence of commands in macOS.

    Attributes:
        key_code: Target key(s). Can be a single string (e.g. 'a') or list (e.g. ['a', 'b']).
        modifiers: Mandatory modifiers applied to ALL keys in the sequence.
        shell_command: A raw terminal command to execute.
    """
    key_code: Optional[Union[str, List[str]]] = None
    modifiers: List[str] = field(default_factory=list)
    shell_command: Optional[str] = None

@dataclass
class ButtonConfig:
    """
    The Input Blueprint: Defines how a physical button should behave.

    Attributes:
        button_id: The physical button identifier (e.g., 'button3', '1').
        behavior: The interaction archetype.
        tap_action: Action for standard click (required for CLICK and DUAL).
        layer_variable: Variable name for modifiers (required for MODIFIER, TOGGLE, DUAL).
        threshold_ms: Tap vs Hold threshold.
        required_modifiers: Modifiers required to trigger this rule.
    """
    button_id: str
    behavior: ButtonBehavior
    tap_action: Optional[Action] = None
    layer_variable: Optional[str] = None
    threshold_ms: int = 200
    required_modifiers: List[str] = field(default_factory=list)

def add_app_restriction(manipulator: Dict[str, Any], app_id: Optional[str]) -> None:
    """
    Injects the 'frontmost_application_if' condition into a rule.
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
    """
    layer_condition = {
        "type": "variable_if",
        "name": layer_name,
        "value": value
    }

    if "conditions" not in manipulator:
        manipulator["conditions"] = []

    manipulator["conditions"].append(layer_condition)

def _create_basic_manipulator(from_button: str, vendor_id: int, product_id: int, required_modifiers: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generates the skeleton of a Karabiner manipulator with hardware enforcement.
    """
    from_event: Dict[str, Any] = {}

    if from_button.startswith("button"):
        from_event["pointing_button"] = from_button
    else:
        from_event["key_code"] = from_button

    if required_modifiers:
        from_event["modifiers"] = {"mandatory": required_modifiers}

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

def _convert_action_to_json(action: Action) -> List[Dict[str, Any]]:
    """
    Serializes an Action object into a list of Karabiner 'to' events.
    Supports macros by returning multiple events if key_code is a list.
    """
    if action.shell_command:
        return [{"shell_command": action.shell_command}]

    events = []
    keys = []

    if isinstance(action.key_code, str):
        keys.append(action.key_code)
    elif isinstance(action.key_code, list):
        keys = action.key_code

    for k in keys:
        payload: Dict[str, Any] = {"key_code": k}
        if action.modifiers:
            payload["modifiers"] = action.modifiers
        if len(keys) > 1:
             payload["hold_down_milliseconds"] = 20
        events.append(payload)

    return events

def compile_click_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    Compiles a Standard Click rule.
    """
    if config.tap_action is None:
        raise ValueError(f"Button {config.button_id} (CLICK) missing tap_action.")

    rule = _create_basic_manipulator(config.button_id, vendor_id, product_id, config.required_modifiers)
    rule["to"] = _convert_action_to_json(config.tap_action)
    return rule

def compile_modifier_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    Compiles a Pure Modifier rule (active only while held).
    """
    if config.layer_variable is None:
        raise ValueError(f"Button {config.button_id} (MODIFIER) missing layer_variable.")

    rule = _create_basic_manipulator(config.button_id, vendor_id, product_id, config.required_modifiers)

    rule["to"] = [{"set_variable": {"name": config.layer_variable, "value": 1}}]
    rule["to_after_key_up"] = [{"set_variable": {"name": config.layer_variable, "value": 0}}]

    if config.button_id.startswith("button"):
        rule["to_if_alone"] = [{"pointing_button": config.button_id}]
        rule["parameters"] = {"basic.to_if_alone_timeout_milliseconds": config.threshold_ms}

    return rule

def compile_dual_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    Compiles a Dual Role rule (Tap for Action, Hold for Layer).
    """
    if config.tap_action is None or config.layer_variable is None:
        raise ValueError(f"Button {config.button_id} (DUAL) missing tap_action or layer_variable.")

    rule = _create_basic_manipulator(config.button_id, vendor_id, product_id, config.required_modifiers)

    rule["to"] = [{"set_variable": {"name": config.layer_variable, "value": 1}}]
    rule["to_after_key_up"] = [{"set_variable": {"name": config.layer_variable, "value": 0}}]
    rule["to_if_alone"] = _convert_action_to_json(config.tap_action)
    rule["parameters"] = {"basic.to_if_alone_timeout_milliseconds": config.threshold_ms}

    return rule

def compile_toggle_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    Placeholder for Toggle behavior.
    """
    print(f"Warning: Toggle behavior for {config.button_id} is not implemented yet.")
    return {}

def compile_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    The Main Dispatcher.
    """
    if config.behavior == ButtonBehavior.CLICK:
        return compile_click_rule(config, vendor_id, product_id)

    elif config.behavior == ButtonBehavior.MODIFIER:
        return compile_modifier_rule(config, vendor_id, product_id)

    elif config.behavior == ButtonBehavior.DUAL:
        return compile_dual_rule(config, vendor_id, product_id)

    elif config.behavior == ButtonBehavior.TOGGLE:
        return compile_toggle_rule(config, vendor_id, product_id)

    return {}

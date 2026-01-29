from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from enum import Enum

class ButtonBehavior(Enum):
    """
    Defines the four architectural archetypes for button interaction.
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

def _add_app_condition(manipulator: Dict[str, Any], app_id: Optional[str]) -> None:
    """
    Injects the 'frontmost_application_if' condition into a rule.
    """
    if not app_id:
        return

    # Create the condition object
    app_condition = {
        "type": "frontmost_application_if",
        "bundle_identifiers": [app_id]
    }

    # Append to existing conditions (don't overwrite device_id!)
    if "conditions" not in manipulator:
        manipulator["conditions"] = []

    manipulator["conditions"].append(app_condition)

def _create_basic_manipulator(from_button: str, vendor_id: int,  product_id: int) -> Dict[str, Any]:
    """
    Generates the skeleton of a Karabiner manipulator with hardware enforcement.

    Args:
        from_button: The physical button ID to listen for.
        vendor_id & product_id: The hardware ID to restrict this rule to.

    Returns:
        A dictionary containing the 'type', 'from', and 'conditions' keys.
    """
    return {
        "type": "basic",
        "from": {"pointing_button": from_button},
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

def compile_scroll_rule(
    vendor_id: int,
    product_id: int,
    layer_name: str,
    scroll_direction: str,  # "up" or "down"
    target_action: Action
) -> dict:
    """
    Constructs a Karabiner manipulator for a Scroll Gesture.

    Input: "When 'layer_name' is active, and user scrolls 'up', do 'target_action'."
    Output: The complex JSON block required to make that happen.
    """

    # 1. Translate logical direction to Karabiner's internal values
    # macOS Natural Scrolling: -1 is physically UP, 1 is physically DOWN
    wheel_value = -1 if scroll_direction.lower() == "up" else 1

    # 2. Build the "From" event (The Trigger)
    from_event = {
        "mouse_key": {"vertical_wheel": wheel_value},
        "modifiers": {"optional": ["any"]} # Allow scrolling even if other keys are held
    }

    # 3. Build the "Conditions" (The Gatekeepers)
    conditions = [
        # Hardware Lock
        {
            "type": "device_if",
            "identifiers": [{"vendor_id": vendor_id, "product_id": product_id}]
        },
        # Layer Lock (The magic switch)
        {
            "type": "variable_if",
            "name": layer_name,
            "value": 1
        }
    ]

    # 4. Build the "To" event (The Result)
    # Reuse our existing helper to convert Action -> JSON
    to_event = _convert_action_to_json(target_action)

    # 5. Assemble the Block
    return {
        "type": "basic",
        "from": from_event,
        "to": [to_event],
        "conditions": conditions
    }

def _convert_action_to_json(action: Action) -> Dict[str, Any]:
    """
    Converts an Action dataclass into a Karabiner 'to' event object.

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
        vendor_id & product_id: The target hardware ID.

    Returns:
        A Karabiner manipulator dictionary.
    """
    rule = _create_basic_manipulator(config.button_id, vendor_id, product_id)
    rule["to"] = [_convert_action_to_json(config.tap_action)]
    return rule

def compile_modifier_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    Compiles a Pure Modifier (Shift-style) rule.

    Sets the layer variable to 1 on key_down and 0 on key_up.

    Args:
        config: The button configuration.
        vendor_id & product_id: The target hardware ID.

    Returns:
        A Karabiner manipulator dictionary.
    """
    rule = _create_basic_manipulator(config.button_id, vendor_id, product_id)
    rule["to"] = [{"set_variable": {"name": config.layer_variable, "value": 1}}]
    rule["to_after_key_up"] = [{"set_variable": {"name": config.layer_variable, "value": 0}}]
    return rule

def compile_dual_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    Compiles a Dual Role (Tap vs Hold) rule.

    Uses 'to_if_alone' for the tap action and 'to' for the hold (layer) action.
    Injects the specific timeout parameter for this button.

    Args:
        config: The button configuration.
        vendor_id & product_id: The target hardware ID.

    Returns:
        A Karabiner manipulator dictionary.
    """
    rule = _create_basic_manipulator(config.button_id, vendor_id, product_id)

    # Hold Behavior (Activate Layer)
    rule["to"] = [{"set_variable": {"name": config.layer_variable, "value": 1}}]
    rule["to_after_key_up"] = [{"set_variable": {"name": config.layer_variable, "value": 0}}]

    # Tap Behavior (Execute Action)
    rule["to_if_alone"] = [_convert_action_to_json(config.tap_action)]

    # Configuration
    rule["parameters"] = {
        "basic.to_if_alone_timeout_milliseconds": config.threshold_ms
    }
    return rule

def compile_rule(config: ButtonConfig, vendor_id: int, product_id: int) -> Dict[str, Any]:
    """
    The Main Dispatcher.

    Routes the configuration to the appropriate compiler based on behavior type.

    Args:
        config: The high-level button configuration.
        vendor_id: The specific USB Vendor ID to target.

    Returns:
        A complete Karabiner manipulator dictionary ready for JSON serialization.

    Raises:
        ValueError: If a required field (like tap_action) is missing for the selected behavior.
    """
    if config.behavior == ButtonBehavior.CLICK:
        if not config.tap_action:
            raise ValueError(f"Button {config.button_id} is set to CLICK but has no tap_action.")
        return compile_click_rule(config, vendor_id, product_id)

    elif config.behavior == ButtonBehavior.MODIFIER:
        if not config.layer_variable:
            raise ValueError(f"Button {config.button_id} is set to MODIFIER but has no layer_variable.")
        return compile_modifier_rule(config, vendor_id, product_id)

    elif config.behavior == ButtonBehavior.DUAL:
        if not config.tap_action or not config.layer_variable:
            raise ValueError(f"Button {config.button_id} (DUAL) requires both tap_action and layer_variable.")
        return compile_dual_rule(config, vendor_id, product_id)

    elif config.behavior == ButtonBehavior.TOGGLE:
        # Note: Toggle logic usually requires complex conditions dependent on current state.
        # This is a placeholder for the Toggle implementation.
        raise NotImplementedError("Toggle behavior implementation pending state-machine logic.")

    return {}

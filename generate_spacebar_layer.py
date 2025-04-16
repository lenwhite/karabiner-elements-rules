import json

# Variables
SPACEBAR_DOWN = "spacebar_down"
LAYER_KEY_DOWN = "layer_key_down"
LAYER_EFFECT_TRIGGERED = "layer_effect_triggered"

# Conditions
IF_LAYER_ACTIVE = {"type": "variable_if", "name": SPACEBAR_DOWN, "value": 1}
IF_NOT_LAYER_ACTIVE = {"type": "variable_if", "name": SPACEBAR_DOWN, "value": 0}
IF_EFFECT_TRIGGERED = {
    "type": "variable_if",
    "name": LAYER_EFFECT_TRIGGERED,
    "value": 1,
}
IF_KEY_UP = {"type": "variable_if", "name": LAYER_KEY_DOWN, "value": 0}
IF_LAYER_KEY_DOWN = {"type": "variable_if", "name": LAYER_KEY_DOWN, "value": 1}
IF_NOT_LAYER_KEY_DOWN = {"type": "variable_if", "name": LAYER_KEY_DOWN, "value": 0}

IF_NOT_LAYER_EFFECT_TRIGGERED = {
    "type": "variable_if",
    "name": LAYER_EFFECT_TRIGGERED,
    "value": 0,
}

# Actions
HALT = {"halt": True}

SET_KEY_DOWN = {"set_variable": {"name": LAYER_KEY_DOWN, "value": 1}}
SET_KEY_UP = {"set_variable": {"name": LAYER_KEY_DOWN, "value": 0}}
SET_EFFECT_TRIGGERED = {"set_variable": {"name": LAYER_EFFECT_TRIGGERED, "value": 1}}

SEND_SPACEBAR_KEYCODE_AND_HALT = {"key_code": "spacebar", "halt": True}

ACTIVATE_LAYER = {"set_variable": {"name": SPACEBAR_DOWN, "value": 1}}
DEACTIVATE_LAYER = {"set_variable": {"name": SPACEBAR_DOWN, "value": 0}}


def generate_spacebar_manipulator():

    return {
        "type": "basic",
        "from": {"key_code": "spacebar", "modifiers": {"optional": ["any"]}},
        "to_if_alone": [
            DEACTIVATE_LAYER,
            SEND_SPACEBAR_KEYCODE_AND_HALT,
        ],
        "to": [
            ACTIVATE_LAYER,
        ],
        "to_after_key_up": [
            DEACTIVATE_LAYER,
        ],
        "to_delayed_action": {
            "to_if_canceled": [
                DEACTIVATE_LAYER,
                SEND_SPACEBAR_KEYCODE_AND_HALT,
            ]
        },
        "parameters": {"basic.to_delayed_action_delay_milliseconds": 200},
    }


def generate_simultaneous_manipulator(from_key, to_key, to_modifiers=None):
    """Generates a manipulator for a key within the spacebar layer based on temp.json structure."""

    SEND_REMAPPED_KEY = {
        "key_code": to_key,
    }

    if to_modifiers:
        SEND_REMAPPED_KEY["modifiers"] = to_modifiers

    return {
        "type": "basic",
        "from": {
            "simultaneous": [{"key_code": "spacebar"}, {"key_code": from_key}],
            "modifiers": {"optional": ["any"]},
            "simultaneous_options": {
                "key_down_order": "strict",
                "key_up_order": "strict_inverse",
                "to_after_key_up": [
                    DEACTIVATE_LAYER,
                ],
            },
        },
        "to": [
            ACTIVATE_LAYER,
            SEND_REMAPPED_KEY,
        ],
        "parameters": {"basic.simultaneous_threshold_milliseconds": 500},
    }


def generate_layer_key_manipulator(from_key, to_key, to_modifiers=None):
    """Generates a manipulator for a key within the spacebar layer based on temp.json structure."""

    SEND_REMAPPED_KEY = {
        "conditions": [IF_LAYER_ACTIVE],
        "key_code": to_key,
        **HALT,
    }

    if to_modifiers:
        SEND_REMAPPED_KEY["modifiers"] = to_modifiers

    return {
        "type": "basic",
        "from": {"key_code": from_key, "modifiers": {"optional": ["any"]}},
        "to": [SEND_REMAPPED_KEY],
        "conditions": [{"type": "variable_if", "name": SPACEBAR_DOWN, "value": 1}],
    }


def main():
    """Generates the complete spacebar layer JSON and writes it to a file."""
    # Merged mappings: from_key -> (to_key, optional_modifiers_list)
    mappings = {
        # Arrows
        "k": ("left_arrow", None),
        "o": ("up_arrow", None),
        "semicolon": ("right_arrow", None),
        "l": ("down_arrow", None),
        # Word navigation
        "i": ("left_arrow", ["left_option"]),
        "p": ("right_arrow", ["left_option"]),
        # line/page navigation
        "a": ("home", None),
        "d": ("end", None),
        "w": ("page_up", None),
        "s": ("page_down", None),
        # select words
        "q": ("left_arrow", ["left_shift", "left_option"]),
        "e": ("right_arrow", ["left_shift", "left_option"]),
        # function key
        "1": ("f1", None),
        "2": ("f2", None),
        "3": ("f3", None),
        "4": ("f4", None),
        "5": ("f5", None),
        "6": ("f6", None),
        "7": ("f7", None),
        "8": ("f8", None),
        "9": ("f9", None),
        "0": ("f10", None),
        "hyphen": ("f11", None),
        "equal_sign": ("f12", None),
    }

    manipulators = []

    manipulators.extend(
        generate_simultaneous_manipulator(from_key, to_key, to_modifiers)
        for from_key, (to_key, to_modifiers) in mappings.items()
    )

    manipulators.append(generate_spacebar_manipulator())

    manipulators.extend(
        generate_layer_key_manipulator(from_key, to_key, to_modifiers=modifiers)
        for from_key, (to_key, modifiers) in mappings.items()
    )

    output_json = {
        "description": "Spacebar layer: Navigation keys (arrows, word, select, home/end, pgup/dn)",
        "manipulators": manipulators,
    }

    output_filename = "spacebar-layer.json"
    try:
        with open(output_filename, "w") as f:
            json.dump(output_json, f, indent=2)
        print(f"Successfully generated {output_filename}")
    except IOError as e:
        print(f"Error writing to file {output_filename}: {e}")


if __name__ == "__main__":
    main()

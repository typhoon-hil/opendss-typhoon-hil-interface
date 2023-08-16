import ast
import string

SCHEMATIC_EXPANDING_FACTOR = 2
SCHEMATIC_GRID_STEP = 8


def snap_to_grid(value):
    base = SCHEMATIC_GRID_STEP * (value // SCHEMATIC_GRID_STEP)
    if value - base >= SCHEMATIC_GRID_STEP / 2:
        return base + SCHEMATIC_GRID_STEP
    else:
        return base


def fix_name(original_name, obj_class=None):
    new_name = original_name

    for character in original_name:
        if character not in list(
            string.ascii_lowercase + string.ascii_uppercase + string.digits
        ) + ["_", "-"]:
            new_name = new_name.replace(character, "_")

    if all(character in list(string.digits) for character in new_name):
        if obj_class:
            new_name = obj_class.lower() + original_name
        else:
            new_name = "_" + original_name

    return new_name


def rotate_component(original_value, direction="left", times=1):
    rotation_states_list = ["up", "left", "down", "right"]  # Left sequence
    start_idx = rotation_states_list.index(original_value)
    if direction == "left":
        return rotation_states_list[(start_idx + times) % len(rotation_states_list)]
    elif direction == "right":
        return rotation_states_list[(start_idx - times) % len(rotation_states_list)]

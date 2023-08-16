from import_to_tse.constants import *

terminal_flip_dict = {
    "left": {"flip_horizontal": "right", "flip_vertical": "left", "flip_none": "left"},
    "right": {"flip_horizontal": "left", "flip_vertical": "right", "flip_none": "right"},
    "top": {"flip_horizontal": "top", "flip_vertical": "bottom", "flip_none": "top"},
    "bottom": {"flip_horizontal": "bottom", "flip_vertical": "top", "flip_none": "bottom"},
}

terminal_rotation_dict = {
    "left": {"up": "left", "left": "bottom", "down": "right", "right": "top"},
    "right": {"up": "right", "left": "top", "down": "left", "right": "bottom"},
    "top": {"up": "top", "left": "left", "down": "bottom", "right": "right"},
    "bottom": {"up": "bottom", "left": "right", "down": "up", "right": "left"},
}


def snap_to_grid(value, grid_size=TSE_GRID_RESOLUTION):
    if grid_size < 1:
        # Normalize to support fractions
        new_grid_size = 10
        multiplication_factor = new_grid_size / grid_size
        value = value * multiplication_factor

        base = new_grid_size * (value // new_grid_size)
        if value - base >= new_grid_size / 2:
            return (base + new_grid_size) / multiplication_factor
        else:
            return base / multiplication_factor
    else:
        base = grid_size * (value // grid_size)
        if value - base >= grid_size / 2:
            return base + grid_size
        else:
            return base


def terminal_side_after_rotation_and_flip(original_side, rotation, flip):
    new_side = original_side

    if rotation:
        new_side = terminal_rotation_dict.get(original_side).get(rotation)
    if flip:
        new_side = terminal_flip_dict.get(new_side).get(flip)

    return new_side


def rotate_tse_object(original_value, direction="left", times=1):

    if not original_value:
        original_value = "up"

    rotation_states_list = ["up", "left", "down", "right"]  # Left sequence
    start_idx = rotation_states_list.index(original_value)
    if direction == "left":
        return rotation_states_list[(start_idx + times) % len(rotation_states_list)]
    elif direction == "right":
        return rotation_states_list[(start_idx - times) % len(rotation_states_list)]


def odd(n):
    """
    Check if number is odd.
    """
    return n & 1

def get_connection_side(comp1, comp2):

    for term1 in comp1.terminals:
        for term2 in comp2.terminals:
            if term1.node == term2.node:
                term1_side = term1.get_side(visual_position=True)
                term2_side = term2.get_side(visual_position=True)
                return term1_side, term2_side

    return None, None

def are_terminals_opposite(term1, term2):
    """
    Checks if terminals' sides on their components are opposite
    """

    term1_side = term1.get_side(True)
    term2_side = term2.get_side(True)

    if term1_side == opposite_side(term2_side):
        return True


def opposite_side(side):
    """
    Returns the opposite side (string) of a component box.
    """

    if side == "left":
        return "right"
    elif side == "right":
        return "left"
    elif side == "top":
        return "bottom"
    elif side == "bottom":
        return "top"


def adjust_step(initial, term_num, dimension):
    """
    Calculate the largest step that will satisfy dimension when
    terminals are set apart one to each other.

    Arguments:
        initial - Initial step.
        term_num - Number of terminals.
        dimension - Dimension in which to fit.

    Returns:
        Calculated step.
    """
    if term_num < 2:
        return initial

    new_step = initial + TSE_GRID_RESOLUTION
    required_dimension = (term_num - 1) * new_step + 4 * TSE_GRID_RESOLUTION

    if required_dimension <= dimension:
        return adjust_step(new_step, term_num, dimension)
    else:
        return initial


def calculate_terminals_relative_positions(comp_size_x, comp_size_y, list_of_terminals):
    # Check if input is valid. Second element of the terminal must be a number.
    try:
        _ = [int(term.position[1]) for term in list_of_terminals]
    except ValueError:
        return None

    Y_STEP = 16
    X_STEP = 16

    if odd(comp_size_x // X_STEP):
        comp_size_x -= X_STEP
    elif odd(comp_size_y // Y_STEP):
        comp_size_y -= Y_STEP

    left = []
    top = []
    right = []
    bottom = []

    for term in list_of_terminals:
        side, order = term.position
        if side == "left":
            left.append(term)
        elif side == "right":
            right.append(term)
        elif side == "top":
            top.append(term)
        elif side == "bottom":
            bottom.append(term)

    left = sorted(left, key=lambda t: t.position)
    right = sorted(right, key=lambda t: t.position)
    top = sorted(top, key=lambda t: t.position)
    right = sorted(right, key=lambda t: t.position)

    terms_pos = {}

    # Left side
    left_len = len(left)

    y_step = adjust_step(initial=Y_STEP,
                         term_num=left_len,
                         dimension=comp_size_y)

    y = -(left_len // 2) * y_step if odd(left_len) else \
        -((left_len / 2) * y_step - y_step / 2)

    for term in left:
        terms_pos[term] = (-comp_size_x // 2, y)
        y += y_step

    # Right side
    right_len = len(right)

    y_step = adjust_step(initial=Y_STEP,
                         term_num=right_len,
                         dimension=comp_size_y)

    y = -(right_len // 2) * y_step if odd(right_len) else \
        -((right_len / 2) * y_step - y_step / 2)

    for term in right:
        terms_pos[term] = (comp_size_x // 2, y)
        y += y_step

    # Top part
    top_len = len(top)

    x_step = adjust_step(initial=X_STEP,
                         term_num=top_len,
                         dimension=comp_size_x)

    x = -(top_len // 2) * x_step if odd(top_len) else \
        -((top_len / 2) * x_step - x_step / 2)

    for term in top:
        terms_pos[term] = (x, -comp_size_y // 2)
        x += x_step

    # Bottom part

    bottom_len = len(bottom)

    x_step = adjust_step(initial=X_STEP,
                         term_num=bottom_len,
                         dimension=comp_size_x)

    x = -(bottom_len // 2) * x_step if odd(bottom_len) else \
        -((bottom_len / 2) * x_step - x_step / 2)

    for term in bottom:
        terms_pos[term] = (x, comp_size_y // 2)
        x += x_step

    return terms_pos

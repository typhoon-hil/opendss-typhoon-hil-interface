import helper_functions


def get_schematic_properties(opendss_class, obj_name, mask_properties):

    if opendss_class == "Bus":
        name = obj_name
        rotation = None
        flip = None
        position = None
        hide_name = False

    elif opendss_class == "Line":
        name = obj_name
        rotation = None
        flip = None
        position = None
        hide_name = False

    elif opendss_class == "Load":
        name = obj_name
        rotation = None
        flip = None
        position = None
        hide_name = False

    elif opendss_class == "Vsource":
        name = obj_name
        rotation = "left"
        flip = None
        position = None
        hide_name = False

    elif opendss_class == "Transformer":
        name = obj_name
        rotation = None
        flip = None
        position = None
        hide_name = False

    elif opendss_class == "Capacitor":
        name = obj_name
        rotation = None
        flip = None
        position = None
        hide_name = False

    schematic_properties = {
        "name": helper_functions.fix_name(name, opendss_class),
        "rotation": rotation,
        "flip": flip,
        "position": position,
        "size": None,
        "hide_name": hide_name,
    }

    return schematic_properties


def get_terminal_number_side_dict(opendss_class, mask_properties):

    if opendss_class == "Load":
        return {1: "top", 2: "bottom"}
    elif opendss_class == "Vsource":
        return {1: "right", 2: "left"}
    elif opendss_class == "Capacitor":
        if mask_properties["tp_connection"] == "In Series":
            return {1: "right", 2: "left"}
        else:
            return {1: "top", 2: "bottom"}
    else:
        return {1: "left", 2: "right"}

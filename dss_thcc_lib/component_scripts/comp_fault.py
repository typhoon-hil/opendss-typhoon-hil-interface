import json
import dss_thcc_lib.component_scripts.util as util
import importlib

old_state = {}


def toggle_inner_fault(mdl, mask_handle, mode="delete"):
    comp_handle = mdl.get_parent(mask_handle)
    inner_fault = mdl.get_item("F1", parent=comp_handle)
    a1 = mdl.get_item("A1", parent=comp_handle, item_type="port")
    b1 = mdl.get_item("B1", parent=comp_handle, item_type="port")
    c1 = mdl.get_item("C1", parent=comp_handle, item_type="port")
    a2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
    b2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
    c2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
    if inner_fault and mode == "delete":
        mdl.delete_item(inner_fault)
        mdl.create_connection(a1, a2)
        mdl.create_connection(b1, b2)
        mdl.create_connection(c1, c2)
    elif not inner_fault and mode == "restore":
        for conn in mdl.find_connections(a1):
            mdl.delete_item(conn)
        for conn in mdl.find_connections(b1):
            mdl.delete_item(conn)
        for conn in mdl.find_connections(c1):
            mdl.delete_item(conn)
        inner_fault = mdl.create_component(
            "core/Grid Fault",
            name="F1",
            parent=comp_handle,
            position=(7736, 7950)
        )
        res = mdl.get_property_value(mdl.prop(comp_handle, "resistance"))
        mdl.set_property_value(mdl.prop(inner_fault, "resistance"), res)
        mdl.create_connection(a1, mdl.term(inner_fault, "A1"))
        mdl.create_connection(b1, mdl.term(inner_fault, "B1"))
        mdl.create_connection(c1, mdl.term(inner_fault, "C1"))
        mdl.create_connection(a2, mdl.term(inner_fault, "A2"))
        mdl.create_connection(b2, mdl.term(inner_fault, "B2"))
        mdl.create_connection(c2, mdl.term(inner_fault, "C2"))


def update_inner_fault(mdl, mask_handle, prop_name, new_value):
    comp_handle = mdl.get_parent(mask_handle)
    type_prop = mdl.prop(mask_handle, "fault_type")
    prop_type = mdl.get_property_value(type_prop)

    if prop_name == "fault_type":
        if new_value == "None":
            toggle_inner_fault(mdl, mask_handle, mode="delete")
        else:
            toggle_inner_fault(mdl, mask_handle, mode="restore")
            inner_fault = mdl.get_item("F1", parent=comp_handle)
            mdl.set_property_value(mdl.prop(inner_fault, prop_name), new_value)
    elif prop_name == "resistance":
        if prop_type in ['A-B-C-GND', 'A-B-C']:
            new_value = str(float(new_value) * 3)
        if prop_type in ['A-B', 'A-C', 'B-C', 'A-B-GND', 'A-C-GND', 'B-C-GND']:
            new_value = str(float(new_value) * 2)
        inner_fault = mdl.get_item("F1", parent=comp_handle)
        if inner_fault:
            mdl.set_property_value(mdl.prop(inner_fault, prop_name), new_value)


def update_inner_gnd(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)
    av_gnd = mdl.get_item("gnd", parent=comp_handle)
    inner_fault = mdl.get_item("F1", parent=comp_handle)
    type_prop = mdl.prop(comp_handle, "fault_type")
    gnd_connection = True if "GND" in mdl.get_property_value(type_prop) else False

    if gnd_connection:
        if not av_gnd:
            av_gnd = mdl.create_component(
                type_name="core/Ground",
                name="gnd",
                parent=comp_handle,
                rotation="up",
                position=(7736, 8142)
            )

        if not mdl.find_connections(mdl.term(av_gnd, "node")):
            mdl.create_connection(mdl.term(av_gnd, "node"), mdl.term(inner_fault, 'GND'))
    else:
        if av_gnd:
            mdl.delete_item(av_gnd)


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    pass


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    deleted_ports = []
    created_ports = {}

    return created_ports, deleted_ports


def define_icon(mdl, mask_handle):
    type_prop = mdl.prop(mask_handle, "fault_type")
    type = mdl.get_property_value(type_prop)

    sld_mode_prop = mdl.prop(mask_handle, "sld_mode")
    sld_mode_disp = mdl.get_property_disp_value(sld_mode_prop)

    sld_image_text = {
        "A-B-C-GND": "ABC",
        "A-B-GND": "AB",
        "A-C-GND": "AC",
        "B-C-GND": "BC",
        "A-GND": "A",
        "B-GND": "B",
        "C-GND": "C",
        "A-B-C": "ABC",
        "A-B": "AB",
        "A-C": "AC",
        "B-C": "BC",
        "None": "No Fault",
    }

    gnd_types = ["A-B-C-GND", "A-B-GND", "A-C-GND", "B-C-GND", "A-GND", "B-GND", "C-GND"]
    if sld_mode_disp in (True, "True"):
        if type in gnd_types:
            mdl.set_component_icon_image(mask_handle, 'images/sc_g_sld.svg')
            mdl.disp_component_icon_text(mask_handle, sld_image_text[type], rotate="rotate",
                                         relpos_x=0.8,
                                         relpos_y=0.25,
                                         size=7, trim_factor=2)
        else:
            if type == "None":
                mdl.set_component_icon_image(mask_handle, 'images/sc_n_sld.svg')
            else:
                mdl.set_component_icon_image(mask_handle, 'images/sc_sld.svg')
            mdl.disp_component_icon_text(mask_handle, sld_image_text[type], rotate="rotate",
                                         relpos_x=0.5,
                                         relpos_y=0.9,
                                         size=7, trim_factor=2)
    else:
        if type == "A-B-C-GND":
            mdl.set_component_icon_image(mask_handle, 'images/sc_abc-g.svg')
        elif type == "A-B-GND":
            mdl.set_component_icon_image(mask_handle, 'images/sc_ab-g.svg')
        elif type == "A-C-GND":
            mdl.set_component_icon_image(mask_handle, 'images/sc_ac-g.svg')
        elif type == "B-C-GND":
            mdl.set_component_icon_image(mask_handle, 'images/sc_bc-g.svg')
        elif type == "A-GND":
            mdl.set_component_icon_image(mask_handle, 'images/sc_a-g.svg')
        elif type == "B-GND":
            mdl.set_component_icon_image(mask_handle, 'images/sc_b-g.svg')
        elif type == "C-GND":
            mdl.set_component_icon_image(mask_handle, 'images/sc_c-g.svg')
        elif type == "A-B-C":
            mdl.set_component_icon_image(mask_handle, 'images/sc_abc.svg')
        elif type == "A-B":
            mdl.set_component_icon_image(mask_handle, 'images/sc_ab.svg')
        elif type == "A-C":
            mdl.set_component_icon_image(mask_handle, 'images/sc_ac.svg')
        elif type == "B-C":
            mdl.set_component_icon_image(mask_handle, 'images/sc_bc.svg')
        elif type == "None":
            mdl.set_component_icon_image(mask_handle, 'images/sc_none.svg')


def get_sld_conversion_info(mdl, mask_handle, sld_name, multiline_ports, side, terminal_positions, sld_term_position):

    # multiline_ports_1 = ["A1", "B1", "C1"]

    port_config_dict = {
        sld_name: {
            "multiline_ports": multiline_ports,
            "side": side,
            "bus_terminal_position": sld_term_position,
            "hide_name": True,
        },
    }
    #
    # Tag info
    #
    tag_config_dict = {}

    #
    # Terminal positions
    #
    # terminal_positions = {
    #     "A1": (-48, -24),
    #     "B1": (-16, -24),
    #     "C1": (16, -24),
    # }

    return port_config_dict, tag_config_dict, terminal_positions


def topology_dynamics(mdl, mask_handle, prop_handle):
    """
    This function is called when the user changes the configuration on the mask
    """

    comp_handle = mdl.get_parent(mask_handle)
    if prop_handle:
        calling_prop_name = mdl.get_name(prop_handle)
    else:
        calling_prop_name = "init_code"

    current_pass_prop_values = {
        k: str(v) for k, v in mdl.get_property_values(comp_handle).items()
    }

    #
    # Get new property values to be applied (display values)
    #
    current_values = {}
    new_prop_values = {}
    for prop in mdl.get_property_values(comp_handle):
        p = mdl.prop(mask_handle, prop)
        new_prop_values[prop] = mdl.get_property_disp_value(p)
        current_values[prop] = mdl.get_property_value(p)
    #
    # If the property values are the same as on the previous run, stop
    #
    global old_state
    if new_prop_values == old_state.get(comp_handle):
        return

    if calling_prop_name == "init_code":
        define_icon(mdl, mask_handle)

    if calling_prop_name not in ["sld_mode", "init_code"]:

        sld_bus_count = 2
        sld_info = []

        for sld_idx in range(sld_bus_count):
            sld_name = "SLD" + str(sld_idx + 1)
            sld_number = {}
            importlib.reload(util)

            if sld_idx == 0:
                sld_side = "left"
                port_x = -32
            else:
                sld_side = "right"
                port_x = 32

            multi_port_list = ["A" + str(sld_idx + 1), "B" + str(sld_idx + 1), "C" + str(sld_idx + 1)]
            terminal_positions = {
                "A" + str(sld_idx + 1): (port_x, -32),
                "B" + str(sld_idx + 1): (port_x, 0),
                "C" + str(sld_idx + 1): (port_x, 32),
            }
            sld_term_position = (port_x, 0)

            sld_number["port_names"] = multi_port_list
            sld_number["side"] = sld_side
            sld_number["multi_term_pos"] = terminal_positions
            sld_number["sld_term_pos"] = sld_term_position

            sld_info.append(get_sld_conversion_info(mdl, mask_handle, sld_name,
                                                    sld_number.get("port_names"),
                                                    sld_number.get("side"),
                                                    sld_number.get("multi_term_pos"),
                                                    sld_number.get("sld_term_pos")
                                                    )
                            )

        for sld_idx in range(sld_bus_count):
            sld_name = "SLD" + str(sld_idx + 1)
            currently_sld = mdl.get_item(sld_name, parent=comp_handle, item_type="port")
            if currently_sld:
                util.convert_to_multiline(mdl, mask_handle, sld_info[sld_idx])

        define_icon(mdl, mask_handle)
        created_ports, _ = port_dynamics(mdl, mask_handle, calling_prop_name)
        update_inner_fault(mdl, mask_handle, calling_prop_name, new_prop_values.get(calling_prop_name))
        update_inner_gnd(mdl, mask_handle, created_ports)
        old_state[comp_handle] = current_values

    good_for_sld = []
    for prop_name in new_prop_values:
        if prop_name in ["fault_type"]:
            cur_pass_value = current_pass_prop_values[prop_name]
            new_value = new_prop_values[prop_name]
            if util.is_float(str(cur_pass_value)) or util.is_float(str(new_value)):
                if float(cur_pass_value) == float(new_value):
                    good_for_sld.append(True)
                    continue
            else:
                if str(current_pass_prop_values[prop_name]) == str(new_prop_values[prop_name]):
                    good_for_sld.append(True)
                    continue
            good_for_sld.append(False)

    final_state = all(good_for_sld)

    if final_state:
        old_state[comp_handle] = new_prop_values

        sld_bus_count = 2
        sld_info = []
        for sld_idx in range(sld_bus_count):
            sld_name = "SLD" + str(sld_idx + 1)
            sld_number = {}
            importlib.reload(util)

            if sld_idx == 0:
                sld_side = "left"
                port_x = -32
            else:
                sld_side = "right"
                port_x = 32

            multi_port_list = ["A" + str(sld_idx + 1), "B" + str(sld_idx + 1), "C" + str(sld_idx + 1)]
            terminal_positions = {
                "A" + str(sld_idx + 1): (port_x, -32),
                "B" + str(sld_idx + 1): (port_x, 0),
                "C" + str(sld_idx + 1): (port_x, 32),
            }
            sld_term_position = (port_x, 0)

            sld_number["port_names"] = multi_port_list
            sld_number["side"] = sld_side
            sld_number["multi_term_pos"] = terminal_positions
            sld_number["sld_term_pos"] = sld_term_position

            sld_info.append(get_sld_conversion_info(mdl, mask_handle, sld_name,
                                                    sld_number.get("port_names"),
                                                    sld_number.get("side"),
                                                    sld_number.get("multi_term_pos"),
                                                    sld_number.get("sld_term_pos")
                                               )
                            )

        if new_prop_values.get("sld_mode") in (True, "True"):
            for sld_idx in range(sld_bus_count):
                util.convert_to_sld(mdl, mask_handle, sld_info[sld_idx])
        else:
            for sld_idx in range(sld_bus_count):
                sld_name = "SLD" + str(sld_idx + 1)
                currently_sld = mdl.get_item(sld_name, parent=comp_handle, item_type="port")
                if currently_sld:
                    util.convert_to_multiline(mdl, mask_handle, sld_info[sld_idx])

    sld_post_processing(mdl, mask_handle)
    define_icon(mdl, mask_handle)


def sld_post_processing(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Resize the buses to 4

    for bus_name in ["SLD1_bus", "SLD2_bus"]:
        bus = mdl.get_item(bus_name, parent=comp_handle)
        if bus:
            bus_size_prop = mdl.prop(bus, "bus_size")
            mdl.set_property_value(bus_size_prop, 4)

import json
import dss_thcc_lib.component_scripts.util as util
import importlib

old_state = {}

def update_inner_property(mdl, mask_handle, prop_name, new_value):
    comp_handle = mdl.get_parent(mask_handle)
    inner_contactor = mdl.get_item("S", parent=comp_handle, item_type="component")
    inner_prop = mdl.prop(inner_contactor, prop_name)
    mdl.set_property_value(inner_prop, new_value)


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    prop_name = mdl.get_name(caller_prop_handle)
    new_value = mdl.get_property_disp_value(caller_prop_handle)

    if prop_name == "enable_fb_out":
        fb_out_type = mdl.prop(mask_handle, "fb_out_type")

        if new_value == "True":
            mdl.show_property(fb_out_type)
        else:
            mdl.hide_property(fb_out_type)

    if mdl.get_name(caller_prop_handle) in ["phases", "sld_mode"]:
        phases_prop = mdl.prop(mask_handle, "phases")
        phases_disp = mdl.get_property_disp_value(phases_prop)
        sld_mode_prop = mdl.prop(mask_handle, "sld_mode")
        sld_mode_disp = mdl.get_property_disp_value(sld_mode_prop)
        sld_1ph_pick_prop = mdl.prop(mask_handle, "sld_1ph_pick")
        sld_2ph_pick_prop = mdl.prop(mask_handle, "sld_2ph_pick")

        if sld_mode_disp in (True, "True"):
            if phases_disp == "1":
                mdl.show_property(sld_1ph_pick_prop)
                mdl.hide_property(sld_2ph_pick_prop)
            elif phases_disp == "2":
                mdl.show_property(sld_2ph_pick_prop)
                mdl.hide_property(sld_1ph_pick_prop)
            else:
                mdl.hide_property(sld_1ph_pick_prop)
                mdl.hide_property(sld_2ph_pick_prop)
        else:
            mdl.hide_property(sld_1ph_pick_prop)
            mdl.hide_property(sld_2ph_pick_prop)


def sld_port_transition(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    ctrl_input_port = mdl.get_item("ctrl", parent=comp_handle, item_type="port")
    fb_conn = mdl.get_item("fb", parent=comp_handle, item_type="port")

    sld_mode_prop = mdl.prop(mask_handle, "sld_mode")
    sld_mode_disp = mdl.get_property_disp_value(sld_mode_prop)

    num_phases = mdl.get_property_value(mdl.prop(comp_handle, "phases"))
    if sld_mode_disp in (True, "True"):
        y_pos = -16
    else:
        if num_phases == "1":
            y_pos = -16
        elif num_phases == "2":
            y_pos = -32
        else:
            y_pos = -48

    if ctrl_input_port:
        mdl.set_port_properties(ctrl_input_port, terminal_position=(-16, y_pos))

    if fb_conn:
        mdl.set_port_properties(fb_conn, terminal_position=(16, y_pos))


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    num_phases = mdl.get_property_value(mdl.prop(comp_handle, "phases"))
    if num_phases == "1":
        y_pos = -16
    elif num_phases == "2":
        y_pos = -32
    else:
        y_pos = -48

    ctrl_input_port = mdl.get_item("ctrl", parent=comp_handle, item_type="port")
    enable_fb_prop = mdl.prop(comp_handle, "enable_fb_out")
    enable_fb_terminal = True if mdl.get_property_value(enable_fb_prop) == "True" else False
    fb_conn = mdl.get_item("fb", parent=comp_handle, item_type="port")
    if enable_fb_terminal:
        if not fb_conn:
            fb_conn = mdl.create_port(
                name="fb",
                kind="sp",
                direction="out",
                parent=comp_handle,
                terminal_position=(16, y_pos),
                rotation="left",
                position=(7786, 7800),
                hide_name=True
            )
            created_ports.update({"fb": fb_conn})
        else:
            mdl.set_port_properties(fb_conn, terminal_position=(16, y_pos))
        mdl.set_port_properties(ctrl_input_port, terminal_position=(-16, y_pos))
    else:
        if fb_conn:
            deleted_ports.append(mdl.get_name(fb_conn))
            mdl.delete_item(fb_conn)
        mdl.set_port_properties(ctrl_input_port, terminal_position=(0, y_pos))

    new_created_ports, new_deleted_ports = change_number_phases_port(mdl, mask_handle, num_phases)

    created_ports.update(new_created_ports)
    for port_name in new_deleted_ports:
        deleted_ports.append(port_name)

    # Container workaround
    mdl.refresh_icon(comp_handle)
    c2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
    if c2:
        mdl.set_port_properties(c2, terminal_position=(32, 32))

    return created_ports, deleted_ports


def update_fb_connection(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)
    fb_conn = mdl.get_item("fb", parent=comp_handle, item_type="port")
    inner_contactor = mdl.get_item("S", parent=comp_handle)
    enable_fb_prop = mdl.prop(comp_handle, "enable_fb_out")
    enable_fb_terminal = True if mdl.get_property_value(enable_fb_prop) == "True" else False

    if fb_conn:
        if enable_fb_terminal:
            mdl.create_connection(fb_conn, mdl.term(inner_contactor, 'feedback_out'))


def define_icon(mdl, mask_handle):
    initial_state = mdl.get_property_value(mdl.prop(mask_handle, "initial_state"))
    phase_num = mdl.get_property_value(mdl.prop(mask_handle, "phases"))

    sld_mode_prop = mdl.prop(mask_handle, "sld_mode")
    sld_mode_disp = mdl.get_property_disp_value(sld_mode_prop)

    sld_1ph_pick = mdl.get_property_disp_value(mdl.prop(mask_handle, "sld_1ph_pick"))
    sld_2ph_pick = mdl.get_property_disp_value(mdl.prop(mask_handle, "sld_2ph_pick"))

    if sld_mode_disp in (True, "True"):
        if phase_num == "3":
            image_text = "ABC"
        elif phase_num == "2":
            if sld_2ph_pick == "A and B":
                image_text = "AB"
            elif sld_2ph_pick == "B and C":
                image_text = "BC"
            elif sld_2ph_pick == "A and C":
                image_text = "AC"
            else:
                image_text = "AB"
        elif phase_num == "1":
            if sld_1ph_pick == "A":
                image_text = "A"
            elif sld_1ph_pick == "B":
                image_text = "B"
            elif sld_1ph_pick == "C":
                image_text = "C"
            else:
                image_text = "AB"
        else:
            image_text = "ABC"

        mdl.disp_component_icon_text(mask_handle, image_text, rotate="rotate",
                                     relpos_x=0.5,
                                     relpos_y=0.8,
                                     size=7, trim_factor=2)

        if initial_state == "on":
            mdl.set_component_icon_image(mask_handle, f'images/switch_closed_1ph.svg')
        else:
            mdl.set_component_icon_image(mask_handle, f'images/switch_open_1ph.svg')
    else:
        if initial_state == "on":
            mdl.set_component_icon_image(mask_handle, f'images/switch_closed_{phase_num}ph.svg')
        else:
            mdl.set_component_icon_image(mask_handle, f'images/switch_open_{phase_num}ph.svg')






def change_number_phases_port(mdl, container_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(container_handle)
    phase_num = int(new_value)

    deleted_ports = []
    created_ports = {}

    port_dict = {"A1": {"terminal_position": (-32, -32),
                        "position": (7600, 7856)},
                 "A2": {"terminal_position": (32, -32),
                        "position": (7872, 7856)},
                 "B1": {"terminal_position": (-32, 0),
                        "position": (7600, 7952)},
                 "B2": {"terminal_position": (32, 0),
                        "position": (7872, 7952)},
                 "C1": {"terminal_position": (-32, 32),
                        "position": (7600, 8048)},
                 "C2": {"terminal_position": (32, 32),
                        "position": (7872, 8048)},
                 }

    if phase_num == 2:
        port_dict["A1"]["terminal_position"] = (-32, -16)
        port_dict["A2"]["terminal_position"] = (32, -16)
        port_dict["B1"]["position"] = port_dict["C1"]["position"]
        port_dict["B1"]["terminal_position"] = (-32, 16)
        port_dict["B2"]["position"] = port_dict["C2"]["position"]
        port_dict["B2"]["terminal_position"] = (32, 16)
    elif phase_num == 1:
        port_dict["A1"]["terminal_position"] = (-32, 0)
        port_dict["A2"]["terminal_position"] = (32, 0)

    phase_list = ["A", "B", "C"]
    used_phase_list = phase_list[0:phase_num]
    unused_phase_list = [phase for phase in phase_list if phase not in used_phase_list]

    for phase in used_phase_list:
        port1 = mdl.get_item(f"{phase}1", parent=comp_handle, item_type="port")
        if phase in ["B", "C"]:
            if not port1:
                port1 = mdl.create_port(name=f"{phase}1",
                                        kind="pe",
                                        parent=comp_handle,
                                        terminal_position=port_dict[f"{phase}1"]["terminal_position"],
                                        rotation="up",
                                        position=port_dict[f"{phase}1"]["position"],
                                        hide_name=True
                                        )
                created_ports.update({f"{phase}1": port1})
            else:
                mdl.set_position(port1, port_dict[f"{phase}1"]["position"])
        mdl.set_port_properties(port1, terminal_position=port_dict[f"{phase}1"]["terminal_position"])

        port2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
        if phase in ["B", "C"]:
            if not port2:
                port2 = mdl.create_port(name=f"{phase}2",
                                        kind="pe",
                                        parent=comp_handle,
                                        terminal_position=port_dict[f"{phase}2"]["terminal_position"],
                                        rotation="down",
                                        position=port_dict[f"{phase}2"]["position"],
                                        hide_name=True
                                        )
                created_ports.update({f"{phase}2": port2})
            else:
                mdl.set_position(port2, port_dict[f"{phase}2"]["position"])
        mdl.set_port_properties(port2, terminal_position=port_dict[f"{phase}2"]["terminal_position"])

    for phase in unused_phase_list:
        port1 = mdl.get_item(f"{phase}1", parent=comp_handle, item_type="port")
        port2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
        if port1:
            deleted_ports.append(mdl.get_name(port1))
            mdl.delete_item(port1)
        if port2:
            deleted_ports.append(mdl.get_name(port2))
            mdl.delete_item(port2)

    return created_ports, deleted_ports


def change_number_phases_switch(mdl, container_handle):
    comp_handle = mdl.get_sub_level_handle(container_handle)
    phases_num = mdl.get_property_disp_value(mdl.prop(container_handle, "phases"))

    switch_dict = {"3": {"type_name": "Triple Pole Single Throw Contactor",
                         "position": (7736, 7952)},
                   "2": {"type_name": "Double Pole Single Throw Contactor",
                         "position": (7736, 7952)},
                   "1": {"type_name": "Single Pole Single Throw Contactor",
                         "position": (7736, 7856)}}

    switch = mdl.get_item("S", parent=comp_handle, item_type="component")
    if mdl.get_component_type_name(switch) != switch_dict[phases_num]["type_name"]:
        mdl.delete_item(switch)
        switch = mdl.create_component(switch_dict[phases_num]["type_name"],
                                      parent=comp_handle,
                                      name="S",
                                      position=switch_dict[phases_num]["position"])
        mdl.set_property_value(mdl.prop(switch, "ctrl_src"), "Model")
        mdl.set_property_value(mdl.prop(switch, "initial_state"), "on")

        ctrl_port = mdl.get_item("ctrl", parent=comp_handle, item_type="port")
        mdl.create_connection(ctrl_port, mdl.term(switch, "ctrl_in"))

        fb_port = mdl.get_item("fb", parent=comp_handle, item_type="port")
        if fb_port:
            mdl.set_property_value(mdl.prop(switch, "enable_fb_out"), True)
            mdl.create_connection(mdl.term(switch, "feedback_out"), fb_port)


def change_number_phases_conn(mdl, container_handle):
    comp_handle = mdl.get_sub_level_handle(container_handle)
    phases_num = mdl.get_property_disp_value(mdl.prop(container_handle, "phases"))
    phase_num = int(phases_num)

    phase_list = ["A", "B", "C"]
    used_phase_list = phase_list[0:phase_num]

    switch = mdl.get_item("S", parent=comp_handle, item_type="component")

    for phase in used_phase_list:
        port1 = mdl.get_item(f"{phase}1", parent=comp_handle, item_type="port")
        port2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
        if len(mdl.find_connections(port1, mdl.term(switch, f"{phase.lower()}_in"))) == 0:
            mdl.create_connection(port1, mdl.term(switch, f"{phase.lower()}_in"))
        if len(mdl.find_connections(mdl.term(switch, f"{phase.lower()}_out"), port2)) == 0:
            mdl.create_connection(mdl.term(switch, f"{phase.lower()}_out"), port2)

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
        change_number_phases_switch(mdl, mask_handle)
        port_dynamics(mdl, mask_handle)
        sld_port_transition(mdl, mask_handle)
        change_number_phases_conn(mdl, mask_handle)

    if calling_prop_name not in ["sld_mode", "init_code"]:

        if old_state:
            current_state = old_state[comp_handle]
        else:
            current_state = new_prop_values

        sld_bus_count = 2

        for sld_idx in range(sld_bus_count):
            sld_name = "SLD" + str(sld_idx+1)
            currently_sld = mdl.get_item(sld_name, parent=comp_handle, item_type="port")
            if currently_sld:
                # The terminal related to the current property hasn't been created yet
                sld_number = {}
                importlib.reload(util)
                phases = current_state.get("phases")
                sld_1ph_pick = current_state.get("sld_1ph_pick")
                sld_2ph_pick = current_state.get("sld_2ph_pick")

                multi_port_list = []
                terminal_positions = {}
                sld_term_position = (0, 0)

                if sld_idx == 0:
                    sld_side = "left"
                    port_x = -32
                else:
                    sld_side = "right"
                    port_x = 32
                if phases == "3":
                    multi_port_list = ["A" + str(sld_idx + 1), "B" + str(sld_idx + 1), "C" + str(sld_idx + 1)]
                    terminal_positions = {
                        "A" + str(sld_idx + 1): (port_x, -32),
                        "B" + str(sld_idx + 1): (port_x, 0),
                        "C" + str(sld_idx + 1): (port_x, 32),
                    }
                    sld_term_position = (port_x, 0)
                elif phases == "2":
                    terminal_positions = {
                        "A" + str(sld_idx + 1): (port_x, -16),
                        "B" + str(sld_idx + 1): (port_x, 16),
                    }
                    sld_term_position = (port_x, 0)
                    if sld_2ph_pick == "A and B":
                        multi_port_list = ["A" + str(sld_idx + 1), "B" + str(sld_idx + 1)]
                    elif sld_2ph_pick == "B and C":
                        multi_port_list = [None, "A" + str(sld_idx + 1), "B" + str(sld_idx + 1)]
                    elif sld_2ph_pick == "A and C":
                        multi_port_list = ["A" + str(sld_idx + 1), None, "B" + str(sld_idx + 1)]
                elif phases == "1":
                    terminal_positions = {
                        "A" + str(sld_idx + 1): (port_x, 0),
                    }
                    sld_term_position = (port_x, 0)
                    if sld_1ph_pick == "A":
                        multi_port_list = ["A" + str(sld_idx + 1)]
                    elif sld_1ph_pick == "B":
                        multi_port_list = [None, "A" + str(sld_idx + 1)]
                    elif sld_1ph_pick == "C":
                        multi_port_list = [None, None, "A" + str(sld_idx + 1)]

                sld_number["port_names"] = multi_port_list
                sld_number["side"] = sld_side
                sld_number["multi_term_pos"] = terminal_positions
                sld_number["sld_term_pos"] = sld_term_position

                sld_info = get_sld_conversion_info(mdl, mask_handle, sld_name,
                                                   sld_number.get("port_names"),
                                                   sld_number.get("side"),
                                                   sld_number.get("multi_term_pos"),
                                                   sld_number.get("sld_term_pos")
                                                   )

                util.convert_to_multiline(mdl, mask_handle, sld_info)

        define_icon(mdl, mask_handle)
        change_number_phases_switch(mdl, mask_handle)
        port_dynamics(mdl, mask_handle)
        sld_port_transition(mdl, mask_handle)
        change_number_phases_conn(mdl, mask_handle)
        old_state[comp_handle] = current_values

    good_for_sld = []
    for prop_name in new_prop_values:
        if prop_name in ["phases", "sld_1ph_pick", "sld_2ph_pick"]:
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
            phases = new_prop_values.get("phases")
            sld_1ph_pick = new_prop_values.get("sld_1ph_pick")
            sld_2ph_pick = new_prop_values.get("sld_2ph_pick")

            multi_port_list = []
            terminal_positions = {}
            sld_term_position = (0, 0)

            if sld_idx == 0:
                sld_side = "left"
                port_x = -32
            else:
                sld_side = "right"
                port_x = 32
            if phases == "3":
                multi_port_list = ["A" + str(sld_idx + 1), "B" + str(sld_idx + 1), "C" + str(sld_idx + 1)]
                terminal_positions = {
                    "A" + str(sld_idx + 1): (port_x, -32),
                    "B" + str(sld_idx + 1): (port_x, 0),
                    "C" + str(sld_idx + 1): (port_x, 32),
                }
                sld_term_position = (port_x, 0)
            elif phases == "2":
                terminal_positions = {
                    "A" + str(sld_idx + 1): (port_x, -16),
                    "B" + str(sld_idx + 1): (port_x, 16),
                }
                sld_term_position = (port_x, 0)
                if sld_2ph_pick == "A and B":
                    multi_port_list = ["A" + str(sld_idx + 1), "B" + str(sld_idx + 1)]
                elif sld_2ph_pick == "B and C":
                    multi_port_list = [None, "A" + str(sld_idx + 1), "B" + str(sld_idx + 1)]
                elif sld_2ph_pick == "A and C":
                    multi_port_list = ["A" + str(sld_idx + 1), None, "B" + str(sld_idx + 1)]
            elif phases == "1":
                terminal_positions = {
                    "A" + str(sld_idx + 1): (port_x, 0),
                }
                sld_term_position = (port_x, 0)
                if sld_1ph_pick == "A":
                    multi_port_list = ["A" + str(sld_idx + 1)]
                elif sld_1ph_pick == "B":
                    multi_port_list = [None, "A" + str(sld_idx + 1)]
                elif sld_1ph_pick == "C":
                    multi_port_list = [None, None, "A" + str(sld_idx + 1)]

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
            sld_port_transition(mdl, mask_handle)
            for sld_idx in range(sld_bus_count):
                util.convert_to_sld(mdl, mask_handle, sld_info[sld_idx])
        else:
            sld_port_transition(mdl, mask_handle)
            for sld_idx in range(sld_bus_count):
                sld_name = "SLD" + str(sld_idx + 1)
                currently_sld = mdl.get_item(sld_name, parent=comp_handle, item_type="port")
                if currently_sld:
                    util.convert_to_multiline(mdl, mask_handle, sld_info[sld_idx])

    sld_post_processing(mdl, mask_handle)


def sld_post_processing(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Resize the buses to 4

    for bus_name in ["SLD1_bus", "SLD2_bus"]:
        bus = mdl.get_item(bus_name, parent=comp_handle)
        if bus:
            bus_size_prop = mdl.prop(bus, "bus_size")
            mdl.set_property_value(bus_size_prop, 4)

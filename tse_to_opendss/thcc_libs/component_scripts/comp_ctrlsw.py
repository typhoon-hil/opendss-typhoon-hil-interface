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
        mdl.set_port_properties(c2, terminal_position=(32, 36))

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


def change_number_phases_switch(mdl, container_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(container_handle)

    switch_dict = {"3": {"type_name": "Triple Pole Single Throw Contactor",
                         "position": (7736, 7952)},
                   "2": {"type_name": "Double Pole Single Throw Contactor",
                         "position": (7736, 7952)},
                   "1": {"type_name": "Single Pole Single Throw Contactor",
                         "position": (7736, 7856)}}

    switch = mdl.get_item("S", parent=comp_handle, item_type="component")
    if mdl.get_component_type_name(switch) != switch_dict[new_value]["type_name"]:
        mdl.delete_item(switch)
        switch = mdl.create_component(switch_dict[new_value]["type_name"],
                                      parent=comp_handle,
                                      name="S",
                                      position=switch_dict[new_value]["position"])
        mdl.set_property_value(mdl.prop(switch, "ctrl_src"), "Model")
        mdl.set_property_value(mdl.prop(switch, "initial_state"), "on")

        ctrl_port = mdl.get_item("ctrl", parent=comp_handle, item_type="port")
        mdl.create_connection(ctrl_port, mdl.term(switch, "ctrl_in"))

        fb_port = mdl.get_item("fb", parent=comp_handle, item_type="port")
        if fb_port:
            mdl.set_property_value(mdl.prop(switch, "enable_fb_out"), True)
            mdl.create_connection(mdl.term(switch, "feedback_out"), fb_port)


def change_number_phases_conn(mdl, container_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(container_handle)
    phase_num = int(new_value)

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

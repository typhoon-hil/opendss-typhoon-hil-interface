def circuit_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:

    """
    # Property Registration
    conf_prop = mdl.prop(container_handle, "conf")
    type_prop = mdl.prop(container_handle, "type_prop")
    i_rms_meas_prop = mdl.prop(container_handle, "i_rms_meas")
    i_inst_meas_prop = mdl.prop(container_handle, "i_inst_meas")
    v_line_rms_meas_prop = mdl.prop(container_handle, "v_line_rms_meas")
    v_line_inst_meas_prop = mdl.prop(container_handle, "v_line_inst_meas")
    v_phase_rms_meas_prop = mdl.prop(container_handle, "v_phase_rms_meas")
    v_phase_inst_meas_prop = mdl.prop(container_handle, "v_phase_inst_meas")
    freq_meas_prop = mdl.prop(container_handle, "freq_meas")
    power_meas_prop = mdl.prop(container_handle, "power_meas")
    enable_output_prop = mdl.prop(container_handle, "enable_output")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "conf" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == conf_prop:
        comp_handle = mdl.get_parent(container_handle)

        comp_type = mdl.get_property_disp_value(type_prop)

        terminal_handlers = {"A": {"+": None, "-": None},
                             "B": {"+": None, "-": None},
                             "C": {"+": None, "-": None},
                             "N": {"+": None, "-": None}}
        meter_pos = {"A": (7672, 7856),
                     "B": (7672, 7952),
                     "C": (7672, 8048),
                     "N": (7672, 8144),
                     "ABC": (7672, 7952)}

        port_attributes = get_port_const_attributes(comp_type)

        if new_value == "on both sides":

            if "ABC" in comp_type:
                for phase in "ABC":
                    meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle, item_type="component")
                    if meter_1ph:
                        mdl.delete_item(meter_1ph)

                # Three-phase meter should be used instead of 3x1ph meter
                meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle, item_type="component")
                if not meter_3ph:
                    meter_3ph = mdl.create_component("core/Three-phase Meter",
                                                     name="meter_3ph",
                                                     parent=comp_handle,
                                                     position=meter_pos["ABC"])
                mdl.set_property_value(mdl.prop(meter_3ph, "enable_out"),
                                       mdl.get_property_value(enable_output_prop))
                tag_3ph = mdl.get_item("tag_3ph", parent=comp_handle, item_type="tag")
                if not tag_3ph:
                    tag_3ph = mdl.create_tag("ground",
                                             name="tag_3ph",
                                             parent=comp_handle,
                                             scope="local",
                                             kind="pe",
                                             rotation="down",
                                             position=(meter_pos["ABC"][0] + 48,
                                                       meter_pos["ABC"][1] + 160))
                    mdl.hide_name(tag_3ph)

                if len(mdl.find_connections(mdl.term(meter_3ph, "GND"), tag_3ph)) == 0:
                    mdl.create_connection(mdl.term(meter_3ph, "GND"), tag_3ph)

                for phase in "ABC":
                    terminal_handlers[phase]["+"] = mdl.term(meter_3ph, f"{phase}+")
                    terminal_handlers[phase]["-"] = mdl.term(meter_3ph, f"{phase}-")
                if "N" in comp_type:
                    meter_1ph = mdl.get_item("meter_N", parent=comp_handle, item_type="component")
                    if not meter_1ph:
                        # replace the SC with single phase meter once it's available
                        meter_1ph = mdl.create_component("core/Short Circuit",
                                                         name="meter_N",
                                                         parent=comp_handle,
                                                         position=meter_pos["N"])
                    # update terminal handler calling to 1ph meter, once available
                    terminal_handlers["N"]["+"] = mdl.term(meter_1ph, "p_node")
                    terminal_handlers["N"]["-"] = mdl.term(meter_1ph, "n_node")
                else:
                    meter_1ph = mdl.get_item("meter_N", parent=comp_handle, item_type="component")
                    if meter_1ph:
                        mdl.delete_item(meter_1ph)

            else:
                meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle, item_type="component")
                if meter_3ph:
                    mdl.delete_item(meter_3ph)
                tag_3ph = mdl.get_item("tag_3ph", parent=comp_handle, item_type="tag")
                if tag_3ph:
                    mdl.delete_item(tag_3ph)
                for phase in "ABCN":
                    if phase not in comp_type:
                        meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle, item_type="component")
                        if meter_1ph:
                            mdl.delete_item(meter_1ph)

                for phase in comp_type:
                    meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle, item_type="component")
                    if not meter_1ph:
                        # replace the SC with single phase meter once it's available
                        meter_1ph = mdl.create_component("core/Short Circuit",
                                                         name=f"meter_{phase}",
                                                         parent=comp_handle,
                                                         position=meter_pos[phase])
                    # update terminal handler calling to 1ph meter, once available
                    terminal_handlers[phase]["+"] = mdl.term(meter_1ph, "p_node")
                    terminal_handlers[phase]["-"] = mdl.term(meter_1ph, "n_node")

            # create the remaining ports and connections
            for phase in "ABCN":
                if phase in comp_type:
                    port_2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
                    if not port_2:
                        port_2 = mdl.create_port(name=f"{phase}2",
                                                 parent=comp_handle,
                                                 kind="pe",
                                                 direction="in",
                                                 flip="flip_horizontal",
                                                 position=port_attributes[f"{phase}2"]["pos"],
                                                 terminal_position=port_attributes[f"{phase}2"]["term_pos"])
                    else:
                        mdl.set_port_properties(port_2, terminal_position=port_attributes[f"{phase}2"]["term_pos"])
                    jun = mdl.get_item(f"jun_{phase}", parent=comp_handle, item_type="junction")
                    conn_term_list = [(jun, terminal_handlers[phase]["+"]),
                                      (terminal_handlers[phase]["-"], port_2)]
                    for conn_term in conn_term_list:
                        if len(mdl.find_connections(conn_term[0], conn_term[1])) == 0:
                            mdl.create_connection(conn_term[0], conn_term[1])
                else:
                    port_2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
                    if port_2:
                        mdl.delete_item(port_2)
        else:
            for phase in "ABCN":
                port_2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
                if port_2:
                    mdl.delete_item(port_2)
                meter_1ph = mdl.get_item("meter_N", parent=comp_handle, item_type="component")
                if meter_1ph:
                    mdl.delete_item(meter_1ph)

            meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle, item_type="component")
            if meter_3ph:
                mdl.delete_item(meter_3ph)
            tag_3ph = mdl.get_item("tag_3ph", parent=comp_handle, item_type="tag")
            if tag_3ph:
                mdl.delete_item(tag_3ph)
        # Updating the icon (not mandatory)
        mdl.refresh_icon(container_handle)
        # Measurements Check (mandatory)
        check_measurements(mdl, container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "type_prop" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == type_prop:
        comp_handle = mdl.get_parent(container_handle)

        terminal_handlers = {"A": {"+": None, "-": None},
                             "B": {"+": None, "-": None},
                             "C": {"+": None, "-": None},
                             "N": {"+": None, "-": None}}
        meter_pos = {"A": (7672, 7856),
                     "B": (7672, 7952),
                     "C": (7672, 8048),
                     "N": (7672, 8144),
                     "ABC": (7672, 7952)}

        port_attributes = get_port_const_attributes(new_value)

        conf = mdl.get_property_disp_value(conf_prop)
        if conf == "on both sides":
            # only when both sides are connected the measurements are applied
            if "ABC" in new_value:
                for phase in "ABC":
                    meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle, item_type="component")
                    if meter_1ph:
                        mdl.delete_item(meter_1ph)

                # Three-phase meter should be used instead of 3x1ph meter
                meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle, item_type="component")
                if not meter_3ph:
                    meter_3ph = mdl.create_component("core/Three-phase Meter",
                                                     name="meter_3ph",
                                                     parent=comp_handle,
                                                     position=meter_pos["ABC"])
                mdl.set_property_value(mdl.prop(meter_3ph, "enable_out"),
                                       mdl.get_property_value(enable_output_prop))
                tag_3ph = mdl.get_item("tag_3ph", parent=comp_handle, item_type="tag")
                if not tag_3ph:
                    tag_3ph = mdl.create_tag("ground",
                                             name="tag_3ph",
                                             parent=comp_handle,
                                             scope="local",
                                             kind="pe",
                                             rotation="down",
                                             position=(meter_pos["ABC"][0] + 48,
                                                       meter_pos["ABC"][1] + 160))
                    mdl.hide_name(tag_3ph)

                if len(mdl.find_connections(mdl.term(meter_3ph, "GND"), tag_3ph)) == 0:
                    mdl.create_connection(mdl.term(meter_3ph, "GND"), tag_3ph)

                for phase in "ABC":
                    terminal_handlers[phase]["+"] = mdl.term(meter_3ph, f"{phase}+")
                    terminal_handlers[phase]["-"] = mdl.term(meter_3ph, f"{phase}-")
                if "N" in new_value:
                    meter_1ph = mdl.get_item("meter_N", parent=comp_handle, item_type="component")
                    if not meter_1ph:
                        # replace the SC with single phase meter once it's available
                        meter_1ph = mdl.create_component("core/Short Circuit",
                                                         name="meter_N",
                                                         parent=comp_handle,
                                                         position=meter_pos["N"])
                    # update terminal handler calling to 1ph meter, once available
                    terminal_handlers["N"]["+"] = mdl.term(meter_1ph, "p_node")
                    terminal_handlers["N"]["-"] = mdl.term(meter_1ph, "n_node")
                else:
                    meter_1ph = mdl.get_item("meter_N", parent=comp_handle, item_type="component")
                    if meter_1ph:
                        mdl.delete_item(meter_1ph)

            else:
                meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle, item_type="component")
                if meter_3ph:
                    mdl.delete_item(meter_3ph)
                tag_3ph = mdl.get_item("tag_3ph", parent=comp_handle, item_type="tag")
                if tag_3ph:
                    mdl.delete_item(tag_3ph)
                for phase in "ABCN":
                    if phase not in new_value:
                        meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle, item_type="component")
                        if meter_1ph:
                            mdl.delete_item(meter_1ph)

                for phase in new_value:
                    meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle, item_type="component")
                    if not meter_1ph:
                        # replace the SC with single phase meter once it's available
                        meter_1ph = mdl.create_component("core/Short Circuit",
                                                         name=f"meter_{phase}",
                                                         parent=comp_handle,
                                                         position=meter_pos[phase])
                    # update terminal handler calling to 1ph meter, once available
                    terminal_handlers[phase]["+"] = mdl.term(meter_1ph, "p_node")
                    terminal_handlers[phase]["-"] = mdl.term(meter_1ph, "n_node")

        for phase in "ABCN":
            if phase in new_value:
                # create the items that should always exist as long as the given phase is selected
                port_1 = mdl.get_item(f"{phase}1", parent=comp_handle, item_type="port")
                if not port_1:
                    port_1 = mdl.create_port(name=f"{phase}1",
                                             parent=comp_handle,
                                             kind="pe",
                                             direction="in",
                                             position=port_attributes[f"{phase}1"]["pos"],
                                             terminal_position=port_attributes[f"{phase}1"]["term_pos"])
                else:
                    mdl.set_port_properties(port_1, terminal_position=port_attributes[f"{phase}1"]["term_pos"])

                jun = mdl.get_item(f"jun_{phase}", parent=comp_handle, item_type="junction")
                if not jun:
                    jun = mdl.create_junction(name=f"jun_{phase}",
                                              parent=comp_handle,
                                              kind="pe",
                                              position=(port_attributes[f"{phase}1"]["pos"][0] + 160,
                                                        port_attributes[f"{phase}1"]["pos"][1]))

                oc_ph = mdl.get_item(f"OC{phase}", parent=comp_handle, item_type="component")
                if not oc_ph:
                    oc_ph = mdl.create_component("core/Open Circuit",
                                                 name=f"OC{phase}",
                                                 parent=comp_handle,
                                                 hide_name=True,
                                                 position=(port_attributes[f"{phase}1"]["pos"][0] + 112,
                                                           port_attributes[f"{phase}1"]["pos"][1] + 48))

                tag_ph = mdl.get_item(f"tag_ph_{phase}", parent=comp_handle, item_type="tag")
                if not tag_ph:
                    tag_ph = mdl.create_tag("ground",
                                            name=f"tag_ph_{phase}",
                                            parent=comp_handle,
                                            scope="local",
                                            kind="pe",
                                            position=(port_attributes[f"{phase}1"]["pos"][0] + 16,
                                                      port_attributes[f"{phase}1"]["pos"][1] + 48))
                    mdl.hide_name(tag_ph)

                conn_term_list = [(port_1, jun),
                                  (jun, mdl.term(oc_ph, "n_node")),
                                  (mdl.term(oc_ph, "p_node"), tag_ph)]
                for conn_term in conn_term_list:
                    if len(mdl.find_connections(conn_term[0], conn_term[1])) == 0:
                        mdl.create_connection(conn_term[0], conn_term[1])
            else:
                port_1 = mdl.get_item(f"{phase}1", parent=comp_handle, item_type="port")
                if port_1:
                    mdl.delete_item(port_1)
                jun = mdl.get_item(f"jun_{phase}", parent=comp_handle, item_type="junction")
                if jun:
                    mdl.delete_item(jun)
                oc_ph = mdl.get_item(f"OC{phase}", parent=comp_handle, item_type="component")
                if oc_ph:
                    mdl.delete_item(oc_ph)
                tag_ph = mdl.get_item(f"tag_ph_{phase}", parent=comp_handle, item_type="tag")
                if tag_ph:
                    mdl.delete_item(tag_ph)

        if conf == "on both sides":
            # create the remaining ports and connections
            for phase in "ABCN":
                if phase in new_value:
                    port_2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
                    if not port_2:
                        port_2 = mdl.create_port(name=f"{phase}2",
                                                 parent=comp_handle,
                                                 kind="pe",
                                                 direction="in",
                                                 flip="flip_horizontal",
                                                 position=port_attributes[f"{phase}2"]["pos"],
                                                 terminal_position=port_attributes[f"{phase}2"]["term_pos"])
                    else:
                        mdl.set_port_properties(port_2, terminal_position=port_attributes[f"{phase}2"]["term_pos"])
                    jun = mdl.get_item(f"jun_{phase}", parent=comp_handle, item_type="junction")
                    conn_term_list = [(jun, terminal_handlers[phase]["+"]),
                                      (terminal_handlers[phase]["-"], port_2)]
                    for conn_term in conn_term_list:
                        if len(mdl.find_connections(conn_term[0], conn_term[1])) == 0:
                            mdl.create_connection(conn_term[0], conn_term[1])
                else:
                    port_2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
                    if port_2:
                        mdl.delete_item(port_2)

        # Updating the icon
        mdl.refresh_icon(container_handle)
        # Measurements Check
        check_measurements(mdl, container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "Measurements" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle in [i_rms_meas_prop, i_inst_meas_prop, v_line_rms_meas_prop, v_line_inst_meas_prop,
                              v_phase_rms_meas_prop, v_phase_inst_meas_prop, freq_meas_prop, power_meas_prop]:

        check_measurements(mdl, container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "enable_output_prop" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == enable_output_prop:

        comp_handle = mdl.get_parent(container_handle)
        comp_type = mdl.get_property_disp_value(type_prop)
        port_attributes = get_port_const_attributes(comp_type)
        meas_handle = mdl.get_item("meter_3ph", parent=comp_handle)
        if meas_handle:
            mdl.set_property_value(mdl.prop(meas_handle, "enable_out"), new_value)
        if new_value:
            new_port = mdl.create_port(name="OUT",
                                       parent=comp_handle,
                                       position=port_attributes["OUT"]["pos"],
                                       kind="sp",
                                       direction="out",
                                       terminal_position=port_attributes["OUT"]["term_pos"],
                                       rotation="left",
                                       hide_name=True)
            mdl.create_connection(mdl.term(meas_handle, "Out"), new_port)

        else:
            new_port = mdl.get_item("OUT", parent=comp_handle, item_type="port")
            if new_port:
                mdl.delete_item(new_port)


def mask_dialog_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """
    # Property Registration
    conf_prop = mdl.prop(container_handle, "conf")
    type_prop = mdl.prop(container_handle, "type_prop")
    i_rms_meas_prop = mdl.prop(container_handle, "i_rms_meas")
    i_inst_meas_prop = mdl.prop(container_handle, "i_inst_meas")
    v_line_rms_meas_prop = mdl.prop(container_handle, "v_line_rms_meas")
    v_line_inst_meas_prop = mdl.prop(container_handle, "v_line_inst_meas")
    v_phase_rms_meas_prop = mdl.prop(container_handle, "v_phase_rms_meas")
    v_phase_inst_meas_prop = mdl.prop(container_handle, "v_phase_inst_meas")
    freq_meas_prop = mdl.prop(container_handle, "freq_meas")
    power_meas_prop = mdl.prop(container_handle, "power_meas")
    enable_output_prop = mdl.prop(container_handle, "enable_output")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_disp_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "conf" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == conf_prop:
        comp_type = mdl.get_property_disp_value(type_prop)

        prop_list = [i_rms_meas_prop, i_inst_meas_prop, v_line_rms_meas_prop, v_line_inst_meas_prop,
                     v_phase_rms_meas_prop, v_phase_inst_meas_prop, freq_meas_prop, power_meas_prop,
                     enable_output_prop]
        if "ABC" in comp_type and new_value == "on both sides":
            [mdl.show_property(prop) for prop in prop_list]
        else:
            [mdl.hide_property(prop) for prop in prop_list]

    # ------------------------------------------------------------------------------------------------------------------
    #  "type" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == type_prop:

        pass

    # ------------------------------------------------------------------------------------------------------------------
    #  "i_rms_meas_prop" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == i_rms_meas_prop:

        if new_value:
            mdl.set_property_disp_value(i_inst_meas_prop, True)
            if init:
                mdl.set_property_value(i_inst_meas_prop, True)
            mdl.disable_property(i_inst_meas_prop)
        else:
            mdl.enable_property(i_inst_meas_prop)

    # ------------------------------------------------------------------------------------------------------------------
    #  "v_line_rms_meas_prop" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == v_line_rms_meas_prop:

        if new_value:
            mdl.set_property_disp_value(v_line_inst_meas_prop, True)
            if init:
                mdl.set_property_value(v_line_inst_meas_prop, True)
            mdl.disable_property(v_line_inst_meas_prop)
        else:
            mdl.enable_property(v_line_inst_meas_prop)

    # ------------------------------------------------------------------------------------------------------------------
    #  "v_phase_rms_meas_prop" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == v_phase_rms_meas_prop:

        if new_value:
            mdl.set_property_disp_value(v_phase_inst_meas_prop, True)
            if init:
                mdl.set_property_value(v_phase_inst_meas_prop, True)
            mdl.disable_property(v_phase_inst_meas_prop)
        else:
            mdl.enable_property(v_phase_inst_meas_prop)

    # ------------------------------------------------------------------------------------------------------------------
    #  "freq_meas_prop" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == freq_meas_prop:

        if new_value:
            mdl.set_property_disp_value(v_phase_inst_meas_prop, True)
            if init:
                mdl.set_property_value(v_phase_inst_meas_prop, True)
            mdl.disable_property(v_phase_inst_meas_prop)
        else:
            mdl.enable_property(v_phase_inst_meas_prop)

    # ------------------------------------------------------------------------------------------------------------------
    #  "power_meas_prop" properties code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == power_meas_prop:

        if new_value:
            [mdl.set_property_disp_value(prop, True)
             for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop, v_phase_inst_meas_prop,
                          freq_meas_prop]]
            if init:
                [mdl.set_property_value(prop, True)
                 for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop, v_phase_inst_meas_prop,
                              freq_meas_prop]]
            [mdl.disable_property(prop)
             for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop, v_phase_inst_meas_prop,
                          freq_meas_prop]]
        else:
            [mdl.enable_property(prop)
             for prop in [i_rms_meas_prop, v_phase_rms_meas_prop, freq_meas_prop]]


def define_icon(mdl, container_handle):
    """
    Defines the component icon based on its type

    :param mdl: Schematic API
    :param container_handle: Component Handle
    :return: no return
    """

    comp_type = mdl.get_property_value(mdl.prop(container_handle, "type_prop"))
    comp_handle = mdl.get_parent(container_handle)
    mask_handle = mdl.get_mask(comp_handle)
    mdl.set_component_icon_image(mask_handle, f"images/bus_{len(comp_type)}ph.svg")


def get_port_const_attributes(comp_type):
    """

    """
    term_positions = [(0, 0)] * 8
    list_index = {"A": 0,
                  "B": 2,
                  "C": 4,
                  "N": 6}

    if len(comp_type) == 4:
        offset_position = [-48, -16, 16, 48]
    elif len(comp_type) == 3:
        offset_position = [-32, 0, 32]
    elif len(comp_type) == 2:
        offset_position = [-16, 16]
    else:
        offset_position = [0]

    for phase, pos in zip(comp_type, offset_position):
        term_positions[list_index[phase]] = (-8, pos)
        term_positions[list_index[phase] + 1] = (8, pos)

    port_dict = {"A1": {"pos": (7400, 7856), "term_pos": term_positions[0]},
                 "A2": {"pos": (7792, 7856), "term_pos": term_positions[1]},
                 "B1": {"pos": (7400, 7952), "term_pos": term_positions[2]},
                 "B2": {"pos": (7792, 7952), "term_pos": term_positions[3]},
                 "C1": {"pos": (7400, 8048), "term_pos": term_positions[4]},
                 "C2": {"pos": (7792, 8048), "term_pos": term_positions[5]},
                 "N1": {"pos": (7400, 8144), "term_pos": term_positions[6]},
                 "N2": {"pos": (7792, 8144), "term_pos": term_positions[7]},
                 "OUT": {"pos": (7672, 7760), "term_pos": [0, -16*len(comp_type)]}}

    return port_dict


def check_measurements(mdl, container_handle):
    """

    """
    comp_handle = mdl.get_parent(container_handle)
    type_prop = mdl.get_property_disp_value(mdl.prop(container_handle, "type_prop"))
    conf = mdl.get_property_disp_value(mdl.prop(container_handle, "conf"))

    # Only supporting three-phase meter at this moment
    if "ABC" in type_prop and conf == "on both sides":
        # Meter vars
        meter_handle = mdl.get_item("meter_3ph", parent=comp_handle)
        meter_props_dict = {"v_phase_inst_meas": ["VAn", "VBn", "VCn"],  # "VN" Neutral Voltage not used for now
                            "v_line_inst_meas": ["VAB", "VBC", "VCA"],
                            "i_inst_meas": ["IA", "IB", "IC"],  # "IN" Neutral Current not used for now
                            "freq_meas": ["freq"],
                            "v_phase_rms_meas": ["VLn_rms", "VLn_avg_rms"],  # "VN_rms" Neutral Voltage not used for now
                            "v_line_rms_meas": ["VLL_rms", "VLL_avg_rms"],
                            "i_rms_meas": ["I_rms", "I_avg_rms"],  # "IN_rms" Neutral Voltage not used for now
                            "power_meas": ["P_meas"]}
        # Component Props
        comp_type = mdl.get_property_disp_value(mdl.prop(container_handle, "type_prop"))
        enabled_phase = [phase in comp_type for phase in ["A", "B", "C"]]
        comp_conf = mdl.get_property_disp_value(mdl.prop(container_handle, "conf"))

        # Enable/Disable the assigned properties
        # per phase props
        for cnt, action in enumerate(enabled_phase):
            i_inst = mdl.get_property_disp_value(mdl.prop(container_handle, "i_inst_meas"))
            mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["i_inst_meas"][cnt]), action and i_inst)

            v_line = mdl.get_property_disp_value(mdl.prop(container_handle, "v_line_inst_meas"))
            mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_line_inst_meas"][cnt]), action and v_line)

            v_phase = mdl.get_property_disp_value(mdl.prop(container_handle, "v_phase_inst_meas"))
            mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_phase_inst_meas"][cnt]),
                                   action and v_phase)

        # Three-Phase props (There are some miss measurements depending on comp_type)
        # Edit Handlers of the Meter is not called from external components (just GUI)
        i_rms_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "i_rms_meas"))
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["i_rms_meas"][0]), i_rms_meas)
        if i_rms_meas:
            [mdl.set_property_value(mdl.prop(meter_handle, prop), True) for prop in meter_props_dict["i_inst_meas"]]

        v_line_rms_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "v_line_rms_meas"))
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_line_rms_meas"][0]), v_line_rms_meas)
        if v_line_rms_meas:
            [mdl.set_property_value(mdl.prop(meter_handle, prop), True)
             for prop in meter_props_dict["v_line_inst_meas"]]

        v_phase_rms_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "v_phase_rms_meas"))
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["v_phase_rms_meas"][0]), v_phase_rms_meas)
        if v_phase_rms_meas:
            [mdl.set_property_value(mdl.prop(meter_handle, prop), True)
             for prop in meter_props_dict["v_phase_inst_meas"]]

        freq_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "freq_meas"))
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["freq_meas"][0]), freq_meas)

        power_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "power_meas"))
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["power_meas"][0]), power_meas)
        # RMS calculation needs all instantaneous measurements (and frequency/voltage)
        if i_rms_meas or v_line_rms_meas or v_phase_rms_meas or freq_meas or power_meas:
            mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["freq_meas"][0]), True)
            [mdl.set_property_value(mdl.prop(meter_handle, prop), True)
             for prop in meter_props_dict["v_phase_inst_meas"]]


def set_bus_phases(mdl, container_handle, caller_handle="value_changed"):
    phase_a = "A" if mdl.get_property_disp_value(mdl.prop(container_handle, "phase_a")) is True else ""
    phase_b = "B" if mdl.get_property_disp_value(mdl.prop(container_handle, "phase_b")) is True else ""
    phase_c = "C" if mdl.get_property_disp_value(mdl.prop(container_handle, "phase_c")) is True else ""
    phase_n = "N" if mdl.get_property_disp_value(mdl.prop(container_handle, "phase_n")) is True else ""
    conf = mdl.get_property_disp_value(mdl.prop(container_handle, "conf"))

    prop_list = ["i_rms_meas", "i_inst_meas", "v_line_rms_meas", "v_line_inst_meas",
                 "v_phase_rms_meas", "v_phase_inst_meas", "freq_meas", "power_meas",
                 "enable_output"]

    phases_used = phase_a + phase_b + phase_c + phase_n
    if phases_used == "":
        phases_used = "A"

    if caller_handle == "value_changed":
        mdl.set_property_value(mdl.prop(container_handle, "type_prop"), phases_used)
    else:
        mdl.set_property_disp_value(mdl.prop(container_handle, "type_prop"), phases_used)
        if "ABC" in phases_used and conf == "on both sides":
            [mdl.show_property(mdl.prop(container_handle, prop)) for prop in prop_list]

        else:
            [mdl.hide_property(mdl.prop(container_handle, prop)) for prop in prop_list]


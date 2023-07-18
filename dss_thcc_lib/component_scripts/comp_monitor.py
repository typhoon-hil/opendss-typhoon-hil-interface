def pos_offset(pos):
    """
    Offset position from center of the schematic
    """
    x0, y0 = 8192, 8192

    pos_x, pos_y = pos

    return x0 + pos_x, y0 + pos_y


def circuit_dynamics(mdl, mask_handle, new_values=None):
    comp_handle = mdl.get_parent(mask_handle)

    # When loading a model
    if not new_values:
        new_values = mdl.get_property_values(comp_handle)

    #
    # Phases checkbox properties
    #
    phase_a = new_values.get("phase_a") in ("True", True)
    phase_b = new_values.get("phase_b") in ("True", True)
    phase_c = new_values.get("phase_c") in ("True", True)

    #
    # Port altering properties
    #
    num_phases = sum((phase_a, phase_b, phase_c))

    #
    # Must select at least one phase
    #
    if num_phases == 0:
        phase_a = True
        mdl.set_property_value(mdl.prop(mask_handle, "phase_a"), True)
        num_phases = 1
        mdl.info(f"{mdl.get_name(comp_handle)}: "
                 f"At least one phase must be selected. Setting to A.")

    #
    # Update ports
    #
    all_port_names = dict()
    all_port_names[1] = [f"{phase}1" for phase in "ABC"]
    all_port_names[2] = [f"{phase}2" for phase in "ABC"]

    # Port positions
    port_positions = {
        "A1": pos_offset((-200, -200)),
        "B1": pos_offset((-200, 0)),
        "C1": pos_offset((-200, 200)),
        "A2": pos_offset((200, -200)),
        "B2": pos_offset((200, 0)),
        "C2": pos_offset((200, 200)),
    }

    # Meter positions
    meter_positions = {
        "ABC": pos_offset((0, 0)),
        "A": pos_offset((0, -200)),
        "B": pos_offset((0, 0)),
        "C": pos_offset((0, 200))
    }

    # Which ports should be added
    new_ports = {
        "A1": phase_a,
        "B1": phase_b,
        "C1": phase_c,
        "A2": phase_a,
        "B2": phase_b,
        "C2": phase_c,
    }

    for side, port_names in all_port_names.items():
        count_port = 0
        for port_name in all_port_names[side]:
            # Find existing port handle
            port = mdl.get_item(port_name, parent=comp_handle, item_type="port")
            # Boolean to determine port addition or removal
            included_port = new_ports.get(port_name)

            # Calculate terminal position
            image_size = 32 * num_phases
            term_x = -8 if side == 1 else 8
            term_y = 32 * count_port - (image_size / 2 - 16)
            term_pos = term_x, term_y

            if included_port:
                count_port += 1
                if not port:
                    # Add the port
                    mdl.create_port(name=port_name,
                                    parent=comp_handle,
                                    flip="flip_horizontal" if side == 2 else None,
                                    position=port_positions[port_name],
                                    terminal_position=term_pos,
                                    )
                else:
                    # Move the terminal into the new position
                    mdl.set_port_properties(port, terminal_position=term_pos)
            else:
                if port:
                    # Remove port
                    mdl.delete_item(port)

    #
    # Three-phase case
    #
    if num_phases == 3:
        # Create measurement component
        tp_meas = mdl.create_component("core/Three-phase Meter",
                                       name="meter_ABC",
                                       parent=comp_handle,
                                       position=meter_positions["ABC"])

        # Create ground tag
        tag_3_ph = mdl.create_tag(
            "gnd",
            name="tag_ABC",
            parent=comp_handle,
            scope="local",
            kind="pe",
            position=(meter_positions["ABC"][0] - 40, meter_positions["ABC"][1] + 200)
        )

        # Create connections
        # A
        port_a1 = mdl.get_item("A1", parent=comp_handle, item_type="port")
        term_a_plus = mdl.term(tp_meas, "A+")
        mdl.create_connection(term_a_plus, port_a1)
        port_a2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
        term_a_minus = mdl.term(tp_meas, "A-")
        mdl.create_connection(term_a_minus, port_a2)
        # B
        port_b1 = mdl.get_item("B1", parent=comp_handle, item_type="port")
        term_b_plus = mdl.term(tp_meas, "B+")
        mdl.create_connection(term_b_plus, port_b1)
        port_b2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
        term_b_minus = mdl.term(tp_meas, "B-")
        mdl.create_connection(term_b_minus, port_b2)
        # C
        port_c1 = mdl.get_item("C1", parent=comp_handle, item_type="port")
        term_c_plus = mdl.term(tp_meas, "C+")
        mdl.create_connection(term_c_plus, port_c1)
        port_c2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
        term_c_minus = mdl.term(tp_meas, "C-")
        mdl.create_connection(term_c_minus, port_c2)
        # Tag
        port_gnd_meter = mdl.term(tp_meas, "GND")
        mdl.create_connection(port_gnd_meter, tag_3_ph)

        # Create output port if needed

    #
    # Single or two phase case
    #
    else:
        pass


# def circuit_dynamicss(mdl, comp_handle, new_values):
#
#     # Port altering properties
#     conf_prop = mdl.prop(comp_handle, "conf")
#     type_prop = mdl.prop(comp_handle, "type_prop")
#
#     # Measurement properties
#     i_rms_meas_prop = mdl.prop(comp_handle, "i_rms_meas")
#     i_inst_meas_prop = mdl.prop(comp_handle, "i_inst_meas")
#     v_line_rms_meas_prop = mdl.prop(comp_handle, "v_line_rms_meas")
#     v_line_inst_meas_prop = mdl.prop(comp_handle, "v_line_inst_meas")
#     v_phase_rms_meas_prop = mdl.prop(comp_handle, "v_phase_rms_meas")
#     v_phase_inst_meas_prop = mdl.prop(comp_handle, "v_phase_inst_meas")
#     freq_meas_prop = mdl.prop(comp_handle, "freq_meas")
#     power_meas_prop = mdl.prop(comp_handle, "power_meas")
#     enable_output_prop = mdl.prop(comp_handle, "enable_output")
#
#     #
#     # Measurement properties
#     #
#     i_inst = new_values.get("i_inst_meas") == "True"
#     v_line_inst = new_values.get("v_line_inst") == "True"
#     v_phase_inst = new_values.get("v_phase_inst") == "True"
#
#     #
#     # Phases checkbox properties
#     #
#     phase_a = new_values.get("phase_a") == "True"
#     phase_b = new_values.get("phase_b") == "True"
#     phase_c = new_values.get("phase_c") == "True"
#     phase_n = new_values.get("phase_n") == "True"
#
#     #
#     # Test if measurements should be added
#     #
#     add_measurements = any((i_inst, v_line_inst, v_phase_inst))
#     is_three_phase = all((phase_a, phase_b, phase_c))
#
#     meter_positions = {
#         "A": (7672, 7856),
#         "B": (7672, 7952),
#         "C": (7672, 8048),
#         "N": (7672, 8144),
#         "ABC": (7672, 7952)
#     }
#
#     sides_conf = new_values.get("conf")
#     if sides_conf == "on one side":
#
#
#     elif sides_conf == "on both sides":
#
#         # If three-phase, delete any existing single-phase meter
#         if is_three_phase:
#             for phase in "ABC":
#                 meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle,
#                                          item_type="component")
#                 if meter_1ph:
#                     mdl.delete_item(meter_1ph)
#         # If single-phase, delete any existing three-phase meter
#         else:
#             meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle,
#                                      item_type="component")
#             if meter_3ph:
#                 mdl.delete_item(meter_3ph)
#
#         # Add measurements if needed
#         if add_measurements:
#             if is_three_phase:
#             else:
#                 for phase in "ABC":
#                     meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle,
#                                              item_type="component")
#                     if not meter_1ph:
#                         mdl.delete_item(meter_1ph)
#
#         if not meter_1ph:
#             # replace the SC with single phase meter once it's available
#             meter_1ph = mdl.create_component("core/Short Circuit",
#                                              name=f"meter_{phase}",
#                                              parent=comp_handle,
#                                              position=meter_pos[phase])
#
#     # "conf" property code
#
#
#         comp_type = mdl.get_property_disp_value(type_prop)
#
#         terminal_handlers = {"A": {"+": None, "-": None},
#                              "B": {"+": None, "-": None},
#                              "C": {"+": None, "-": None},
#                              "N": {"+": None, "-": None}}
#         meter_pos = {"A": (7672, 7856),
#                      "B": (7672, 7952),
#                      "C": (7672, 8048),
#                      "N": (7672, 8144),
#                      "ABC": (7672, 7952)}
#
#         port_attributes = get_port_const_attributes(comp_type)
#
#         if new_value == "on both sides":
#
#             if "ABC" in comp_type:
#                 for phase in "ABC":
#                     meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle,
#                                              item_type="component")
#                     if meter_1ph:
#                         mdl.delete_item(meter_1ph)
#
#                 # Three-phase meter should be used instead of 3x1ph meter
#                 if any(
#                     (
#                         mdl.get_property_value(i_inst_meas_prop),
#                         mdl.get_property_value(v_line_inst_meas_prop),
#                         mdl.get_property_value(v_phase_inst_meas_prop),
#                     )
#                 ):
#                     meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle,
#                                              item_type="component")
#                     if not meter_3ph:
#                         meter_3ph = mdl.create_component("core/Three-phase Meter",
#                                                          name="meter_3ph",
#                                                          parent=comp_handle,
#                                                          position=meter_pos["ABC"])
#                     mdl.set_property_value(mdl.prop(meter_3ph, "enable_out"),
#                                            mdl.get_property_value(enable_output_prop))
#                 tag_3ph = mdl.get_item("tag_3ph", parent=comp_handle, item_type="tag")
#                 if not tag_3ph:
#                     tag_3ph = mdl.create_tag("ground",
#                                              name="tag_3ph",
#                                              parent=comp_handle,
#                                              scope="local",
#                                              kind="pe",
#                                              rotation="down",
#                                              position=(meter_pos["ABC"][0] + 48,
#                                                        meter_pos["ABC"][1] + 160))
#                     mdl.hide_name(tag_3ph)
#
#                 if len(mdl.find_connections(mdl.term(meter_3ph, "GND"), tag_3ph)) == 0:
#                     mdl.create_connection(mdl.term(meter_3ph, "GND"), tag_3ph)
#
#                 for phase in "ABC":
#                     terminal_handlers[phase]["+"] = mdl.term(meter_3ph, f"{phase}+")
#                     terminal_handlers[phase]["-"] = mdl.term(meter_3ph, f"{phase}-")
#                 if "N" in comp_type:
#                     meter_1ph = mdl.get_item("meter_N", parent=comp_handle,
#                                              item_type="component")
#                     if not meter_1ph:
#                         # replace the SC with single phase meter once it's available
#                         meter_1ph = mdl.create_component("core/Short Circuit",
#                                                          name="meter_N",
#                                                          parent=comp_handle,
#                                                          position=meter_pos["N"])
#                     # update terminal handler calling to 1ph meter, once available
#                     terminal_handlers["N"]["+"] = mdl.term(meter_1ph, "p_node")
#                     terminal_handlers["N"]["-"] = mdl.term(meter_1ph, "n_node")
#                 else:
#                     meter_1ph = mdl.get_item("meter_N", parent=comp_handle,
#                                              item_type="component")
#                     if meter_1ph:
#                         mdl.delete_item(meter_1ph)
#
#             else:
#                 meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle,
#                                          item_type="component")
#                 if meter_3ph:
#                     mdl.delete_item(meter_3ph)
#                 tag_3ph = mdl.get_item("tag_3ph", parent=comp_handle, item_type="tag")
#                 if tag_3ph:
#                     mdl.delete_item(tag_3ph)
#                 for phase in "ABCN":
#                     if phase not in comp_type:
#                         meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle,
#                                                  item_type="component")
#                         if meter_1ph:
#                             mdl.delete_item(meter_1ph)
#
#                 for phase in comp_type:
#                     meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle,
#                                              item_type="component")
#                     if not meter_1ph:
#                         # replace the SC with single phase meter once it's available
#                         meter_1ph = mdl.create_component("core/Short Circuit",
#                                                          name=f"meter_{phase}",
#                                                          parent=comp_handle,
#                                                          position=meter_pos[phase])
#                     # update terminal handler calling to 1ph meter, once available
#                     terminal_handlers[phase]["+"] = mdl.term(meter_1ph, "p_node")
#                     terminal_handlers[phase]["-"] = mdl.term(meter_1ph, "n_node")
#
#             # create the remaining ports and connections
#             for phase in "ABCN":
#                 if phase in comp_type:
#                     port_2 = mdl.get_item(f"{phase}2", parent=comp_handle,
#                                           item_type="port")
#                     if not port_2:
#                         port_2 = mdl.create_port(name=f"{phase}2",
#                                                  parent=comp_handle,
#                                                  kind="pe",
#                                                  direction="in",
#                                                  flip="flip_horizontal",
#                                                  position=port_attributes[f"{phase}2"][
#                                                      "pos"],
#                                                  terminal_position=
#                                                  port_attributes[f"{phase}2"][
#                                                      "term_pos"])
#                     else:
#                         mdl.set_port_properties(port_2, terminal_position=
#                         port_attributes[f"{phase}2"]["term_pos"])
#                     jun = mdl.get_item(f"jun_{phase}", parent=comp_handle,
#                                        item_type="junction")
#                     conn_term_list = [(jun, terminal_handlers[phase]["+"]),
#                                       (terminal_handlers[phase]["-"], port_2)]
#                     for conn_term in conn_term_list:
#                         if len(mdl.find_connections(conn_term[0], conn_term[1])) == 0:
#                             mdl.create_connection(conn_term[0], conn_term[1])
#                 else:
#                     port_2 = mdl.get_item(f"{phase}2", parent=comp_handle,
#                                           item_type="port")
#                     if port_2:
#                         mdl.delete_item(port_2)
#         else:
#             for phase in "ABCN":
#                 port_2 = mdl.get_item(f"{phase}2", parent=comp_handle, item_type="port")
#                 if port_2:
#                     mdl.delete_item(port_2)
#                 meter_1ph = mdl.get_item("meter_N", parent=comp_handle,
#                                          item_type="component")
#                 if meter_1ph:
#                     mdl.delete_item(meter_1ph)
#
#             meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle,
#                                      item_type="component")
#             if meter_3ph:
#                 mdl.delete_item(meter_3ph)
#             tag_3ph = mdl.get_item("tag_3ph", parent=comp_handle, item_type="tag")
#             if tag_3ph:
#                 mdl.delete_item(tag_3ph)
#         # Updating the icon (not mandatory)
#         mdl.refresh_icon(comp_handle)
#         # Measurements Check (mandatory)
#         check_measurements(mdl, comp_handle)
#
#     # ------------------------------------------------------------------------------------------------------------------
#     #  "type_prop" property code
#     # ------------------------------------------------------------------------------------------------------------------
#     if caller_prop_handle == type_prop:
#         comp_handle = mdl.get_parent(comp_handle)
#
#         terminal_handlers = {"A": {"+": None, "-": None},
#                              "B": {"+": None, "-": None},
#                              "C": {"+": None, "-": None},
#                              "N": {"+": None, "-": None}}
#         meter_pos = {"A": (7672, 7856),
#                      "B": (7672, 7952),
#                      "C": (7672, 8048),
#                      "N": (7672, 8144),
#                      "ABC": (7672, 7952)}
#
#         port_attributes = get_port_const_attributes(new_value)
#
#         conf = mdl.get_property_disp_value(conf_prop)
#         if conf == "on both sides":
#             # only when both sides are connected the measurements are applied
#             if "ABC" in new_value:
#                 for phase in "ABC":
#                     meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle,
#                                              item_type="component")
#                     if meter_1ph:
#                         mdl.delete_item(meter_1ph)
#
#                 if any(
#                         (
#                                 mdl.get_property_value(i_inst_meas_prop),
#                                 mdl.get_property_value(v_line_inst_meas_prop),
#                                 mdl.get_property_value(v_phase_inst_meas_prop),
#                         )
#                 ):
#                     # Three-phase meter should be used instead of 3x1ph meter
#                     meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle,
#                                              item_type="component")
#                     if not meter_3ph:
#                         meter_3ph = mdl.create_component("core/Three-phase Meter",
#                                                          name="meter_3ph",
#                                                          parent=comp_handle,
#                                                          position=meter_pos["ABC"])
#                     mdl.set_property_value(mdl.prop(meter_3ph, "enable_out"),
#                                            mdl.get_property_value(enable_output_prop))
#                 tag_3ph = mdl.get_item("tag_3ph", parent=comp_handle, item_type="tag")
#                 if not tag_3ph:
#                     tag_3ph = mdl.create_tag("ground",
#                                              name="tag_3ph",
#                                              parent=comp_handle,
#                                              scope="local",
#                                              kind="pe",
#                                              rotation="down",
#                                              position=(meter_pos["ABC"][0] + 48,
#                                                        meter_pos["ABC"][1] + 160))
#                     mdl.hide_name(tag_3ph)
#
#                 if len(mdl.find_connections(mdl.term(meter_3ph, "GND"), tag_3ph)) == 0:
#                     mdl.create_connection(mdl.term(meter_3ph, "GND"), tag_3ph)
#
#                 for phase in "ABC":
#                     terminal_handlers[phase]["+"] = mdl.term(meter_3ph, f"{phase}+")
#                     terminal_handlers[phase]["-"] = mdl.term(meter_3ph, f"{phase}-")
#                 if "N" in new_value:
#                     meter_1ph = mdl.get_item("meter_N", parent=comp_handle,
#                                              item_type="component")
#                     if not meter_1ph:
#                         # replace the SC with single phase meter once it's available
#                         meter_1ph = mdl.create_component("core/Short Circuit",
#                                                          name="meter_N",
#                                                          parent=comp_handle,
#                                                          position=meter_pos["N"])
#                     # update terminal handler calling to 1ph meter, once available
#                     terminal_handlers["N"]["+"] = mdl.term(meter_1ph, "p_node")
#                     terminal_handlers["N"]["-"] = mdl.term(meter_1ph, "n_node")
#                 else:
#                     meter_1ph = mdl.get_item("meter_N", parent=comp_handle,
#                                              item_type="component")
#                     if meter_1ph:
#                         mdl.delete_item(meter_1ph)
#
#             else:
#                 meter_3ph = mdl.get_item("meter_3ph", parent=comp_handle,
#                                          item_type="component")
#                 if meter_3ph:
#                     mdl.delete_item(meter_3ph)
#                 tag_3ph = mdl.get_item("tag_3ph", parent=comp_handle, item_type="tag")
#                 if tag_3ph:
#                     mdl.delete_item(tag_3ph)
#                 for phase in "ABCN":
#                     if phase not in new_value:
#                         meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle,
#                                                  item_type="component")
#                         if meter_1ph:
#                             mdl.delete_item(meter_1ph)
#
#                 for phase in new_value:
#                     meter_1ph = mdl.get_item(f"meter_{phase}", parent=comp_handle,
#                                              item_type="component")
#                     if not meter_1ph:
#                         # replace the SC with single phase meter once it's available
#                         meter_1ph = mdl.create_component("core/Short Circuit",
#                                                          name=f"meter_{phase}",
#                                                          parent=comp_handle,
#                                                          position=meter_pos[phase])
#                     # update terminal handler calling to 1ph meter, once available
#                     terminal_handlers[phase]["+"] = mdl.term(meter_1ph, "p_node")
#                     terminal_handlers[phase]["-"] = mdl.term(meter_1ph, "n_node")
#
#         for phase in "ABCN":
#             if phase in new_value:
#                 # create the items that should always exist as long as the given phase is selected
#                 port_1 = mdl.get_item(f"{phase}1", parent=comp_handle, item_type="port")
#                 if not port_1:
#                     port_1 = mdl.create_port(name=f"{phase}1",
#                                              parent=comp_handle,
#                                              kind="pe",
#                                              direction="in",
#                                              position=port_attributes[f"{phase}1"][
#                                                  "pos"],
#                                              terminal_position=
#                                              port_attributes[f"{phase}1"]["term_pos"])
#                 else:
#                     mdl.set_port_properties(port_1, terminal_position=
#                     port_attributes[f"{phase}1"]["term_pos"])
#
#                 jun = mdl.get_item(f"jun_{phase}", parent=comp_handle,
#                                    item_type="junction")
#                 if not jun:
#                     jun = mdl.create_junction(name=f"jun_{phase}",
#                                               parent=comp_handle,
#                                               kind="pe",
#                                               position=(
#                                               port_attributes[f"{phase}1"]["pos"][
#                                                   0] + 160,
#                                               port_attributes[f"{phase}1"]["pos"][1]))
#
#                 oc_ph = mdl.get_item(f"OC{phase}", parent=comp_handle,
#                                      item_type="component")
#                 if not oc_ph:
#                     oc_ph = mdl.create_component("core/Open Circuit",
#                                                  name=f"OC{phase}",
#                                                  parent=comp_handle,
#                                                  hide_name=True,
#                                                  position=(
#                                                  port_attributes[f"{phase}1"]["pos"][
#                                                      0] + 112,
#                                                  port_attributes[f"{phase}1"]["pos"][
#                                                      1] + 48))
#
#                 tag_ph = mdl.get_item(f"tag_ph_{phase}", parent=comp_handle,
#                                       item_type="tag")
#                 if not tag_ph:
#                     tag_ph = mdl.create_tag("ground",
#                                             name=f"tag_ph_{phase}",
#                                             parent=comp_handle,
#                                             scope="local",
#                                             kind="pe",
#                                             position=(
#                                             port_attributes[f"{phase}1"]["pos"][0] + 16,
#                                             port_attributes[f"{phase}1"]["pos"][
#                                                 1] + 48))
#                     mdl.hide_name(tag_ph)
#
#                 conn_term_list = [(port_1, jun),
#                                   (jun, mdl.term(oc_ph, "n_node")),
#                                   (mdl.term(oc_ph, "p_node"), tag_ph)]
#                 for conn_term in conn_term_list:
#                     if len(mdl.find_connections(conn_term[0], conn_term[1])) == 0:
#                         mdl.create_connection(conn_term[0], conn_term[1])
#             else:
#                 port_1 = mdl.get_item(f"{phase}1", parent=comp_handle, item_type="port")
#                 if port_1:
#                     mdl.delete_item(port_1)
#                 jun = mdl.get_item(f"jun_{phase}", parent=comp_handle,
#                                    item_type="junction")
#                 if jun:
#                     mdl.delete_item(jun)
#                 oc_ph = mdl.get_item(f"OC{phase}", parent=comp_handle,
#                                      item_type="component")
#                 if oc_ph:
#                     mdl.delete_item(oc_ph)
#                 tag_ph = mdl.get_item(f"tag_ph_{phase}", parent=comp_handle,
#                                       item_type="tag")
#                 if tag_ph:
#                     mdl.delete_item(tag_ph)
#
#         if conf == "on both sides":
#             # create the remaining ports and connections
#             for phase in "ABCN":
#                 if phase in new_value:
#                     port_2 = mdl.get_item(f"{phase}2", parent=comp_handle,
#                                           item_type="port")
#                     if not port_2:
#                         port_2 = mdl.create_port(name=f"{phase}2",
#                                                  parent=comp_handle,
#                                                  kind="pe",
#                                                  direction="in",
#                                                  flip="flip_horizontal",
#                                                  position=port_attributes[f"{phase}2"][
#                                                      "pos"],
#                                                  terminal_position=
#                                                  port_attributes[f"{phase}2"][
#                                                      "term_pos"])
#                     else:
#                         mdl.set_port_properties(port_2, terminal_position=
#                         port_attributes[f"{phase}2"]["term_pos"])
#                     jun = mdl.get_item(f"jun_{phase}", parent=comp_handle,
#                                        item_type="junction")
#                     conn_term_list = [(jun, terminal_handlers[phase]["+"]),
#                                       (terminal_handlers[phase]["-"], port_2)]
#                     for conn_term in conn_term_list:
#                         if len(mdl.find_connections(conn_term[0], conn_term[1])) == 0:
#                             mdl.create_connection(conn_term[0], conn_term[1])
#                 else:
#                     port_2 = mdl.get_item(f"{phase}2", parent=comp_handle,
#                                           item_type="port")
#                     if port_2:
#                         mdl.delete_item(port_2)
#
#         # Updating the icon
#         mdl.refresh_icon(comp_handle)
#         # Measurements Check
#         check_measurements(mdl, comp_handle)
#
#
#     # Add measurements if checkboxes are selected
#     check_measurements(mdl, comp_handle)

# ------------------------------------------------------------------------------------------------------------------
#  "enable_output_prop" property code
# ------------------------------------------------------------------------------------------------------------------

# comp_handle = mdl.get_parent(comp_handle)
# comp_type = mdl.get_property_disp_value(type_prop)
# port_attributes = get_port_const_attributes(comp_type)
# meas_handle = mdl.get_item("meter_3ph", parent=comp_handle)
# if meas_handle:
#     mdl.set_property_value(mdl.prop(meas_handle, "enable_out"), new_value)
# if new_value:
#     new_port = mdl.create_port(name="OUT",
#                                parent=comp_handle,
#                                position=port_attributes["OUT"]["pos"],
#                                kind="sp",
#                                direction="out",
#                                terminal_position=port_attributes["OUT"][
#                                    "term_pos"],
#                                rotation="left",
#                                hide_name=True)
#     mdl.create_connection(mdl.term(meas_handle, "Out"), new_port)
#
# else:
#     new_port = mdl.get_item("OUT", parent=comp_handle, item_type="port")
#     if new_port:
#         mdl.delete_item(new_port)


def mask_dialog_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """
    return
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

        prop_list = [i_rms_meas_prop, i_inst_meas_prop, v_line_rms_meas_prop,
                     v_line_inst_meas_prop,
                     v_phase_rms_meas_prop, v_phase_inst_meas_prop, freq_meas_prop,
                     power_meas_prop,
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
             for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop,
                          v_phase_inst_meas_prop,
                          freq_meas_prop]]
            if init:
                [mdl.set_property_value(prop, True)
                 for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop,
                              v_phase_inst_meas_prop,
                              freq_meas_prop]]
            [mdl.disable_property(prop)
             for prop in [i_rms_meas_prop, i_inst_meas_prop, v_phase_rms_meas_prop,
                          v_phase_inst_meas_prop,
                          freq_meas_prop]]
        else:
            [mdl.enable_property(prop)
             for prop in [i_rms_meas_prop, v_phase_rms_meas_prop, freq_meas_prop]]


def define_icon(mdl, mask_handle):
    """
    Defines the component icon based on the number of phases
    """

    phase_a = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_a"))
    phase_b = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_b"))
    phase_c = mdl.get_property_disp_value(mdl.prop(mask_handle, "phase_c"))

    num_phases = sum((phase_a, phase_b, phase_c))
    image = f"images/bus_{num_phases}ph.svg"
    mdl.set_component_icon_image(mask_handle, image)


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
                 "OUT": {"pos": (7672, 7760), "term_pos": [0, -16 * len(comp_type)]}}

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
        meter_props_dict = {"v_phase_inst_meas": ["VAn", "VBn", "VCn"],
                            # "VN" Neutral Voltage not used for now
                            "v_line_inst_meas": ["VAB", "VBC", "VCA"],
                            "i_inst_meas": ["IA", "IB", "IC"],
                            # "IN" Neutral Current not used for now
                            "freq_meas": ["freq"],
                            "v_phase_rms_meas": ["VLn_rms", "VLn_avg_rms"],
                            # "VN_rms" Neutral Voltage not used for now
                            "v_line_rms_meas": ["VLL_rms", "VLL_avg_rms"],
                            "i_rms_meas": ["I_rms", "I_avg_rms"],
                            # "IN_rms" Neutral Voltage not used for now
                            "power_meas": ["P_meas"]}
        # Component Props
        comp_type = mdl.get_property_disp_value(mdl.prop(container_handle, "type_prop"))
        enabled_phase = [phase in comp_type for phase in ["A", "B", "C"]]
        comp_conf = mdl.get_property_disp_value(mdl.prop(container_handle, "conf"))

        # Enable/Disable the assigned properties
        # per phase props
        for cnt, action in enumerate(enabled_phase):
            i_inst = mdl.get_property_disp_value(
                mdl.prop(container_handle, "i_inst_meas"))
            mdl.set_property_value(
                mdl.prop(meter_handle, meter_props_dict["i_inst_meas"][cnt]),
                action and i_inst)

            v_line = mdl.get_property_disp_value(
                mdl.prop(container_handle, "v_line_inst_meas"))
            mdl.set_property_value(
                mdl.prop(meter_handle, meter_props_dict["v_line_inst_meas"][cnt]),
                action and v_line)

            v_phase = mdl.get_property_disp_value(
                mdl.prop(container_handle, "v_phase_inst_meas"))
            mdl.set_property_value(
                mdl.prop(meter_handle, meter_props_dict["v_phase_inst_meas"][cnt]),
                action and v_phase)

        # Three-Phase props (There are some miss measurements depending on comp_type)
        # Edit Handlers of the Meter is not called from external components (just GUI)
        i_rms_meas = mdl.get_property_disp_value(
            mdl.prop(container_handle, "i_rms_meas"))
        mdl.set_property_value(
            mdl.prop(meter_handle, meter_props_dict["i_rms_meas"][0]), i_rms_meas)
        if i_rms_meas:
            [mdl.set_property_value(mdl.prop(meter_handle, prop), True) for prop in
             meter_props_dict["i_inst_meas"]]

        v_line_rms_meas = mdl.get_property_disp_value(
            mdl.prop(container_handle, "v_line_rms_meas"))
        mdl.set_property_value(
            mdl.prop(meter_handle, meter_props_dict["v_line_rms_meas"][0]),
            v_line_rms_meas)
        if v_line_rms_meas:
            [mdl.set_property_value(mdl.prop(meter_handle, prop), True)
             for prop in meter_props_dict["v_line_inst_meas"]]

        v_phase_rms_meas = mdl.get_property_disp_value(
            mdl.prop(container_handle, "v_phase_rms_meas"))
        mdl.set_property_value(
            mdl.prop(meter_handle, meter_props_dict["v_phase_rms_meas"][0]),
            v_phase_rms_meas)
        if v_phase_rms_meas:
            [mdl.set_property_value(mdl.prop(meter_handle, prop), True)
             for prop in meter_props_dict["v_phase_inst_meas"]]

        freq_meas = mdl.get_property_disp_value(mdl.prop(container_handle, "freq_meas"))
        mdl.set_property_value(mdl.prop(meter_handle, meter_props_dict["freq_meas"][0]),
                               freq_meas)

        power_meas = mdl.get_property_disp_value(
            mdl.prop(container_handle, "power_meas"))
        mdl.set_property_value(
            mdl.prop(meter_handle, meter_props_dict["power_meas"][0]), power_meas)
        # RMS calculation needs all instantaneous measurements (and frequency/voltage)
        if i_rms_meas or v_line_rms_meas or v_phase_rms_meas or freq_meas or power_meas:
            mdl.set_property_value(
                mdl.prop(meter_handle, meter_props_dict["freq_meas"][0]), True)
            [mdl.set_property_value(mdl.prop(meter_handle, prop), True)
             for prop in meter_props_dict["v_phase_inst_meas"]]


def set_bus_phases(mdl, container_handle, caller_handle="value_changed"):
    phase_a = "A" if mdl.get_property_disp_value(
        mdl.prop(container_handle, "phase_a")) is True else ""
    phase_b = "B" if mdl.get_property_disp_value(
        mdl.prop(container_handle, "phase_b")) is True else ""
    phase_c = "C" if mdl.get_property_disp_value(
        mdl.prop(container_handle, "phase_c")) is True else ""
    phase_n = "N" if mdl.get_property_disp_value(
        mdl.prop(container_handle, "phase_n")) is True else ""
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
        mdl.set_property_disp_value(mdl.prop(container_handle, "type_prop"),
                                    phases_used)
        if "ABC" in phases_used and conf == "on both sides":
            [mdl.show_property(mdl.prop(container_handle, prop)) for prop in prop_list]

        else:
            [mdl.hide_property(mdl.prop(container_handle, prop)) for prop in prop_list]


def retro_compatibility(mdl, mask_handle):
    phase_a_prop = mdl.prop(mask_handle, "phase_a")
    phase_b_prop = mdl.prop(mask_handle, "phase_b")
    phase_c_prop = mdl.prop(mask_handle, "phase_c")

    prop_mapping = {
        "A": phase_a_prop,
        "B": phase_b_prop,
        "C": phase_c_prop,
    }

    type_prop = mdl.prop(mask_handle, "type_prop")
    old_type_value = mdl.get_property_value(type_prop)

    # Mark the correspondent checkbox for each letter in the old value
    for letter in "ABC":
        if letter in old_type_value:
            mdl.set_property_value(prop_mapping[letter], True)
        else:
            mdl.set_property_value(prop_mapping[letter], False)

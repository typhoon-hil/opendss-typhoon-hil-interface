def circuit_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:

    """
    # Property Registration
    filter_type_prop = mdl.prop(container_handle, "filter_type")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "filter_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == filter_type_prop:

        comp_handle = mdl.get_parent(container_handle)
        rl1_handle = mdl.get_item("RL1", parent=comp_handle)
        # RC vars
        rc_handle = mdl.get_item("RC", parent=comp_handle)
        rc_pos = mdl.get_position(rc_handle)
        rc_type = mdl.get_component_type_name(rc_handle)
        # RL vars
        rl2_handle = mdl.get_item("RL2", parent=comp_handle)
        rl2_pos = mdl.get_position(rl2_handle)
        rl2_type = mdl.get_component_type_name(rl2_handle)
        # Other components
        nport_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
        lport_handle = mdl.get_item("L", parent=comp_handle, item_type="port")
        vmeas_handle = mdl.get_item("Vout", parent=comp_handle)

        # Workaround for the RLC Series Branch (is deleting all port in the initialization)
        imeas_handle = mdl.get_item("Iout", parent=comp_handle)
        if not mdl.find_connections(mdl.term(imeas_handle, "n_node"), mdl.term(rl1_handle, "P1_pos")):
            mdl.create_connection(mdl.term(imeas_handle, "n_node"), mdl.term(rl1_handle, "P1_pos"))

        if new_value == "L":
            if rc_type == "Series RLC Branch":
                mdl.delete_item(rc_handle)
                rc_handle = mdl.create_component("core/Open Circuit",
                                                 parent=comp_handle,
                                                 name="RC",
                                                 position=rc_pos,
                                                 rotation="right")
                mdl.create_connection(mdl.term(rl1_handle, "P1_neg"), mdl.term(rc_handle, "p_node"))
                mdl.create_connection(mdl.term(rc_handle, "n_node"), nport_handle)

            if rl2_type == "Series RLC Branch":
                mdl.delete_item(rl2_handle)
                rl2_handle = mdl.create_component("core/Short Circuit",
                                                  parent=comp_handle,
                                                  name="RL2",
                                                  position=rl2_pos)
                mdl.create_connection(mdl.term(rl1_handle, "P1_neg"), mdl.term(rl2_handle, "p_node"))
                mdl.create_connection(mdl.term(rl2_handle, "n_node"), lport_handle)
                mdl.create_connection(mdl.term(rl2_handle, "n_node"), mdl.term(vmeas_handle, "p_node"))
        elif new_value == "LC":
            if rc_type == "el_open":
                mdl.delete_item(rc_handle)
                rc_handle = mdl.create_component("core/Series RLC Branch",
                                                 parent=comp_handle,
                                                 name="RC",
                                                 position=rc_pos,
                                                 rotation="right")
                mdl.set_property_value(mdl.prop(rc_handle, "num_phases"), "Single-Phase")
                mdl.set_property_value(mdl.prop(rc_handle, "branch_type"), "RC")
                mdl.set_property_value(mdl.prop(rc_handle, "resistance"), "rc_resistance")
                mdl.set_property_value(mdl.prop(rc_handle, "capacitance"), "rc_capacitance")
                mdl.create_connection(mdl.term(rl1_handle, "P1_neg"), mdl.term(rc_handle, "P1_pos"))
                mdl.create_connection(mdl.term(rc_handle, "P1_neg"), nport_handle)

            if rl2_type == "Series RLC Branch":
                mdl.delete_item(rl2_handle)
                rl2_handle = mdl.create_component("core/Short Circuit",
                                                  parent=comp_handle,
                                                  name="RL2",
                                                  position=rl2_pos)
                mdl.create_connection(mdl.term(rl1_handle, "P1_neg"), mdl.term(rl2_handle, "p_node"))
                mdl.create_connection(mdl.term(rl2_handle, "n_node"), lport_handle)
                mdl.create_connection(mdl.term(rl2_handle, "n_node"), mdl.term(vmeas_handle, "p_node"))
        elif new_value == "LCL":
            if rc_type == "el_open":
                mdl.delete_item(rc_handle)
                rc_handle = mdl.create_component("core/Series RLC Branch",
                                                 parent=comp_handle,
                                                 name="RC",
                                                 position=rc_pos,
                                                 rotation="right")
                mdl.set_property_value(mdl.prop(rc_handle, "num_phases"), "Single-Phase")
                mdl.set_property_value(mdl.prop(rc_handle, "branch_type"), "RC")
                mdl.set_property_value(mdl.prop(rc_handle, "resistance"), "rc_resistance")
                mdl.set_property_value(mdl.prop(rc_handle, "capacitance"), "rc_capacitance")
                mdl.create_connection(mdl.term(rl1_handle, "P1_neg"), mdl.term(rc_handle, "P1_pos"))
                mdl.create_connection(mdl.term(rc_handle, "P1_neg"), nport_handle)

            if rl2_type == "el_short":
                mdl.delete_item(rl2_handle)
                rl2_handle = mdl.create_component("core/Series RLC Branch",
                                                  parent=comp_handle,
                                                  name="RL2",
                                                  position=rl2_pos)
                mdl.set_property_value(mdl.prop(rl2_handle, "num_phases"), "Single-Phase")
                mdl.set_property_value(mdl.prop(rl2_handle, "branch_type"), "RL")
                mdl.set_property_value(mdl.prop(rl2_handle, "resistance"), "rl_resistance")
                mdl.set_property_value(mdl.prop(rl2_handle, "inductance"), "rl_inductance")
                mdl.create_connection(mdl.term(rl1_handle, "P1_neg"), mdl.term(rl2_handle, "P1_pos"))
                mdl.create_connection(mdl.term(rl2_handle, "P1_neg"), lport_handle)
                mdl.create_connection(mdl.term(rl2_handle, "P1_neg"), mdl.term(vmeas_handle, "p_node"))


def mask_dialog_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """
    # Property Registration
    filter_type_prop = mdl.prop(container_handle, "filter_type")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_disp_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "filter_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == filter_type_prop:

        rl1_prop_names = ["rl1_resistance", "rl1_inductance"]
        rl1_prop_handles = [mdl.prop(container_handle, pname) for pname in rl1_prop_names]
        rc_prop_names = ["rc_resistance", "rc_capacitance"]
        rc_prop_handles = [mdl.prop(container_handle, pname) for pname in rc_prop_names]
        rl2_prop_names = ["rl2_resistance", "rl2_inductance"]
        rl2_prop_handles = [mdl.prop(container_handle, pname) for pname in rl2_prop_names]

        if new_value == "L":
            [mdl.show_property(props) for props in rl1_prop_handles]
            [mdl.hide_property(props) for props in rc_prop_handles + rl2_prop_handles]
        elif new_value == "LC":
            [mdl.show_property(props) for props in rl1_prop_handles + rc_prop_handles]
            [mdl.hide_property(props) for props in rl2_prop_handles]
        elif new_value == "LCL":
            [mdl.show_property(props) for props in rl1_prop_handles + rc_prop_handles + rl2_prop_handles]

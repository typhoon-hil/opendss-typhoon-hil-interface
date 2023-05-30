def circuit_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:

    """
    # Property Registration
    itm_csnb_type_prop = mdl.prop(container_handle, "itm_csnb_type")
    itm_vsnb_type_prop = mdl.prop(container_handle, "itm_vsnb_type")
    itm_csnb_fixed_prop = mdl.prop(container_handle, "itm_csnb_fixed")
    itm_vsnb_fixed_prop = mdl.prop(container_handle, "itm_vsnb_fixed")
    auto_mode_prop = mdl.prop(container_handle, "auto_mode")
    flip_status_prop = mdl.prop(container_handle, "flip_status")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_csnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == itm_csnb_type_prop:

        comp_handle = mdl.get_parent(container_handle)
        coupling_handle = mdl.get_item("Coupling", parent=comp_handle)
        mdl.set_property_value(mdl.prop(coupling_handle, "snb_type_i"), new_value)

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_vsnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == itm_vsnb_type_prop:

        comp_handle = mdl.get_parent(container_handle)
        coupling_handle = mdl.get_item("Coupling", parent=comp_handle)
        mdl.set_property_value(mdl.prop(coupling_handle, "snb_type_u"), new_value)

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_csnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == itm_csnb_fixed_prop:

        comp_handle = mdl.get_parent(container_handle)
        coupling_handle = mdl.get_item("Coupling", parent=comp_handle)

        if new_value:
            mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_i"), "true")
        else:
            mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_i"), "false")

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_vsnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == itm_vsnb_fixed_prop:

        comp_handle = mdl.get_parent(container_handle)
        coupling_handle = mdl.get_item("Coupling", parent=comp_handle)

        if new_value:
            mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_u"), "true")
        else:
            mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_u"), "false")

    # ------------------------------------------------------------------------------------------------------------------
    #  "auto_mode" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == auto_mode_prop:

        # Change Coupling properties
        comp_handle = mdl.get_parent(container_handle)
        coupling_handle = mdl.get_item("Coupling", parent=comp_handle)
        prop_names = ["R1", "C1", "R2", "L1", "snb_type_i", "snb_type_u"]
        manual_itm_csnb_type = mdl.get_property_disp_value(mdl.prop(container_handle, "itm_csnb_type"))
        manual_itm_vsnb_type = mdl.get_property_disp_value(mdl.prop(container_handle, "itm_vsnb_type"))

        if new_value == "Manual":
            prop_values = ["itm_csnb_r", "itm_csnb_c", "itm_vsnb_r", "itm_vsnb_l", manual_itm_csnb_type, manual_itm_vsnb_type]
        else:
            prop_values = ["itm_csnb_r_auto", "itm_csnb_c_auto", "itm_vsnb_r_auto", "itm_vsnb_l_auto", "none", "none"]
        [mdl.set_property_value(mdl.prop(coupling_handle, pname), value)
         for pname, value in zip(prop_names, prop_values)]

        # Changing Component properties
        if new_value == "Manual":
            mdl.set_property_value(mdl.prop(container_handle, "flip_status"), False)
        else:
            mdl.set_property_value(mdl.prop(container_handle, "itm_csnb_fixed"), True)
            mdl.set_property_value(mdl.prop(container_handle, "itm_vsnb_fixed"), True)

        # Update the Icon
        mdl.refresh_icon(container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "flip_status" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == flip_status_prop:

        # Flip Action
        flip_coupling(mdl, container_handle, new_value)
        # Update the Icon
        mdl.refresh_icon(container_handle)


def mask_dialog_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """
    # Property Registration
    auto_mode_prop = mdl.prop(container_handle, "auto_mode")
    itm_csnb_type_prop = mdl.prop(container_handle, "itm_csnb_type")
    itm_vsnb_type_prop = mdl.prop(container_handle, "itm_vsnb_type")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_disp_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "conf" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == auto_mode_prop:

        csnb_prop_handles = [mdl.prop(container_handle, pname)
                             for pname in ["itm_csnb_type", "itm_csnb_r", "itm_csnb_c", "itm_csnb_fixed"]]
        vsnb_prop_handles = [mdl.prop(container_handle, pname)
                             for pname in ["itm_vsnb_type", "itm_vsnb_r", "itm_vsnb_l", "itm_vsnb_fixed"]]

        if new_value == "Manual":
            [mdl.show_property(prop) for prop in csnb_prop_handles + vsnb_prop_handles]
        elif new_value == "Automatic":
            [mdl.hide_property(prop) for prop in csnb_prop_handles + vsnb_prop_handles]

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_csnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == itm_csnb_type_prop:

        prop_names = ["itm_csnb_r", "itm_csnb_c", "itm_csnb_fixed"]
        if new_value == "none":
            [mdl.disable_property(mdl.prop(container_handle, pname)) for pname in prop_names]
        elif new_value == "R1":
            [mdl.enable_property(mdl.prop(container_handle, pname)) for pname in prop_names]
            mdl.disable_property(mdl.prop(container_handle, prop_names[1]))
        elif new_value == "R1-C1":
            [mdl.enable_property(mdl.prop(container_handle, pname)) for pname in prop_names]

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_vsnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == itm_vsnb_type_prop:

        prop_names = ["itm_vsnb_r", "itm_vsnb_l", "itm_vsnb_fixed"]
        if new_value == "none":
            [mdl.disable_property(mdl.prop(container_handle, pname)) for pname in prop_names]
        elif new_value == "R2":
            [mdl.enable_property(mdl.prop(container_handle, pname)) for pname in prop_names]
            mdl.disable_property(mdl.prop(container_handle, prop_names[1]))
        elif new_value == "R2||L1":
            [mdl.enable_property(mdl.prop(container_handle, pname)) for pname in prop_names]


def define_icon(mdl, container_handle):
    """
    Defines the component icon based on its type

    :param mdl: Schematic API
    :param container_handle: Component Handle
    :return: no return
    """
    flip = mdl.get_property_value(mdl.prop(container_handle, "flip_status"))
    mode = mdl.get_property_value(mdl.prop(container_handle, "auto_mode"))

    if flip:
        mdl.set_component_icon_image(container_handle, f'images/coupling_flip.svg')
        mdl.disp_component_icon_text(container_handle, "Flipped", relpos_x=0.5, relpos_y=0.95, size=5)
    else:
        mdl.set_component_icon_image(container_handle, f'images/coupling.svg')

    if mode == "Automatic":
        mdl.disp_component_icon_text(container_handle, "Auto", relpos_x=0.5, relpos_y=0.05, size=5)


def flip_coupling(mdl, container_handle, flip):

    comp_handle = mdl.get_parent(container_handle)
    mode = mdl.get_property_value(mdl.prop(container_handle, "auto_mode"))
    fixed_csnb = mdl.get_property_disp_value(mdl.prop(container_handle, "itm_csnb_fixed"))
    fixed_vsnb = mdl.get_property_disp_value(mdl.prop(container_handle, "itm_vsnb_fixed"))
    csnb_type = mdl.get_property_disp_value(mdl.prop(container_handle, "itm_csnb_type"))
    vsnb_type = mdl.get_property_disp_value(mdl.prop(container_handle, "itm_vsnb_type"))


    port1_names = ["A1", "B1", "C1"]
    gnd1_names = ["gnd1"]
    port2_names = ["A2", "B2", "C2"]
    gnd2_names = ["gnd2"]

    coupling_cside_names = ["a_in", "b_in", "c_in", "d_in"]
    coupling_vside_names = ["a_out", "b_out", "c_out", "d_out"]

    coupling_handle = mdl.get_item("Coupling", parent=comp_handle)
    coupling_position = mdl.get_position(coupling_handle)
    mdl.delete_item(coupling_handle)
    if flip:
        comp_flip = "flip_horizontal"
    else:
        comp_flip = "flip_none"
    coupling_handle = mdl.create_component("core/Four Phase Core Coupling",
                                           name="Coupling",
                                           parent=comp_handle,
                                           position=coupling_position,
                                           flip=comp_flip)
    port1_handles = [mdl.get_item(pname, parent=comp_handle, item_type="port") for pname in port1_names]
    gnd1_handle = [mdl.get_item(pname, parent=comp_handle) for pname in gnd1_names]
    port2_handles = [mdl.get_item(pname, parent=comp_handle, item_type="port") for pname in port2_names]
    gnd2_handle = [mdl.get_item(pname, parent=comp_handle) for pname in gnd2_names]

    if flip:
        # Current Side
        [mdl.create_connection(c1, mdl.term(coupling_handle, pname))
         for c1, pname in zip(port2_handles, coupling_cside_names)]
        mdl.create_connection(mdl.term(coupling_handle, "d_in"), mdl.term(gnd2_handle[0], "node"))
        # Voltage Side
        [mdl.create_connection(c1, mdl.term(coupling_handle, pname))
         for c1, pname in zip(port1_handles, coupling_vside_names)]
        mdl.create_connection(mdl.term(coupling_handle, "d_out"), mdl.term(gnd1_handle[0], "node"))
    else:
        # Current Side
        [mdl.create_connection(c1, mdl.term(coupling_handle, pname))
         for c1, pname in zip(port1_handles, coupling_cside_names)]
        mdl.create_connection(mdl.term(coupling_handle, "d_in"), mdl.term(gnd1_handle[0], "node"))
        # Voltage Side
        [mdl.create_connection(c1, mdl.term(coupling_handle, pname))
         for c1, pname in zip(port2_handles, coupling_vside_names)]
        mdl.create_connection(mdl.term(coupling_handle, "d_out"), mdl.term(gnd2_handle[0], "node"))

    prop_names = ["R1", "C1", "R2", "L1"]
    if mode == "Manual":
        prop_values = ["itm_csnb_r", "itm_csnb_c", "itm_vsnb_r", "itm_vsnb_l"]
    else:
        prop_values = ["itm_csnb_r_auto", "itm_csnb_c_auto", "itm_vsnb_r_auto", "itm_vsnb_l_auto"]
        mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_i"), "true")
        mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_u"), "true")
    [mdl.set_property_value(mdl.prop(coupling_handle, pname), value)
     for pname, value in zip(prop_names, prop_values)]
    mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_i"), str(fixed_csnb).lower())
    mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_u"), str(fixed_vsnb).lower())
    mdl.set_property_value(mdl.prop(coupling_handle, "snb_type_i"), csnb_type)
    mdl.set_property_value(mdl.prop(coupling_handle, "snb_type_u"), vsnb_type)

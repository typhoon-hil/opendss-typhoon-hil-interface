def circuit_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:

    """
    # Property Registration
    grounding_prop = mdl.prop(container_handle, "grounding")
    phases_prop = mdl.prop(container_handle, "phases")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "grounding" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == grounding_prop:
        comp_handle = mdl.get_parent(container_handle)
        # port_dynamics function to support container component
        port_dynamics(mdl, container_handle, grounding_prop)
        # Connections and Internal Items
        ntag_handle = mdl.get_item("gnd_src", parent=comp_handle, item_type="tag")
        if new_value:
            xpos, ypos = get_port_const_attributes("N")["pos"]
            gnd_handle = mdl.create_component("core/Ground",
                                              name="gnd",
                                              parent=comp_handle,
                                              position=(xpos, ypos+48))
            mdl.create_connection(ntag_handle, mdl.term(gnd_handle, "node"))
        else:
            gnd_handle = mdl.get_item("gnd", parent=comp_handle)
            if gnd_handle:
                mdl.delete_item(gnd_handle)
            nport_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
            if nport_handle:
                if not mdl.find_connections(ntag_handle, nport_handle):
                    mdl.create_connection(ntag_handle, nport_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "phases" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == phases_prop:

        comp_handle = mdl.get_parent(container_handle)
        # port_dynamics function to support container component
        port_dynamics(mdl, container_handle, phases_prop)
        # Connections and Internal Items
        phase_names = ["B", "C"]
        port_handles = [mdl.get_item(pname, parent=comp_handle, item_type="port") for pname in ["B1", "C1"]]
        ground_handle = mdl.get_item("gnd_tag", parent=comp_handle, item_type="tag")
        xpos_ref = mdl.get_position(mdl.get_item("InvLeg_A", parent=comp_handle))[0]
        inv_leg_handles = [mdl.get_item(cname, parent=comp_handle) for cname in ["InvLeg_B", "InvLeg_C"]]
        mod_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                       for tname in ["from_modB", "from_modC"]]
        term_mod_handles = [mdl.get_item(tname, parent=comp_handle) for tname in ["term_modB", "term_modC"]]
        imeas_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                         for tname in ["goto_IB", "goto_IC"]]
        ct_imeas_handles = [mdl.get_item(cname, parent=comp_handle) for cname in ["ct_IB", "ct_IC"]]
        vmeas_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                         for tname in ["goto_VB", "goto_VC"]]
        ct_vmeas_handles = [mdl.get_item(cname, parent=comp_handle) for cname in ["ct_VB", "ct_VC"]]

        if new_value == "3":
            # mod_handles
            for cnt, fhandle in enumerate(term_mod_handles):
                if fhandle:
                    mdl.delete_item(fhandle)
            # imeas_handles
            for cnt, ihandle in enumerate(ct_imeas_handles):
                if ihandle:
                    mdl.delete_item(ihandle)
            # vmeas_handles
            for cnt, vhandle in enumerate(ct_vmeas_handles):
                if vhandle:
                    mdl.delete_item(vhandle)
            # inv_legs
            for cnt, leg_handle in enumerate(inv_leg_handles):
                if not leg_handle:
                    ypos = mdl.get_position(port_handles[cnt])[1]
                    leg_handle = mdl.create_component("OpenDSS/Generic Leg Inverter (avg)",
                                                      name=f"InvLeg_{phase_names[cnt]}",
                                                      parent=comp_handle,
                                                      position=[xpos_ref, ypos])
                    mdl.create_connection(mdl.term(leg_handle, "N"), ground_handle)
                    mdl.create_connection(mdl.term(leg_handle, "L"), port_handles[cnt])
                    mdl.create_connection(mdl.term(leg_handle, "mod"), mod_handles[cnt])
                    mdl.create_connection(mdl.term(leg_handle, "Imeas"), imeas_handles[cnt])
                    mdl.create_connection(mdl.term(leg_handle, "Vmeas"), vmeas_handles[cnt])
        else:
            # inv_legs
            for cnt, leg_handle in enumerate(inv_leg_handles):
                if leg_handle:
                    mdl.delete_item(leg_handle)
            # mod_handles
            for cnt, fhandle in enumerate(mod_handles):
                posx, posy = mdl.get_position(fhandle)
                if not term_mod_handles[cnt]:
                    term_handle = mdl.create_component("core/Termination",
                                                       name=f"term_mod{phase_names[cnt]}",
                                                       parent=comp_handle,
                                                       position=[posx+64, posy])
                    mdl.create_connection(fhandle, mdl.term(term_handle, "in"))
            # imeas_handles
            for cnt, ihandle in enumerate(imeas_handles):
                posx, posy = mdl.get_position(ihandle)
                if not ct_imeas_handles[cnt]:
                    const_handle = mdl.create_component("core/Constant",
                                                        name=f"ct_I{phase_names[cnt]}",
                                                        parent=comp_handle,
                                                        position=[posx-64, posy])
                    mdl.set_property_value(mdl.prop(const_handle, "value"), 0)
                    mdl.set_property_value(mdl.prop(const_handle, "execution_rate"), "ts")
                    mdl.create_connection(mdl.term(const_handle, "out"), ihandle)
            # vmeas_handles
            for cnt, vhandle in enumerate(vmeas_handles):
                posx, posy = mdl.get_position(vhandle)
                if not ct_vmeas_handles[cnt]:
                    const_handle = mdl.create_component("core/Constant",
                                                        name=f"ct_V{phase_names[cnt]}",
                                                        parent=comp_handle,
                                                        position=[posx-64, posy])
                    mdl.set_property_value(mdl.prop(const_handle, "value"), 0)
                    mdl.set_property_value(mdl.prop(const_handle, "execution_rate"), "ts")
                    mdl.create_connection(mdl.term(const_handle, "out"), vhandle)


def port_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """
    Ports modification (to support container component)

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """

    comp_handle = mdl.get_parent(container_handle)
    prop_name = None
    new_value = None
    if caller_prop_handle:
        prop_name = mdl.get_name(caller_prop_handle)
        new_value = mdl.get_property_value(caller_prop_handle)

    if prop_name == "grounding":
        if new_value:
            nport_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
            if nport_handle:
                mdl.delete_item(nport_handle)
        else:
            nport_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
            if not nport_handle:
                nport_param = get_port_const_attributes("N")
                nport_handle = mdl.create_port(name=nport_param["name"],
                                               parent=comp_handle,
                                               position=nport_param["pos"],
                                               terminal_position=nport_param["term_pos"],
                                               kind="pe",
                                               flip="flip_horizontal")

    elif prop_name == "phases":
        port_names = ["B1", "C1"]
        port_handles = [mdl.get_item(pname, parent=comp_handle, item_type="port") for pname in port_names]
        if new_value == "3":
            for cnt, phandle in enumerate(port_handles):
                if not phandle:
                    port_param = get_port_const_attributes(port_names[cnt])
                    nport_handle = mdl.create_port(name=port_param["name"],
                                                   parent=comp_handle,
                                                   position=port_param["pos"],
                                                   terminal_position=port_param["term_pos"],
                                                   kind="pe",
                                                   flip="flip_horizontal")
        else:
            for cnt, phandle in enumerate(port_handles):
                if phandle:
                    mdl.delete_item(phandle)


def define_icon(mdl, container_handle):
    """
    Defines the component icon based on its type

    :param mdl: Schematic API
    :param container_handle: Component Handle
    :return: no return
    """
    comp_handle = mdl.get_parent(container_handle)
    mask_handle = mdl.get_mask(comp_handle)
    mdl.set_component_icon_image(mask_handle, "images/PVSystem.svg")


def get_port_const_attributes(port_name):
    """

    """
    port_dict = {"A1": {"name": "A1", "pos": (7984, 7984), "term_pos": (40.0, -48.0), "label": "A"},
                 "B1": {"name": "B1", "pos": (7984, 8128), "term_pos": (40.0, -16.0), "label": "B"},
                 "C1": {"name": "C1", "pos": (7984, 8280), "term_pos": (40.0, 16.0), "label": "C"},
                 "N": {"name": "N", "pos": (7984, 8408), "term_pos": (40.0, 48.0), "label": "N"}}

    return port_dict[port_name]

import os
import pathlib
import json
import ast

got_loadshape_points_list = []


def circuit_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:

    """
    # Property Registration
    connection_prop = mdl.prop(container_handle, "connection")
    phases_prop = mdl.prop(container_handle, "phases")
    power_ref_prop = mdl.prop(container_handle, "power_ref")
    t_mode_prop = mdl.prop(container_handle, "t_mode")
    filter_type_prop = mdl.prop(container_handle, "filter_type")

    new_value = None
    if init:
        return

    if caller_prop_handle:
        new_value = mdl.get_property_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "grounding" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == connection_prop:
        comp_handle = mdl.get_parent(container_handle)
        # port_dynamics function to support container component
        port_dynamics(mdl, container_handle, connection_prop)
        # Connections and Internal Items
        ntag_handle = mdl.get_item("gnd_src", parent=comp_handle, item_type="tag")
        if new_value == "Y":
            xpos, ypos = get_port_const_attributes(mdl, container_handle, "N")["pos"]
            gnd_handle = mdl.get_item("gnd", parent=comp_handle)
            if not gnd_handle:
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
        # Controller
        inv_control_handle = mdl.get_item("InvControl", parent=comp_handle)
        inv_control_pos = mdl.get_position(inv_control_handle)
        vlist_handle = mdl.get_item("Vlist", parent=comp_handle)
        vlist_pos = mdl.get_position(vlist_handle)
        ilist_handle = mdl.get_item("Ilist", parent=comp_handle)
        ilist_pos = mdl.get_position(ilist_handle)
        goto_mod_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                            for tname in ["mod_vb", "mod_vc"]]
        bus_mod_handle = mdl.get_item("Bus Split mod", parent=comp_handle)
        goto_en_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                           for tname in ["en_swB", "en_swC"]]
        term_en_handles = [mdl.get_item(tname, parent=comp_handle)
                           for tname in ["term_enB", "term_enC"]]
        filter_type = mdl.get_property_disp_value(mdl.prop(container_handle, "filter_type"))

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
            # term_en
            for cnt, thandle in enumerate(term_en_handles):
                if thandle:
                    mdl.delete_item(thandle)
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
                    mdl.create_connection(mdl.term(leg_handle, "sw"), goto_en_handles[cnt])
                    prop_values = ["rl1_resistance", "rl1_inductance", "rc_resistance", "rc_capacitance",
                                   "rl2_resistance", "rl2_inductance", "ts"]
                    [mdl.set_property_value(mdl.prop(leg_handle, prop), prop) for prop in prop_values]
                    mdl.set_property_value(mdl.prop(leg_handle, "filter_type"), filter_type)
                    mdl.set_property_value(mdl.prop(leg_handle, "sw_r"), "pv_r")
            # Control
            mdl.set_property_value(mdl.prop(inv_control_handle, "phases"), "3")
            isel_handle = mdl.get_item("ilist_sel", parent=comp_handle)
            if isel_handle:
                mdl.delete_item(isel_handle)
                mdl.create_connection(mdl.term(ilist_handle, "out"), mdl.term(inv_control_handle, "Imeas"))
            vsel_handle = mdl.get_item("vlist_sel", parent=comp_handle)
            if vsel_handle:
                mdl.delete_item(vsel_handle)
                mdl.create_connection(mdl.term(vlist_handle, "out"), mdl.term(inv_control_handle, "Vmeas"))
            ct_mod_handle = mdl.get_item("ct_mod", parent=comp_handle)
            if ct_mod_handle:
                mdl.delete_item(ct_mod_handle)
                mdl.set_property_value(mdl.prop(bus_mod_handle, "outputs"), "3")
                mdl.create_connection(mdl.term(bus_mod_handle, "out2"), goto_mod_handles[1])
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
            # Control
            mdl.set_property_value(mdl.prop(inv_control_handle, "phases"), "1")
            vlist_conn = mdl.find_connections(mdl.term(vlist_handle, "out"), mdl.term(inv_control_handle, "Vmeas"))
            ilist_conn = mdl.find_connections(mdl.term(ilist_handle, "out"), mdl.term(inv_control_handle, "Imeas"))
            if vlist_conn:
                mdl.delete_item(vlist_conn[0])
            if ilist_conn:
                mdl.delete_item(ilist_conn[0])
            vsel_handle = mdl.create_component("core/Bus Selector",
                                               name="vlist_sel",
                                               parent=comp_handle,
                                               position=[vlist_pos[0]+64, vlist_pos[1]])
            mdl.set_property_value(mdl.prop(vsel_handle, "signal_indexes"), "[0]")
            mdl.create_connection(mdl.term(vlist_handle, "out"), mdl.term(vsel_handle, "in"))
            mdl.create_connection(mdl.term(vsel_handle, "out"), mdl.term(inv_control_handle, "Vmeas"))
            isel_handle = mdl.create_component("core/Bus Selector",
                                               name="ilist_sel",
                                               parent=comp_handle,
                                               position=[ilist_pos[0]+64, ilist_pos[1]])
            mdl.set_property_value(mdl.prop(isel_handle, "signal_indexes"), "[0]")
            mdl.create_connection(mdl.term(ilist_handle, "out"), mdl.term(isel_handle, "in"))
            mdl.create_connection(mdl.term(isel_handle, "out"), mdl.term(inv_control_handle, "Imeas"))
            mdl.set_property_value(mdl.prop(bus_mod_handle, "outputs"), "2")
            goto_mod_pos = mdl.get_position(goto_mod_handles[1])
            ct_mod_handle = mdl.create_component("core/Constant",
                                                 name="ct_mod",
                                                 parent=comp_handle,
                                                 position=[goto_mod_pos[0]-128, goto_mod_pos[1]])
            mdl.set_property_value(mdl.prop(ct_mod_handle, "execution_rate"), "ts")
            mdl.create_connection(mdl.term(ct_mod_handle, "out"), goto_mod_handles[1])
            # term_en
            for cnt, thandle in enumerate(goto_en_handles):
                posx, posy = mdl.get_position(thandle)
                if not term_en_handles[cnt]:
                    term_handle = mdl.create_component("core/Termination",
                                                       name=f"term_en{phase_names[cnt]}",
                                                       parent=comp_handle,
                                                       position=[posx+64, posy])
                    mdl.create_connection(thandle, mdl.term(term_handle, "in"))

    # ------------------------------------------------------------------------------------------------------------------
    #  "power_ref" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == power_ref_prop:

        comp_handle = mdl.get_parent(container_handle)
        port_dynamics(mdl, container_handle, caller_prop_handle)

        irrad_lut_handle = mdl.get_item("Irrad_lut", parent=comp_handle)
        irrad_lut_pos = mdl.get_position(irrad_lut_handle)
        temp_lut_handle = mdl.get_item("Temp_lut", parent=comp_handle)
        temp_lut_pos = mdl.get_position(temp_lut_handle)
        pdc_product_handle = mdl.get_item("Pdc_prod", parent=comp_handle)
        pvst_lut_handle = mdl.get_item("PvsT", parent=comp_handle)
        reset_irrad_handle = mdl.get_item("Rst Irrad", parent=comp_handle)
        reset_temp_handle = mdl.get_item("Rst Temp", parent=comp_handle)

        irrad_port_handle = mdl.get_item("Irradiance_p", parent=comp_handle, item_type="port")
        temp_port_handle = mdl.get_item("Temperature_p", parent=comp_handle, item_type="port")
        time_port_handle = mdl.get_item("Time_p", parent=comp_handle, item_type="port")

        irrad_attrib = get_port_const_attributes(mdl, container_handle, "Irradiance")
        temp_attrib = get_port_const_attributes(mdl, container_handle, "Temperature")
        time_attrib = get_port_const_attributes(mdl, container_handle, "Time")

        t_mode = mdl.get_property_value(mdl.prop(container_handle, "t_mode"))

        if new_value == "Internal Scada Input":

            mdl.delete_item(reset_irrad_handle) if reset_irrad_handle else None
            mdl.delete_item(reset_temp_handle) if reset_temp_handle else None

            irrad_handle = mdl.get_item("Irradiance", parent=comp_handle)
            if not irrad_handle:
                irrad_handle = mdl.create_component("core/SCADA Input",
                                                    name="Irradiance",
                                                    parent=comp_handle,
                                                    position=irrad_attrib.get("pos"))
                mdl.set_property_value(mdl.prop(irrad_handle, "min"), "0")
                mdl.set_property_value(mdl.prop(irrad_handle, "max"), "100")
                mdl.set_property_value(mdl.prop(irrad_handle, "def_value"), "irrad")
                mdl.set_property_value(mdl.prop(irrad_handle, "unit"), "kw/m2")
                mdl.set_property_value(mdl.prop(irrad_handle, "execution_rate"), "ts")

                irrad_lut_pos = mdl.get_position(irrad_lut_handle)
                mdl.delete_item(irrad_lut_handle)
                irrad_lut_handle = mdl.create_component("core/Gain",
                                                        name="Irrad_lut",
                                                        parent=comp_handle,
                                                        position=irrad_lut_pos)
                if not mdl.find_connections(mdl.term(irrad_handle, "out"), mdl.term(irrad_lut_handle, "in")):
                    mdl.create_connection(mdl.term(irrad_handle, "out"), mdl.term(irrad_lut_handle, "in"))
                if not mdl.find_connections(mdl.term(irrad_lut_handle, "out"), mdl.term(pdc_product_handle, "in1")):
                    mdl.create_connection(mdl.term(irrad_lut_handle, "out"), mdl.term(pdc_product_handle, "in1"))

            temp_handle = mdl.get_item("Temperature", parent=comp_handle)
            if not temp_handle:
                temp_handle = mdl.create_component("core/SCADA Input",
                                                   name="Temperature",
                                                   parent=comp_handle,
                                                   position=temp_attrib.get("pos"))
                mdl.set_property_value(mdl.prop(temp_handle, "min"), "0")
                mdl.set_property_value(mdl.prop(temp_handle, "max"), "150")
                mdl.set_property_value(mdl.prop(temp_handle, "def_value"), "temp")
                mdl.set_property_value(mdl.prop(temp_handle, "unit"), "°C")
                mdl.set_property_value(mdl.prop(temp_handle, "execution_rate"), "ts")

                temp_lut_pos = mdl.get_position(temp_lut_handle)
                mdl.delete_item(temp_lut_handle)
                temp_lut_handle = mdl.create_component("core/Gain",
                                                       name="Temp_lut",
                                                       parent=comp_handle,
                                                       position=temp_lut_pos)
                if not mdl.find_connections(mdl.term(temp_handle, "out"), mdl.term(temp_lut_handle, "in")):
                    mdl.create_connection(mdl.term(temp_handle, "out"), mdl.term(temp_lut_handle, "in"))
                if not mdl.find_connections(mdl.term(temp_lut_handle, "out"), mdl.term(pvst_lut_handle, "addr")):
                    mdl.create_connection(mdl.term(temp_lut_handle, "out"), mdl.term(pvst_lut_handle, "addr"))

        elif new_value == "Time Series":

            irrad_handle = mdl.get_item("Irradiance", parent=comp_handle)
            if irrad_handle:
                mdl.delete_item(irrad_handle)

                mdl.delete_item(irrad_lut_handle)
                irrad_lut_handle = mdl.create_component("1D look-up table",
                                                        name="Irrad_lut",
                                                        parent=comp_handle,
                                                        position=irrad_lut_pos)
                mdl.set_property_value(mdl.prop(irrad_lut_handle, "in_vec_x"), "loadshape_time")
                mdl.set_property_value(mdl.prop(irrad_lut_handle, "out_vec_f_x"), "loadshape")
                mdl.set_property_value(mdl.prop(irrad_lut_handle, "table_impl"), "Non-equidistant")
                reset_irrad_handle = mdl.create_component("OpenDSS/TS Reset",
                                                          name="Rst Irrad",
                                                          parent=comp_handle,
                                                          position=[irrad_lut_pos[0]-128, irrad_lut_pos[1]])
                mdl.set_property_value(mdl.prop(reset_irrad_handle, "max"), "irrad_max")

                mdl.create_connection(mdl.term(reset_irrad_handle, "Out"), mdl.term(irrad_lut_handle, "addr"))
                mdl.create_connection(mdl.term(irrad_lut_handle, "value"), mdl.term(pdc_product_handle, "in1"))

            temp_handle = mdl.get_item("Temperature", parent=comp_handle)
            if temp_handle:
                mdl.delete_item(temp_handle)

                mdl.delete_item(temp_lut_handle)
                temp_lut_handle = mdl.create_component("1D look-up table",
                                                       name="Temp_lut",
                                                       parent=comp_handle,
                                                       position=temp_lut_pos)
                mdl.set_property_value(mdl.prop(temp_lut_handle, "in_vec_x"), "tshape_time")
                mdl.set_property_value(mdl.prop(temp_lut_handle, "out_vec_f_x"), "tshape_temp")
                mdl.set_property_value(mdl.prop(temp_lut_handle, "table_impl"), "Non-equidistant")
                reset_temp_handle = mdl.create_component("OpenDSS/TS Reset",
                                                         name="Rst Temp",
                                                         parent=comp_handle,
                                                         position=[temp_lut_pos[0]-128, temp_lut_pos[1]])
                mdl.set_property_value(mdl.prop(reset_temp_handle, "max"), "temp_max")

                mdl.create_connection(mdl.term(reset_temp_handle, "Out"), mdl.term(temp_lut_handle, "addr"))
                mdl.create_connection(mdl.term(temp_lut_handle, "value"), mdl.term(pvst_lut_handle, "addr"))

            if t_mode == "Time value (h)":

                if not mdl.find_connections(time_port_handle, mdl.term(reset_irrad_handle, "In")):
                    mdl.create_connection(time_port_handle, mdl.term(reset_irrad_handle, "In"))

                if not mdl.find_connections(time_port_handle, mdl.term(reset_temp_handle, "In")):
                    mdl.create_connection(time_port_handle, mdl.term(reset_temp_handle, "In"))

                mdl.set_property_value(mdl.prop(reset_irrad_handle, "input_type"), "Hour")
                mdl.set_property_value(mdl.prop(reset_temp_handle, "input_type"), "Hour")

            elif t_mode == "Index":

                if not mdl.find_connections(irrad_port_handle, mdl.term(reset_irrad_handle, "In")):
                    mdl.create_connection(irrad_port_handle, mdl.term(reset_irrad_handle, "In"))

                if not mdl.find_connections(temp_port_handle, mdl.term(reset_temp_handle, "In")):
                    mdl.create_connection(temp_port_handle, mdl.term(reset_temp_handle, "In"))

                mdl.set_property_value(mdl.prop(reset_irrad_handle, "input_type"), "Index")
                mdl.set_property_value(mdl.prop(reset_temp_handle, "input_type"), "Index")

    # ------------------------------------------------------------------------------------------------------------------
    #  "t_mode" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == t_mode_prop:

        comp_handle = mdl.get_parent(container_handle)
        power_ref = mdl.get_property_value(power_ref_prop)
        port_dynamics(mdl, container_handle, caller_prop_handle)

        irrad_handle = mdl.get_item("Irradiance_p", parent=comp_handle, item_type="port")
        temp_handle = mdl.get_item("Temperature_p", parent=comp_handle, item_type="port")
        time_handle = mdl.get_item("Time_p", parent=comp_handle, item_type="port")

        irrad_lut_handle = mdl.get_item("Irrad_lut", parent=comp_handle)
        temp_lut_handle = mdl.get_item("Temp_lut", parent=comp_handle)

        reset_irrad_handle = mdl.get_item("Rst Irrad", parent=comp_handle)
        reset_temp_handle = mdl.get_item("Rst Temp", parent=comp_handle)

        if power_ref == "Time Series":

            if new_value == "Time":

                if not mdl.find_connections(time_handle, mdl.term(reset_irrad_handle, "In")):
                    mdl.create_connection(time_handle, mdl.term(reset_irrad_handle, "In"))

                if not mdl.find_connections(time_handle, mdl.term(reset_temp_handle, "In")):
                    mdl.create_connection(time_handle, mdl.term(reset_temp_handle, "In"))

                mdl.set_property_value(mdl.prop(reset_irrad_handle, "input_type"), "Hour")
                mdl.set_property_value(mdl.prop(reset_temp_handle, "input_type"), "Hour")

            elif new_value == "Index":

                if not mdl.find_connections(irrad_handle, mdl.term(reset_irrad_handle, "In")):
                    mdl.create_connection(irrad_handle, mdl.term(reset_irrad_handle, "In"))

                if not mdl.find_connections(temp_handle, mdl.term(reset_temp_handle, "In")):
                    mdl.create_connection(temp_handle, mdl.term(reset_temp_handle, "In"))

                mdl.set_property_value(mdl.prop(reset_irrad_handle, "input_type"), "Index")
                mdl.set_property_value(mdl.prop(reset_temp_handle, "input_type"), "Index")

    # ------------------------------------------------------------------------------------------------------------------
    #  "filter_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == filter_type_prop:

        comp_handle = mdl.get_parent(container_handle)
        inv_handles = [mdl.get_item(inv_name, parent=comp_handle) for inv_name in ["InvLeg_A", "InvLeg_B", "InvLeg_C"]]

        for inv_ph_handle in inv_handles:
            if inv_ph_handle:
                mdl.set_property_value(mdl.prop(inv_ph_handle, "filter_type"), new_value)


def mask_dialog_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """
    # Property Registration
    phases_prop = mdl.prop(container_handle, "phases")
    filter_type_prop = mdl.prop(container_handle, "filter_type")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_disp_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "phases" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == phases_prop:

        connection_prop = mdl.prop(container_handle, "connection")
        if new_value == "1":
            mdl.enable_property(connection_prop)
        else:
            mdl.disable_property(connection_prop)
            mdl.set_property_disp_value(connection_prop, "Y")

    # ------------------------------------------------------------------------------------------------------------------
    #  "filter_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == filter_type_prop:

        rl1_properties = [mdl.prop(container_handle, pname) for pname in ["rl1_resistance", "rl1_inductance"]]
        rc_properties = [mdl.prop(container_handle, pname) for pname in ["rc_resistance", "rc_capacitance"]]
        rl2_properties = [mdl.prop(container_handle, pname) for pname in ["rl2_resistance", "rl2_inductance"]]

        if new_value == "L":
            [mdl.show_property(prop) for prop in rl1_properties]
            [mdl.hide_property(prop) for prop in rl2_properties + rc_properties]
        elif new_value == "LC":
            [mdl.show_property(prop) for prop in rl1_properties + rc_properties]
            [mdl.hide_property(prop) for prop in rl2_properties]
        elif new_value == "LCL":
            [mdl.show_property(prop) for prop in rl1_properties + rc_properties + rl2_properties]


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
    mdl.refresh_icon(container_handle)
    prop_name = None
    new_value = None
    if caller_prop_handle:
        prop_name = mdl.get_name(caller_prop_handle)
        new_value = mdl.get_property_value(caller_prop_handle)

    if prop_name == "connection":
        if new_value == "Y":
            nport_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
            if nport_handle:
                mdl.delete_item(nport_handle)
        else:
            nport_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
            if not nport_handle:
                nport_param = get_port_const_attributes(mdl, container_handle, "N")
                nport_handle = mdl.create_port(name=nport_param["name"],
                                               parent=comp_handle,
                                               position=nport_param["pos"],
                                               terminal_position=nport_param["term_pos"],
                                               kind="pe",
                                               flip="flip_horizontal",
                                               hide_name=True)

    elif prop_name == "phases":
        port_names = ["B1", "C1"]
        port_handles = [mdl.get_item(pname, parent=comp_handle, item_type="port") for pname in port_names]
        if new_value == "3":
            for cnt, phandle in enumerate(port_handles):
                if not phandle:
                    port_param = get_port_const_attributes(mdl, container_handle, port_names[cnt])
                    nport_handle = mdl.create_port(name=port_param["name"],
                                                   parent=comp_handle,
                                                   position=port_param["pos"],
                                                   terminal_position=port_param["term_pos"],
                                                   kind="pe",
                                                   flip="flip_horizontal",
                                                   hide_name=True)
        else:
            for cnt, phandle in enumerate(port_handles):
                if phandle:
                    mdl.delete_item(phandle)

    elif prop_name in ["power_ref", "t_mode"]:

        power_ref = mdl.get_property_disp_value(mdl.prop(container_handle, "power_ref"))
        mode = mdl.get_property_disp_value(mdl.prop(container_handle, "t_mode"))

        # pmpp_attrib = get_port_const_attributes(mdl, container_handle, "Pmpp")
        irrad_attrib = get_port_const_attributes(mdl, container_handle, "Irradiance")
        temp_attrib = get_port_const_attributes(mdl, container_handle, "Temperature")
        time_attrib = get_port_const_attributes(mdl, container_handle, "Time")

        # pmpp_handle = mdl.get_item(pmpp_attrib.get("name"), parent=comp_handle, item_type="port")
        irrad_handle = mdl.get_item(irrad_attrib.get("name"), parent=comp_handle, item_type="port")
        temp_handle = mdl.get_item(temp_attrib.get("name"), parent=comp_handle, item_type="port")
        time_handle = mdl.get_item(time_attrib.get("name"), parent=comp_handle, item_type="port")

        if power_ref == "Internal Scada Input":

            # mdl.delete_item(pmpp_handle) if pmpp_handle else None
            mdl.delete_item(irrad_handle) if irrad_handle else None
            mdl.delete_item(temp_handle) if temp_handle else None
            mdl.delete_item(time_handle) if time_handle else None

        elif power_ref == "Time Series":

            if mode == "Index":
                mdl.delete_item(time_handle) if time_handle else None
                """
                if not pmpp_handle:
                    pmpp_handle = mdl.create_port(name=pmpp_attrib.get("name"),
                                                  parent=comp_handle,
                                                  label=pmpp_attrib.get("label"),
                                                  kind="sp",
                                                  terminal_position=pmpp_attrib.get("term_pos"),
                                                  position=pmpp_attrib.get("pos"),
                                                  direction="in")
                """

                if not irrad_handle:
                    irrad_handle = mdl.create_port(name=irrad_attrib.get("name"),
                                                   parent=comp_handle,
                                                   label=irrad_attrib.get("label"),
                                                   kind="sp",
                                                   terminal_position=irrad_attrib.get("term_pos"),
                                                   position=irrad_attrib.get("pos"),
                                                   direction="in")

                if not temp_handle:
                    temp_handle = mdl.create_port(name=temp_attrib.get("name"),
                                                  parent=comp_handle,
                                                  label=temp_attrib.get("label"),
                                                  kind="sp",
                                                  terminal_position=temp_attrib.get("term_pos"),
                                                  position=temp_attrib.get("pos"),
                                                  direction="in")

            elif mode == "Time value (h)":
                # mdl.delete_item(pmpp_handle) if pmpp_handle else None
                mdl.delete_item(irrad_handle) if irrad_handle else None
                mdl.delete_item(temp_handle) if temp_handle else None
                if not time_handle:
                    time_handle = mdl.create_port(name=time_attrib.get("name"),
                                                  parent=comp_handle,
                                                  label=time_attrib.get("label"),
                                                  kind="sp",
                                                  terminal_position=time_attrib.get("term_pos"),
                                                  position=time_attrib.get("pos"),
                                                  direction="in")

    port_names = ["A1", "B1", "C1", "N"]
    port_handles = [mdl.get_item(pname, parent=comp_handle, item_type="port") for pname in port_names]
    port_attrib = [get_port_const_attributes(mdl, container_handle, pname) for pname in port_names]
    for idx, phandle in enumerate(port_handles):
        if phandle:
            mdl.set_port_properties(phandle, terminal_position=port_attrib[idx].get("term_pos"))


def define_icon(mdl, container_handle):
    """
    Defines the component icon based on its type

    :param mdl: Schematic API
    :param container_handle: Component Handle
    :return: no return
    """
    comp_handle = mdl.get_parent(container_handle)
    mask_handle = mdl.get_mask(comp_handle)
    phases = mdl.get_property_disp_value(mdl.prop(container_handle, "phases"))
    connection = mdl.get_property_disp_value(mdl.prop(container_handle, "connection"))
    power_ref = mdl.get_property_disp_value(mdl.prop(container_handle, "power_ref"))

    img_ctrl = "noctrl" if power_ref == "Internal Scada Input" else "ctrl"
    if phases == "3":
        img_ph = "3ph"
    else:
        img_ph = "1phg" if connection == "Y" else "2ph"
    mdl.set_component_icon_image(mask_handle, f"images/pv_{img_ph}_{img_ctrl}.svg")
    if power_ref != "Internal Scada Input":
        mdl.disp_component_icon_text(mask_handle, "Time Series", relpos_x=0.32, relpos_y=0.06, trim_factor=1.0, size=6)


def get_port_const_attributes(mdl, container_handle, port_name):
    """

    """
    power_ref = mdl.get_property_disp_value(mdl.prop(container_handle, "power_ref"))
    if power_ref == "Internal Scada Input":
        term_positions = [(40.0, -32.0), (40.0, -0.0), (40.0, 32.0), (40.0, 32.0)]
    else:
        term_positions = [(40.0, -8.0), (40.0, 24), (40.0, 56.0), (40.0, 56.0)]

    port_dict = {"A1": {"name": "A1", "pos": (7984, 7984), "term_pos": term_positions[0], "label": "A"},
                 "B1": {"name": "B1", "pos": (7984, 8128), "term_pos": term_positions[1], "label": "B"},
                 "C1": {"name": "C1", "pos": (7984, 8280), "term_pos": term_positions[2], "label": "C"},
                 "N": {"name": "N", "pos": (7984, 8408), "term_pos": term_positions[3], "label": "N"},
                 "Pmpp": {"name": "Pmpp_p", "pos": (7192, 7448), "term_pos": (-32, -64.0), "label": "Pmpp_i"},
                 "Irradiance": {"name": "Irradiance_p", "pos": (7064, 7512), "term_pos": (-48.0, -48.0), "label": "Irrad_i"},
                 "Temperature": {"name": "Temperature_p", "pos": (7064, 7576), "term_pos": (-48, -32.0), "label": "Temp_i"},
                 "Time": {"name": "Time_p", "pos": (7064, 7512), "term_pos": (-48.0, -48.0), "label": "t (h)"}}

    return port_dict[port_name]


def load_loadshape(mdl, container_handle):
    import os
    import dss_thcc_lib.gui_scripts.load_object as load_obj
    import pathlib
    import json
    import ast

    # Find objects file
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder_path = pathlib.Path(mdlfile_target_folder).joinpath('dss')
    fname = os.path.join(dss_folder_path, 'data', 'general_objects.json')

    loadshape_name_prop = mdl.prop(container_handle, "loadshape_name")
    loadshape_name = mdl.get_property_disp_value(loadshape_name_prop)
    loadshape_name = "" if loadshape_name == "-" else loadshape_name

    obj_type = "LoadShape"

    try:
        with open(fname, 'r') as f:
            obj_dicts = json.load(f)
    except FileNotFoundError:
        obj_dicts = None

    if obj_dicts:
        new_load_window = load_obj.LoadObject(mdl, obj_type, obj_dicts=obj_dicts, starting_object=loadshape_name)
    else:
        new_load_window = load_obj.LoadObject(mdl, obj_type)

    if new_load_window.exec():

        selected_object = new_load_window.selected_object

        obj_dicts = new_load_window.obj_dicts

        # Property handles
        loadshape_prop = mdl.prop(container_handle, "loadshape")
        loadshape_prop_int = mdl.prop(container_handle, "loadshape_int")
        loadshape_time_range_prop = mdl.prop(container_handle, "loadshape_hour")
        useactual_prop = mdl.prop(container_handle, "useactual")
        loadshape_from_file_prop = mdl.prop(container_handle, "loadshape_from_file")
        loadshape_from_file_path_prop = mdl.prop(container_handle, "loadshape_from_file_path")
        loadshape_from_file_header_prop = mdl.prop(container_handle, "loadshape_from_file_header")
        loadshape_from_file_column_prop = mdl.prop(container_handle, "loadshape_from_file_column")
        loadshape_hour_prop = mdl.prop(container_handle, "loadshape_hour")
        loadshape_npts_prop = mdl.prop(container_handle, "loadshape_npts")

        selected_obj_dict = obj_dicts.get("loadshapes").get(selected_object)
        loadshape_name = selected_object

        useactual = selected_obj_dict.get("useactual")
        loadshape_from_file = selected_obj_dict.get("csv_file") == "True"
        loadshape_from_file_path = selected_obj_dict.get("csv_path")
        loadshape_from_file_header = selected_obj_dict.get("headers")
        loadshape_from_file_column = selected_obj_dict.get("column")

        npts = selected_obj_dict.get("npts")
        if npts:
            npts = ast.literal_eval(npts)
        else:
            npts = len(ast.literal_eval(loadshape))

        hour = selected_obj_dict.get("hour")
        if hour:
            hour = ast.literal_eval(hour)
        interval = selected_obj_dict.get("interval")
        if interval:
            interval = ast.literal_eval(interval)

        if not loadshape_from_file:
            loadshape = selected_obj_dict.get("mult")
        else:
            selected_obj_dict.update({"loadshape_name": selected_object})
            loadshape = str(read_loadshape_from_json(mdl, container_handle, reload_dict=selected_obj_dict))

        if loadshape:
            loadshape = ast.literal_eval(loadshape)
            if interval == 0:  # Check hour points
                if hour:
                    loadshape = loadshape[:npts]
                else:
                    mdl.info("interval property is zero, but hour property is not defined")
            else:
                if npts <= len(loadshape):
                    loadshape = loadshape[:npts]
                else:
                    loadshape = loadshape + [0]*(npts-len(loadshape))

            mdl.set_property_disp_value(loadshape_prop, str(loadshape))

        mdl.set_property_disp_value(loadshape_name_prop, str(loadshape_name))
        mdl.set_property_disp_value(loadshape_prop_int, str(interval))
        mdl.set_property_disp_value(loadshape_from_file_prop, str(loadshape_from_file))
        mdl.set_property_disp_value(useactual_prop, useactual)
        if interval == 0:
            if hour:
                mdl.set_property_value(loadshape_time_range_prop, str(hour)) # Non-visible prop
        else:
            time_range_str = f"[{', '.join(str(interval * n) for n in range(npts))}]"
            mdl.set_property_value(loadshape_time_range_prop, time_range_str) # Non-visible prop
        mdl.set_property_disp_value(loadshape_from_file_path_prop, str(loadshape_from_file_path))
        mdl.set_property_disp_value(loadshape_from_file_header_prop, str(loadshape_from_file_header))
        mdl.set_property_disp_value(loadshape_from_file_column_prop, str(loadshape_from_file_column))
        mdl.set_property_value(mdl.prop(container_handle, "loadshape_npts"), npts)


def verify_time_loadshape_sizes(mdl, mask_handle, caller=None):
    import ast

    comp_name = mdl.get_name(mdl.get_parent(mask_handle))

    loadshape_prop = mdl.prop(mask_handle, "loadshape")
    time_prop = mdl.prop(mask_handle, "T_Ts")
    loadshape = mdl.get_property_value(loadshape_prop)

    time_list = ast.literal_eval(mdl.get_property_value(time_prop))
    ls_list = ast.literal_eval(loadshape)

    # Verify matching sizes
    mode = mdl.get_property_value(mdl.prop(mask_handle, "t_mode"))
    if mode == "Time" and time_list and ls_list:
        # The time vector and the loadshape must be the same size
        if not len(ls_list) == len(time_list):
            mdl.info(f"Component {comp_name}: The number of points on the time range "
                     f"({len(time_list)}) and loadshape ({len(ls_list)}) must be equal for correct operation.")
            min_points = min(len(time_list), len(ls_list))
            mdl.info(f"HIL simulation will use the first {min_points} points.")
            if caller == "pre_compile":
                if len(time_list) > len(ls_list):
                    mdl.set_property_value(time_prop, time_list[:min_points])
                elif len(time_list) < len(ls_list):
                    mdl.set_property_value(loadshape_prop, ls_list[:min_points])


def load_xycurve(mdl, container_handle, caller_prop_handle):

    import os
    import dss_thcc_lib.gui_scripts.load_object as load_obj
    # Tirar o importlib depois
    import importlib
    importlib.reload(load_obj)
    import pathlib
    import json
    import ast

    # Find objects file
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder_path = pathlib.Path(mdlfile_target_folder).joinpath('dss')
    fname = os.path.join(dss_folder_path, 'data', 'general_objects.json')

    obj_type = "XYCurve"
    if caller_prop_handle == mdl.prop(container_handle, "load_xycurve_eff"):
        xycurve_name_prop = mdl.prop(container_handle, "xycurve_name_eff")
    elif caller_prop_handle == mdl.prop(container_handle, "load_xycurve_cf"):
        xycurve_name_prop = mdl.prop(container_handle, "xycurve_name_cf")

    xycurve_name = mdl.get_property_disp_value(xycurve_name_prop)
    xycurve_name = "" if xycurve_name == "-" else xycurve_name

    try:
        with open(fname, 'r') as f:
            obj_dicts = json.load(f)
    except FileNotFoundError:
        obj_dicts = None

    if obj_dicts:
        new_load_window = load_obj.LoadObject(mdl, obj_type, obj_dicts=obj_dicts, starting_object=xycurve_name)
    else:
        new_load_window = load_obj.LoadObject(mdl, obj_type)

    if new_load_window.exec():

        selected_object = new_load_window.selected_object
        obj_dicts = new_load_window.obj_dicts
        selected_obj_dict = obj_dicts.get("xycurves").get(selected_object)
        xycurve_name = selected_object
        xycurve_npts_eff = selected_obj_dict.get("npts")
        xycurve_xarray_eff = selected_obj_dict.get("xarray")
        xycurve_yarray_eff = selected_obj_dict.get("yarray")

        if caller_prop_handle == mdl.prop(container_handle, "load_xycurve_eff"):
            # Property handles
            xycurve_name_eff_prop = mdl.prop(container_handle, "xycurve_name_eff")
            xycurve_npts_eff_prop = mdl.prop(container_handle, "xycurve_npts_eff")
            xycurve_xarray_eff_prop = mdl.prop(container_handle, "xycurve_xarray_eff")
            xycurve_yarray_eff_prop = mdl.prop(container_handle, "xycurve_yarray_eff")

            mdl.set_property_disp_value(xycurve_name_eff_prop, str(xycurve_name))
            mdl.set_property_disp_value(xycurve_xarray_eff_prop, str(xycurve_xarray_eff))
            mdl.set_property_disp_value(xycurve_yarray_eff_prop, str(xycurve_yarray_eff))
            mdl.set_property_value(xycurve_npts_eff_prop, str(xycurve_npts_eff)) # Non-visible prop

        elif caller_prop_handle == mdl.prop(container_handle, "load_xycurve_cf"):
            # Property handles
            xycurve_name_cf_prop = mdl.prop(container_handle, "xycurve_name_cf")
            xycurve_npts_cf_prop = mdl.prop(container_handle, "xycurve_npts_cf")
            xycurve_xarray_cf_prop = mdl.prop(container_handle, "xycurve_xarray_cf")
            xycurve_yarray_cf_prop = mdl.prop(container_handle, "xycurve_yarray_cf")

            mdl.set_property_disp_value(xycurve_name_cf_prop, str(xycurve_name))
            mdl.set_property_disp_value(xycurve_xarray_cf_prop, str(xycurve_xarray_eff))
            mdl.set_property_disp_value(xycurve_yarray_cf_prop, str(xycurve_yarray_eff))
            mdl.set_property_value(xycurve_npts_cf_prop, str(xycurve_npts_eff)) # Non-visible prop


def load_tshape(mdl, container_handle, caller_prop_handle):

    import os
    import dss_thcc_lib.gui_scripts.load_object as load_obj
    # Tirar o importlib depois
    import importlib
    importlib.reload(load_obj)
    import pathlib
    import json
    import ast

    # Find objects file
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder_path = pathlib.Path(mdlfile_target_folder).joinpath('dss')
    fname = os.path.join(dss_folder_path, 'data', 'general_objects.json')

    obj_type = "TShape"
    tshape_name_prop = mdl.prop(container_handle, "tshape_name")
    tshape_name = mdl.get_property_disp_value(tshape_name_prop)
    tshape_name = "" if tshape_name == "-" else tshape_name

    try:
        with open(fname, 'r') as f:
            obj_dicts = json.load(f)
    except FileNotFoundError:
        obj_dicts = None

    if obj_dicts:
        new_load_window = load_obj.LoadObject(mdl, obj_type, obj_dicts=obj_dicts, starting_object=tshape_name)
    else:
        new_load_window = load_obj.LoadObject(mdl, obj_type)

    if new_load_window.exec():

        selected_object = new_load_window.selected_object
        obj_dicts = new_load_window.obj_dicts
        selected_obj_dict = obj_dicts.get("tshapes").get(selected_object)

        tshape_name = selected_object
        tshape_npts = ast.literal_eval(selected_obj_dict.get("npts"))
        tshape_int = ast.literal_eval(selected_obj_dict.get("interval"))
        tshape_temp = ast.literal_eval(selected_obj_dict.get("temp"))

        # Property handles
        tshape_name_prop = mdl.prop(container_handle, "tshape_name")
        tshape_npts_prop = mdl.prop(container_handle, "tshape_npts")
        tshape_temp_prop = mdl.prop(container_handle, "tshape_temp")
        tshape_int_prop = mdl.prop(container_handle, "tshape_int")
        tshape_hour_prop = mdl.prop(container_handle, "tshape_hour")

        if not tshape_npts:
            tshape_npts = len(tshape_temp)

        if tshape_temp:
            if tshape_npts <= len(tshape_temp):
                tshape_temp = tshape_temp[:tshape_npts]
            else:
                tshape_temp = tshape_temp + [0]*(tshape_npts-len(tshape_temp))
            mdl.set_property_disp_value(tshape_temp_prop, str(tshape_temp))

        time_range_str = f"[{', '.join(str(tshape_int * n) for n in range(tshape_npts))}]"

        mdl.set_property_disp_value(tshape_name_prop, str(tshape_name))
        mdl.set_property_disp_value(tshape_temp_prop, str(tshape_temp))
        mdl.set_property_disp_value(tshape_int_prop, str(tshape_int))
        mdl.set_property_value(tshape_npts_prop, str(tshape_npts)) # Non-visible prop
        mdl.set_property_value(tshape_hour_prop, time_range_str) # Non-visible prop


def read_loadshape_from_json(mdl, mask_handle, reload_dict=None):
    global got_loadshape_points_list

    comp_handle = mdl.get_parent(mask_handle)

    try:
        current_points = ast.literal_eval(mdl.get_property_disp_value(mdl.prop(mask_handle, "loadshape")))
    except:
        current_points = []
    useactual = mdl.get_property_disp_value(mdl.prop(mask_handle, "useactual"))
    interval = mdl.get_property_disp_value(mdl.prop(mask_handle, "loadshape_int"))

    if not reload_dict:
        loadshape_name = mdl.get_property_disp_value(mdl.prop(mask_handle, "loadshape_name"))
        loadshape_from_file = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file")) == "True"
        loadshape_from_file_header = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_header")) == "True"
        loadshape_from_file_column = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_column"))
        loadshape_from_file_path = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_path"))
    else:
        loadshape_name = reload_dict.get("loadshape_name")
        loadshape_from_file = reload_dict.get("csv_file") == "True"
        loadshape_from_file_header = reload_dict.get("headers") == "True"
        loadshape_from_file_column = reload_dict.get("column")
        loadshape_from_file_path = reload_dict.get("csv_path")

    model_path = pathlib.Path(mdl.get_model_file_path())

    if model_path:
        filename = model_path.stem
        data_folder_path = model_path.parent.joinpath(filename + " Target files").joinpath('dss').joinpath("data")
        general_objects_json = data_folder_path.joinpath(f"general_objects.json")
        if general_objects_json.is_file():
            with open(general_objects_json, 'r') as f:
                general_objects_dict = json.load(f)
            loadshape_points = general_objects_dict.get("loadshapes", {}).get(loadshape_name, {}).get("mult", [])
            if loadshape_from_file:
                if pathlib.Path(loadshape_from_file_path).is_file():
                    with open(pathlib.Path(loadshape_from_file_path), 'r', encoding='utf-8-sig') as ls_f:
                        if loadshape_from_file_header:
                            table = pd.read_csv(ls_f)
                            table = table.fillna(0)
                        else:
                            table = pd.read_csv(ls_f, header=None)
                            table = table.fillna(0)
                        loadshape_points = list(table.iloc[:, int(loadshape_from_file_column) - 1])
                    mdl.set_property_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
                    mdl.set_property_disp_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
                else:
                    mdl.error(f"Could not find the CSV file '{loadshape_from_file_path}'."
                              f" Please edit or choose a new LoadShape.", context=mdl.get_parent(mask_handle))
                if loadshape_name not in general_objects_dict.get("loadshapes"):
                    with open(general_objects_json, 'w') as f:
                        new_loadshape_dict = {
                            "npts": str(len(current_points)),
                            "mult": "[]",
                            "interval": interval,
                            "interval_unit": "h",
                            "hour": "",
                            "useactual": str(useactual),
                            "csv_file": str(loadshape_from_file),
                            "csv_path": loadshape_from_file_path,
                            "headers": str(loadshape_from_file_header),
                            "column": loadshape_from_file_column
                        }
                        general_objects_dict.get("loadshapes")[loadshape_name] = new_loadshape_dict
                        f.write(json.dumps(general_objects_dict, indent=4))
            elif not loadshape_points:
                new_loadshape_dict = {
                    "npts": str(len(current_points)),
                    "mult": str(current_points),
                    "interval": interval,
                    "interval_unit": "h",
                    "hour": "",
                    "useactual": str(useactual),
                    "csv_file": str(loadshape_from_file),
                    "csv_path": loadshape_from_file_path,
                    "headers": str(loadshape_from_file_header),
                    "column": loadshape_from_file_column
                }

                general_objects_dict.get("loadshapes")[loadshape_name] = new_loadshape_dict
                with open(general_objects_json, 'w') as f:
                    f.write(json.dumps(general_objects_dict, indent=4))
            else:
                mdl.set_property_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
                mdl.set_property_disp_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
        else:
            loadshape_points = str(current_points)
            if not data_folder_path.is_dir():
                data_folder_path.mkdir(parents=True)
            with open(general_objects_json, 'w') as f:
                new_loadshape_dict = {
                    "npts": str(len(current_points)),
                    "mult": str(current_points),
                    "interval": interval,
                    "interval_unit": "h",
                    "hour": "",
                    "useactual": str(useactual),
                    "csv_file": str(loadshape_from_file),
                    "csv_path": loadshape_from_file_path,
                    "headers": str(loadshape_from_file_header),
                    "column": loadshape_from_file_column
                }
                f.write(json.dumps({"loadshapes": {loadshape_name: new_loadshape_dict}}, indent=4))

    if comp_handle not in got_loadshape_points_list:
        got_loadshape_points_list.append(comp_handle)

    return loadshape_points


def ini_general_objects_from_json(mdl, mask_handle):


    comp_handle = mdl.get_parent(mask_handle)

    xycurve_eff_name = mdl.get_property_value(mdl.prop(mask_handle, "xycurve_name_eff"))
    xycurve_cf_name = mdl.get_property_value(mdl.prop(mask_handle, "xycurve_name_cf"))
    temp_name = mdl.get_property_value(mdl.prop(mask_handle, "tshape_name"))
    irrad_name = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_name"))

    mask_gen_dict = {}
    mask_gen_dict.update({"xycurves": {}})
    mask_gen_dict.update({"tshapes": {}})
    mask_gen_dict.update({"loadshapes": {}})
    # XYCurves
    eff_dict = {"npts": str(mdl.get_property_value(mdl.prop(mask_handle, "xycurve_npts_eff"))),
                "xarray": str(mdl.get_property_value(mdl.prop(mask_handle, "xycurve_xarray_eff"))),
                "yarray": str(mdl.get_property_value(mdl.prop(mask_handle, "xycurve_yarray_eff")))
               }
    cf_dict = {"npts": str(mdl.get_property_value(mdl.prop(mask_handle, "xycurve_npts_cf"))),
               "xarray": str(mdl.get_property_value(mdl.prop(mask_handle, "xycurve_xarray_cf"))),
               "yarray": str(mdl.get_property_value(mdl.prop(mask_handle, "xycurve_yarray_cf")))
               }
    xycurves_dict = {}
    xycurves_dict.update({f"{xycurve_eff_name}": eff_dict})
    xycurves_dict.update({f"{xycurve_cf_name}": cf_dict})
    # Tshapes
    temp_dict = {"npts": str(mdl.get_property_value(mdl.prop(mask_handle, "tshape_npts"))),
                 "temp": str(mdl.get_property_value(mdl.prop(mask_handle, "tshape_temp"))),
                 "interval": str(mdl.get_property_value(mdl.prop(mask_handle, "tshape_int")))
                 }
    tshapes_dict = {}
    tshapes_dict.update({f"{temp_name}": temp_dict})
    # Loadshapes
    irrad_dict = {"npts": len(mdl.get_property_value(mdl.prop(mask_handle, "loadshape"))),
                  "interval": mdl.get_property_value(mdl.prop(mask_handle, "loadshape_int")),
                  "mult": mdl.get_property_value(mdl.prop(mask_handle, "loadshape")),
                  "hour": mdl.get_property_value(mdl.prop(mask_handle, "loadshape_hour")),
                  "interval_unit": "h",
                  "useactual": mdl.get_property_value(mdl.prop(mask_handle, "useactual")),
                  "csv_file": mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file")),
                  "csv_path": mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_path")),
                  "headers": mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_header")),
                  "column": mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_column"))
                  }
    loadshapes_dict = {}
    loadshapes_dict.update({f"{irrad_name}": irrad_dict})

    # Updating the general dict
    mask_gen_dict.get("xycurves").update(xycurves_dict)
    mask_gen_dict.get("tshapes").update(tshapes_dict)
    mask_gen_dict.get("loadshapes").update(loadshapes_dict)

    model_path = pathlib.Path(mdl.get_model_file_path())

    if model_path:
        filename = model_path.stem
        data_folder_path = model_path.parent.joinpath(filename + " Target files").joinpath('dss').joinpath("data")
        general_objects_json = data_folder_path.joinpath(f"general_objects.json")
        if general_objects_json.is_file():
            with open(general_objects_json, 'r') as f:
                general_objects_dict = json.load(f)
            for gen_type, gen_type_dict in mask_gen_dict.copy().items():
                if gen_type in general_objects_dict:
                    for gen_name, gen_values in gen_type_dict.items():
                        if gen_name in general_objects_dict.get(gen_type):
                            mask_gen_dict.get(gen_type).update({f"{gen_name}": general_objects_dict.get(gen_type).get(gen_name)})
                        else:
                            general_objects_dict.get(gen_type).update({f"{gen_name}": gen_values})
                else:
                    general_objects_dict.update({f"{gen_type}": gen_type_dict})

            with open(general_objects_json, 'w') as f:
                f.write(json.dumps(general_objects_dict, indent=4))

        else:
            if not data_folder_path.is_dir():
                data_folder_path.mkdir(parents=True)
            with open(general_objects_json, 'w') as f:
                f.write(json.dumps(mask_gen_dict, indent=4))

    # Update the mask properties

    # EFF Properties
    # Values
    xycurve_eff_new = mask_gen_dict.get("xycurves").get(f"{xycurve_eff_name}")
    xycurve_npts_eff = xycurve_eff_new.get("npts")
    xycurve_xarray_eff = xycurve_eff_new.get("xarray")
    xycurve_yarray_eff = xycurve_eff_new.get("yarray")
    # Property handles
    xycurve_npts_eff_prop = mdl.prop(mask_handle, "xycurve_npts_eff")
    xycurve_xarray_eff_prop = mdl.prop(mask_handle, "xycurve_xarray_eff")
    xycurve_yarray_eff_prop = mdl.prop(mask_handle, "xycurve_yarray_eff")
    # Set values
    mdl.set_property_value(xycurve_npts_eff_prop, str(xycurve_npts_eff))
    mdl.set_property_value(xycurve_xarray_eff_prop, str(xycurve_xarray_eff))
    mdl.set_property_value(xycurve_yarray_eff_prop, str(xycurve_yarray_eff))

    # CF Properties
    xycurve_cf_new = mask_gen_dict.get("xycurves").get(f"{xycurve_cf_name}")
    xycurve_npts_cf = xycurve_cf_new.get("npts")
    xycurve_xarray_cf = xycurve_cf_new.get("xarray")
    xycurve_yarray_cf = xycurve_cf_new.get("yarray")
    # Property handles
    xycurve_npts_cf_prop = mdl.prop(mask_handle, "xycurve_npts_cf")
    xycurve_xarray_cf_prop = mdl.prop(mask_handle, "xycurve_xarray_cf")
    xycurve_yarray_cf_prop = mdl.prop(mask_handle, "xycurve_yarray_cf")
    # Set Values
    mdl.set_property_value(xycurve_npts_cf_prop, str(xycurve_npts_cf))
    mdl.set_property_value(xycurve_xarray_cf_prop, str(xycurve_xarray_cf))
    mdl.set_property_value(xycurve_yarray_cf_prop, str(xycurve_yarray_cf))

    # Tshape Properties
    tshape_new = mask_gen_dict.get("tshapes").get(f"{temp_name}")
    tshape_npts = tshape_new.get("npts")
    tshape_int = tshape_new.get("interval")
    tshape_temp = tshape_new.get("temp")
    # Property handles
    tshape_npts_prop = mdl.prop(mask_handle, "tshape_npts")
    tshape_temp_prop = mdl.prop(mask_handle, "tshape_temp")
    tshape_int_prop = mdl.prop(mask_handle, "tshape_int")
    # Set Values
    mdl.set_property_value(tshape_npts_prop, str(tshape_npts))
    mdl.set_property_value(tshape_temp_prop, str(tshape_temp))
    mdl.set_property_value(tshape_int_prop, str(tshape_int))

    # Irrad Properties
    irrad_new = mask_gen_dict.get("loadshapes").get(f"{irrad_name}")

    loadshape = irrad_new.get("mult")
    loadshape_int = irrad_new.get("interval")
    loadshape_hour = irrad_new.get("hour")
    useactual = irrad_new.get("useactual")
    loadshape_from_file = irrad_new.get("csv_file")
    loadshape_from_file_path = irrad_new.get("csv_path")
    loadshape_from_file_header = irrad_new.get("headers")
    loadshape_from_file_column = irrad_new.get("column")
    # Property handles
    loadshape_prop = mdl.prop(mask_handle, "loadshape")
    loadshape_int_prop = mdl.prop(mask_handle, "loadshape_int")
    loadshape_hour_prop = mdl.prop(mask_handle, "loadshape_hour")
    useactual_prop = mdl.prop(mask_handle, "useactual")
    loadshape_from_file_prop = mdl.prop(mask_handle, "loadshape_from_file")
    loadshape_from_file_path_prop = mdl.prop(mask_handle, "loadshape_from_file_path")
    loadshape_from_file_header_prop = mdl.prop(mask_handle, "loadshape_from_file_header")
    loadshape_from_file_column_prop = mdl.prop(mask_handle, "loadshape_from_file_column")
    # Set Values
    mdl.set_property_value(loadshape_prop, str(loadshape))
    mdl.set_property_value(loadshape_int_prop, str(loadshape_int))
    mdl.set_property_value(loadshape_hour_prop, str(loadshape_hour))
    mdl.set_property_value(useactual_prop, str(useactual))
    mdl.set_property_value(loadshape_from_file_prop, str(loadshape_from_file))
    mdl.set_property_value(loadshape_from_file_path_prop, str(loadshape_from_file_path))
    mdl.set_property_value(loadshape_from_file_header_prop, str(loadshape_from_file_header))
    mdl.set_property_value(loadshape_from_file_column_prop, str(loadshape_from_file_column))

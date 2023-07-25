def circuit_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:

    """
    # Property Registration
    phases_prop = mdl.prop(container_handle, "phases")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "filter_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == phases_prop:

        comp_handle = mdl.get_parent(container_handle)
        voltage_port = mdl.get_item("Vmeas", parent=comp_handle, item_type="port")
        current_port = mdl.get_item("Imeas", parent=comp_handle, item_type="port")
        modsig_port = mdl.get_item("Mod", parent=comp_handle, item_type="port")
        # For connections
        vtags_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                         for tname in ["goto_vd", "goto_vq", "goto_theta"]]
        vterm_term_handles = [mdl.term(mdl.get_item(tname, parent=comp_handle), "in")
                              for tname in ["term_freq", "term_sinwt"]]
        itag_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                        for tname in ["goto_id", "goto_iq"]]
        term_vpu_handle = mdl.get_item("Vpu", parent=comp_handle)
        term_ipu_handle = mdl.get_item("Ipu", parent=comp_handle)
        from_theta_handle = [mdl.get_item("from_theta", parent=comp_handle, item_type="tag")]
        mod_tag_handle = mdl.get_item("goto_mod", parent=comp_handle, item_type="tag")
        prod_term_handles = [mdl.term(mdl.get_item(pname, parent=comp_handle), "out")
                             for pname in ["Prod_d", "Prod_q"]]
        mod_from_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                            for tname in ["from_zero_mod", "from_theta_mod"]]
        zero_from_handle = mdl.get_item("from_zero_md", parent=comp_handle, item_type="tag")

        if new_value == "1":
            mdl.set_port_properties(voltage_port, term_label="VL")
            mdl.set_port_properties(current_port, term_label="IL")
            mdl.set_port_properties(modsig_port, term_label="mab")
            # Voltage
            pll_voltage_handle = mdl.get_item("Vdq", parent=comp_handle)
            pll_voltage_pos = mdl.get_position(pll_voltage_handle)
            mdl.delete_item(pll_voltage_handle)
            pll_voltage_handle = mdl.create_component("core/Single phase PLL",
                                                      name="Vdq",
                                                      parent=comp_handle,
                                                      position=pll_voltage_pos)
            mdl.set_property_value(mdl.prop(pll_voltage_handle, "scheduling_mode"), "Disable")
            mdl.set_property_value(mdl.prop(pll_voltage_handle, "vd_init"), "1.0")
            pll_out_term_handles = [mdl.term(pll_voltage_handle, tname)
                                    for tname in ["d", "q", "wt", "f", "sin(wt)"]]
            [mdl.create_connection(pll_terms, tag_terms) for
             pll_terms, tag_terms in zip(pll_out_term_handles, vtags_handles+vterm_term_handles)]
            bus_split_v_handle = mdl.get_item("Bus Split V", parent=comp_handle)
            bus_split_v_pos = mdl.get_position(bus_split_v_handle)
            mdl.delete_item(bus_split_v_handle)
            pll_gain_handle = mdl.create_component("core/Gain",
                                                   name="pll_error",
                                                   parent=comp_handle,
                                                   position=bus_split_v_pos)
            mdl.set_property_value(mdl.prop(pll_gain_handle, "gain"), "1/1.1025")
            mdl.create_connection(mdl.term(term_vpu_handle, "out"), mdl.term(pll_gain_handle, "in"))
            mdl.create_connection(mdl.term(pll_gain_handle, "out"), mdl.term(pll_voltage_handle, "In"))
            # Current
            pll_current_handle = mdl.get_item("Idq", parent=comp_handle)
            pll_current_pos = mdl.get_position(pll_current_handle)
            mdl.delete_item(pll_current_handle)
            pll_current_handle = mdl.create_component("core/alpha beta to dq",
                                                      name="Idq",
                                                      parent=comp_handle,
                                                      position=pll_current_pos)
            pll_out_term_handles = [mdl.term(pll_current_handle, tname) for tname in ["d", "q"]]
            [mdl.create_connection(pll_terms, tag_terms)
             for pll_terms, tag_terms in zip(pll_out_term_handles, itag_handles)]
            term_i0 = mdl.get_item("term_i0", parent=comp_handle)
            mdl.delete_item(term_i0)
            ibus_split = mdl.get_item("Bus Split I", parent=comp_handle)
            mdl.delete_item(ibus_split)
            ts_handle = mdl.create_component("core/Discrete Transfer Function",
                                             name="90deg_delay",
                                             parent=comp_handle,
                                             position=[pll_current_pos[0]-128, pll_current_pos[1]])
            mdl.set_property_value(mdl.prop(ts_handle, "a_coeff"), "[1,wref]")
            mdl.set_property_value(mdl.prop(ts_handle, "b_coeff"), "[-1,wref]")
            mdl.set_property_value(mdl.prop(ts_handle, "domain"), "S-domain")
            mdl.set_property_value(mdl.prop(ts_handle, "method"), "Euler")
            mdl.create_connection(mdl.term(term_ipu_handle, "out"), mdl.term(pll_current_handle, "alpha"))
            mdl.create_connection(mdl.term(term_ipu_handle, "out"), mdl.term(ts_handle, "in"))
            mdl.create_connection(mdl.term(ts_handle, "out"), mdl.term(pll_current_handle, "beta"))
            mdl.create_connection(from_theta_handle[0], mdl.term(pll_current_handle, "wt"))
            # Modulation
            mod_handle = mdl.get_item("dq2abc", parent=comp_handle)
            mod_pos = mdl.get_position(mod_handle)
            mdl.delete_item(mod_handle)
            mod_handle = mdl.create_component("core/dq to alpha beta",
                                              name="dq2abc",
                                              parent=comp_handle,
                                              position=mod_pos)
            bus_join_mod_handle = mdl.get_item("Bus Join Mod", parent=comp_handle)
            mdl.set_property_value(mdl.prop(bus_join_mod_handle, "inputs"), "2")
            mod_out_term_handles = [mdl.term(mod_handle, tname) for tname in ["alpha", "beta"]]
            bus_in_term_handles = [mdl.term(bus_join_mod_handle, tname) for tname in ["in", "in1"]]
            [mdl.create_connection(mod_terms, bus_terms)
             for mod_terms, bus_terms in zip(mod_out_term_handles, bus_in_term_handles)]
            mod_in_term_handle = [mdl.term(mod_handle, tname)
                                  for tname in ["d", "q", "wt"]]
            [mdl.create_connection(mod_terms, tag_names)
             for mod_terms, tag_names in zip(mod_in_term_handle, prod_term_handles+[mod_from_handles[1]])]
            bus_zero_md_handle = mdl.get_item("Bus Join Zero", parent=comp_handle)
            mdl.set_property_value(mdl.prop(bus_zero_md_handle, "inputs"), "2")

        elif new_value == "3":
            mdl.set_port_properties(voltage_port, term_label="Vabc")
            mdl.set_port_properties(current_port, term_label="Iabc")
            mdl.set_port_properties(modsig_port, term_label="mabc")
            # Voltage
            pll_voltage_handle = mdl.get_item("Vdq", parent=comp_handle)
            pll_voltage_pos = mdl.get_position(pll_voltage_handle)
            mdl.delete_item(pll_voltage_handle)
            pll_voltage_handle = mdl.create_component("core/Three phase PLL",
                                                      name="Vdq",
                                                      parent=comp_handle,
                                                      position=pll_voltage_pos)
            mdl.set_property_value(mdl.prop(pll_voltage_handle, "enable_zero"), "False")
            mdl.set_property_value(mdl.prop(pll_voltage_handle, "initial_filter_output"), "freq")
            pll_out_term_handles = [mdl.term(pll_voltage_handle, tname)
                                    for tname in ["d_axis", "q_axis", "theta", "freq", "sin_theta"]]
            [mdl.create_connection(pll_terms, tag_terms)
             for pll_terms, tag_terms in zip(pll_out_term_handles, vtags_handles+vterm_term_handles)]
            # WorkAround for the initilization
            bus_split = mdl.get_item("Bus Split V", parent=comp_handle)
            if bus_split:
                bus_pos_ref = mdl.get_position(bus_split)
                mdl.delete_item(bus_split)
            pll_gain_handle = mdl.get_item("pll_error", parent=comp_handle)
            if pll_gain_handle:
                bus_pos_ref = mdl.get_position(pll_gain_handle)
                mdl.delete_item(pll_gain_handle)

            bus_split_v_handle = mdl.create_component("core/Bus Split",
                                                      name="Bus Split V",
                                                      parent=comp_handle,
                                                      position=bus_pos_ref)
            mdl.set_property_value(mdl.prop(bus_split_v_handle, "outputs"), "3")
            bus_split_term_handles = [mdl.term(bus_split_v_handle, tname) for tname in ["out", "out1", "out2"]]
            pll_in_term_handles = [mdl.term(pll_voltage_handle, tname) for tname in ["va", "vb", "vc"]]
            [mdl.create_connection(pll_terms, bus_terms)
             for pll_terms, bus_terms in zip(pll_in_term_handles, bus_split_term_handles)]
            mdl.create_connection(mdl.term(term_vpu_handle, "out"), mdl.term(bus_split_v_handle, "in"))
            # Current
            pll_current_handle = mdl.get_item("Idq", parent=comp_handle)
            pll_current_pos = mdl.get_position(pll_current_handle)
            mdl.delete_item(pll_current_handle)
            pll_current_handle = mdl.create_component("core/abc to dq",
                                                      name="Idq",
                                                      parent=comp_handle,
                                                      position=pll_current_pos)
            ipll_out_terms = [mdl.term(pll_current_handle, tname) for tname in ["d_axis", "q_axis"]]
            [mdl.create_connection(pll_terms, tag_terms)
             for pll_terms, tag_terms in zip(ipll_out_terms, itag_handles)]
            term_io_handle = mdl.get_item("term_i0", parent=comp_handle)
            if term_io_handle:
                mdl.delete_item(term_io_handle)
            term_i0_handle = mdl.create_component("core/Termination",
                                                  name="term_i0",
                                                  parent=comp_handle,
                                                  position=[pll_current_pos[0]+128, pll_current_pos[1]+64])
            mdl.create_connection(mdl.term(pll_current_handle, "zero_axis"), mdl.term(term_i0_handle, "in"))
            ts_handle = mdl.get_item("90deg_delay", parent=comp_handle)
            if ts_handle:
                mdl.delete_item(ts_handle)
            bus_split = mdl.get_item("Bus Split I", parent=comp_handle)
            if bus_split:
                mdl.delete_item(bus_split)
            bus_split_i_handle = mdl.create_component("core/Bus Split",
                                                      name="Bus Split I",
                                                      parent=comp_handle,
                                                      position=[pll_current_pos[0]-128, pll_current_pos[1]-8])
            mdl.set_property_value(mdl.prop(bus_split_i_handle, "outputs"), "3")
            pll_in_term_handles = [mdl.term(pll_current_handle, tname) for tname in ["va", "vb", "vc", "wt"]]
            bus_split_term_handles = [mdl.term(bus_split_i_handle, tname) for tname in ["out", "out1", "out2"]]
            [mdl.create_connection(pll_terms, bus_terms)
             for pll_terms, bus_terms in zip(pll_in_term_handles, bus_split_term_handles+from_theta_handle)]
            mdl.create_connection(mdl.term(term_ipu_handle, "out"), mdl.term(bus_split_i_handle, "in"))
            # Modulation
            mod_handle = mdl.get_item("dq2abc", parent=comp_handle)
            mod_pos = mdl.get_position(mod_handle)
            mdl.delete_item(mod_handle)
            mod_handle = mdl.create_component("core/dq to abc",
                                              name="dq2abc",
                                              parent=comp_handle,
                                              position=mod_pos)
            bus_join_mod_handle = mdl.get_item("Bus Join Mod", parent=comp_handle)
            mdl.set_property_value(mdl.prop(bus_join_mod_handle, "inputs"), "3")
            mod_out_term_handles = [mdl.term(mod_handle, tname) for tname in ["phase_a", "phase_b", "phase_c"]]
            bus_in_term_handles = [mdl.term(bus_join_mod_handle, tname) for tname in ["in", "in1", "in2"]]
            [mdl.create_connection(mod_terms, bus_terms)
             for mod_terms, bus_terms in zip(mod_out_term_handles, bus_in_term_handles)]
            mod_in_term_handle = [mdl.term(mod_handle, tname)
                                  for tname in ["d_input", "q_input", "zero_input", "wt"]]
            [mdl.create_connection(mod_terms, tag_names)
             for mod_terms, tag_names in zip(mod_in_term_handle, prod_term_handles+mod_from_handles)]
            bus_zero_md_handle = mdl.get_item("Bus Join Zero", parent=comp_handle)
            mdl.set_property_value(mdl.prop(bus_zero_md_handle, "inputs"), "3")
            if not mdl.find_connections(zero_from_handle, mdl.term(bus_zero_md_handle, "in2")):
                mdl.create_connection(zero_from_handle, mdl.term(bus_zero_md_handle, "in2"))






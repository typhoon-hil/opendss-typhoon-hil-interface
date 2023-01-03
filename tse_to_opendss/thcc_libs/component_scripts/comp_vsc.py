def inv_control_mode_value_edited(mdl, container_handle, new_value):
    if new_value == "PQ":
        mdl.set_property_disp_value(mdl.prop(container_handle, 'V_ref_str'), "Converter nominal")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'vdc_ref_str'), "Converter nominal")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'fs_ref_str'), "Converter nominal")
        mdl.disable_property(mdl.prop(container_handle, "V_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "V_kp"))
        mdl.disable_property(mdl.prop(container_handle, "V_ki"))
        mdl.disable_property(mdl.prop(container_handle, "vdc_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "vdc_kp"))
        mdl.disable_property(mdl.prop(container_handle, "vdc_ki"))
        mdl.disable_property(mdl.prop(container_handle, "fs_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "Q_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "Q_kp"))
        mdl.enable_property(mdl.prop(container_handle, "Q_ki"))
        mdl.enable_property(mdl.prop(container_handle, "P_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "P_kp"))
        mdl.enable_property(mdl.prop(container_handle, "P_ki"))
    elif new_value == "PV":
        mdl.set_property_disp_value(mdl.prop(container_handle, 'Q_ref_str'), "Converter nominal")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'vdc_ref_str'), "Converter nominal")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'fs_ref_str'), "Converter nominal")
        mdl.disable_property(mdl.prop(container_handle, "Q_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "Q_kp"))
        mdl.disable_property(mdl.prop(container_handle, "Q_ki"))
        mdl.disable_property(mdl.prop(container_handle, "vdc_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "vdc_kp"))
        mdl.disable_property(mdl.prop(container_handle, "vdc_ki"))
        mdl.disable_property(mdl.prop(container_handle, "fs_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "V_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "V_kp"))
        mdl.enable_property(mdl.prop(container_handle, "V_ki"))
        mdl.enable_property(mdl.prop(container_handle, "P_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "P_kp"))
        mdl.enable_property(mdl.prop(container_handle, "P_ki"))
    elif new_value == "Vdc-Vac":
        mdl.set_property_disp_value(mdl.prop(container_handle, 'P_ref_str'), "Converter nominal")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'Q_ref_str'), "Converter nominal")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'fs_ref_str'), "Converter nominal")
        mdl.disable_property(mdl.prop(container_handle, "P_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "P_kp"))
        mdl.disable_property(mdl.prop(container_handle, "P_ki"))
        mdl.disable_property(mdl.prop(container_handle, "Q_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "Q_kp"))
        mdl.disable_property(mdl.prop(container_handle, "Q_ki"))
        mdl.disable_property(mdl.prop(container_handle, "fs_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "V_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "V_kp"))
        mdl.enable_property(mdl.prop(container_handle, "V_ki"))
        mdl.enable_property(mdl.prop(container_handle, "vdc_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "vdc_kp"))
        mdl.enable_property(mdl.prop(container_handle, "vdc_ki"))
    elif new_value == "Vdc-Q":
        mdl.set_property_disp_value(mdl.prop(container_handle, 'P_ref_str'), "Converter nominal")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'V_ref_str'), "Converter nominal")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'fs_ref_str'), "Converter nominal")
        mdl.disable_property(mdl.prop(container_handle, "P_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "P_kp"))
        mdl.disable_property(mdl.prop(container_handle, "P_ki"))
        mdl.disable_property(mdl.prop(container_handle, "V_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "V_kp"))
        mdl.disable_property(mdl.prop(container_handle, "V_ki"))
        mdl.disable_property(mdl.prop(container_handle, "fs_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "Q_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "Q_kp"))
        mdl.enable_property(mdl.prop(container_handle, "Q_ki"))
        mdl.enable_property(mdl.prop(container_handle, "vdc_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "vdc_kp"))
        mdl.enable_property(mdl.prop(container_handle, "vdc_ki"))
    elif new_value == "Grid Forming":
        mdl.set_property_disp_value(mdl.prop(container_handle, 'P_ref_str'), "Converter nominal")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'Q_ref_str'), "Converter nominal")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'vdc_ref_str'), "Converter nominal")
        mdl.disable_property(mdl.prop(container_handle, "P_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "P_kp"))
        mdl.disable_property(mdl.prop(container_handle, "P_ki"))
        mdl.disable_property(mdl.prop(container_handle, "Q_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "Q_kp"))
        mdl.disable_property(mdl.prop(container_handle, "Q_ki"))
        mdl.disable_property(mdl.prop(container_handle, "vdc_ref_str"))
        mdl.disable_property(mdl.prop(container_handle, "vdc_kp"))
        mdl.disable_property(mdl.prop(container_handle, "vdc_ki"))
        mdl.enable_property(mdl.prop(container_handle, "V_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "V_kp"))
        mdl.enable_property(mdl.prop(container_handle, "V_ki"))
        mdl.enable_property(mdl.prop(container_handle, "fs_ref_str"))
    elif new_value == "External Control":
        mdl.enable_property(mdl.prop(container_handle, "P_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "P_kp"))
        mdl.enable_property(mdl.prop(container_handle, "P_ki"))
        mdl.enable_property(mdl.prop(container_handle, "Q_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "Q_kp"))
        mdl.enable_property(mdl.prop(container_handle, "Q_ki"))
        mdl.enable_property(mdl.prop(container_handle, "fs_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "V_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "V_kp"))
        mdl.enable_property(mdl.prop(container_handle, "V_ki"))
        mdl.enable_property(mdl.prop(container_handle, "vdc_ref_str"))
        mdl.enable_property(mdl.prop(container_handle, "vdc_kp"))
        mdl.enable_property(mdl.prop(container_handle, "vdc_ki"))
        mdl.set_property_disp_value(mdl.prop(container_handle, 'P_ref_str'), "External input")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'Q_ref_str'), "External input")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'V_ref_str'), "External input")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'vdc_ref_str'), "External input")
        mdl.set_property_disp_value(mdl.prop(container_handle, 'fs_ref_str'), "External input")


def define_icon(mdl, mask_handle):
    dc_cap = mdl.get_property_value(mdl.prop(mask_handle, "dc_cap_en"))
    if dc_cap:
        mdl.set_component_icon_image(mask_handle, 'images/vsc_cap.svg')
    else:
        mdl.set_component_icon_image(mask_handle, 'images/vsc_nocap.svg')


def toggle_frequency_prop(mdl, mask_handle, init=False):
    frequency_prop = mdl.prop(mask_handle, "Fs")
    global_frequency_prop = mdl.prop(mask_handle, "global_basefreq")
    use_global = mdl.get_property_disp_value(global_frequency_prop)

    if use_global:
        if "simdss_basefreq" in mdl.get_ns_vars():
            mdl.set_property_value(frequency_prop, mdl.get_ns_var("simdss_basefreq"))
            mdl.hide_property(frequency_prop)
        else:
            mdl.set_property_disp_value(global_frequency_prop, False)
            mdl.info("Add a SimDSS component to define the global frequency value.")
    else:
        mdl.show_property(frequency_prop)


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    pass


def update_frequency_property(mdl, mask_handle, init=False):

    frequency_prop = mdl.prop(mask_handle, "Fs")
    global_frequency_prop = mdl.prop(mask_handle, "global_basefreq")
    use_global = mdl.get_property_value(global_frequency_prop)

    if init:
        mdl.hide_property(frequency_prop)
    else:
        if use_global:
            if "simdss_basefreq" in mdl.get_ns_vars():
                mdl.set_property_value(frequency_prop, mdl.get_ns_var("simdss_basefreq"))
            else:
                mdl.set_property_value(global_frequency_prop, False)
        toggle_frequency_prop(mdl, mask_handle, init)


def set_timeseries_switch(mdl, mask_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(mask_handle)

    ref_pos = (5600, 8504)

    if new_value is True:
        ts_switch = mdl.get_item("Ts_switch", parent=comp_handle, item_type="component")
        if not ts_switch:
            ts_switch = mdl.create_component("Constant", parent=comp_handle,
                                             name="Ts_switch", position=(ref_pos[0], ref_pos[1]))
            mdl.set_property_value(mdl.prop(ts_switch, "value"), "Ts_switch")
            mdl.set_property_value(mdl.prop(ts_switch, "execution_rate"), "Tfast")

        port_t = mdl.get_item("T", parent=comp_handle, item_type="port")
        if not port_t:
            port_t = mdl.create_port(parent=comp_handle, name="T", direction="in", kind="sp",
                                     terminal_position=(-40, -88), label="T_series",
                                     position=(ref_pos[0], ref_pos[1] + 128))
        else:
            mdl.set_port_properties(port_t, terminal_position=(50, 0))

        signal_switch = mdl.get_item("Signal switch", parent=comp_handle, item_type="component")
        if not signal_switch:
            signal_switch = mdl.create_component("Signal switch", parent=comp_handle,
                                                 name="Signal switch", position=(ref_pos[0] + 256, ref_pos[1] + 112))
            mdl.set_property_value(mdl.prop(signal_switch, "criterion"), "ctrl >= threshold")
            mdl.set_property_value(mdl.prop(signal_switch, "threshold"), 0.5)

        round_comp = mdl.get_item("Round", parent=comp_handle, item_type="component")
        if not round_comp:
            round_comp = mdl.create_component("Round", parent=comp_handle,
                                              name="Round", position=(ref_pos[0] + 128, ref_pos[1] + 128))
            mdl.set_property_value(mdl.prop(round_comp, "round_fn"), "floor")

        limit = mdl.get_item("Limit", parent=comp_handle, item_type="component")
        if not limit:
            limit = mdl.create_component("Limit", parent=comp_handle,
                                         name="Limit", position=(ref_pos[0] + 376, ref_pos[1] + 112))
            mdl.set_property_value(mdl.prop(limit, "upper_limit"), "T_lim_high")
            mdl.set_property_value(mdl.prop(limit, "lower_limit"), "T_lim_low")

        ts_module = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
        if not ts_module:
            ts_module = mdl.create_component("OpenDSS/TS_module", parent=comp_handle,
                                             name="TS_module", position=(ref_pos[0] + 456, ref_pos[1] + 48),
                                             rotation="left")
        conn_term_list = [(mdl.term(ts_switch, "out"), mdl.term(signal_switch, "in2")),
                          (port_t, mdl.term(signal_switch, "in")),
                          (port_t, mdl.term(round_comp, "in")),
                          (mdl.term(round_comp, "out"), mdl.term(signal_switch, "in1")),
                          (mdl.term(signal_switch, "out"), mdl.term(limit, "in")),
                          (mdl.term(limit, "out"), mdl.term(ts_module, "T"))]
        for conn_term in conn_term_list:
            if len(mdl.find_connections(conn_term[0], conn_term[1])) == 0:
                mdl.create_connection(conn_term[0], conn_term[1])

    else:
        ts_switch = mdl.get_item("Ts_switch", parent=comp_handle, item_type="component")
        if ts_switch:
            mdl.delete_item(ts_switch)

        port_t = mdl.get_item("T", parent=comp_handle, item_type="port")
        if port_t:
            mdl.delete_item(port_t)

        signal_switch = mdl.get_item("Signal switch", parent=comp_handle, item_type="component")
        if signal_switch:
            mdl.delete_item(signal_switch)

        round_comp = mdl.get_item("Round", parent=comp_handle, item_type="component")
        if round_comp:
            mdl.delete_item(round_comp)

        limit = mdl.get_item("Limit", parent=comp_handle, item_type="component")
        if limit:
            mdl.delete_item(limit)

        ts_module = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
        if ts_module:
            mdl.delete_item(ts_module)

    return port_t


def set_control_mode(mdl, container_handle, new_value):

    comp_handle = mdl.get_sub_level_handle(container_handle)

    mode_ext = mdl.get_item("mode", parent=comp_handle, item_type="port")
    mode_inp = mdl.get_item("Gain32", parent=comp_handle, item_type="component")
    term_mode = mdl.get_item("Termination5", parent=comp_handle, item_type="component")
    mode_int = mdl.get_item("From25", parent=comp_handle, item_type="tag")

    if new_value == "External Control":
        if len(mdl.find_connections(mode_int, mdl.term(mode_inp, "in"))) > 0:
            for conn in mdl.find_connections(mode_int, mdl.term(mode_inp, "in")):
                mdl.delete_item(conn)

        if not term_mode:
            term_mode = mdl.create_component("Termination", parent=comp_handle,
                                             name="Termination5", position=(7047, 9200),
                                             hide_name=True)
        if len(mdl.find_connections(mdl.term(term_mode, "in"), mode_int)) == 0:
            mdl.create_connection(mdl.term(term_mode, "in"), mode_int)

        if not mode_ext:
            mode_ext = mdl.create_port(parent=comp_handle, name="mode", direction="in", kind="sp",
                                       terminal_position=(-10, 87),
                                       position=(7120, 9201))
        if len(mdl.find_connections(mdl.term(mode_inp, "in"), mode_ext)) == 0:
            mdl.create_connection(mdl.term(mode_inp, "in"), mode_ext)
    else:
        if mode_ext:
            mdl.delete_item(mode_ext)
        if term_mode:
            mdl.delete_item(term_mode)
        if len(mdl.find_connections(mode_int, mdl.term(mode_inp, "in"))) == 0:
            mdl.create_connection(mdl.term(mode_inp, "in"), mode_int)


def set_external_input(mdl, container_handle, prop_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(container_handle)

    input_dict = {"P_ref_str": {"external_port": {"name": "Pset",
                                                  "position": (6642, 8348),
                                                  "terminal_position": (-10, -87)},
                                "input_comp": {"name": "Sum9"},
                                "input_term": {"name": "Termination1",
                                               "position": (6567, 8352),
                                               "comp_type": "Termination"},
                                "input_tag": {"name": "From11"}},
                  "Q_ref_str": {"external_port": {"name": "Qset",
                                                  "position": (6504, 8753),
                                                  "terminal_position": (25, -87)},
                                "input_comp": {"name": "Sum7"},
                                "input_term": {"name": "Termination2",
                                               "position": (6424, 8751),
                                               "comp_type": "Termination"},
                                "input_tag": {"name": "From10"}},
                  "V_ref_str": {"external_port": {"name": "V_set",
                                                  "position": (6450, 8926),
                                                  "terminal_position": (55, -87)},
                                "input_comp": {"name": "Sum11"},
                                "input_term": {"name": "Termination3",
                                               "position": (6376, 8930),
                                               "comp_type": "Termination"},
                                "input_tag": {"name": "From15"}},
                  "vdc_ref_str": {"external_port": {"name": "vdc_set",
                                                    "position": (6695, 8660),
                                                    "terminal_position": (25, 87)},
                                  "input_comp": {"name": "Gain30"},
                                  "input_term": {"name": "Termination4",
                                                 "position": (6621, 8663),
                                                 "comp_type": "Termination"},
                                  "input_tag": {"name": "From22"}},
                  "fs_ref_str": {"external_port": {"name": "fs_set",
                                                   "position": (6893, 8248),
                                                   "terminal_position": (55, 87)},
                                 "input_comp": {"name": "Gain33"},
                                 "input_term": {"name": "Termination8",
                                                "position": (6767, 8247),
                                                "comp_type": "Termination"},
                                 "input_tag": {"name": "From44"}},
                  }

    prop_name = mdl.get_property_type_attributes(prop_handle)["name"]

    external_port = mdl.get_item(input_dict[prop_name]["external_port"]["name"],
                                 parent=comp_handle, item_type="port")
    input_comp = mdl.get_item(input_dict[prop_name]["input_comp"]["name"],
                              parent=comp_handle, item_type="component")
    input_term = mdl.get_item(input_dict[prop_name]["input_term"]["name"],
                              parent=comp_handle, item_type="component")
    input_tag = mdl.get_item(input_dict[prop_name]["input_tag"]["name"],
                             parent=comp_handle, item_type="tag")

    if new_value == "External input":
        if len(mdl.find_connections(input_tag, mdl.term(input_comp, "in"))) > 0:
            for conn in mdl.find_connections(input_tag, mdl.term(input_comp, "in")):
                mdl.delete_item(conn)

        if not input_term:
            input_term = mdl.create_component(input_dict[prop_name]["input_term"]["comp_type"], parent=comp_handle,
                                              name=input_dict[prop_name]["input_term"]["name"],
                                              position=input_dict[prop_name]["input_term"]["position"],
                                              hide_name=True)
            mdl.create_connection(mdl.term(input_term, "in"), input_tag)

        if not external_port:
            external_port = mdl.create_port(parent=comp_handle, name=input_dict[prop_name]["external_port"]["name"],
                                            direction="in", kind="sp",
                                            terminal_position=input_dict[prop_name]["external_port"]["terminal_"
                                                                                                     "position"],
                                            position=input_dict[prop_name]["external_port"]["position"])
            mdl.create_connection(mdl.term(input_comp, "in"), external_port)
    elif new_value == "Converter nominal":

        if external_port:
            mdl.delete_item(external_port)
        if input_term:
            mdl.delete_item(input_term)

        if len(mdl.find_connections(input_tag, mdl.term(input_comp, "in"))) == 0:
            mdl.create_connection(mdl.term(input_comp, "in"), input_tag)


def enable_time_series(mdl, container_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(container_handle)

    pref_in = mdl.get_item("Constant22", parent=comp_handle, item_type="component")
    qref_in = mdl.get_item("Constant23", parent=comp_handle, item_type="component")
    pref_tag = mdl.get_item("Goto10", parent=comp_handle, item_type="tag")
    qref_tag = mdl.get_item("Goto11", parent=comp_handle, item_type="tag")
    pref_term = mdl.get_item("pref_term", parent=comp_handle, item_type="component")
    qref_term = mdl.get_item("qref_term", parent=comp_handle, item_type="component")

    pos_ref = (6112, 8384)

    if new_value:

        set_timeseries_switch(mdl, container_handle, True)

        ts_module = mdl.get_item("TS_module", parent=comp_handle, item_type="component")

        if len(mdl.find_connections(mdl.term(pref_in, "out"), pref_tag)) > 0:
            for conn in mdl.find_connections(mdl.term(pref_in, "out"), pref_tag):
                mdl.delete_item(conn)
        if len(mdl.find_connections(mdl.term(qref_in, "out"), qref_tag)) > 0:
            for conn in mdl.find_connections(mdl.term(qref_in, "out"), qref_tag):
                mdl.delete_item(conn)

        if len(mdl.find_connections(mdl.term(ts_module, "P"), pref_tag)) == 0:
            mdl.create_connection(mdl.term(ts_module, "P"), pref_tag)
        if len(mdl.find_connections(mdl.term(ts_module, "Q"), qref_tag)) == 0:
            mdl.create_connection(mdl.term(ts_module, "Q"), qref_tag)

        mdl.set_position(pref_tag, pos_ref)
        mdl.set_position(qref_tag, (pos_ref[0], pos_ref[1] + 40))

        if not pref_term:
            pref_term = mdl.create_component("Termination", name="pref_term", position=(pos_ref[0] + 216, pos_ref[1]),
                                             parent=comp_handle, hide_name=True)

        if not qref_term:
            qref_term = mdl.create_component("Termination", name="qref_term",
                                             position=(pos_ref[0] + 216, pos_ref[1] + 40),
                                             parent=comp_handle, hide_name=True)

        if len(mdl.find_connections(mdl.term(pref_in, "out"), mdl.term(pref_term, "in"))) == 0:
            mdl.create_connection(mdl.term(pref_in, "out"), mdl.term(pref_term, "in"))
        if len(mdl.find_connections(mdl.term(qref_in, "out"), mdl.term(qref_term, "in"))) == 0:
            mdl.create_connection(mdl.term(qref_in, "out"), mdl.term(qref_term, "in"))

    else:
        set_timeseries_switch(mdl, container_handle, False)

        if pref_term:
            mdl.delete_item(pref_term)
        if qref_term:
            mdl.delete_item(qref_term)

        if len(mdl.find_connections(mdl.term(pref_in, "out"), pref_tag)) == 0:
            mdl.create_connection(mdl.term(pref_in, "out"), pref_tag)
        if len(mdl.find_connections(mdl.term(qref_in, "out"), qref_tag)) == 0:
            mdl.create_connection(mdl.term(qref_in, "out"), qref_tag)

        mdl.set_position(pref_tag, (pos_ref[0] + 216, pos_ref[1]))
        mdl.set_position(qref_tag, (pos_ref[0] + 216, pos_ref[1] + 40))


def place_internal_dc_capacitor(mdl, container_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(container_handle)

    mdl.refresh_icon(container_handle)

    if new_value:
        c_dc = mdl.get_item("dccap", parent=comp_handle, item_type="component")
        dc_p_port = mdl.get_item("Junction121", parent=comp_handle, item_type="junction")
        dc_n_port = mdl.get_item("Junction120", parent=comp_handle, item_type="junction")
        if not c_dc:
            c_dc = mdl.create_component("Capacitor", parent=comp_handle, name="dccap", position=(7709, 9516),
                                        rotation="right")
            mdl.set_property_value(mdl.prop(c_dc, "capacitance"), "dc_cap")
            mdl.set_property_value(mdl.prop(c_dc, "initial_voltage"), "1000*vdc_set")
            mdl.create_connection(mdl.term(c_dc, "p_node"), dc_p_port, name="dcConnp")
            mdl.create_connection(mdl.term(c_dc, "n_node"), dc_n_port, name="dcConnn")

    else:
        c_dc = mdl.get_item("dccap", parent=comp_handle, item_type="component")
        if c_dc:
            mdl.delete_item(c_dc)


def enable_time_series_value_edited(mdl, container_handle, new_value):
    prop_list = ["ctrl_mode_str",
                 "P_ref_str",
                 "Q_ref_str",
                 "V_ref_str",
                 "vdc_ref_str",
                 "fs_ref_str"]

    if new_value:
        for prop_name in prop_list:
            if prop_name != "ctrl_mode_str":
                mdl.set_property_value(mdl.prop(container_handle, prop_name), "Converter nominal")
            else:
                mdl.set_property_value(mdl.prop(container_handle, prop_name), "PQ")

            mdl.disable_property(mdl.prop(container_handle, prop_name))

    else:
        for prop_name in prop_list:
            mdl.enable_property(mdl.prop(container_handle, prop_name))


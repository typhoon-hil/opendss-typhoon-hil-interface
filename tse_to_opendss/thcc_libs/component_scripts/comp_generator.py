from typhoon.api.schematic_editor.const import ITEM_CONNECTION, ITEM_PORT, ITEM_COMPONENT
from typhoon.api.schematic_editor.exception import SchApiException


def components_and_connections(mdl, mask_handle, created_ports, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_sub_level_handle(mask_handle)

    new_value = mdl.get_property_value(caller_prop_handle)

    if mdl.get_name(caller_prop_handle) == "Init_En":
        if new_value is True:
            try:
                vfd00 = created_ports.get("Vfd0")
                tm00 = created_ports.get("Tm00")
                vfd_pre = mdl.get_item("Junction184", parent=comp_handle, item_type="junction")
                tm_pre = mdl.get_item("Junction178", parent=comp_handle, item_type="junction")
                mdl.create_connection(vfd_pre, vfd00)
                mdl.create_connection(tm_pre, tm00)

            except SchApiException:
                pass

        mdl.refresh_icon(mask_handle)

    elif mdl.get_name(caller_prop_handle) == "gen_ts_en":
        s_mode = mdl.get_property_disp_value(mdl.prop(mask_handle, "S_Ts_mode"))
        bus_join = mdl.get_item("Bus Join4", parent=comp_handle)

        if new_value:

            const = mdl.get_item("Constant33", parent=comp_handle, item_type=ITEM_COMPONENT)
            if const:
                mdl.delete_item(const)
            # Create the constant
            const_102 = mdl.create_component(type_name="core/Constant",
                                             name="Constant102",
                                             parent=comp_handle,
                                             position=(6200, 8536))
            mdl.set_property_value(mdl.prop(const_102, "value"), "Ts_switch")
            mdl.set_property_value(mdl.prop(const_102, "execution_rate"), "Ts")
            mdl.set_property_value(mdl.prop(const_102, "signal_type"), "real")
            # Create Ts_Switch subsystem (used a try/except just to separate the subsystem components)
            try:
                ts_subsystem = mdl.create_component(type_name="core/Subsystem",
                                                    name="T_switch",
                                                    parent=comp_handle,
                                                    position=(6320, 8504),
                                                    size=(72, 64))
                port1 = mdl.get_item("P1", parent=ts_subsystem, item_type=ITEM_PORT)
                if port1:
                    mdl.delete_item(port1)
                port2 = mdl.get_item("P2", parent=ts_subsystem, item_type=ITEM_PORT)
                if port2:
                    mdl.delete_item(port2)
                port_t = mdl.create_port(name="T",
                                         parent=ts_subsystem,
                                         terminal_position=("left", 1),
                                         kind="sp",
                                         sp_type="auto",
                                         position=(7424, 8040),
                                         direction="in")
                port_t_out = mdl.create_port(name="T_out",
                                             parent=ts_subsystem,
                                             terminal_position=("right", 1),
                                             kind="sp",
                                             sp_type="inherit",
                                             position=(7784, 8056),
                                             direction="out")
                port_mode = mdl.create_port(name="mode",
                                            parent=ts_subsystem,
                                            terminal_position=("left", 2),
                                            kind="sp",
                                            sp_type="inherit",
                                            position=(7536, 7984),
                                            direction="in")
                comp_round = mdl.create_component(type_name="core/Round",
                                                  name="Round1",
                                                  parent=ts_subsystem,
                                                  position=(7536, 8072))
                comp_limit = mdl.create_component(type_name="core/Limit",
                                                  name="Limit1",
                                                  parent=ts_subsystem,
                                                  position=(7704, 8056))
                mdl.set_property_value(mdl.prop(comp_limit, "lower_limit"), "T_lim_low")
                mdl.set_property_value(mdl.prop(comp_limit, "upper_limit"), "T_lim_high")
                ts_select = mdl.create_component(type_name="core/Signal switch",
                                                 name="Signal switch1",
                                                 parent=ts_subsystem,
                                                 position=(7632, 8056))
                mdl.set_property_value(mdl.prop(ts_select, "criterion"), "ctrl >= threshold")
                mdl.set_property_value(mdl.prop(ts_select, "threshold"), "0.5")
                mdl.create_connection(port_t, mdl.term(ts_select, "in"))
                mdl.create_connection(port_t, mdl.term(comp_round, "in"))
                mdl.create_connection(mdl.term(comp_round, "out"), mdl.term(ts_select, "in1"))
                mdl.create_connection(port_mode, mdl.term(ts_select, "in2"))
                mdl.create_connection(mdl.term(ts_select, "out"), mdl.term(comp_limit, "in"))
                mdl.create_connection(mdl.term(comp_limit, "out"), port_t_out)

            except:
                pass

            ts_module = mdl.create_component(type_name="OpenDSS/TS_module",
                                             parent=comp_handle,
                                             name="TS_module",
                                             position=(6440, 8504))
            # resetting properties avoiding errors from the ts_component modifications
            mdl.set_property_value(mdl.prop(ts_module, "P_nom"), "kw")
            mdl.set_property_value(mdl.prop(ts_module, "Q_nom"), "kvar")
            mdl.set_property_value(mdl.prop(ts_module, "S_vec"), "S_Ts")
            mdl.set_property_value(mdl.prop(ts_module, "P_mode"), "Manual input")
            mdl.set_property_value(mdl.prop(ts_module, "T_vec"), "T_Ts_internal")
            mdl.set_property_value(mdl.prop(ts_module, "Tmax"), "T_Ts_max")
            mdl.set_property_value(mdl.prop(ts_module, "Tdel"), "del_Ts + Mech_En")
            mdl.set_property_value(mdl.prop(ts_module, "Texec"), "Ts")
            ext_port = mdl.get_item("T", parent=comp_handle, item_type=ITEM_PORT)
            mdl.create_connection(ext_port, mdl.term(ts_subsystem, "T"))
            mdl.create_connection(mdl.term(const_102, "out"), mdl.term(ts_subsystem, "mode"))
            mdl.create_connection(mdl.term(ts_subsystem, "T_out"), mdl.term(ts_module, "T"))
            mdl.create_connection(mdl.term(ts_module, "P"), mdl.term(bus_join, "in9"))
            mdl.create_connection(mdl.term(ts_module, "Q"), mdl.term(bus_join, "in10"))

            # s_mode has only Manual input combo (I'll disable it for while)
            """
            if s_mode == "Manual input":
                mdl.set_property_value(mdl.prop(ts_mdl, "P_mode"), "Manual input")
                t_ext = created_ports.get("T")
                if not conn_ts_in:
                    mdl.create_connection(mdl.term(ts_select, "T"), t_ext, "ConnTs")

            conn_tsp_int = mdl.get_item("ConnTsP", parent=comp_handle, item_type=ITEM_CONNECTION)
            conn_tsq_int = mdl.get_item("ConnTsQ", parent=comp_handle, item_type=ITEM_CONNECTION)

            if not conn_tsp_int:
                mdl.create_connection(mdl.term(p_inp, "in9"), mdl.term(ts_mdl, "P"), "ConnTsP")
            if not conn_tsq_int:
                mdl.create_connection(mdl.term(p_inp, "in10"), mdl.term(ts_mdl, "Q"), "ConnTsQ")
            """
        else:
            const_102 = mdl.get_item("Constant102", parent=comp_handle, item_type=ITEM_COMPONENT)
            if const_102:
                mdl.delete_item(const_102)
            ts_module = mdl.get_item("TS_module", parent=comp_handle, item_type=ITEM_COMPONENT)
            if ts_module:
                mdl.delete_item(ts_module)
            ts_subs = mdl.get_item("T_switch", parent=comp_handle, item_type=ITEM_COMPONENT)
            if ts_subs:
                mdl.delete_item(ts_subs)

            const_33 = mdl.get_item("Constant33", parent=comp_handle)
            if not const_33:
                const_33 = mdl.create_component(type_name="core/Constant",
                                                name="Constant33",
                                                parent=comp_handle,
                                                position=(6472, 8400))
                mdl.set_property_value(mdl.prop(const_33, "value"), "0")
                mdl.set_property_value(mdl.prop(const_33, "execution_rate"), "Ts")
                mdl.create_connection(mdl.term(const_33, "out"), mdl.term(bus_join, "in10"))
                mdl.create_connection(mdl.term(const_33, "out"), mdl.term(bus_join, "in9"))

    elif mdl.get_name(caller_prop_handle) == "S_Ts_mode":
        gen_en = mdl.get_property_disp_value(mdl.prop(mask_handle, "gen_ts_en"))

        if gen_en:
            ts_mdl = mdl.get_item("TS_module", parent=comp_handle, item_type=ITEM_COMPONENT)
            conn_ts_in = mdl.get_item("ConnTs", parent=comp_handle, item_type=ITEM_CONNECTION)
            if new_value == "Manual input":
                mdl.set_property_value(mdl.prop(ts_mdl, "P_mode"), "Manual input")
                t_ext = created_ports.get("T")
                if not conn_ts_in:
                    mdl.create_connection(mdl.term(ts_mdl, "T"), t_ext, "ConnTs")


def toggle_frequency_prop(mdl, mask_handle, init=False):
    frequency_prop = mdl.prop(mask_handle, "basefreq")
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

    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    if caller_prop_handle:
        new_value = mdl.get_property_value(caller_prop_handle)

        if mdl.get_name(caller_prop_handle) == "Init_En":
            if new_value is True:
                try:
                    Vfd00 = mdl.create_port(
                        name="Vfd0",
                        parent=comp_handle,
                        label="Vfd0",
                        kind="sp",
                        direction="out",
                        terminal_position=(-88, -51),
                        position=(5968, 7640)
                    )
                    created_ports.update({"Vfd0": Vfd00})
                    Tm00 = mdl.create_port(
                        name="Tm0",
                        parent=comp_handle,
                        label="Tm0",
                        kind="sp",
                        direction="out",
                        terminal_position=(-88, -65),
                        position=(5936, 7824)
                    )
                    created_ports.update({"Tm00": Tm00})

                except SchApiException:
                    pass

            elif new_value is False:
                Vfd00 = mdl.get_item("Vfd0", parent=comp_handle, item_type=ITEM_PORT)
                Tm00 = mdl.get_item("Tm0", parent=comp_handle, item_type=ITEM_PORT)
                if Vfd00:
                    mdl.delete_item(Vfd00)
                    deleted_ports.append("Vfd00")
                if Tm00:
                    mdl.delete_item(Tm00)
                    deleted_ports.append("Tm00")

        elif mdl.get_name(caller_prop_handle) == "gen_ts_en":
            s_mode = mdl.get_property_disp_value(mdl.prop(mask_handle, "S_Ts_mode"))
            t_ext = mdl.get_item("T", parent=comp_handle, item_type=ITEM_PORT)

            if new_value:
                if s_mode == "Manual input":
                    if not t_ext:
                        t_ext = mdl.create_port(parent=comp_handle,
                                                name="T",
                                                direction="in",
                                                kind="sp",
                                                terminal_position=(-88, 40),
                                                position=(6200, 8477),
                                                label="T_series")
                        created_ports.update({"T": t_ext})
                else:
                    if t_ext:
                        deleted_ports.append(mdl.get_name(t_ext))
                        mdl.delete_item(t_ext)
            else:
                if t_ext:
                    deleted_ports.append(mdl.get_name(t_ext))
                    mdl.delete_item(t_ext)

        elif mdl.get_name(caller_prop_handle) == "S_Ts_mode":
            gen_en = mdl.get_property_disp_value(mdl.prop(mask_handle, "gen_ts_en"))
            t_ext = mdl.get_item("T", parent=comp_handle, item_type=ITEM_PORT)

            if gen_en:
                if new_value == "Manual input":
                    if not t_ext:
                        t_ext = mdl.create_port(parent=comp_handle, name="T", direction="in", kind="sp",
                                                terminal_position=(-88, 40),
                                                position=(6200, 8477))
                        created_ports.update({"T": t_ext})
                else:
                    if t_ext:
                        deleted_ports.append(mdl.get_name(t_ext))
                        mdl.delete_item(t_ext)
            else:
                if t_ext:
                    deleted_ports.append(mdl.get_name(t_ext))
                    mdl.delete_item(t_ext)

    return created_ports, deleted_ports


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):

    if caller_prop_handle:

        new_value = mdl.get_property_disp_value(caller_prop_handle)

        if mdl.get_name(caller_prop_handle) == "S_Ts_mode":

            if new_value == "Manual input":
                mdl.disable_property(mdl.prop(mask_handle, "T_Ts_max"))
                mdl.disable_property(mdl.prop(mask_handle, "del_Ts"))
                mdl.enable_property(mdl.prop(mask_handle, "T_Ts"))
            else:
                mdl.enable_property(mdl.prop(mask_handle, "T_Ts_max"))
                mdl.enable_property(mdl.prop(mask_handle, "del_Ts"))
                mdl.disable_property(mdl.prop(mask_handle, "T_Ts"))

        elif mdl.get_name(caller_prop_handle) == "T_mode":
            if new_value == "Time":
                mdl.enable_property(mdl.prop(mask_handle, "T_Ts"))
            else:
                mdl.disable_property(mdl.prop(mask_handle, "T_Ts"))

        elif mdl.get_name(caller_prop_handle) == "global_basefreq":
            toggle_frequency_prop(mdl, mask_handle)

        elif mdl.get_name(caller_prop_handle) == "gen_ts_en":
            if new_value:
                mdl.set_property_disp_value(mdl.prop(mask_handle, "G_mod"), "Constant kW")
                mdl.disable_property(mdl.prop(mask_handle, "G_mod"))
            else:
                mdl.enable_property(mdl.prop(mask_handle, "G_mod"))


def update_frequency_property(mdl, mask_handle, init=False):

    frequency_prop = mdl.prop(mask_handle, "basefreq")
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


def define_icon(mdl, mask_handle):
    mdl.set_component_icon_image(mask_handle, 'images/mchn_wrsync_generic2.svg')

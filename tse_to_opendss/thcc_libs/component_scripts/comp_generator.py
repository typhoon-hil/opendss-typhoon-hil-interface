def components_and_connections(mdl, mask_handle, created_ports, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_sub_level_handle(mask_handle)

    from typhoon.api.schematic_editor.const import ITEM_CONNECTION, ITEM_PORT, ITEM_COMPONENT
    from typhoon.api.schematic_editor.exception import SchApiException

    new_value = mdl.get_property_value(caller_prop_handle)

    if mdl.get_name(caller_prop_handle) == "Init_En":
        if new_value is True:
            try:
                Vfd00 = created_ports.get("Vfd0")
                Tm00 = created_ports.get("Tm00")
                Vfd_pre = mdl.get_item("Junction184", parent=comp_handle, item_type="junction")
                Tm_pre = mdl.get_item("Junction178", parent=comp_handle, item_type="junction")
                mdl.create_connection(Vfd_pre, Vfd00)
                mdl.create_connection(Tm_pre, Tm00)

            except SchApiException:
                pass

        mdl.refresh_icon(mask_handle)

    elif mdl.get_name(caller_prop_handle) == "gen_ts_en":
        S_mode = mdl.get_property_disp_value(mdl.prop(mask_handle, "S_Ts_mode"))

        if new_value:
            nulls = mdl.get_item("Constant33", parent=comp_handle, item_type=ITEM_COMPONENT)
            TSmdl = mdl.get_item("TS_module", parent=comp_handle, item_type=ITEM_COMPONENT)
            Ts_select = mdl.get_item("T_switch", parent=comp_handle, item_type=ITEM_COMPONENT)
            Ts_select1 = mdl.get_item("Constant102", parent=comp_handle, item_type=ITEM_COMPONENT)
            conn_Ts_in = mdl.get_item("ConnTs", parent=comp_handle, item_type=ITEM_CONNECTION)
            conn_P_int = mdl.get_item("connP", parent=comp_handle, item_type=ITEM_CONNECTION)
            conn_Q_int = mdl.get_item("connQ", parent=comp_handle, item_type=ITEM_CONNECTION)
            P_inp = mdl.get_item("Bus Join4", parent=comp_handle, item_type=ITEM_COMPONENT)

            if conn_P_int:
                mdl.delete_item(conn_P_int)
            if conn_Q_int:
                mdl.delete_item(conn_Q_int)

            mdl.enable_items(TSmdl)
            mdl.enable_items(Ts_select)
            mdl.enable_items(Ts_select1)
            mdl.disable_items(nulls)
            if S_mode == "Manual input":
                mdl.set_property_value(mdl.prop(TSmdl, "P_mode"), "Manual input")
                T_ext = created_ports.get("T")
                if not conn_Ts_in:
                    mdl.create_connection(mdl.term(Ts_select, "T"), T_ext, "ConnTs")

            conn_TsP_int = mdl.get_item("ConnTsP", parent=comp_handle, item_type=ITEM_CONNECTION)
            conn_TsQ_int = mdl.get_item("ConnTsQ", parent=comp_handle, item_type=ITEM_CONNECTION)

            if not conn_TsP_int:
                mdl.create_connection(mdl.term(P_inp, "in9"), mdl.term(TSmdl, "P"), "ConnTsP")
            if not conn_TsQ_int:
                mdl.create_connection(mdl.term(P_inp, "in10"), mdl.term(TSmdl, "Q"), "ConnTsQ")
        else:
            nulls = mdl.get_item("Constant33", parent=comp_handle, item_type=ITEM_COMPONENT)
            TSmdl = mdl.get_item("TS_module", parent=comp_handle, item_type=ITEM_COMPONENT)
            Ts_select = mdl.get_item("T_switch", parent=comp_handle, item_type=ITEM_COMPONENT)
            Ts_select1 = mdl.get_item("Constant102", parent=comp_handle, item_type=ITEM_COMPONENT)
            conn_P_int = mdl.get_item("connP", parent=comp_handle, item_type=ITEM_CONNECTION)
            conn_Q_int = mdl.get_item("connQ", parent=comp_handle, item_type=ITEM_CONNECTION)
            conn_TsP_int = mdl.get_item("ConnTsP", parent=comp_handle, item_type=ITEM_CONNECTION)
            conn_TsQ_int = mdl.get_item("ConnTsQ", parent=comp_handle, item_type=ITEM_CONNECTION)
            P_inp = mdl.get_item("Bus Join4", parent=comp_handle, item_type=ITEM_COMPONENT)

            mdl.set_property_value(mdl.prop(TSmdl, "P_mode"), "Manual input")

            if conn_TsP_int:
                mdl.delete_item(conn_TsP_int)
            if conn_TsQ_int:
                mdl.delete_item(conn_TsQ_int)

            if conn_P_int:
                mdl.delete_item(conn_P_int)
            if conn_Q_int:
                mdl.delete_item(conn_Q_int)

            mdl.enable_items(nulls)
            mdl.disable_items(TSmdl)
            mdl.disable_items(Ts_select)
            mdl.disable_items(Ts_select1)

            mdl.create_connection(mdl.term(P_inp, "in9"), mdl.term(nulls, "out"), "connP")
            mdl.create_connection(mdl.term(P_inp, "in10"), mdl.term(nulls, "out"), "connQ")

    elif mdl.get_name(caller_prop_handle) == "S_Ts_mode":
        gen_en = mdl.get_property_disp_value(mdl.prop(mask_handle, "gen_ts_en"))

        if gen_en:
            TSmdl = mdl.get_item("TS_module", parent=comp_handle, item_type=ITEM_COMPONENT)
            conn_Ts_in = mdl.get_item("ConnTs", parent=comp_handle, item_type=ITEM_CONNECTION)
            if new_value == "Manual input":
                mdl.set_property_value(mdl.prop(TSmdl, "P_mode"), "Manual input")
                T_ext = created_ports.get("T")
                if not conn_Ts_in:
                    mdl.create_connection(mdl.term(TSmdl, "T"), T_ext, "ConnTs")

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

    from typhoon.api.schematic_editor.const import ITEM_PORT
    from typhoon.api.schematic_editor.exception import SchApiException

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
            S_mode = mdl.get_property_disp_value(mdl.prop(mask_handle, "S_Ts_mode"))
            T_ext = mdl.get_item("T", parent=comp_handle, item_type=ITEM_PORT)

            if new_value:
                if S_mode == "Manual input":
                    if not T_ext:
                        T_ext = mdl.create_port(parent=comp_handle, name="T", direction="in", kind="sp",
                                                terminal_position=(-88, 40),
                                                position=(6200, 8477))
                        created_ports.update({"T": T_ext})
                else:
                    if T_ext:
                        deleted_ports.append(mdl.get_name(T_ext))
                        mdl.delete_item(T_ext)
            else:
                if T_ext:
                    deleted_ports.append(mdl.get_name(T_ext))
                    mdl.delete_item(T_ext)

        elif mdl.get_name(caller_prop_handle) == "S_Ts_mode":
            gen_en = mdl.get_property_disp_value(mdl.prop(mask_handle, "gen_ts_en"))
            T_ext = mdl.get_item("T", parent=comp_handle, item_type=ITEM_PORT)

            if gen_en:
                if new_value == "Manual input":
                    if not T_ext:
                        T_ext = mdl.create_port(parent=comp_handle, name="T", direction="in", kind="sp",
                                                terminal_position=(-88, 40),
                                                position=(6200, 8477))
                        created_ports.update({"T": T_ext})
                else:
                    if T_ext:
                        deleted_ports.append(mdl.get_name(T_ext))
                        mdl.delete_item(T_ext)
            else:
                if T_ext:
                    deleted_ports.append(mdl.get_name(T_ext))
                    mdl.delete_item(T_ext)

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

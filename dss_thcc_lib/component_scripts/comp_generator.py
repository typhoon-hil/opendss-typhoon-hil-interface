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
            mdl.set_property_value(mdl.prop(const_102, "execution_rate"), "execution_rate")
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
            mdl.set_property_value(mdl.prop(ts_module, "Texec"), "execution_rate")
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
                mdl.set_property_value(mdl.prop(const_33, "execution_rate"), "execution_rate")
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
    frequency_prop = mdl.prop(mask_handle, "baseFreq")
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
                        terminal_position=(-48, 48),
                        position=(5968, 7640)
                    )
                    created_ports.update({"Vfd0": Vfd00})
                    Tm00 = mdl.create_port(
                        name="Tm0",
                        parent=comp_handle,
                        label="Tm0",
                        kind="sp",
                        direction="out",
                        terminal_position=(-48, 32),
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
                                                terminal_position=(-48, 32),
                                                position=(6200, 8477),
                                                label="t")
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
                                                terminal_position=(-48, 64),
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

    frequency_prop = mdl.prop(mask_handle, "baseFreq")
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
    mdl.set_component_icon_image(mask_handle, 'images/generator.svg')


def generator_pre_compile_function(mdl, item_handle, prop_dict):
    import numpy

    pp = 60 * prop_dict["baseFreq"] / prop_dict["nom_rpm"]

    if prop_dict["Init_En"] is True:
        init_switch = 1
    else:
        init_switch = 0

    phases = 3

    if prop_dict["gen_ts_en"]:
        gen_ts_en_bit = 1
    else:
        gen_ts_en_bit = 0

    dssnpts = len(prop_dict["S_Ts"])

    s_ts = prop_dict["loadshape"]
    dss_t = prop_dict["loadshape_int"]
    s_len = len(s_ts)

    if prop_dict["T_mode"] == "Time":
        t_ts_internal = [t_val for t_val in prop_dict["T_Ts"]]
    else:
        t_ts_internal = [x for x in range(s_len)]

    t_lim_low = t_ts_internal[0]
    t_lim_high = t_ts_internal[-1]

    if prop_dict["T_mode"] == "Time":
        ts_switch = 1
    else:
        ts_switch = 0

    if prop_dict["G_mod"] == "Constant kW":
        model = 1
    elif prop_dict["G_mod"] == "Constant admittance":
        model = 2
    elif prop_dict["G_mod"] == "Constant kW, Constant kV":
        model = 3
    elif prop_dict["G_mod"] == "Constant kW, Fixed Q":
        model = 4
    elif prop_dict["G_mod"] == "Constant kW, Fixed Q (constant reactance)":
        model = 5
    else:
        model = 3

    kw = prop_dict["pf"] * prop_dict["kVA"]
    kvar = prop_dict["kVA"] * ((1 - prop_dict["pf"] ** 2) ** 0.5)

    ws = prop_dict["baseFreq"] * 2 * numpy.pi
    ws_inv = 1 / ws
    z_base = 1000 * (prop_dict["kv"] ** 2) / prop_dict["kVA"]

    rs = 0.01 * z_base
    lmd = prop_dict["Xd"] * z_base / ws
    lmq = lmd
    lls = 0.05 * lmd
    llfd = (((prop_dict["Xdp"] * z_base / ws) - lls) * lmd) / (lmd - ((prop_dict["Xdp"] * z_base / ws) - lls))
    llkd = (((prop_dict["Xdpp"] * z_base / ws) - lls) * llfd) / (llfd - ((prop_dict["Xdpp"] * z_base / ws) - lls))

    rfd = (prop_dict["Xdp"] * z_base) / prop_dict["XRdp"]
    rkd = (prop_dict["Xdpp"] * z_base) / prop_dict["XRdp"]

    llkq = llkd
    llkq2 = llkq
    rkq = rkd
    rkq2 = rkq

    moment_of_inertia = prop_dict["H"] * 1000 * prop_dict["kVA"] / (0.5 * (ws / pp) * (ws / pp))

    w_base = ws / 2
    trq_base = 1000 * prop_dict["kVA"] / w_base

    lmzq = 1 / (1 / lmq + 1 / llkq + 1 / llkq2)
    lmzd = 1 / (1 / lmd + 1 / llkd + 1 / llfd)

    a_matrix = [[(rkq / llkq) * ((lmzq / llkq) - 1), rkq * lmzq / (llkq * llkq2), 0, 0],
                [rkq2 * lmzq / (llkq * llkq2), (rkq2 / llkq2) * ((lmzq / llkq2) - 1), 0, 0],
                [0, 0, (rkd / llkd) * ((lmzd / llkd) - 1), rkd * lmzd / (llkd * llfd)],
                [0, 0, rfd * lmzd / (llkd * llfd), (rfd / llfd) * ((lmzd / llfd) - 1)]]
    b_matrix = [[rkq * lmzq / llkq, 0, 0],
                [rkq2 * lmzq / llkq2, 0, 0],
                [0, rkd * lmzd / llkd, 0],
                [0, rfd * lmzd / llfd, 1]]

    a_matrix = numpy.matrix(a_matrix)
    b_matrix = numpy.matrix(b_matrix)

    d_a_matrix = numpy.linalg.inv((numpy.eye(4) -
                                   (0.5 * prop_dict["execution_rate"]) *
                                   a_matrix)) * (numpy.eye(4) + (0.5 * prop_dict["execution_rate"]) * a_matrix)
    d_b_matrix = numpy.linalg.inv((numpy.eye(4) -
                                   (0.5 * prop_dict["execution_rate"])
                                   * a_matrix)) * (prop_dict["execution_rate"] * b_matrix)
    for row in range(d_a_matrix.shape[0]):
        for column in range(d_a_matrix.shape[1]):
            mdl.set_property_value(mdl.prop(item_handle, f"dA{row + 1}{column + 1}"), d_a_matrix[row, column])

    for row in range(d_b_matrix.shape[0]):
        for column in range(d_b_matrix.shape[1]):
            mdl.set_property_value(mdl.prop(item_handle, f"dB{row + 1}{column + 1}"), d_b_matrix[row, column])

    mdl.set_property_value(mdl.prop(item_handle, "ws"), ws)
    mdl.set_property_value(mdl.prop(item_handle, "ws_inv"), ws_inv)
    mdl.set_property_value(mdl.prop(item_handle, "Z_base"), z_base)
    mdl.set_property_value(mdl.prop(item_handle, "rs"), rs)
    mdl.set_property_value(mdl.prop(item_handle, "Lmd"), lmd)
    mdl.set_property_value(mdl.prop(item_handle, "Lmq"), lmq)
    mdl.set_property_value(mdl.prop(item_handle, "Lmzd"), lmzd)
    mdl.set_property_value(mdl.prop(item_handle, "Lmzq"), lmzq)
    mdl.set_property_value(mdl.prop(item_handle, "Lls"), lls)
    mdl.set_property_value(mdl.prop(item_handle, "Llfd"), llfd)
    mdl.set_property_value(mdl.prop(item_handle, "Llkd"), llkd)
    mdl.set_property_value(mdl.prop(item_handle, "Llkq"), llkq)
    mdl.set_property_value(mdl.prop(item_handle, "Llkq2"), llkq2)
    mdl.set_property_value(mdl.prop(item_handle, "rfd"), rfd)
    mdl.set_property_value(mdl.prop(item_handle, "rkd"), rkd)
    mdl.set_property_value(mdl.prop(item_handle, "rkq"), rkq)
    mdl.set_property_value(mdl.prop(item_handle, "rkq2"), rkq2)
    mdl.set_property_value(mdl.prop(item_handle, "J"), moment_of_inertia)
    mdl.set_property_value(mdl.prop(item_handle, "kw"), kw)
    mdl.set_property_value(mdl.prop(item_handle, "w_base"), w_base)
    mdl.set_property_value(mdl.prop(item_handle, "T_base"), trq_base)
    mdl.set_property_value(mdl.prop(item_handle, "phases"), phases)
    mdl.set_property_value(mdl.prop(item_handle, "PP"), pp)
    mdl.set_property_value(mdl.prop(item_handle, "model"), model)
    mdl.set_property_value(mdl.prop(item_handle, "kvar"), kvar)

    mdl.set_property_value(mdl.prop(item_handle, "Init_switch"), init_switch)

    mdl.set_property_value(mdl.prop(item_handle, "gen_ts_en_bit"), gen_ts_en_bit)
    mdl.set_property_value(mdl.prop(item_handle, "S_Ts"), s_ts)
    mdl.set_property_value(mdl.prop(item_handle, "dssT"), dss_t)
    mdl.set_property_value(mdl.prop(item_handle, "dssnpts"), dssnpts)

    mdl.set_property_value(mdl.prop(item_handle, "T_lim_low"), t_lim_low)
    mdl.set_property_value(mdl.prop(item_handle, "T_lim_high"), t_lim_high)
    mdl.set_property_value(mdl.prop(item_handle, "Ts_switch"), ts_switch)
    mdl.set_property_value(mdl.prop(item_handle, "Slen"), s_len)
    mdl.set_property_value(mdl.prop(item_handle, "T_Ts_internal"), t_ts_internal)

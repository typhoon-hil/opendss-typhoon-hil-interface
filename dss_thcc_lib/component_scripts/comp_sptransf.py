import numpy as np
from itertools import combinations

x0, y0 = (8192, 8192)


def delete_port(mdl, name, parent):
    comp = mdl.get_item(name, parent=parent, item_type="port")
    if comp:
        mdl.delete_item(comp)


def update_subsystem_components(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)
    num_windings = int(mdl.get_property_value(mdl.prop(mask_handle, "num_windings")))
    wdg_n_list = [str(n) for n in range(1, num_windings + 1)]
    trafo_tag_names = [f"TagT{phase}{winding}" for winding in wdg_n_list for phase in "AB"]
    all_trafo_tag_names = [f"TagT{phase}{winding}" for winding in range(1, 11) for phase in "AB"]

    # Delete trafo tags
    for tag in all_trafo_tag_names:
        tag_handle = mdl.get_item(tag, parent=comp_handle, item_type="tag")
        if tag_handle:
            mdl.delete_item(tag_handle)

    trafo_handle = mdl.get_item("T1", parent=comp_handle)
    mdl.set_property_value(mdl.prop(trafo_handle, "num_of_windings"), num_windings)

    # Y positions
    tx0, ty0 = (8400, 8200)

    # Create transformer tags
    trafo_tag_labels = [f"T_{phase}{winding}" for winding in wdg_n_list for phase in "AB"]
    for idx in range(1, num_windings + 1):
        ypos_a = (-96 - 56 * (num_windings - 3)) + 112 * (idx - 2)
        ypos_b = (-96 - 56 * (num_windings - 3) + 80) + 112 * (idx - 2)

        # A
        new_tag_a = mdl.create_tag(
            name=trafo_tag_names[2*(idx-1)],
            value=trafo_tag_labels[2*(idx-1)],
            scope='local',
            parent=comp_handle,
            flip="none" if idx == 1 else "flip_horizontal",
            rotation='up',
            position=(tx0 - 160 if idx == 1 else tx0 + 160, ty0 - 96 if idx == 1 else ty0 + ypos_a)
        )

        if idx == 1:
            mdl.create_connection(mdl.term(trafo_handle, "prm_1"), new_tag_a)
        else:
            mdl.create_connection(mdl.term(trafo_handle, "sec_" + str(2 * (idx - 2) + 1)), new_tag_a)
        # B
        new_tag_b = mdl.create_tag(
            name=trafo_tag_names[2*(idx-1)+1],
            value=trafo_tag_labels[2*(idx-1)+1],
            scope='local',
            parent=comp_handle,
            flip="none" if idx == 1 else "flip_horizontal",
            rotation='up',
            position=(tx0 - 160 if idx == 1 else tx0 + 160, ty0 + 96 if idx == 1 else ty0 + ypos_b)
        )
        if idx == 1:
            mdl.create_connection(mdl.term(trafo_handle, "prm_2"), new_tag_b)
        else:
            mdl.create_connection(mdl.term(trafo_handle, "sec_" + str(2 * (idx - 2) + 2)), new_tag_b)

    # Right ports and tags
    port_names = [f"{phase}{winding}" for winding in wdg_n_list[1:] for phase in "AB"]
    tag_names = [f"Tag{phase}{winding}" for winding in wdg_n_list[1:] for phase in "AB"]
    all_tag_names = [f"Tag{phase}{winding}" for winding in range(2, 11) for phase in "AB"]
    tag_labels = [f"T_{phase}{winding}" for winding in wdg_n_list[1:] for phase in "AB"]

    # Delete tags
    for it in all_tag_names:
        it_handle = mdl.get_item(it, parent=comp_handle, item_type="tag")
        if it_handle:
            mdl.delete_item(it_handle)

    porty0 = y0 - 48 * 2 * (num_windings - 1)
    for idx in range(1, 2 * (num_windings - 1) + 1):
        # A
        new_tag = mdl.create_tag(
            name=tag_names[idx - 1],
            value=tag_labels[idx - 1],
            scope='local',
            parent=comp_handle,
            flip="none",
            rotation='up',
            position=(x0 + 1080, porty0 + idx * 96)
        )
        new_port = created_ports.get(port_names[idx - 1])
        mdl.create_connection(new_tag, new_port)

    vreg_connection(mdl, mask_handle)


def vreg_connection(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)
    vreg_handle = mdl.get_item("Vreg", parent=comp_handle)
    wdg_n_list = [str(n) for n in range(1, 11)]

    # Defaults
    trafo_tag_names = [f"TagT{phase}{winding}" for winding in wdg_n_list for phase in "AB"]
    left_reg_tag_names = ["TagRegA1", "TagRegB1"]
    right_reg_tag_names = ["TagRegA2", "TagRegB2"]
    port_tag_names = [f"Tag{phase}{winding}" for winding in wdg_n_list for phase in "AB"]

    trafo_labels = [f"T{phase}_{winding}" for winding in wdg_n_list for phase in "AB"]

    place_voltage_regulator(mdl, mask_handle, False)

    for idx, tag in enumerate(left_reg_tag_names):
        this_tag = mdl.get_item(tag, parent=comp_handle, item_type="tag")
        if this_tag:
            mdl.set_tag_properties(this_tag, value="not_used", scope='local')
    for idx, tag in enumerate(right_reg_tag_names):
        this_tag = mdl.get_item(tag, parent=comp_handle, item_type="tag")
        if this_tag:
            mdl.set_tag_properties(this_tag, value="not_used", scope='local')
    for idx, tag in enumerate(trafo_tag_names):
        this_tag = mdl.get_item(tag, parent=comp_handle, item_type="tag")
        if this_tag:
            mdl.set_tag_properties(this_tag, value=trafo_labels[idx], scope='local')
    for idx, tag in enumerate(port_tag_names):
        this_tag = mdl.get_item(tag, parent=comp_handle, item_type="tag")
        if this_tag:
            mdl.set_tag_properties(this_tag, value=trafo_labels[idx], scope='local')

    regcontrol_on = mdl.get_property_value(mdl.prop(mask_handle, "regcontrol_on"))

    if regcontrol_on:
        place_voltage_regulator(mdl, mask_handle, True)

        ctrl_winding = mdl.get_property_value(mdl.prop(mask_handle, "ctrl_winding"))
        n_ctrl = ctrl_winding[-1]  # Get number of the ctrl winding
        trafo_tag_names = [f"TagTA{n_ctrl}", f"TagTB{n_ctrl}"]
        port_tag_names = [f"TagA{n_ctrl}", f"TagB{n_ctrl}"]

        trafo_labels = [f"TA_{n_ctrl}", f"TB_{n_ctrl}"]
        port_labels = [f"Reg_A2", f"Reg_B2"]

        for idx, tag in enumerate(left_reg_tag_names):
            this_tag = mdl.get_item(tag, parent=comp_handle, item_type="tag")
            if this_tag:
                mdl.set_tag_properties(this_tag, value=trafo_labels[idx], scope='local')
        for idx, tag in enumerate(right_reg_tag_names):
            this_tag = mdl.get_item(tag, parent=comp_handle, item_type="tag")
            if this_tag:
                mdl.set_tag_properties(this_tag, value=port_labels[idx], scope='local')
        for idx, tag in enumerate(trafo_tag_names):
            this_tag = mdl.get_item(tag, parent=comp_handle, item_type="tag")
            if this_tag:
                mdl.set_tag_properties(this_tag, value=trafo_labels[idx], scope='local')
        for idx, tag in enumerate(port_tag_names):
            this_tag = mdl.get_item(tag, parent=comp_handle, item_type="tag")
            if this_tag:
                mdl.set_tag_properties(this_tag, value=port_labels[idx], scope='local')


def update_regctrl_combo(mdl, mask_handle):
    num_windings = mdl.get_property_disp_value(mdl.prop(mask_handle, "num_windings"))
    combo_vals = [f"Winding {n}" for n in range(1, int(num_windings) + 1)]
    mdl.set_property_combo_values(mdl.prop(mask_handle, "ctrl_winding"), combo_vals)


def validate_properties(mdl, mask_handle):
    # Validate lengths
    comp_handle = mdl.get_parent(mask_handle)
    num_windings = int(mdl.get_property_value(mdl.prop(comp_handle, "num_windings")))

    prop_names = ["KVs", "KVAs", "percentRs", "XArray"]

    for prop_name in prop_names:
        prop_handle = mdl.prop(mask_handle, prop_name)
        prop_value = mdl.get_property_value(prop_handle)

        base_str = mdl.get_name(comp_handle) + " -- Incorrect number of array elements for the"

        if not len(prop_value) == num_windings:
            mdl.info(f'{base_str} {prop_name} property: {len(prop_value)} ({num_windings} expected)')


def convert_all_properties(mdl, mask_handle, prop_names=None):
    comp_handle = mdl.get_parent(mask_handle)
    num_windings = int(mdl.get_property_value(mdl.prop(mask_handle, "num_windings")))
    trafo_inner = mdl.get_item("T1", parent=comp_handle)
    regcontrol_on = mdl.get_property_value(mdl.prop(mask_handle, "regcontrol_on"))

    if not prop_names:
        prop_names = ["KVs", "KVAs", "baseFreq", "percentRs", "percentNoloadloss", "percentimag", "XArray"]

    try:
        for prop_name in prop_names:
            prop_handle = mdl.prop(mask_handle, prop_name)
            prop_value = mdl.get_property_value(prop_handle)

            if type(prop_value) == float or type(prop_value) == int:
                prop_value = [prop_value]

            # Power
            if prop_name == "KVAs":
                sn_prop = mdl.prop(trafo_inner, "Sn")
                converted_value = prop_value[0] * 1000
                mdl.set_property_value(sn_prop, converted_value)
            # Frequency
            elif prop_name == "baseFreq":
                f_prop = mdl.prop(trafo_inner, "f")
                prop_value = prop_value[0]
                converted_value = prop_value
                mdl.set_property_value(f_prop, converted_value)
            # Nominal voltages
            elif prop_name == "KVs":
                n_prim_prop = mdl.prop(trafo_inner, "n_prim")
                n_sec_prop = mdl.prop(trafo_inner, "n_sec")
                mdl.set_property_value(n_prim_prop, 1000 * prop_value[0])
                mdl.set_property_value(n_sec_prop, [1000 * v for v in prop_value[1:]])
            # Resistances
            elif prop_name == "percentRs":
                r_prim_prop = mdl.prop(trafo_inner, "R_prim")
                r_sec_prop = mdl.prop(trafo_inner, "R_sec")
                kvs_prop = mdl.prop(comp_handle, "KVs")
                kvas_prop = mdl.prop(comp_handle, "KVAs")
                kvs = mdl.get_property_value(kvs_prop)
                kvas = mdl.get_property_value(kvas_prop)
                base_r = kvs[0] * kvs[0] / kvas[0] * 1000
                resistances_si = []
                for num in range(1, num_windings + 1):
                    a = kvs[0] / kvs[num - 1]
                    converted_value = (base_r / 100 * prop_value[num - 1]) / a ** 2
                    resistances_si.append(converted_value)
                mdl.set_property_value(r_prim_prop, resistances_si[0])
                mdl.set_property_value(r_sec_prop, resistances_si[1:])
            # Magnetization
            elif prop_name in ["percentNoloadloss", "percentimag"]:
                prop_value = prop_value[0]
                kvs_prop = mdl.prop(comp_handle, "KVs")
                kvas_prop = mdl.prop(comp_handle, "KVAs")
                kvs = mdl.get_property_value(kvs_prop)
                kvas = mdl.get_property_value(kvas_prop)
                base_v = kvs[0] * 1000
                base_p = kvas[0] * 1000
                rm_prop = mdl.prop(trafo_inner, "Rm")
                lm_prop = mdl.prop(trafo_inner, "Lm")
                if prop_name == "percentNoloadloss":
                    try:
                        converted_value = ((base_v * base_v) / base_p) / (prop_value / 100)
                    except ZeroDivisionError:
                        converted_value = "inf"
                    mdl.set_property_value(rm_prop, converted_value)
                elif prop_name == "percentimag":
                    basefreq = mdl.get_property_value(mdl.prop(mask_handle, "baseFreq"))
                    if not prop_value <= 0:
                        converted_value = ((base_v * base_v) / base_p) / (prop_value / 100) / (
                                2 * np.pi * basefreq)
                    else:
                        converted_value = "inf"
                    mdl.set_property_value(lm_prop, converted_value)
            # Inductances
            elif prop_name == "XArray":
                kvs_prop = mdl.prop(comp_handle, "KVs")
                kvas_prop = mdl.prop(comp_handle, "KVAs")
                kvs = mdl.get_property_value(kvs_prop)
                kvas = mdl.get_property_value(kvas_prop)
                basefreq = mdl.get_property_value(mdl.prop(mask_handle, "baseFreq"))
                reactances_pct = prop_value
                l_prim_prop = mdl.prop(trafo_inner, "L_prim")
                l_sec_prop = mdl.prop(trafo_inner, "L_sec")
                xsc_array = []
                inductances_si = []

                for num in range(1, num_windings + 1):
                    base_prim = kvs[0] * kvs[0] / kvas[0] * 1000

                    a = kvs[0] / kvs[num - 1]
                    ind = reactances_pct[num - 1] * base_prim / 100 / 2 / np.pi / basefreq / a ** 2
                    inductances_si.append(ind)

                xsc_idxs = list(combinations(range(num_windings), 2))
                for idx in xsc_idxs:
                    xsc_array.append(reactances_pct[idx[0]] + reactances_pct[idx[1]])

                mdl.set_property_value(mdl.prop(comp_handle, "XscArray"), str(xsc_array))
                mdl.set_property_value(l_prim_prop, inductances_si[0])
                mdl.set_property_value(l_sec_prop, inductances_si[1:])
        set_autotrafo_properties(mdl, mask_handle)

    except IndexError:
        mdl.error(f"Make sure the arrays match the size required for {num_windings} windings.")


def set_autotrafo_properties(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)
    regcontrol_on = mdl.get_property_value(mdl.prop(mask_handle, "regcontrol_on"))
    if regcontrol_on:
        vreg_handle = mdl.get_item("Vreg", parent=comp_handle)
        t_inner_handle = mdl.get_item("T1", parent=comp_handle)
        autotrafo_handle = mdl.get_item("Auto1", parent=vreg_handle)

        for prop_name in ["R1", "R2", "L1", "L2", "Rm", "Lm", "n_taps", "reg_range"]:
            at_prop = mdl.prop(autotrafo_handle, prop_name)

            if prop_name == "n_taps":
                numtaps = mdl.get_property_value(mdl.prop(mask_handle, "numtaps"))
                mdl.set_property_value(at_prop, int(numtaps))
            elif prop_name == "reg_range":
                maxtap = mdl.get_property_value(mdl.prop(mask_handle, "maxtap"))
                mintap = mdl.get_property_value(mdl.prop(mask_handle, "mintap"))
                regrange = max((float(maxtap)-1), (1-float(mintap)))*100
                mdl.set_property_value(at_prop, regrange)
            elif prop_name in ["Rm", "Lm"]:
                t_prop = mdl.prop(t_inner_handle, prop_name)
                t_prop_value = mdl.get_property_value(t_prop)
                mdl.set_property_value(at_prop, t_prop_value)
            else:
                ctrl_winding = mdl.get_property_value(mdl.prop(mask_handle, "ctrl_winding"))
                n_ctrl = int(ctrl_winding[-1])  # Get number of the ctrl winding
                if n_ctrl == 1:
                    orig_prop_name = prop_name[0] + "_prim"
                    t_prop = mdl.prop(t_inner_handle, orig_prop_name)
                    t_prop_value = mdl.get_property_value(t_prop)
                    mdl.set_property_value(at_prop, float(t_prop_value / 1000))
                else:
                    orig_prop_name = prop_name[0] + "_sec"
                    t_prop = mdl.prop(t_inner_handle, orig_prop_name)
                    t_prop_value = mdl.get_property_value(t_prop)
                    mdl.set_property_value(at_prop, float(t_prop_value[n_ctrl-2]/1000))


def show_hide_couplings(mdl, mask_handle):
    num_windings = int(mdl.get_property_disp_value(mdl.prop(mask_handle, "num_windings")))

    for n in range(2, 11):
        coup_prop = mdl.prop(mask_handle, "embedded_cpl_1" + str(n))
        if n < num_windings + 1:
            mdl.show_property(coup_prop)
        else:
            mdl.hide_property(coup_prop)


def calculate_winding_voltage(mdl, mask_handle):

    winding_voltage_prop = mdl.prop(mask_handle, "winding_voltage")

    vreg_prop = mdl.prop(mask_handle, "vreg")
    vreg = mdl.get_property_disp_value(vreg_prop)

    ptratio_prop = mdl.prop(mask_handle, "ptratio")
    ptratio = mdl.get_property_disp_value(ptratio_prop)

    def try_calculation(vreg, ptratio):

        try:
            vreg = float(vreg)
        except:
            try:
                vreg = float(mdl.get_ns_var(vreg))
            except:
                mdl.set_property_disp_value(winding_voltage_prop,
                                            f"Variable {vreg} is invalid (make sure to compile once)")
                return

        try:
            ptratio = float(ptratio)
        except:
            try:
                ptratio = float(mdl.get_ns_var(ptratio))
            except:
                mdl.set_property_disp_value(winding_voltage_prop,
                                            f"Variable {ptratio} is invalid (make sure to compile once)")
                return

        mdl.set_property_disp_value(winding_voltage_prop, str(vreg * ptratio))
        mdl.set_property_value(winding_voltage_prop, str(vreg * ptratio))

        return

    try_calculation(vreg, ptratio)


def toggle_regcontrol_props(mdl, mask_handle):

    regcontrol_on_prop = mdl.prop(mask_handle, "regcontrol_on")
    regcontrol_on = mdl.get_property_disp_value(regcontrol_on_prop)

    props_list = ["ctrl_winding", "vreg", "ptratio", "winding_voltage", "band", "delay", "mintap",
                  "maxtap", "numtaps", "execution_rate"]

    if regcontrol_on:
        for i in range(len(props_list)):
            prop = mdl.prop(mask_handle, props_list[i])
            mdl.enable_property(prop)
    else:
        for i in range(len(props_list)):
            prop = mdl.prop(mask_handle, props_list[i])
            mdl.disable_property(prop)


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


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    num_windings = int(mdl.get_property_value(mdl.prop(mask_handle, "num_windings")))
    wdg_n_list = [str(n) for n in range(1, num_windings + 1)]

    # Delete secondary ports
    for i in range(2, 11):
        delete_port(mdl, "A" + str(i), comp_handle)
        delete_port(mdl, "B" + str(i), comp_handle)

    # Right ports and tags
    port_names = [f"{phase}{winding}" for winding in wdg_n_list[1:] for phase in "AB"]

    porty0 = y0 - 48 * 2 * (num_windings - 1)

    for sec_n in range(2, num_windings + 1):
        for term_idx in range(2):
            ty_start = -16 - 48 * (num_windings - 2)
            new_port = mdl.create_port(
                name=port_names[(sec_n - 2) * 2 + term_idx],
                parent=comp_handle,
                flip="flip_horizontal",
                rotation='up',
                position=(x0 + 1180, porty0 + ((sec_n - 1) * 2 + (term_idx - 1)) * 96),
                terminal_position=(32, ty_start + (sec_n - 2) * 96 + (term_idx) * 32),
                hide_name=True
            )
            created_ports.update({port_names[(sec_n - 2) * 2 + term_idx]: new_port})

    return created_ports, deleted_ports

def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):

    if caller_prop_handle:

        new_value = mdl.get_property_disp_value(caller_prop_handle)

        if mdl.get_name(caller_prop_handle) == "ptratio":
            calculate_winding_voltage(mdl, mask_handle)


def define_icon(mdl, mask_handle):
    images = {
        2: "t_2p2w.svg",
        3: "t_2p3w.svg",
        4: "t_2p4w.svg",
        5: "t_2p5w.svg",
        6: "t_2p6w.svg",
        7: "t_2p7w.svg",
        8: "t_2p8w.svg",
        9: "t_2p9w.svg",
        10: "t_2p10w.svg",
    }
    num_windings = int(mdl.get_property_value(mdl.prop(mask_handle, "num_windings")))

    mdl.set_component_icon_image(mask_handle, "images/" + images[num_windings])

    #
    # Set text
    #
    mdl.set_color(mask_handle, "blue")

    for wdg_number in range(1, num_windings + 1):
        size_y = 64 + 96 * (num_windings - 2)

        # Winding number
        if wdg_number == 1:
            mdl.disp_component_icon_text(mask_handle, "1", rotate="rotate",
                                         relpos_x=0.14,
                                         relpos_y=(36 + 48 * (
                                                     num_windings - 2)) / size_y,
                                         size=8, trim_factor=2)
        else:
            mdl.disp_component_icon_text(mask_handle, f"{wdg_number}", rotate="rotate",
                                         relpos_x=0.88,
                                         relpos_y=(36 + 96 * (wdg_number - 2)) / size_y,
                                         size=8, trim_factor=2)


def place_voltage_regulator(mdl, mask_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(mask_handle)
    if new_value:
        vreg = mdl.get_item("Vreg", parent=comp_handle, item_type="component")
        if not vreg:
            vreg = mdl.create_component("OpenDSS/single-phase voltage regulator",
                                        parent=comp_handle, name="Vreg",
                                        position=(8960, 8232), rotation="up")
        tag_reg_a1 = mdl.get_item("TagRegA1", parent=comp_handle, item_type="tag")
        if not tag_reg_a1:
            tag_reg_a1 = mdl.create_tag(name="TagRegA1", value="not_used", scope='local',
                                        parent=comp_handle, rotation='up', position=(8776, 8136))

        tag_reg_b1 = mdl.get_item("TagRegB1", parent=comp_handle, item_type="tag")
        if not tag_reg_b1:
            tag_reg_b1 = mdl.create_tag(name="TagRegB1", value="not_used", scope='local',
                                        parent=comp_handle, rotation='up', position=(8776, 8328))

        tag_reg_a2 = mdl.get_item("TagRegA2", parent=comp_handle, item_type="tag")
        if not tag_reg_a2:
            tag_reg_a2 = mdl.create_tag(name="TagRegA2", value="not_used", scope='local',
                                        parent=comp_handle, rotation='down', position=(9128, 8136))

        tag_reg_b2 = mdl.get_item("TagRegB2", parent=comp_handle, item_type="tag")
        if not tag_reg_b2:
            tag_reg_b2 = mdl.create_tag(name="TagRegB2", value="not_used", scope='local',
                                        parent=comp_handle, rotation='down', position=(9128, 8328))

        conn_netlist = [(tag_reg_a1, mdl.term(vreg, "RegA1")),
                        (tag_reg_b1, mdl.term(vreg, "RegB1")),
                        (mdl.term(vreg, "RegA2"), tag_reg_a2),
                        (mdl.term(vreg, "RegB2"), tag_reg_b2)]
        for conn_handle in conn_netlist:
            if len(mdl.find_connections(conn_handle[0], conn_handle[1])) == 0:
                mdl.create_connection(conn_handle[0], conn_handle[1])
    else:
        vreg = mdl.get_item("Vreg", parent=comp_handle, item_type="component")
        tag_reg_a1 = mdl.get_item("TagRegA1", parent=comp_handle, item_type="tag")
        tag_reg_b1 = mdl.get_item("TagRegB1", parent=comp_handle, item_type="tag")
        tag_reg_a2 = mdl.get_item("TagRegA2", parent=comp_handle, item_type="tag")
        tag_reg_b2 = mdl.get_item("TagRegB2", parent=comp_handle, item_type="tag")

        delete_list = [vreg,
                       tag_reg_a1,
                       tag_reg_b1,
                       tag_reg_a2,
                       tag_reg_b2]

        for component in delete_list:
            if component:
                mdl.delete_item(component)

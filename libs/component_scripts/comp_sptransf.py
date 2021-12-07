import numpy as np
from itertools import combinations

x0, y0 = (8192, 8192)

def delete_port(mdl, name, parent):
    comp = mdl.get_item(name, parent=parent, item_type="port")
    if comp:
        mdl.delete_item(comp)

def update_subsystem_components(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)
    num_windings = int(mdl.get_property_value(mdl.prop(mask_handle, "num_windings")))
    wdg_n_list = [str(n) for n in range(1, num_windings + 1)]
    trafo_tag_names = [f"TagT{phase}{winding}" for winding in wdg_n_list for phase in "AB"]

    # Delete trafo tags
    for tag in trafo_tag_names:
        tag_handle = mdl.get_item(tag, parent=comp_handle, item_type="tag")
        if tag_handle:
            mdl.delete_item(tag_handle)

    # Delete secondary ports
    for i in range(2, 11):
        delete_port(mdl, "A" + str(i), comp_handle)
        delete_port(mdl, "B" + str(i), comp_handle)

    T_handle = mdl.get_item("T1", parent=comp_handle)
    mdl.set_property_value(mdl.prop(T_handle, "num_of_windings"), num_windings)

    # Y positions
    tx0, ty0 = (8400, 8200)

    # Create transformer tags
    trafo_tag_labels = [f"T_{phase}{winding}" for winding in wdg_n_list for phase in "AB"]
    for idx in range(1, num_windings + 1):
        yposA = (-96 - 56 * (num_windings - 3)) + 112 * (idx - 2)
        yposB = (-96 - 56 * (num_windings - 3) + 80) + 112 * (idx - 2)

        # A
        new_tag_A = mdl.create_tag(
            name=trafo_tag_names[2*(idx-1)],
            value=trafo_tag_labels[2*(idx-1)],
            scope='local',
            parent=comp_handle,
            flip="none" if idx == 1 else "flip_horizontal",
            rotation='up',
            position=(tx0 - 160 if idx == 1 else tx0 + 160, ty0 - 96 if idx == 1 else ty0 + yposA)
        )

        if idx == 1:
            mdl.create_connection(mdl.term(T_handle, "prm_1"), new_tag_A)
        else:
            mdl.create_connection(mdl.term(T_handle, "sec_" + str(2 * (idx - 2) + 1)), new_tag_A)
        # B
        new_tag_B = mdl.create_tag(
            name=trafo_tag_names[2*(idx-1)+1],
            value=trafo_tag_labels[2*(idx-1)+1],
            scope='local',
            parent=comp_handle,
            flip="none" if idx == 1 else "flip_horizontal",
            rotation='up',
            position=(tx0 - 160 if idx == 1 else tx0 + 160, ty0 + 96 if idx == 1 else ty0 + yposB)
        )
        if idx == 1:
            mdl.create_connection(mdl.term(T_handle, "prm_2"), new_tag_B)
        else:
            mdl.create_connection(mdl.term(T_handle, "sec_" + str(2 * (idx - 2) + 2)), new_tag_B)

    # Right ports and tags
    port_names = [f"{phase}{winding}" for winding in wdg_n_list[1:] for phase in "AB"]
    tag_names = [f"Tag{phase}{winding}" for winding in wdg_n_list[1:] for phase in "AB"]
    tag_labels = [f"T_{phase}{winding}" for winding in wdg_n_list[1:] for phase in "AB"]

    # Delete tags and ports
    for it in port_names + tag_names:
        it_handle = mdl.get_item(it, parent=comp_handle)
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
        new_port = mdl.create_port(
            name=port_names[idx - 1],
            parent=comp_handle,
            flip="flip_horizontal",
            rotation='up',
            position=(x0 + 1180, porty0 + idx * 96),
            terminal_position=(32, - 16 - 16 * 2 * (num_windings - 1) + idx * 32)
        )
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

    mdl.disable_items(vreg_handle)
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
        mdl.enable_items(vreg_handle)
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
    T_inner = mdl.get_item("T1", parent=comp_handle)
    regcontrol_on = mdl.get_property_value(mdl.prop(mask_handle, "regcontrol_on"))

    if not prop_names:
        prop_names = ["KVs", "KVAs", "Basefreq", "percentRs", "percentNoloadloss", "percentimag", "XArray"]

    try:
        for prop_name in prop_names:
            prop_handle = mdl.prop(mask_handle, prop_name)
            prop_value = mdl.get_property_value(prop_handle)

            if type(prop_value) == float or type(prop_value) == int:
                prop_value = [prop_value]

            # Power
            if prop_name == "KVAs":
                Sn_prop = mdl.prop(T_inner, "Sn")
                converted_value = prop_value[0] * 1000
                mdl.set_property_value(Sn_prop, converted_value)
            # Frequency
            elif prop_name == "Basefreq":
                f_prop = mdl.prop(T_inner, "f")
                prop_value = prop_value[0]
                converted_value = prop_value
                mdl.set_property_value(f_prop, converted_value)
            # Nominal voltages
            elif prop_name == "KVs":
                n_prim_prop = mdl.prop(T_inner, "n_prim")
                n_sec_prop = mdl.prop(T_inner, "n_sec")
                mdl.set_property_value(n_prim_prop, 1000 * prop_value[0])
                mdl.set_property_value(n_sec_prop, [1000 * v for v in prop_value[1:]])
            # Resistances
            elif prop_name == "percentRs":
                R_prim_prop = mdl.prop(T_inner, "R_prim")
                R_sec_prop = mdl.prop(T_inner, "R_sec")
                KVs_prop = mdl.prop(comp_handle, "KVs")
                KVAs_prop = mdl.prop(comp_handle, "KVAs")
                KVs = mdl.get_property_value(KVs_prop)
                KVAs = mdl.get_property_value(KVAs_prop)
                baseR = KVs[0] * KVs[0] / KVAs[0] * 1000
                resistances_SI = []
                for num in range(1, num_windings + 1):
                    a = KVs[0] / KVs[num - 1]
                    converted_value = (baseR / 100 * prop_value[num - 1]) / a ** 2
                    resistances_SI.append(converted_value)
                mdl.set_property_value(R_prim_prop, resistances_SI[0])
                mdl.set_property_value(R_sec_prop, resistances_SI[1:])
            # Magnetization
            elif prop_name in ["percentNoloadloss", "percentimag"]:
                prop_value = prop_value[0]
                KVs_prop = mdl.prop(comp_handle, "KVs")
                KVAs_prop = mdl.prop(comp_handle, "KVAs")
                KVs = mdl.get_property_value(KVs_prop)
                KVAs = mdl.get_property_value(KVAs_prop)
                baseV = KVs[0] * 1000
                baseP = KVAs[0] * 1000
                Rm_prop = mdl.prop(T_inner, "Rm")
                Lm_prop = mdl.prop(T_inner, "Lm")
                if prop_name == "percentNoloadloss":
                    try:
                        converted_value = ((baseV * baseV) / baseP) / (prop_value / 100)
                    except ZeroDivisionError:
                        converted_value = "inf"
                    mdl.set_property_value(Rm_prop, converted_value)
                elif prop_name == "percentimag":
                    Basefreq = mdl.get_property_value(mdl.prop(mask_handle, "Basefreq"))
                    if not prop_value <= 0:
                        converted_value = ((baseV * baseV) / baseP) / (prop_value / 100) / (
                                    2 * np.pi * Basefreq)
                    else:
                        converted_value = "inf"
                    mdl.set_property_value(Lm_prop, converted_value)
            # Inductances
            elif prop_name == "XArray":
                KVs_prop = mdl.prop(comp_handle, "KVs")
                KVAs_prop = mdl.prop(comp_handle, "KVAs")
                KVs = mdl.get_property_value(KVs_prop)
                KVAs = mdl.get_property_value(KVAs_prop)
                Basefreq = mdl.get_property_value(mdl.prop(mask_handle, "Basefreq"))
                reactances_pct = prop_value
                L_prim_prop = mdl.prop(T_inner, "L_prim")
                L_sec_prop = mdl.prop(T_inner, "L_sec")
                xsc_array = []
                inductances_SI = []

                for num in range(1, num_windings + 1):
                    base_prim = KVs[0] * KVs[0] / KVAs[0] * 1000

                    a = KVs[0] / KVs[num - 1]
                    ind = reactances_pct[num - 1] * base_prim / 100 / 2 / np.pi / Basefreq / a ** 2
                    inductances_SI.append(ind)

                xsc_idxs = list(combinations(range(num_windings), 2))
                for idx in xsc_idxs:
                    xsc_array.append(reactances_pct[idx[0]] + reactances_pct[idx[1]])

                mdl.set_property_value(mdl.prop(comp_handle, "XscArray"), str(xsc_array))
                mdl.set_property_value(L_prim_prop, inductances_SI[0])
                mdl.set_property_value(L_sec_prop, inductances_SI[1:])
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
                mdl.set_property_disp_value(winding_voltage_prop, f"Variable {vreg} is invalid (make sure to compile once)")
                return

        try:
            ptratio = float(ptratio)
        except:
            try:
                ptratio = float(mdl.get_ns_var(ptratio))
            except:
                mdl.set_property_disp_value(winding_voltage_prop, f"Variable {ptratio} is invalid (make sure to compile once)")
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
    frequency_prop = mdl.prop(mask_handle, "Basefreq")
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

    frequency_prop = mdl.prop(mask_handle, "Basefreq")
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

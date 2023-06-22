from typhoon.api.schematic_editor.const import ITEM_JUNCTION, ITEM_CONNECTION, ITEM_PORT, ITEM_COMPONENT


def tp_conn_change(mdl, container_handle, new_value):
    comp_handle = mdl.get_parent(container_handle)
    mdl.refresh_icon(container_handle)

    if new_value == "Δ":
        junA0 = mdl.get_item("JA0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junB0 = mdl.get_item("JB0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junC0 = mdl.get_item("JC0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junA1 = mdl.get_item("JA1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junB1 = mdl.get_item("JB1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junC1 = mdl.get_item("JC1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junN = mdl.get_item("JN", parent=comp_handle, item_type=ITEM_JUNCTION)

        connAB = mdl.get_item("Conn_AB", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not connAB:
            mdl.create_connection(junA1, junB0, name="Conn_AB")
        connBC = mdl.get_item("Conn_BC", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not connBC:
            mdl.create_connection(junB1, junC0, name="Conn_BC")
        connCA = mdl.get_item("Conn_CA", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not connCA:
            mdl.create_connection(junC1, junA0, name="Conn_CA")

        if junN:
            mdl.delete_item(junN)

        portN = mdl.get_item("N", parent=comp_handle, item_type=ITEM_PORT)
        if portN:
            mdl.delete_item(portN)

    else:
        junA1 = mdl.get_item("JA1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junB1 = mdl.get_item("JB1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junC1 = mdl.get_item("JC1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junN = mdl.get_item("JN", parent=comp_handle, item_type=ITEM_JUNCTION)

        if not junN:
            junN = mdl.create_junction(name='JN', parent=comp_handle, kind='pe',
                                       position=(8192, 8328))

        connAN = mdl.get_item("Conn_AN", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not connAN:
            mdl.create_connection(junA1, junN, name="Conn_AN")
        connBN = mdl.get_item("Conn_BN", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not connBN:
            mdl.create_connection(junB1, junN, name="Conn_BN")
        connCN = mdl.get_item("Conn_CN", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not connCN:
            mdl.create_connection(junC1, junN, name="Conn_CN")

        connAB = mdl.get_item("Conn_AB", parent=comp_handle, item_type=ITEM_CONNECTION)
        if connAB:
            mdl.delete_item(connAB)
        connBC = mdl.get_item("Conn_BC", parent=comp_handle, item_type=ITEM_CONNECTION)
        if connBC:
            mdl.delete_item(connBC)
        connCA = mdl.get_item("Conn_CA", parent=comp_handle, item_type=ITEM_CONNECTION)
        if connCA:
            mdl.delete_item(connCA)


def ground_sw_change(mdl, container_handle, new_value):
    comp_handle = mdl.get_parent(container_handle)
    mdl.refresh_icon(container_handle)
    if new_value:   # if ground connection is checked
        portN = mdl.get_item("N", parent=comp_handle, item_type=ITEM_PORT)
        gnd1 = mdl.get_item("gndc", parent=comp_handle, item_type=ITEM_COMPONENT)
        junN = mdl.get_item("JN", parent=comp_handle, item_type=ITEM_JUNCTION)
        if portN:
            mdl.delete_item(portN)
        if junN:
            if not gnd1:
                gnd1 = mdl.create_component("src_ground", parent=comp_handle, name="gndc", position=(8192, 8378))
            connG = mdl.get_item("Conn_G", parent=comp_handle, item_type=ITEM_CONNECTION)
            if not connG:
                mdl.create_connection(mdl.term(gnd1, "node"), junN, name="ConnG")
    else:   # whithout ground connection
        junN = mdl.get_item("JN", parent=comp_handle, item_type=ITEM_JUNCTION)
        gnd1 = mdl.get_item("gndc", parent=comp_handle, item_type=ITEM_COMPONENT)
        if gnd1:
            mdl.delete_item(gnd1)
        if junN:
            portN = mdl.get_item("N", parent=comp_handle, item_type=ITEM_PORT)
            if not portN:
                portN = mdl.create_port(parent=comp_handle, name="N", direction="out", kind="pe",
                                        terminal_position=(0, 30),
                                        position=(8192, 8378), rotation="left")
            connN = mdl.get_item("Conn_N", parent=comp_handle, item_type=ITEM_CONNECTION)
            if not connN:
                mdl.create_connection(junN, portN, name="Conn_N")


def set_balanced(mdl, mask_handle, new_value):
    if new_value is True:
        mdl.disable_property(mdl.prop(mask_handle, "VAn"))
        mdl.disable_property(mdl.prop(mask_handle, "VBn"))
        mdl.disable_property(mdl.prop(mask_handle, "VCn"))
        mdl.disable_property(mdl.prop(mask_handle, "VAB"))
        mdl.disable_property(mdl.prop(mask_handle, "VBC"))
        mdl.disable_property(mdl.prop(mask_handle, "VCA"))
        mdl.disable_property(mdl.prop(mask_handle, "SAn"))
        mdl.disable_property(mdl.prop(mask_handle, "SBn"))
        mdl.disable_property(mdl.prop(mask_handle, "SCn"))
        mdl.disable_property(mdl.prop(mask_handle, "SAB"))
        mdl.disable_property(mdl.prop(mask_handle, "SBC"))
        mdl.disable_property(mdl.prop(mask_handle, "SCA"))
        mdl.disable_property(mdl.prop(mask_handle, "pf_modeA"))
        mdl.disable_property(mdl.prop(mask_handle, "pf_modeB"))
        mdl.disable_property(mdl.prop(mask_handle, "pf_modeC"))
        mdl.disable_property(mdl.prop(mask_handle, "pfA"))
        mdl.disable_property(mdl.prop(mask_handle, "pfB"))
        mdl.disable_property(mdl.prop(mask_handle, "pfC"))

        mdl.enable_property(mdl.prop(mask_handle, "Vn_3ph"))
        mdl.enable_property(mdl.prop(mask_handle, "Sn_3ph"))
        mdl.enable_property(mdl.prop(mask_handle, "pf_mode_3ph"))

        vn_3ph = mdl.get_property_disp_value(mdl.prop(mask_handle, "Vn_3ph"))
        sn_3ph = mdl.get_property_disp_value(mdl.prop(mask_handle, "Sn_3ph"))
        phases = mdl.get_property_disp_value(mdl.prop(mask_handle, "phases"))
        pf_mode_3ph = mdl.get_property_disp_value(mdl.prop(mask_handle, "pf_mode_3ph"))
        if not pf_mode_3ph == "Unit":
            mdl.enable_property(mdl.prop(mask_handle, "pf_3ph"))
        pf_3ph = mdl.get_property_disp_value(mdl.prop(mask_handle, "pf_3ph"))

        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VAn'), vn_3ph + '*1000/(3**0.5)')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VBn'), vn_3ph + '*1000/(3**0.5)')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VCn'), vn_3ph + '*1000/(3**0.5)')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VAB'), vn_3ph + '*1000')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VBC'), vn_3ph + '*1000')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VCA'), vn_3ph + '*1000')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SAn'), sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SBn'), sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SCn'), sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SAB'), sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SBC'), sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SCA'), sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'pf_modeA'), pf_mode_3ph)
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'pf_modeB'), pf_mode_3ph)
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'pf_modeC'), pf_mode_3ph)
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'pfA'), pf_3ph)
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'pfB'), pf_3ph)
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'pfC'), pf_3ph)

    else:
        mdl.enable_property(mdl.prop(mask_handle, "VAn"))
        mdl.enable_property(mdl.prop(mask_handle, "VBn"))
        mdl.enable_property(mdl.prop(mask_handle, "VCn"))
        mdl.enable_property(mdl.prop(mask_handle, "VAB"))
        mdl.enable_property(mdl.prop(mask_handle, "VBC"))
        mdl.enable_property(mdl.prop(mask_handle, "VCA"))
        mdl.enable_property(mdl.prop(mask_handle, "SAn"))
        mdl.enable_property(mdl.prop(mask_handle, "SBn"))
        mdl.enable_property(mdl.prop(mask_handle, "SCn"))
        mdl.enable_property(mdl.prop(mask_handle, "SAB"))
        mdl.enable_property(mdl.prop(mask_handle, "SBC"))
        mdl.enable_property(mdl.prop(mask_handle, "SCA"))
        mdl.enable_property(mdl.prop(mask_handle, "pf_modeA"))
        mdl.enable_property(mdl.prop(mask_handle, "pf_modeB"))
        mdl.enable_property(mdl.prop(mask_handle, "pf_modeC"))
        pf_mode_a = mdl.get_property_disp_value(mdl.prop(mask_handle, "pf_modeA"))
        if not pf_mode_a == "Unit":
            mdl.enable_property(mdl.prop(mask_handle, "pfA"))
        pf_mode_b = mdl.get_property_disp_value(mdl.prop(mask_handle, "pf_modeB"))
        if not pf_mode_b == "Unit":
            mdl.enable_property(mdl.prop(mask_handle, "pfB"))
        pf_mode_c = mdl.get_property_disp_value(mdl.prop(mask_handle, "pf_modeC"))
        if not pf_mode_c == "Unit":
            mdl.enable_property(mdl.prop(mask_handle, "pfC"))

        mdl.disable_property(mdl.prop(mask_handle, "Vn_3ph"))
        mdl.disable_property(mdl.prop(mask_handle, "Sn_3ph"))
        mdl.disable_property(mdl.prop(mask_handle, "pf_mode_3ph"))
        mdl.disable_property(mdl.prop(mask_handle, "pf_3ph"))

def conn_type_value_edited_fnc(mdl, container_handle, new_value):
    phases = mdl.get_property_disp_value(mdl.prop(container_handle, "phases"))

    if phases == "3":
        if new_value == "Δ":
            mdl.disable_property(mdl.prop(container_handle, "ground_connected"))
            mdl.set_property_disp_value(mdl.prop(container_handle, 'ground_connected'), False)
        else:
            mdl.enable_property(mdl.prop(container_handle, "ground_connected"))
            mdl.set_property_disp_value(mdl.prop(container_handle, 'ground_connected'), False)
    elif phases == "1":
        mdl.enable_property(mdl.prop(container_handle, "ground_connected"))


def phase_value_changed(mdl, container_handle, new_value):
    conn_type_prop = mdl.prop(container_handle, "conn_type")
    conn_type = mdl.get_property_value(conn_type_prop)
    if new_value == "1":
        if conn_type == "Δ":
            mdl.set_property_value(mdl.prop(container_handle, 'ground_connected'), True)
        mdl.enable_property(mdl.prop(container_handle, "ground_connected"))
        mdl.set_property_disp_value(mdl.prop(container_handle, 'conn_type'), "Y")
        mdl.set_property_value(mdl.prop(container_handle, 'conn_type'), "Y")
        mdl.disable_property(mdl.prop(container_handle, "conn_type"))

    elif new_value == "3":
        mdl.enable_property(mdl.prop(container_handle, "conn_type"))
        if conn_type == "Y":
            mdl.enable_property(mdl.prop(container_handle, "ground_connected"))
        else:
            mdl.set_property_disp_value(mdl.prop(container_handle, 'ground_connected'), False)
            mdl.set_property_value(mdl.prop(container_handle, 'ground_connected'), False)
            mdl.disable_property(mdl.prop(container_handle, "ground_connected"))


def lock_prop(mdl, comp_handle, mask_property, new_value, locking_value):
    if new_value == locking_value:
        mdl.disable_property(mdl.prop(comp_handle, mask_property))
    else:
        mdl.enable_property(mdl.prop(comp_handle, mask_property))

def pf_mode_fcn(mdl, mask_handle, new_value, phase, comp_pos, jun_pos):

    comp_handle = mdl.get_sub_level_handle(mask_handle)
    resistance = mdl.get_item("R" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)



    jun1 = mdl.get_item("J" + phase + "1", parent=comp_handle, item_type=ITEM_JUNCTION)
    if not jun1:
        jun1 = mdl.create_junction(name="J" + phase + "1", parent=comp_handle, kind='pe', position=jun_pos)

    if new_value == "Unit":
        inductance = mdl.get_item("L" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)
        capacitance = mdl.get_item("C" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)

        if inductance:
            mdl.delete_item(inductance)
        if capacitance:
            mdl.delete_item(capacitance)

        conn = mdl.get_item("Conn_" + phase, parent=comp_handle, item_type=ITEM_CONNECTION)
        if not conn:
            mdl.create_connection(mdl.term(resistance, "n_node"), jun1, name="Conn_" + phase)

    elif new_value == "Lead":
        inductance = mdl.get_item("L" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)
        capacitance = mdl.get_item("C" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)

        if inductance:
            mdl.delete_item(inductance)
        if not capacitance:
            capacitance = mdl.create_component("Capacitor", parent=comp_handle, name="C" + phase.lower(),
                                               position=comp_pos, rotation="right")
            mdl.set_property_value(mdl.prop(capacitance, "capacitance"), "C" + phase.lower())

        conn = mdl.get_item("Conn_" + phase, parent=comp_handle, item_type=ITEM_CONNECTION)
        if conn:
            mdl.delete_item(conn)

        mdl.create_connection(mdl.term(capacitance, "n_node"), jun1, name="Conn_" + phase)

        conn0 = mdl.get_item("Conn_" + phase + "0", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not conn0:
            mdl.create_connection(mdl.term(resistance, "n_node"), mdl.term(capacitance, "p_node"),
                                  name="Conn_" + phase + "0")

    else:
        inductance = mdl.get_item("L" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)
        capacitance = mdl.get_item("C" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)

        if capacitance:
            mdl.delete_item(capacitance)
        if not inductance:
            inductance = mdl.create_component("Inductor", parent=comp_handle, name="L" + phase.lower(),
                                              position=comp_pos, rotation="right")
            mdl.set_property_value(mdl.prop(inductance, "inductance"), "L" + phase.lower())

        conn = mdl.get_item("Conn_" + phase, parent=comp_handle, item_type=ITEM_CONNECTION)
        if conn:
            mdl.delete_item(conn)

        mdl.create_connection(mdl.term(inductance, "n_node"), jun1, name="Conn_" + phase)

        conn0 = mdl.get_item("Conn_" + phase + "0", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not conn0:
            mdl.create_connection(mdl.term(resistance, "n_node"), mdl.term(inductance, "p_node"),
                                  name="Conn_" + phase + "0")


def phase_n_selector(mdl, container_handle, new_value):
    pf_mode_3ph = mdl.get_property_disp_value(mdl.prop(container_handle, "pf_mode_3ph"))
    comp_handle = mdl.get_sub_level_handle(container_handle)

    mdl.refresh_icon(container_handle)

    if new_value == "3":
        mdl.enable_property(mdl.prop(container_handle, "ground_connected"))
        mdl.enable_property(mdl.prop(container_handle, "conn_type"))
        junA0 = mdl.get_item("JA0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junB0 = mdl.get_item("JB0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junC0 = mdl.get_item("JC0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junA1 = mdl.get_item("JA1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junB1 = mdl.get_item("JB1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junC1 = mdl.get_item("JC1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junN = mdl.get_item("JN", parent=comp_handle, item_type=ITEM_JUNCTION)
        pA = mdl.get_item("A1", parent=comp_handle, item_type=ITEM_PORT)
        pB = mdl.get_item("B1", parent=comp_handle, item_type=ITEM_PORT)
        pC = mdl.get_item("C1", parent=comp_handle, item_type=ITEM_PORT)
        connAA0 = mdl.get_item("Conn_AA0", parent=comp_handle, item_type=ITEM_CONNECTION)
        connBB0 = mdl.get_item("Conn_BB0", parent=comp_handle, item_type=ITEM_CONNECTION)
        connCC0 = mdl.get_item("Conn_CC0", parent=comp_handle, item_type=ITEM_CONNECTION)
        Ra = mdl.get_item("Ra", parent=comp_handle, item_type=ITEM_COMPONENT)
        Rb = mdl.get_item("Rb", parent=comp_handle, item_type=ITEM_COMPONENT)
        Rc = mdl.get_item("Rc", parent=comp_handle, item_type=ITEM_COMPONENT)
        La = mdl.get_item("Ra", parent=comp_handle, item_type=ITEM_COMPONENT)
        Lb = mdl.get_item("Rb", parent=comp_handle, item_type=ITEM_COMPONENT)
        Lc = mdl.get_item("Rc", parent=comp_handle, item_type=ITEM_COMPONENT)
        Ca = mdl.get_item("Ra", parent=comp_handle, item_type=ITEM_COMPONENT)
        Cb = mdl.get_item("Rb", parent=comp_handle, item_type=ITEM_COMPONENT)
        Cc = mdl.get_item("Rc", parent=comp_handle, item_type=ITEM_COMPONENT)

        if not pA:
            pA = mdl.create_port(parent=comp_handle, name="A1", direction="out", kind="pe",
                                 terminal_position=(-30, -30),
                                 position=(8112, 8024), rotation="right")
            mdl.create_connection(junA0, pA, name="ConnAA0")
        else:
            mdl.set_port_properties(pA, terminal_position=(-30, -30))
        if not Ra:
            Ra = mdl.create_component("pas_resistor", parent=comp_handle, name="Ra", position=(8112, 8128),
                                      rotation="right")
            mdl.set_property_value(mdl.prop(Ra, "resistance"), "Ra")
            mdl.create_connection(mdl.term(Ra, "p_node"), junA0, name="Conn17")
            mdl.create_connection(mdl.term(Ra, "n_node"), junA1, name="Conn_A")
            pf_mode_fcn(mdl, container_handle, pf_mode_3ph, 'A', (8112, 8232), (8112, 8288))

        if not pB:
            pB = mdl.create_port(parent=comp_handle, name="B1", direction="out", kind="pe",
                                 terminal_position=(0, -30),
                                 position=(8192, 8024), rotation="right")
            mdl.create_connection(junB0, pB, name="ConnBB0")
        if not Rb:
            Rb = mdl.create_component("pas_resistor", parent=comp_handle, name="Rb", position=(8192, 8128),
                                      rotation="right")
            mdl.set_property_value(mdl.prop(Rb, "resistance"), "Rb")
            mdl.create_connection(mdl.term(Rb, "p_node"), junB0, name="Conn19")
            mdl.create_connection(mdl.term(Rb, "n_node"), junB1, name="Conn_B")
            pf_mode_fcn(mdl, container_handle, pf_mode_3ph, 'B', (8192, 8232), (8192, 8288))
        if not pC:
            pC = mdl.create_port(parent=comp_handle, name="C1", direction="out", kind="pe",
                                 terminal_position=(30, -30),
                                 position=(8272, 8024), rotation="right")
            mdl.create_connection(junC0, pC, name="ConnCC0")
        if not Rc:
            Rc = mdl.create_component("pas_resistor", parent=comp_handle, name="Rc", position=(8272, 8128),
                                      rotation="right")
            mdl.set_property_value(mdl.prop(Rc, "resistance"), "Rc")
            mdl.create_connection(mdl.term(Rc, "p_node"), junC0, name="Conn21")
            mdl.create_connection(mdl.term(Rc, "n_node"), junC1, name="Conn_C")
            pf_mode_fcn(mdl, container_handle, pf_mode_3ph, 'C', (8272, 8232), (8272, 8288))

    elif new_value == "2":
        junA0 = mdl.get_item("JA0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junB0 = mdl.get_item("JB0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junC0 = mdl.get_item("JC0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junA1 = mdl.get_item("JA1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junB1 = mdl.get_item("JB1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junC1 = mdl.get_item("JC1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junN = mdl.get_item("JN", parent=comp_handle, item_type=ITEM_JUNCTION)
        pA = mdl.get_item("A1", parent=comp_handle, item_type=ITEM_PORT)
        pB = mdl.get_item("B1", parent=comp_handle, item_type=ITEM_PORT)
        pC = mdl.get_item("C1", parent=comp_handle, item_type=ITEM_PORT)
        connAA0 = mdl.get_item("Conn_AA0", parent=comp_handle, item_type=ITEM_CONNECTION)
        connBB0 = mdl.get_item("Conn_BB0", parent=comp_handle, item_type=ITEM_CONNECTION)
        connCC0 = mdl.get_item("Conn_CC0", parent=comp_handle, item_type=ITEM_CONNECTION)
        Ra = mdl.get_item("Ra", parent=comp_handle, item_type=ITEM_COMPONENT)
        Rb = mdl.get_item("Rb", parent=comp_handle, item_type=ITEM_COMPONENT)
        Rc = mdl.get_item("Rc", parent=comp_handle, item_type=ITEM_COMPONENT)
        La = mdl.get_item("Ra", parent=comp_handle, item_type=ITEM_COMPONENT)
        Lb = mdl.get_item("Rb", parent=comp_handle, item_type=ITEM_COMPONENT)
        Lc = mdl.get_item("Rc", parent=comp_handle, item_type=ITEM_COMPONENT)
        Ca = mdl.get_item("Ra", parent=comp_handle, item_type=ITEM_COMPONENT)
        Cb = mdl.get_item("Rb", parent=comp_handle, item_type=ITEM_COMPONENT)
        Cc = mdl.get_item("Rc", parent=comp_handle, item_type=ITEM_COMPONENT)
        if not pA:
            pA = mdl.create_port(parent=comp_handle, name="A1", direction="out", kind="pe",
                                 terminal_position=("top", 1),
                                 position=(8112, 8024), rotation="right")
            mdl.create_connection(junA0, pA, name="ConnAA0")
        if not Ra:
            Ra = mdl.create_component("pas_resistor", parent=comp_handle, name="Ra", position=(8112, 8128),
                                      rotation="right")
            mdl.set_property_value(mdl.prop(Ra, "resistance"), "Ra")
            mdl.create_connection(mdl.term(Ra, "p_node"), junA0, name="Conn21")
            mdl.create_connection(mdl.term(Ra, "n_node"), junA1, name="Conn_A")
            pf_mode_fcn(mdl, container_handle, pf_mode_3ph, 'A', (8112, 8232), (8112, 8288))
        if not pB:
            pB = mdl.create_port(parent=comp_handle, name="B1", direction="out", kind="pe",
                                 terminal_position=("top", 2),
                                 position=(8192, 8024), rotation="right")
            mdl.create_connection(junB0, pB, name="ConnBB0")
        if not Rb:
            Rb = mdl.create_component("pas_resistor", parent=comp_handle, name="Rb", position=(8192, 8128),
                                      rotation="right")
            mdl.set_property_value(mdl.prop(Rb, "resistance"), "Rb")
            mdl.create_connection(mdl.term(Rb, "p_node"), junB0, name="Conn19")
            mdl.create_connection(mdl.term(Rb, "n_node"), junB1, name="Conn_B")
            pf_mode_fcn(mdl, container_handle, pf_mode_3ph, 'B', (8192, 8232), (8192, 8288))
        if pC:
            pf_mode_fcn(mdl, container_handle, "Unit", 'C', (8272, 8232), (8272, 8288))
            mdl.delete_item(pC)
            mdl.delete_item(Rc)



    elif new_value == "1":
        junA0 = mdl.get_item("JA0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junB0 = mdl.get_item("JB0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junC0 = mdl.get_item("JC0", parent=comp_handle, item_type=ITEM_JUNCTION)
        junA1 = mdl.get_item("JA1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junB1 = mdl.get_item("JB1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junC1 = mdl.get_item("JC1", parent=comp_handle, item_type=ITEM_JUNCTION)
        junN = mdl.get_item("JN", parent=comp_handle, item_type=ITEM_JUNCTION)
        pA = mdl.get_item("A1", parent=comp_handle, item_type=ITEM_PORT)
        pB = mdl.get_item("B1", parent=comp_handle, item_type=ITEM_PORT)
        pC = mdl.get_item("C1", parent=comp_handle, item_type=ITEM_PORT)
        connAA0 = mdl.get_item("Conn_AA0", parent=comp_handle, item_type=ITEM_CONNECTION)
        connBB0 = mdl.get_item("Conn_BB0", parent=comp_handle, item_type=ITEM_CONNECTION)
        connCC0 = mdl.get_item("Conn_CC0", parent=comp_handle, item_type=ITEM_CONNECTION)
        Ra = mdl.get_item("Ra", parent=comp_handle, item_type=ITEM_COMPONENT)
        Rb = mdl.get_item("Rb", parent=comp_handle, item_type=ITEM_COMPONENT)
        Rc = mdl.get_item("Rc", parent=comp_handle, item_type=ITEM_COMPONENT)
        La = mdl.get_item("Ra", parent=comp_handle, item_type=ITEM_COMPONENT)
        Lb = mdl.get_item("Rb", parent=comp_handle, item_type=ITEM_COMPONENT)
        Lc = mdl.get_item("Rc", parent=comp_handle, item_type=ITEM_COMPONENT)
        Ca = mdl.get_item("Ra", parent=comp_handle, item_type=ITEM_COMPONENT)
        Cb = mdl.get_item("Rb", parent=comp_handle, item_type=ITEM_COMPONENT)
        Cc = mdl.get_item("Rc", parent=comp_handle, item_type=ITEM_COMPONENT)

        if not junN:
            junN = mdl.create_junction(name='JN', parent=comp_handle, kind='pe',
                                       position=(8192, 8328))

        connAN = mdl.get_item("Conn_AN", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not connAN:
            mdl.create_connection(junA1, junN, name="Conn_AN")
        connBN = mdl.get_item("Conn_BN", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not connBN:
            mdl.create_connection(junB1, junN, name="Conn_BN")
        connCN = mdl.get_item("Conn_CN", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not connCN:
            mdl.create_connection(junC1, junN, name="Conn_CN")

        if not pA:
            pA = mdl.create_port(parent=comp_handle, name="A1", direction="out", kind="pe",
                                 terminal_position=(0, -30),
                                 position=(8112, 8024), rotation="right")
            mdl.create_connection(junA0, pA, name="ConnAA0")
        else:
            mdl.set_port_properties(pA, terminal_position=(0, -30))

        if not Ra:
            Ra = mdl.create_component("pas_resistor", parent=comp_handle, name="Ra", position=(8112, 8128),
                                      rotation="right")
            mdl.set_property_value(mdl.prop(Ra, "resistance"), "Ra")
            mdl.create_connection(mdl.term(Ra, "p_node"), junA0, name="Conn21")
            mdl.create_connection(mdl.term(Ra, "n_node"), junA1, name="Conn_A")
            pf_mode_fcn(mdl, container_handle, pf_mode_3ph, 'A', (8112, 8232), (8112, 8288))
        if pB:
            pf_mode_fcn(mdl, container_handle, "Unit", 'B', (8192, 8232), (8192, 8288))
            mdl.delete_item(pB)
            mdl.delete_item(Rb)

        if pC:
            pf_mode_fcn(mdl, container_handle, "Unit", 'C', (8272, 8232), (8272, 8288))
            mdl.delete_item(pC)
            mdl.delete_item(Rc)

def define_icon(mdl, mask_handle):
    phases = mdl.get_property_value(mdl.prop(mask_handle, "phases"))
    grounded = mdl.get_property_value(mdl.prop(mask_handle, "ground_connected"))

    conn_type = mdl.get_property_value(mdl.prop(mask_handle, "conn_type"))

    if int(phases) == 1:
        if grounded:
            mdl.set_component_icon_image(mask_handle, 'images/load_1ph_gnd.svg')
        else:
            mdl.set_component_icon_image(mask_handle, 'images/load_1ph.svg')
    else:
        if grounded:
            mdl.set_component_icon_image(mask_handle, 'images/load_3Y_gnd.svg')
        else:
            if conn_type == 'Δ':
                mdl.set_component_icon_image(mask_handle, 'images/load_3D.svg')
            else:
                mdl.set_component_icon_image(mask_handle, 'images/load_3Y.svg')






import numpy as np
from itertools import combinations
import dss_thcc_lib.component_scripts.util as util
import importlib

x0, y0 = (8192, 8192)
old_state = {}


def get_sld_conversion_info(mdl, mask_handle, sld_name, multiline_ports, side, terminal_positions, sld_term_position):

    # multiline_ports_1 = ["A1", "B1", "C1"]

    port_config_dict = {
        sld_name: {
            "multiline_ports": multiline_ports,
            "side": side,
            "bus_terminal_position": sld_term_position,
            "hide_name": True,
        },
    }
    #
    # Tag info
    #
    tag_config_dict = {}

    #
    # Terminal positions
    #
    # terminal_positions = {
    #     "A1": (-48, -24),
    #     "B1": (-16, -24),
    #     "C1": (16, -24),
    # }

    return port_config_dict, tag_config_dict, terminal_positions


def tp_connection_edited(mdl, mask_handle, new_value):
    """
    This function manages the mask properties
    If tp_connection == "Y - Grounded", the fields for Rneut and Xneut
    will be available.
    """
    rneut_prop = mdl.prop(mask_handle, "Rneut")
    xneut_prop = mdl.prop(mask_handle, "Xneut")

    if new_value == "Y - Grounded":
        # Enable user input fields for N to Gnd impedance
        mdl.enable_property(mdl.prop(mask_handle, "Rneut"))
        mdl.enable_property(mdl.prop(mask_handle, "Xneut"))
        # We don't want to modify Rneut and Xneut user values
        # on the 'on change' event. We put zeros only when
        # the user commuted from "Y" or "Δ" to "Y - Grounded"
        if mdl.get_property_disp_value(rneut_prop) == "'inf'":
            mdl.set_property_value(rneut_prop, "0.0")
        if mdl.get_property_disp_value(xneut_prop) == "'inf'":
            mdl.set_property_value(xneut_prop, "0.0")
    else:
        # Disable user input fields for N to Gnd impedance
        # show 'inf' because they are disconnected
        mdl.set_property_disp_value(rneut_prop, "'inf'")
        mdl.set_property_disp_value(xneut_prop, "'inf'")
        mdl.disable_property(mdl.prop(mask_handle, "Rneut"))
        mdl.disable_property(mdl.prop(mask_handle, "Xneut"))


def delete_port(mdl, name, parent):
    comp = mdl.get_item(name, parent=parent, item_type="port")
    if comp:
        mdl.delete_item(comp)
        return True


def enable_disable_grounds(mdl, mask_handle, num_windings):
    """
    This function enable or disable the combobox to select the type of the
    connection according to the number of windings.
    For instance, if num_windings == 3, disable the fourth type of connection
    combobox (sec3_conn), and so on.
    """
    tp_prim_prop = mdl.prop(mask_handle, "prim_conn")
    tp_sec1_prop = mdl.prop(mask_handle, "sec1_conn")
    tp_sec2_prop = mdl.prop(mask_handle, "sec2_conn")
    tp_sec3_prop = mdl.prop(mask_handle, "sec3_conn")

    enable_disable_conn(mdl, mask_handle)

    if num_windings == 2:
        mdl.disable_property(tp_sec3_prop)
        mdl.disable_property(tp_sec2_prop)
        mdl.enable_property(tp_sec1_prop)
        mdl.enable_property(tp_prim_prop)

    elif num_windings == 3:
        mdl.disable_property(tp_sec3_prop)
        mdl.enable_property(tp_sec1_prop)
        mdl.enable_property(tp_sec2_prop)
        mdl.enable_property(tp_prim_prop)

    elif num_windings == 4:
        mdl.enable_property(tp_sec1_prop)
        mdl.enable_property(tp_sec2_prop)
        mdl.enable_property(tp_sec3_prop)
        mdl.enable_property(tp_prim_prop)


def update_neutrals(mdl, mask_handle, trafo_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)
    num_windings = int(mdl.get_property_disp_value(mdl.prop(mask_handle, "num_windings")))
    trafo_handle = mdl.get_item("T1", parent=comp_handle)

    conn_dict = ["prim", "sec1", "sec2", "sec3"]
    pos_y = 346 if num_windings == 4 else 240

    # for loop for each winding
    # It takes the tp_conn for each winding
    for idx in range(0, num_windings):
        conn_prop = mdl.prop(mask_handle, conn_dict[idx] + "_conn")
        tp_conn = mdl.get_property_disp_value(conn_prop)

        if tp_conn == "Y" or tp_conn == "Y - Grounded" and created_ports:
            if idx == 0:
                new_port_n = created_ports.get("N1")

                if not mdl.get_item(f"N1n{str(idx + 1)}", parent=comp_handle, item_type="connection"):
                    mdl.create_connection(mdl.term(trafo_handle, "n" + str(idx + 1)),
                                          new_port_n, name=f"N1n{str(idx + 1)}")
            else:
                new_port_n = created_ports.get("N" + str(idx + 1))

                if not mdl.get_item(f"N{str(idx + 1)}n{str(idx + 1)}", parent=comp_handle, item_type="connection"):
                    mdl.create_connection(mdl.term(trafo_handle, "n" + str(idx + 1)),
                                          new_port_n, name=f"N{str(idx + 1)}n{str(idx + 1)}")

        # If it is selected "Y - Grounded", place the grounding impedance for each neutral of the trafo...
        if tp_conn == "Y - Grounded":

            if idx == 0:
                gnd0 = mdl.get_item("gnd0", parent=comp_handle)
                if not gnd0:
                    gnd0 = mdl.create_component("core/Ground", name="gnd0", parent=comp_handle,
                                                position=(x0 + 150, y0 + 750))

                gnd_z0 = mdl.get_item("Gnd Z0", parent=comp_handle, item_type="component")
                if not gnd_z0:
                    gnd_z0 = mdl.create_component("OpenDSS/Ground Impedance", parent=comp_handle, name="Gnd Z0",
                                                  position=(x0 + 150, y0 + 650), rotation="up")
                    mdl.set_property_value(mdl.prop(gnd_z0, "f"), "baseFreq")
                    mdl.set_property_value(mdl.prop(gnd_z0, "Rneut"), "Rneut_prim")
                    mdl.set_property_value(mdl.prop(gnd_z0, "Xneut"), "Xneut_prim")

                # Create connections:
                # Ground impedance to GND, and
                # Ground impedance to the transformer terminal
                con_z02gnd = mdl.get_item("Conn_Z02gnd", parent=comp_handle, item_type="connection")
                if not con_z02gnd:
                    mdl.create_connection(mdl.term(gnd_z0, "G"), mdl.term(gnd0, "node"), "Conn_Z02gnd")

                con_z02n = mdl.get_item("Conn_Z02N", parent=comp_handle, item_type="connection")
                if not con_z02n:
                    mdl.create_connection(mdl.term(gnd_z0, "N"), mdl.term(trafo_handle, "n1"), "Conn_Z02N")

            elif idx == 1:
                gnd1 = mdl.get_item("gnd1", parent=comp_handle)
                if not gnd1:
                    gnd1 = mdl.create_component("core/Ground", name="gnd1", parent=comp_handle,
                                                position=(x0 + 250, y0 + 750))

                gnd_z1 = mdl.get_item("Gnd Z1", parent=comp_handle, item_type="component")
                if not gnd_z1:
                    gnd_z1 = mdl.create_component("OpenDSS/Ground Impedance", parent=comp_handle, name="Gnd Z1",
                                                  position=(x0 + 250, y0 + 650), rotation="up")
                    mdl.set_property_value(mdl.prop(gnd_z1, "f"), "baseFreq")
                    mdl.set_property_value(mdl.prop(gnd_z1, "Rneut"), "Rneut_sec1")
                    mdl.set_property_value(mdl.prop(gnd_z1, "Xneut"), "Xneut_sec1")

                # Create connections:
                # Ground impedance to GND, and
                # Ground impedance to the transformer Neutral terminal
                con_z12gnd = mdl.get_item("Conn_Z12gnd", parent=comp_handle, item_type="connection")
                if not con_z12gnd:
                    mdl.create_connection(mdl.term(gnd_z1, "G"), mdl.term(gnd1, "node"), "Conn_Z12gnd")

                con_z12n = mdl.get_item("Conn_Z12N", parent=comp_handle, item_type="connection")
                if not con_z12n:
                    mdl.create_connection(mdl.term(gnd_z1, "N"), mdl.term(trafo_handle, "n2"), "Conn_Z12N")

            elif idx == 2:
                gnd2 = mdl.get_item("gnd2", parent=comp_handle)

                if not gnd2:
                    gnd2 = mdl.create_component("core/Ground", name="gnd2", parent=comp_handle,
                                                position=(x0 + 350, y0 + 750))

                gnd_z2 = mdl.get_item("Gnd Z2", parent=comp_handle, item_type="component")
                if not gnd_z2:
                    gnd_z2 = mdl.create_component("OpenDSS/Ground Impedance", parent=comp_handle, name="Gnd Z2",
                                                  position=(x0 + 350, y0 + 650), rotation="up")
                    mdl.set_property_value(mdl.prop(gnd_z2, "f"), "baseFreq")
                    mdl.set_property_value(mdl.prop(gnd_z2, "Rneut"), "Rneut_sec2")
                    mdl.set_property_value(mdl.prop(gnd_z2, "Xneut"), "Xneut_sec2")

                # Create connections:
                # Ground impedance to GND, and
                # Ground impedance to the transformer terminal
                con_z22gnd = mdl.get_item("Conn_Z22gnd", parent=comp_handle, item_type="connection")
                if not con_z22gnd:
                    mdl.create_connection(mdl.term(gnd_z2, "G"), mdl.term(gnd2, "node"), "Conn_Z22gnd")

                con_z22n = mdl.get_item("Conn_Z22N", parent=comp_handle, item_type="connection")
                if not con_z22n:
                    mdl.create_connection(mdl.term(gnd_z2, "N"), mdl.term(trafo_handle, "n3"), "Conn_Z22N")

            elif idx == 3:
                gnd3 = mdl.get_item("gnd3", parent=comp_handle)
                if not gnd3:
                    gnd3 = mdl.create_component("core/Ground", name="gnd3", parent=comp_handle,
                                                position=(x0 + 450, y0 + 750))

                gnd_z3 = mdl.get_item("Gnd Z3", parent=comp_handle, item_type="component")
                if not gnd_z3:
                    gnd_z3 = mdl.create_component("OpenDSS/Ground Impedance", parent=comp_handle, name="Gnd Z3",
                                                  position=(x0 + 450, y0 + 650), rotation="up")
                    mdl.set_property_value(mdl.prop(gnd_z3, "f"), "baseFreq")
                    mdl.set_property_value(mdl.prop(gnd_z3, "Rneut"), "Rneut_sec3")
                    mdl.set_property_value(mdl.prop(gnd_z3, "Xneut"), "Xneut_sec3")

                # Create connections:
                # Ground impedance to GND, and
                # Ground impedance to the transformer terminal
                con_z32gnd = mdl.get_item("Conn_Z32gnd", parent=comp_handle, item_type="connection")
                if not con_z32gnd:
                    mdl.create_connection(mdl.term(gnd_z3, "G"), mdl.term(gnd3, "node"), "Conn_Z32gnd")

                con_z32n = mdl.get_item("Conn_Z32N", parent=comp_handle, item_type="connection")
                if not con_z32n:
                    mdl.create_connection(mdl.term(gnd_z3, "N"), mdl.term(trafo_handle, "n4"), "Conn_Z32N")



        # if the tp_conn is not "Y - Grounded", we delete the grounds and ground impedance
        else:
            if idx == 0:
                gnd0 = mdl.get_item("gnd0", parent=comp_handle)
                if gnd0:
                    mdl.delete_item(gnd0)

                gnd_z0 = mdl.get_item("Gnd Z0", parent=comp_handle, item_type="component")
                if gnd_z0:
                    mdl.delete_item(gnd_z0)

            elif idx == 1:
                gnd1 = mdl.get_item("gnd1", parent=comp_handle)
                if gnd1:
                    mdl.delete_item(gnd1)

                gnd_z1 = mdl.get_item("Gnd Z1", parent=comp_handle, item_type="component")
                if gnd_z1:
                    mdl.delete_item(gnd_z1)

            elif idx == 2:
                gnd2 = mdl.get_item("gnd2", parent=comp_handle)
                if gnd2:
                    mdl.delete_item(gnd2)

                gnd_z2 = mdl.get_item("Gnd Z2", parent=comp_handle, item_type="component")
                if gnd_z2:
                    mdl.delete_item(gnd_z2)

            elif idx == 3:
                gnd3 = mdl.get_item("gnd3", parent=comp_handle)
                if gnd3:
                    mdl.delete_item(gnd3)

                gnd_z3 = mdl.get_item("Gnd Z3", parent=comp_handle, item_type="component")
                if gnd_z3:
                    mdl.delete_item(gnd_z3)

    # Now check if the num_windings is less than the max allowed ( < 4 ). If it is,
    # we need to check if there are remaining grounds and Grounding Impedances to delete them.
    if num_windings < 3:
        # if num_windings < 3, we have only 2 windings (0 and 1), so we delete the 3 and 4 gnd z comps
        gnd2 = mdl.get_item("gnd2", parent=comp_handle)
        if gnd2:
            mdl.delete_item(gnd2)

        gnd_z2 = mdl.get_item("Gnd Z2", parent=comp_handle, item_type="component")
        if gnd_z2:
            mdl.delete_item(gnd_z2)

        gnd3 = mdl.get_item("gnd3", parent=comp_handle)
        if gnd3:
            mdl.delete_item(gnd3)

        gnd_z3 = mdl.get_item("Gnd Z3", parent=comp_handle, item_type="component")
        if gnd_z3:
            mdl.delete_item(gnd_z3)

    elif num_windings < 4:
        # If the num_windings is less than 4, we delete the gnd z comps of the last winding if they exists
        gnd3 = mdl.get_item("gnd3", parent=comp_handle)
        if gnd3:
            mdl.delete_item(gnd3)

        gnd_z3 = mdl.get_item("Gnd Z3", parent=comp_handle, item_type="component")
        if gnd_z3:
            mdl.delete_item(gnd_z3)


def update_subsystem_components(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)
    num_windings = int(mdl.get_property_disp_value(mdl.prop(mask_handle, "num_windings")))

    trafo_tag_names = [f"TagT{phase}{winding}" for winding in "1234" for phase in "ABCN"]
    conn_dict = ["prim", "sec1", "sec2", "sec3"]

    # Delete trafo tags
    for tag in trafo_tag_names:
        tag_handle = mdl.get_item(tag, parent=comp_handle, item_type="tag")
        if tag_handle:
            mdl.delete_item(tag_handle)

    trafo_handle = mdl.get_item("T1", parent=comp_handle)

    # Delete 3P transformer
    if trafo_handle:
        mdl.delete_item(trafo_handle)

    tr_dict = {2: "core/Three Phase Two Winding Transformer",
               3: "core/Three Phase Three Winding Transformer",
               4: "core/Three Phase Four Winding Transformer"}

    # Create new 3P transformer
    trafo_handle = mdl.create_component(
        tr_dict[num_windings],
        parent=comp_handle,
        name="T1",
        position=(x0 + 256, y0)
    )
    mdl.set_property_value(mdl.prop(trafo_handle, "input"), "SI")

    # Y positions
    if num_windings == 2:
        pos_a = [-96, -96]
        pos_b = [0, 0]
        pos_c = [96, 96]

    else:
        pos_a = [-96, -346, -96, 154] if num_windings == 4 else [-96, -240, 48]
        pos_b = [y + 96 for y in pos_a]
        pos_c = [y + 96 for y in pos_b]

    update_all_windings(mdl, mask_handle, created_ports)

    # Create transformer tags
    trafo_tag_labels = [f"T_{phase}{winding}" for winding in "1234" for phase in "ABCN"]

    for idx in range(1, num_windings + 1):
        conn_prop = mdl.prop(mask_handle, conn_dict[idx - 1] + "_conn")
        tp_conn = mdl.get_property_disp_value(conn_prop)

        # A
        new_tag_a = mdl.create_tag(
            name=trafo_tag_names[4 * (idx - 1)],
            value=trafo_tag_labels[4 * (idx - 1)],
            scope='local',
            parent=comp_handle,
            flip="none" if idx == 1 else "flip_horizontal",
            rotation='up',
            position=(x0 + 60 if idx == 1 else x0 + 408, y0 - 96 if idx == 1 else y0 + pos_a[idx - 1])
        )

        if idx == 1:
            mdl.create_connection(mdl.term(trafo_handle, "prm_1"), new_tag_a)
        else:
            mdl.create_connection(mdl.term(trafo_handle, "sec_" + str(3 * (idx - 2) + 1)), new_tag_a)
        # B
        new_tag_b = mdl.create_tag(
            name=trafo_tag_names[4 * (idx - 1) + 1],
            value=trafo_tag_labels[4 * (idx - 1) + 1],
            scope='local',
            parent=comp_handle,
            flip="none" if idx == 1 else "flip_horizontal",
            rotation='up',
            position=(x0 + 60 if idx == 1 else x0 + 408, y0 if idx == 1 else y0 + pos_b[idx - 1])
        )
        if idx == 1:
            mdl.create_connection(mdl.term(trafo_handle, "prm_2"), new_tag_b)
        else:
            mdl.create_connection(mdl.term(trafo_handle, "sec_" + str(3 * (idx - 2) + 2)), new_tag_b)
        # C
        new_tag_c = mdl.create_tag(
            name=trafo_tag_names[4 * (idx - 1) + 2],
            value=trafo_tag_labels[4 * (idx - 1) + 2],
            scope='local',
            parent=comp_handle,
            flip="none" if idx == 1 else "flip_horizontal",
            rotation='up',
            position=(x0 + 60 if idx == 1 else x0 + 408, y0 + 96 if idx == 1 else y0 + pos_c[idx - 1])
        )
        if idx == 1:
            mdl.create_connection(mdl.term(trafo_handle, "prm_3"), new_tag_c)
        else:
            mdl.create_connection(mdl.term(trafo_handle, "sec_" + str(3 * (idx - 2) + 3)), new_tag_c)
        # N
        # if not idx == 1:
        # If the connection type is Δ, we don't create the Neutral tags
        if tp_conn != "Δ":
            new_tag_n = mdl.create_tag(
                name=trafo_tag_names[4 * (idx - 1) + 3],
                value=trafo_tag_labels[4 * (idx - 1) + 3],
                scope='local',
                parent=comp_handle,
                flip="none" if idx == 1 else "flip_horizontal",
                rotation='up',
                position=(x0 + 60 if idx == 1 else x0 + 408, y0 + 48 * idx + 90 * num_windings)
            )

            mdl.create_connection(mdl.term(trafo_handle, f"n{idx}"), new_tag_n)

    # Right ports and tags
    port_names = [f"{phase}{winding}" for winding in "234" for phase in "ABC"]
    tag_names = [f"Tag{phase}{winding}" for winding in "234" for phase in "ABC"]
    tag_labels = [f"T_{phase}{winding}" for winding in "234" for phase in "ABC"]

    # Delete tags
    for t in tag_names:
        t_handle = mdl.get_item(t, parent=comp_handle)
        if t_handle:
            mdl.delete_item(t_handle)

    porty0 = y0 - 48 * 3 * (num_windings - 1)
    for idx in range(1, 3 * (num_windings - 1) + 1):
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

    update_neutrals(mdl, mask_handle, trafo_handle, created_ports)
    vreg_connection(mdl, mask_handle)


def vreg_connection(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Defaults
    trafo_tag_names = [f"TagT{phase}{winding}" for winding in "1234" for phase in "ABC"]
    left_reg_tag_names = ["TagRegA1", "TagRegB1", "TagRegC1"]
    right_reg_tag_names = ["TagRegA2", "TagRegB2", "TagRegC2"]
    port_tag_names = [f"Tag{phase}{winding}" for winding in "1234" for phase in "ABC"]

    trafo_labels = [f"T{phase}_{winding}" for winding in "1234" for phase in "ABC"]

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
        vreg_handle = mdl.get_item("Vreg", parent=comp_handle)

        ctrl_winding = mdl.get_property_value(mdl.prop(mask_handle, "ctrl_winding"))
        n_ctrl = ctrl_winding[-1]  # Get number of the ctrl winding
        trafo_tag_names = [f"TagTA{n_ctrl}", f"TagTB{n_ctrl}", f"TagTC{n_ctrl}"]
        port_tag_names = [f"TagA{n_ctrl}", f"TagB{n_ctrl}", f"TagC{n_ctrl}"]

        trafo_labels = [f"TA_{n_ctrl}", f"TB_{n_ctrl}", f"TC_{n_ctrl}"]
        port_labels = [f"Reg_A2", f"Reg_B2", f"Reg_C2"]

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

        if not prop_name == "XArray":
            if not len(prop_value) == num_windings:
                mdl.info(f'{base_str} {prop_name} property: {len(prop_value)} ({num_windings} expected)')
        else:
            if type(prop_value) == float or type(prop_value) == int:
                prop_value = [prop_value]
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
                prop_value = prop_value[0]
                f_prop = mdl.prop(trafo_inner, "f")
                converted_value = prop_value
                mdl.set_property_value(f_prop, converted_value)
            # Nominal voltages
            elif prop_name == "KVs":
                for num in range(1, num_windings + 1):
                    v_prop = mdl.prop(trafo_inner, "V" + str(num))
                    converted_value = 1000 * prop_value[num - 1]
                    mdl.set_property_value(v_prop, converted_value)
            # Resistances
            elif prop_name == "percentRs":
                kvs_prop = mdl.prop(comp_handle, "KVs")
                kvas_prop = mdl.prop(comp_handle, "KVAs")
                kvs = mdl.get_property_value(kvs_prop)
                kvas = mdl.get_property_value(kvas_prop)
                for num in range(1, num_windings + 1):
                    r_prop = mdl.prop(trafo_inner, "R" + str(num))
                    a = kvs[0] / kvs[num - 1]
                    base_r = kvs[0] * kvs[0] / kvas[0] * 1000
                    ''' Account for winding type '''
                    conn = 'prim_conn' if num == 1 else f'sec{num - 1}_conn'
                    yd = mdl.get_property_value(mdl.prop(comp_handle, conn))
                    factor = 1 if yd in ('Y', 'Y - Grounded') else 3
                    ''' ------------------------ '''
                    converted_value = factor * (
                            base_r / 100 * prop_value[num - 1]) / a ** 2
                    # if regcontrol_on:
                    #     converted_value = converted_value*0.99
                    mdl.set_property_value(r_prop, converted_value)
            # Magnetization
            elif prop_name in ["percentNoloadloss", "percentimag"]:
                prop_value = prop_value[0]
                kvs_prop = mdl.prop(comp_handle, "KVs")
                kvas_prop = mdl.prop(comp_handle, "KVAs")
                kvs = mdl.get_property_value(kvs_prop)
                kvas = mdl.get_property_value(kvas_prop)
                base_v = kvs[0] * 1000
                base_p = kvas[0] * 1000
                if prop_name == "percentNoloadloss":
                    try:
                        ''' Account for winding type '''
                        yd = mdl.get_property_value(mdl.prop(comp_handle, 'prim_conn'))
                        factor = 1 if yd in ('Y', 'Y - Grounded') else 3
                        ''' ------------------------ '''
                        converted_value = factor * ((base_v * base_v) / base_p) / (
                                prop_value / 100)  # baseV*baseV/(baseP*prop_value/100)
                        # if converted_value >= 0.99e5:
                        #    converted_value = "inf"
                    except ZeroDivisionError:
                        converted_value = "inf"
                    rm_prop = mdl.prop(trafo_inner, "Rm")
                    mdl.set_property_value(rm_prop, converted_value)
                elif prop_name == "percentimag":
                    ''' Account for winding type '''
                    yd = mdl.get_property_value(mdl.prop(comp_handle, 'prim_conn'))
                    factor = 1 if yd in ('Y', 'Y - Grounded') else 3
                    ''' ------------------------ '''
                    base_i = base_p / base_v
                    lm_prop = mdl.prop(trafo_inner, "Lm")
                    basefreq = mdl.get_property_value(mdl.prop(mask_handle, "baseFreq"))
                    if not prop_value <= 0:
                        converted_value = factor * ((base_v * base_v) / base_p) / (prop_value / 100) / (
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
                xsc_array = []

                for num in range(1, num_windings + 1):
                    base_prim = kvs[0] * kvs[0] / kvas[0] * 1000

                    ''' Account for winding type '''
                    conn = 'prim_conn' if num == 1 else f'sec{num - 1}_conn'
                    yd = mdl.get_property_value(mdl.prop(comp_handle, conn))
                    factor = 1 if yd in ('Y', 'Y - Grounded') else 3
                    ''' ------------------------ '''

                    a = kvs[0] / kvs[num - 1]
                    ind = factor * reactances_pct[num - 1] * base_prim / 100 / 2 / np.pi / basefreq / a ** 2
                    # if regcontrol_on:
                    #     ind = ind*0.99
                    l_prop = mdl.prop(trafo_inner, "L" + str(num))
                    converted_value = ind
                    mdl.set_property_value(l_prop, converted_value)

                xsc_idxs = list(combinations(range(num_windings), 2))
                for idx in xsc_idxs:
                    xsc_array.append(reactances_pct[idx[0]] + reactances_pct[idx[1]])

                mdl.set_property_value(mdl.prop(comp_handle, "XscArray"), str(xsc_array))
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
                regrange = max((float(maxtap) - 1), (1 - float(mintap))) * 100
                mdl.set_property_value(at_prop, regrange)
            elif prop_name in ["Rm", "Lm"]:
                t_prop = mdl.prop(t_inner_handle, prop_name)
                t_prop_value = mdl.get_property_value(t_prop)
                mdl.set_property_value(at_prop, t_prop_value)
            else:
                ctrl_winding = mdl.get_property_value(mdl.prop(mask_handle, "ctrl_winding"))
                n_ctrl = ctrl_winding[-1]  # Get number of the ctrl winding
                orig_prop_name = prop_name[0] + str(n_ctrl)
                t_prop = mdl.prop(t_inner_handle, orig_prop_name)
                t_prop_value = mdl.get_property_value(t_prop)
                mdl.set_property_value(at_prop, float(t_prop_value / 1000))


'''**********************************************************************
Function to manages the combobox to select the type of connection
It enables or disable the *_conn combobox according to the number
of windings of the transformer.
For instance, if the user selects num_windings == 3, the "sec3_conn"
combobox will be disabled because we don't have the fourth winding.

The Ground Impedance Rneut and Xneut fields are enabled if the
corresponding tp_conn is "Y - Grounded", otherwise they are disabled.
**********************************************************************'''


def enable_disable_conn(mdl, mask_handle):
    tp_prim_prop = mdl.prop(mask_handle, "prim_conn")
    tp_prim = mdl.get_property_disp_value(tp_prim_prop)
    rneut_prim_prop = mdl.prop(mask_handle, "Rneut_prim")
    xneut_prim_prop = mdl.prop(mask_handle, "Xneut_prim")
    tp_sec1_prop = mdl.prop(mask_handle, "sec1_conn")
    tp_sec1 = mdl.get_property_disp_value(tp_sec1_prop)
    rneut_sec1_prop = mdl.prop(mask_handle, "Rneut_sec1")
    xneut_sec1_prop = mdl.prop(mask_handle, "Xneut_sec1")
    tp_sec2_prop = mdl.prop(mask_handle, "sec2_conn")
    tp_sec2 = mdl.get_property_disp_value(tp_sec2_prop)
    rneut_sec2_prop = mdl.prop(mask_handle, "Rneut_sec2")
    xneut_sec2_prop = mdl.prop(mask_handle, "Xneut_sec2")
    tp_sec3_prop = mdl.prop(mask_handle, "sec3_conn")
    tp_sec3 = mdl.get_property_disp_value(tp_sec3_prop)
    rneut_sec3_prop = mdl.prop(mask_handle, "Rneut_sec3")
    xneut_sec3_prop = mdl.prop(mask_handle, "Xneut_sec3")

    num_windings_prop = mdl.prop(mask_handle, "num_windings")
    num_windings = mdl.get_property_disp_value(num_windings_prop)

    if tp_prim == "Y - Grounded":
        mdl.enable_property(rneut_prim_prop)
        mdl.enable_property(xneut_prim_prop)
    else:
        mdl.disable_property(rneut_prim_prop)
        mdl.disable_property(xneut_prim_prop)

    if num_windings == "2":
        mdl.enable_property(tp_sec1_prop)
        if tp_sec1 == "Y - Grounded":
            mdl.enable_property(rneut_sec1_prop)
            mdl.enable_property(xneut_sec1_prop)
        else:
            mdl.disable_property(rneut_sec1_prop)
            mdl.disable_property(xneut_sec1_prop)
        mdl.disable_property(tp_sec2_prop)
        mdl.disable_property(rneut_sec2_prop)
        mdl.disable_property(xneut_sec2_prop)
        mdl.disable_property(tp_sec3_prop)
        mdl.disable_property(rneut_sec3_prop)
        mdl.disable_property(xneut_sec3_prop)

    elif num_windings == "3":
        mdl.enable_property(tp_sec1_prop)
        mdl.enable_property(tp_sec2_prop)
        if tp_sec1 == "Y - Grounded":
            mdl.enable_property(rneut_sec1_prop)
            mdl.enable_property(xneut_sec1_prop)
        else:
            mdl.disable_property(rneut_sec1_prop)
            mdl.disable_property(xneut_sec1_prop)
        mdl.enable_property(tp_sec2_prop)
        if tp_sec2 == "Y - Grounded":
            mdl.enable_property(rneut_sec2_prop)
            mdl.enable_property(xneut_sec2_prop)
        else:
            mdl.disable_property(rneut_sec2_prop)
            mdl.disable_property(xneut_sec2_prop)
        mdl.disable_property(tp_sec3_prop)
        mdl.disable_property(rneut_sec3_prop)
        mdl.disable_property(xneut_sec3_prop)


    elif num_windings == "4":
        mdl.enable_property(tp_sec1_prop)
        mdl.enable_property(tp_sec2_prop)
        mdl.enable_property(tp_sec3_prop)
        if tp_sec1 == "Y - Grounded":
            mdl.enable_property(rneut_sec1_prop)
            mdl.enable_property(xneut_sec1_prop)
        else:
            mdl.disable_property(rneut_sec1_prop)
            mdl.disable_property(xneut_sec1_prop)
        mdl.enable_property(tp_sec2_prop)
        if tp_sec2 == "Y - Grounded":
            mdl.enable_property(rneut_sec2_prop)
            mdl.enable_property(xneut_sec2_prop)
        else:
            mdl.disable_property(rneut_sec2_prop)
            mdl.disable_property(xneut_sec2_prop)
        if tp_sec3 == "Y - Grounded":
            mdl.enable_property(rneut_sec3_prop)
            mdl.enable_property(xneut_sec3_prop)
        else:
            mdl.disable_property(rneut_sec3_prop)
            mdl.disable_property(xneut_sec3_prop)


def show_hide_couplings(mdl, mask_handle):
    num_windings = int(mdl.get_property_disp_value(mdl.prop(mask_handle, "num_windings")))

    if num_windings == 2:
        coup_prop = mdl.prop(mask_handle, "embedded_cpl")
        mdl.show_property(coup_prop)
        for n in range(2, 5):
            coup_prop = mdl.prop(mask_handle, "embedded_cpl_1" + str(n))
            mdl.hide_property(coup_prop)
    else:
        coup_prop = mdl.prop(mask_handle, "embedded_cpl")
        mdl.hide_property(coup_prop)
        for n in range(2, 5):
            coup_prop = mdl.prop(mask_handle, "embedded_cpl_1" + str(n))
            if n < num_windings + 1:
                mdl.show_property(coup_prop)
            else:
                mdl.hide_property(coup_prop)


def update_winding_configs(mdl, prop_handle, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)
    num_windings = int(mdl.get_property_disp_value(mdl.prop(mask_handle, "num_windings")))
    trafo_inner = mdl.get_item("T1", parent=comp_handle)

    wdg_num_dict = {"prim": "1", "sec1": "2", "sec2": "3", "sec3": "4"}
    wdg_conn_dict = {"Y": "Y", "Δ": "D", "Y - Grounded": "Y"}
    # wdg_clock_dict = {"Y": "0", "Δ": "1", "Y - Grounded": "0"}

    # y_or_d_prim = mdl.get_property_value(mdl.prop(comp_handle, "prim_conn"))
    ydprim_tmp = mdl.get_property_value(mdl.prop(comp_handle, "prim_conn"))
    if ydprim_tmp == "Δ":
        y_or_d_prim = "Δ"
    else:
        y_or_d_prim = "Y"

    wdg_name = mdl.get_name(prop_handle)[:4]

    yd_tmp = mdl.get_property_disp_value(prop_handle)

    if yd_tmp == "Δ":
        y_or_d = "Δ"
    else:
        y_or_d = "Y"

    if int(wdg_num_dict[wdg_name]) <= num_windings:
        inner_conn_prop = mdl.prop(trafo_inner, f"winding_{wdg_num_dict[wdg_name]}_connection")
        mdl.set_property_value(inner_conn_prop, wdg_conn_dict[y_or_d])

        if int(wdg_num_dict[wdg_name]) > 1:  # Secondaries
            if num_windings == 2:
                inner_clock_prop = mdl.prop(trafo_inner, "clock_number")
                if not y_or_d == y_or_d_prim:
                    mdl.set_property_value(inner_clock_prop, "1")
                else:
                    mdl.set_property_value(inner_clock_prop, "0")
            else:
                inner_clock_prop = mdl.prop(trafo_inner, "clk_num_1" + wdg_num_dict[wdg_name])
                if not y_or_d == y_or_d_prim:
                    mdl.set_property_value(inner_clock_prop, "1")
                else:
                    mdl.set_property_value(inner_clock_prop, "0")
        else:  # Primary
            # Update all others
            prop_names = ["sec1_conn", "sec2_conn", "sec3_conn"]

            for p in prop_names:
                update_winding_configs(mdl, mdl.prop(mask_handle, p), mask_handle)

    mdl.refresh_icon(mask_handle)


def update_all_windings(mdl, mask_handle, created_ports):
    prop_names = ["prim_conn", "sec1_conn", "sec2_conn", "sec3_conn"]
    for p in prop_names:
        update_winding_configs(mdl, mdl.prop(mask_handle, p), mask_handle)


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

        mdl.set_property_disp_value(winding_voltage_prop, str(vreg * ptratio * np.sqrt(3)))
        mdl.set_property_value(winding_voltage_prop, str(vreg * ptratio * np.sqrt(3)))

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


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    toggle_frequency_prop(mdl, mask_handle)


def delete_unused_ports(mdl, comp_handle, new_ports, current_ports):
    deleted_ports = []

    all_new_ports = [port for winding in new_ports for port in new_ports[winding]]
    for port_name in current_ports:
        if port_name not in all_new_ports:
            if delete_port(mdl, name=port_name, parent=comp_handle):
                deleted_ports.append(port_name)

    return deleted_ports


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    created_ports = {}

    comp_handle = mdl.get_parent(mask_handle)
    num_windings = int(mdl.get_property_disp_value(mdl.prop(mask_handle, "num_windings")))
    winding_names = ["prim", "sec1", "sec2", "sec3"]

    # Get current ports
    current_ports = {mdl.get_name(port): port for port in mdl.get_items(parent=comp_handle, item_type="port")}

    #
    # New ports for the selected configuration
    #

    # Default ports
    winding_ports = {
        1: [f"{phase}1" for phase in "ABCN"],
        2: [f"{phase}2" for phase in "ABCN"],
    }
    if num_windings > 2:
        winding_ports.update({3: [f"{phase}3" for phase in "ABCN"]})
    if num_windings > 3:
        winding_ports.update({4: [f"{phase}4" for phase in "ABCN"]})

    # Remove neutral for Delta connections
    for idx, wdg_name in enumerate(winding_names[:]):
        conn_type_prop = mdl.prop(mask_handle, wdg_name + "_conn")
        conn_type_value = mdl.get_property_disp_value(conn_type_prop)

        if conn_type_value == "Δ":
            winding_ports[idx + 1].remove(f"N{idx + 1}")

    # Delete ports
    deleted_ports = delete_unused_ports(mdl, comp_handle, winding_ports, current_ports)

    #
    # Create new ports if necessary
    #

    # Primary side ports always exist, except for neutral
    primary_ports = winding_ports[1]
    for prim_port in primary_ports:
        new_port = mdl.get_item(prim_port, parent=comp_handle, item_type="port")
        port_pos = (8224, 8200 + (164 * num_windings))
        if prim_port == "N1":
            if not new_port:
                new_port = mdl.create_port(
                    name="N1",
                    parent=comp_handle,
                    flip="flip_none",
                    rotation='up',
                    position=port_pos,
                    hide_name=True,
                    terminal_position=(-32, 48)
                )
            else:
                mdl.set_position(new_port, port_pos)
        created_ports.update({prim_port: new_port})

    # for idx in range(1, 3 * (num_windings - 1) + 1)
    # Check/create the secondary ports
    porty0 = y0 - 48 - 48 * 3 * (num_windings - 2)
    for sec_n in range(2, num_windings + 1):
        # Phase ports
        for idx, port in enumerate(winding_ports[sec_n]):
            new_port = mdl.get_item(port, parent=comp_handle, item_type="port")
            if port.startswith("N"):
                port_pos = (x0 + 408, y0 + (164 * num_windings) + (sec_n - 2) * 48)
            else:
                port_pos = (x0 + 1180, porty0 + idx * 96 + (sec_n - 2) * 3 * 96)
            term_pos = (32, -48 - 80 * (num_windings - 2) + idx * 32 + (sec_n - 2) * 160)
            if not new_port:
                new_port = mdl.create_port(
                    name=port,
                    parent=comp_handle,
                    flip="flip_horizontal",
                    rotation='up',
                    position=port_pos,
                    hide_name=True,
                    terminal_position=term_pos
                )
            else:
                mdl.set_position(new_port, port_pos)
                mdl.set_port_properties(new_port, terminal_position=term_pos, hide_term_label=True)

            created_ports.update({port: new_port})

    return created_ports, deleted_ports


def define_icon(mdl, mask_handle):
    wdg_names = ["prim", "sec1", "sec2", "sec3"]
    num_windings = int(mdl.get_property_disp_value(mdl.prop(mask_handle, "num_windings")))
    sld_mode = mdl.get_property_disp_value(mdl.prop(mask_handle, "sld_mode"))

    if sld_mode in (True, "True"):
        sld = True
    else:
        sld = False

    #
    # Set image
    #
    neutral_strings = ""
    for wdg_name in wdg_names[:num_windings]:
        conn_prop = mdl.prop(mask_handle, wdg_name + "_conn")
        conn_value = mdl.get_property_disp_value(conn_prop)

        if sld:
            neutral_strings += "n"
        else:
            if conn_value in ("Y", "Δ"):
                neutral_strings += "n"
            else:
                neutral_strings += "g"

    if sld:
        image_name = f"t_3p{num_windings}w_{neutral_strings}_sld.svg"
    else:
        image_name = f"t_3p{num_windings}w_{neutral_strings}.svg"

    mdl.set_component_icon_image(mask_handle, f"images/{image_name}")

    if sld:
        wdg_conn_dict = {"Y": "Y", "Δ": "Δ", "Y - Grounded": "Yg"}
    else:
        wdg_conn_dict = {"Y": "Y", "Δ": "Δ", "Y - Grounded": "Y"}

    #
    # Set text
    #
    mdl.set_color(mask_handle, "blue")

    for idx, wdg_name in enumerate(wdg_names[:num_windings]):
        conn_prop = mdl.prop(mask_handle, wdg_name + "_conn")
        conn_value = mdl.get_property_disp_value(conn_prop)

        if sld:
            size_y = 64 + 64 * (int(num_windings) - 2)
            port_dist = 64
            sld_mult = 0.8
        else:
            size_y = 124 + 160 * (int(num_windings) - 2)
            port_dist = 160
            sld_mult = 1

        if wdg_name == "prim":
            # Y or D
            mdl.disp_component_icon_text(mask_handle, wdg_conn_dict[conn_value], rotate="rotate", relpos_x=0.2,
                                         relpos_y=(6 + 0.5 * port_dist * (num_windings - 2)) / size_y,
                                         size=8, trim_factor=2)
            # Winding number
            mdl.disp_component_icon_text(mask_handle, "1", rotate="rotate", relpos_x=0.1,
                                         relpos_y=(sld_mult * 60 + 0.5 * port_dist * (num_windings - 2)) / size_y,
                                         size=8, trim_factor=2)
            # Neutral
            if not conn_value == "Δ" and not sld:
                mdl.disp_component_icon_text(mask_handle, "N", rotate="rotate", relpos_x=0.1,
                                             relpos_y=(100 + 0.5 * port_dist * (num_windings - 2)) / size_y,
                                             size=8, trim_factor=2)
        else:
            # Y or D
            mdl.disp_component_icon_text(mask_handle, wdg_conn_dict[conn_value], rotate="rotate", relpos_x=0.8,
                                         relpos_y=(6 + port_dist * (idx - 1)) / size_y,
                                         size=8, trim_factor=2)
            # Winding number
            mdl.disp_component_icon_text(mask_handle, f"{idx + 1}", rotate="rotate", relpos_x=0.9,
                                         relpos_y=(sld_mult * 60 + port_dist * (idx - 1)) / size_y,
                                         size=8, trim_factor=2)
            # Neutral
            if not conn_value == "Δ" and not sld:
                mdl.disp_component_icon_text(mask_handle, "N", rotate="rotate", relpos_x=0.95,
                                             relpos_y=(100 + port_dist * (idx - 1)) / size_y,
                                             size=8, trim_factor=2)


def place_voltage_regulator(mdl, mask_handle, new_value):
    comp_handle = mdl.get_sub_level_handle(mask_handle)
    if new_value:
        vreg = mdl.get_item("Vreg", parent=comp_handle, item_type="component")
        if not vreg:
            vreg = mdl.create_component("OpenDSS/three-phase voltage regulator",
                                        parent=comp_handle, name="Vreg",
                                        position=(8960, 8232), rotation="up")
        tag_reg_a1 = mdl.get_item("TagRegA1", parent=comp_handle, item_type="tag")
        if not tag_reg_a1:
            tag_reg_a1 = mdl.create_tag(name="TagRegA1", value="not_used", scope='local',
                                        parent=comp_handle, rotation='up', position=(8776, 8088))

        tag_reg_b1 = mdl.get_item("TagRegB1", parent=comp_handle, item_type="tag")
        if not tag_reg_b1:
            tag_reg_b1 = mdl.create_tag(name="TagRegB1", value="not_used", scope='local',
                                        parent=comp_handle, rotation='up', position=(8776, 8184))

        tag_reg_c1 = mdl.get_item("TagRegC1", parent=comp_handle, item_type="tag")
        if not tag_reg_c1:
            tag_reg_c1 = mdl.create_tag(name="TagRegC1", value="not_used", scope='local',
                                        parent=comp_handle, rotation='up', position=(8776, 8280))

        tag_reg_n1 = mdl.get_item("Reg_N1", parent=comp_handle, item_type="tag")
        if not tag_reg_n1:
            tag_reg_n1 = mdl.create_tag(name="Reg_N1", value="T_N2", scope='local',
                                        parent=comp_handle, rotation='up', position=(8776, 8376))

        tag_reg_a2 = mdl.get_item("TagRegA2", parent=comp_handle, item_type="tag")
        if not tag_reg_a2:
            tag_reg_a2 = mdl.create_tag(name="TagRegA2", value="not_used", scope='local',
                                        parent=comp_handle, rotation='down', position=(9128, 8088))

        tag_reg_b2 = mdl.get_item("TagRegB2", parent=comp_handle, item_type="tag")
        if not tag_reg_b2:
            tag_reg_b2 = mdl.create_tag(name="TagRegB2", value="not_used", scope='local',
                                        parent=comp_handle, rotation='down', position=(9128, 8232))

        tag_reg_c2 = mdl.get_item("TagRegC2", parent=comp_handle, item_type="tag")
        if not tag_reg_c2:
            tag_reg_c2 = mdl.create_tag(name="TagRegC2", value="not_used", scope='local',
                                        parent=comp_handle, rotation='down', position=(9128, 8376))

        conn_netlist = [(tag_reg_a1, mdl.term(vreg, "RegA1")),
                        (tag_reg_b1, mdl.term(vreg, "RegB1")),
                        (tag_reg_c1, mdl.term(vreg, "RegC1")),
                        (tag_reg_n1, mdl.term(vreg, "RegN")),
                        (mdl.term(vreg, "RegA2"), tag_reg_a2),
                        (mdl.term(vreg, "RegB2"), tag_reg_b2),
                        (mdl.term(vreg, "RegC2"), tag_reg_c2)]
        for conn_handle in conn_netlist:
            if len(mdl.find_connections(conn_handle[0], conn_handle[1])) == 0:
                mdl.create_connection(conn_handle[0], conn_handle[1])
    else:
        vreg = mdl.get_item("Vreg", parent=comp_handle, item_type="component")
        tag_reg_a1 = mdl.get_item("TagRegA1", parent=comp_handle, item_type="tag")
        tag_reg_b1 = mdl.get_item("TagRegB1", parent=comp_handle, item_type="tag")
        tag_reg_c1 = mdl.get_item("TagRegC1", parent=comp_handle, item_type="tag")
        tag_reg_n1 = mdl.get_item("Reg_N1", parent=comp_handle, item_type="tag")
        tag_reg_a2 = mdl.get_item("TagRegA2", parent=comp_handle, item_type="tag")
        tag_reg_b2 = mdl.get_item("TagRegB2", parent=comp_handle, item_type="tag")
        tag_reg_c2 = mdl.get_item("TagRegC2", parent=comp_handle, item_type="tag")

        delete_list = [vreg,
                       tag_reg_a1,
                       tag_reg_b1,
                       tag_reg_c1,
                       tag_reg_n1,
                       tag_reg_a2,
                       tag_reg_b2,
                       tag_reg_c2]

        for component in delete_list:
            if component:
                mdl.delete_item(component)


def topology_dynamics(mdl, mask_handle, prop_handle):
    """
    This call the functions to build the transformer configuration according
    to the user selected parameters and configurations.
    """

    comp_handle = mdl.get_parent(mask_handle)

    if prop_handle:
        calling_prop_name = mdl.get_name(prop_handle)
    else:
        calling_prop_name = "init_code"

    current_pass_prop_values = {
        k: str(v) for k, v in mdl.get_property_values(comp_handle).items()
    }

    #
    # Get new property values to be applied (display values)
    #
    current_values = {}
    new_prop_values = {}
    for prop in mdl.get_property_values(comp_handle):
        p = mdl.prop(mask_handle, prop)
        new_prop_values[prop] = mdl.get_property_disp_value(p)
        current_values[prop] = mdl.get_property_value(p)

    #
    # If the property values are the same as on the previous run, stop
    #
    global old_state
    if new_prop_values == old_state.get(comp_handle):
        return

    if calling_prop_name == "init_code":
        mdl.refresh_icon(mask_handle)
        created_ports, _ = port_dynamics(mdl, mask_handle)
        update_subsystem_components(mdl, mask_handle, created_ports)
        enable_disable_conn(mdl, mask_handle)

    num_windings = new_prop_values.get("num_windings")
    if num_windings == "2":
        Y2_offset = 160
        Y3_offset = 0
        Y4_offset = 0
    elif num_windings == "3":
        Y2_offset = 80
        Y3_offset = 80
        Y4_offset = 0
    elif num_windings == "4":
        Y2_offset = 0
        Y3_offset = 0
        Y4_offset = 0
    else:
        Y2_offset = 160
        Y3_offset = 0
        Y4_offset = 0

    sld_info_dict = {
        "SLD1": {
            "port_names": ["A1", "B1", "C1"],
            "side": "left",
            "multi_term_pos": {
                "A1": (-32, -48),
                "B1": (-32, -16),
                "C1": (-32, 16),
            },
            "sld_term_pos": (-32, 0),
        },
        "SLD2": {
            "port_names": ["A2", "B2", "C2"],
            "side": "right",
            "multi_term_pos": {
                "A2": (32, -208 + Y2_offset),
                "B2": (32, -176 + Y2_offset),
                "C2": (32, -144 + Y2_offset),
            },
            "sld_term_pos": (32, -64 + 32 * Y2_offset / 80),
        },
        "SLD3": {
            "port_names": ["A3", "B3", "C3"],
            "side": "right",
            "multi_term_pos": {
                "A3": (32, -48 + Y3_offset),
                "B3": (32, -16 + Y3_offset),
                "C3": (32, 16 + Y3_offset),
            },
            "sld_term_pos": (32, 0 + 32 * Y3_offset / 80),
        },
        "SLD4": {
            "port_names": ["A4", "B4", "C4"],
            "side": "right",
            "multi_term_pos": {
                "A4": (32, 112 + Y4_offset),
                "B4": (32, 144 + Y4_offset),
                "C4": (32, 176 + Y4_offset),
            },
            "sld_term_pos": (32, 64 + 32 * Y4_offset / 80),
        },
    }

    if calling_prop_name not in ["sld_mode", "init_code"]:

        if old_state:
            current_state = old_state[comp_handle]
        else:
            current_state = new_prop_values

        prim_config = current_state.get("prim_conn")
        sec1_config = current_state.get("sec1_conn")
        sec2_config = current_state.get("sec2_conn")
        sec3_config = current_state.get("sec3_conn")

        if prim_config in ["Y - Grounded", "Y"]:
            if "N1" not in sld_info_dict.get("SLD1").get("port_names"):
                sld_info_dict.get("SLD1").get("port_names").append("N1")
            if "N1" not in sld_info_dict.get("SLD1").get("multi_term_pos").keys():
                sld_info_dict.get("SLD1").get("multi_term_pos")["N1"] = (-32, 48)
        else:
            if "N1" in sld_info_dict.get("SLD1").get("port_names"):
                sld_info_dict.get("SLD1").get("port_names").remove("N1")
            if "N1" in sld_info_dict.get("SLD1").get("multi_term_pos").keys():
                sld_info_dict.get("SLD1").get("multi_term_pos").pop("N1")

        if sec1_config in ["Y - Grounded", "Y"]:
            if "N2" not in sld_info_dict.get("SLD2").get("port_names"):
                sld_info_dict.get("SLD2").get("port_names").append("N2")
            if "N2" not in sld_info_dict.get("SLD2").get("multi_term_pos").keys():
                sld_info_dict.get("SLD2").get("multi_term_pos")["N2"] = (32, -112 + Y2_offset)
        else:
            if "N2" in sld_info_dict.get("SLD2").get("port_names"):
                sld_info_dict.get("SLD2").get("port_names").remove("N2")
            if "N2" in sld_info_dict.get("SLD2").get("multi_term_pos").keys():
                sld_info_dict.get("SLD2").get("multi_term_pos").pop("N2")

        if sec2_config in ["Y - Grounded", "Y"]:
            if "N3" not in sld_info_dict.get("SLD3").get("port_names"):
                sld_info_dict.get("SLD3").get("port_names").append("N3")
            if "N3" not in sld_info_dict.get("SLD3").get("multi_term_pos").keys():
                sld_info_dict.get("SLD3").get("multi_term_pos")["N3"] = (32, 48 + Y3_offset)
        else:
            if "N3" in sld_info_dict.get("SLD3").get("port_names"):
                sld_info_dict.get("SLD3").get("port_names").remove("N3")
            if "N3" in sld_info_dict.get("SLD3").get("multi_term_pos").keys():
                sld_info_dict.get("SLD3").get("multi_term_pos").pop("N3")

        if sec3_config in ["Y - Grounded", "Y"]:
            if "N4" not in sld_info_dict.get("SLD4").get("port_names"):
                sld_info_dict.get("SLD4").get("port_names").append("N4")
            if "N4" not in sld_info_dict.get("SLD4").get("multi_term_pos").keys():
                sld_info_dict.get("SLD4").get("multi_term_pos")["N4"] = (32, 208 + Y4_offset)
        else:
            if "N4" in sld_info_dict.get("SLD4").get("port_names"):
                sld_info_dict.get("SLD4").get("port_names").remove("N4")
            if "N4" in sld_info_dict.get("SLD4").get("multi_term_pos").keys():
                sld_info_dict.get("SLD4").get("multi_term_pos").pop("N4")

        for sld_winding in sld_info_dict.keys():
            currently_sld = mdl.get_item(sld_winding, parent=comp_handle, item_type="port")
            if currently_sld:
                # The terminal related to the current property hasn't been created yet
                importlib.reload(util)
                sld_info = get_sld_conversion_info(mdl, mask_handle, sld_winding,
                                                   sld_info_dict.get(sld_winding).get("port_names"),
                                                   sld_info_dict.get(sld_winding).get("side"),
                                                   sld_info_dict.get(sld_winding).get("multi_term_pos"),
                                                   sld_info_dict.get(sld_winding).get("sld_term_pos")
                                                   )

                util.convert_to_multiline(mdl, mask_handle, sld_info)

        mdl.refresh_icon(mask_handle)
        created_ports, _ = port_dynamics(mdl, mask_handle)
        update_subsystem_components(mdl, mask_handle, created_ports)
        enable_disable_conn(mdl, mask_handle)
        old_state[comp_handle] = current_values

    good_for_sld = []
    for prop_name in new_prop_values:
        if prop_name in ["num_windings"]:
            cur_pass_value = current_pass_prop_values[prop_name]
            new_value = new_prop_values[prop_name]
            if util.is_float(str(cur_pass_value)) or util.is_float(str(new_value)):
                if float(cur_pass_value) == float(new_value):
                    good_for_sld.append(True)
                    continue
            else:
                if str(current_pass_prop_values[prop_name]) == str(new_prop_values[prop_name]):
                    good_for_sld.append(True)
                    continue
            good_for_sld.append(False)

    final_state = all(good_for_sld)

    if final_state:

        old_state[comp_handle] = new_prop_values

        prim_config = new_prop_values.get("prim_conn")
        sec1_config = new_prop_values.get("sec1_conn")
        sec2_config = new_prop_values.get("sec2_conn")
        sec3_config = new_prop_values.get("sec3_conn")

        if prim_config in ["Y - Grounded", "Y"]:
            if "N1" not in sld_info_dict.get("SLD1").get("port_names"):
                sld_info_dict.get("SLD1").get("port_names").append("N1")
            if "N1" not in sld_info_dict.get("SLD1").get("multi_term_pos").keys():
                sld_info_dict.get("SLD1").get("multi_term_pos")["N1"] = (-32, 48)
        else:
            if "N1" in sld_info_dict.get("SLD1").get("port_names"):
                sld_info_dict.get("SLD1").get("port_names").remove("N1")
            if "N1" in sld_info_dict.get("SLD1").get("multi_term_pos").keys():
                sld_info_dict.get("SLD1").get("multi_term_pos").pop("N1")

        if sec1_config in ["Y - Grounded", "Y"]:
            if "N2" not in sld_info_dict.get("SLD2").get("port_names"):
                sld_info_dict.get("SLD2").get("port_names").append("N2")
            if "N2" not in sld_info_dict.get("SLD2").get("multi_term_pos").keys():
                sld_info_dict.get("SLD2").get("multi_term_pos")["N2"] = (32, -112 + Y2_offset)
        else:
            if "N2" in sld_info_dict.get("SLD2").get("port_names"):
                sld_info_dict.get("SLD2").get("port_names").remove("N2")
            if "N2" in sld_info_dict.get("SLD2").get("multi_term_pos").keys():
                sld_info_dict.get("SLD2").get("multi_term_pos").pop("N2")

        if sec2_config in ["Y - Grounded", "Y"]:
            if "N3" not in sld_info_dict.get("SLD3").get("port_names"):
                sld_info_dict.get("SLD3").get("port_names").append("N3")
            if "N3" not in sld_info_dict.get("SLD3").get("multi_term_pos").keys():
                sld_info_dict.get("SLD3").get("multi_term_pos")["N3"] = (32, 48 + Y3_offset)
        else:
            if "N3" in sld_info_dict.get("SLD3").get("port_names"):
                sld_info_dict.get("SLD3").get("port_names").remove("N3")
            if "N3" in sld_info_dict.get("SLD3").get("multi_term_pos").keys():
                sld_info_dict.get("SLD3").get("multi_term_pos").pop("N3")

        if sec3_config in ["Y - Grounded", "Y"]:
            if "N4" not in sld_info_dict.get("SLD4").get("port_names"):
                sld_info_dict.get("SLD4").get("port_names").append("N4")
            if "N4" not in sld_info_dict.get("SLD4").get("multi_term_pos").keys():
                sld_info_dict.get("SLD4").get("multi_term_pos")["N4"] = (32, 208 + Y4_offset)
        else:
            if "N4" in sld_info_dict.get("SLD4").get("port_names"):
                sld_info_dict.get("SLD4").get("port_names").remove("N4")
            if "N4" in sld_info_dict.get("SLD4").get("multi_term_pos").keys():
                sld_info_dict.get("SLD4").get("multi_term_pos").pop("N4")

        importlib.reload(util)
        num_windings = new_prop_values.get("num_windings")
        if num_windings == "2":
            sld_winding_list = ["SLD1", "SLD2"]
        elif num_windings == "3":
            sld_winding_list = ["SLD1", "SLD2", "SLD3"]
        elif num_windings == "4":
            sld_winding_list = ["SLD1", "SLD2", "SLD3", "SLD4"]
        else:
            sld_winding_list = ["SLD1", "SLD2"]

        if new_prop_values.get("sld_mode") in (True, "True"):
            for sld_winding in sld_winding_list:
                sld_info = get_sld_conversion_info(mdl, mask_handle, sld_winding,
                                                   sld_info_dict.get(sld_winding).get("port_names"),
                                                   sld_info_dict.get(sld_winding).get("side"),
                                                   sld_info_dict.get(sld_winding).get("multi_term_pos"),
                                                   sld_info_dict.get(sld_winding).get("sld_term_pos")
                                                   )
                util.convert_to_sld(mdl, mask_handle, sld_info)
        else:
            for sld_winding in sld_winding_list:
                currently_sld = mdl.get_item(sld_winding, parent=comp_handle, item_type="port")
                if currently_sld:
                    # The terminal related to the current property hasn't been created yet
                    importlib.reload(util)
                    sld_info = get_sld_conversion_info(mdl, mask_handle, sld_winding,
                                                       sld_info_dict.get(sld_winding).get("port_names"),
                                                       sld_info_dict.get(sld_winding).get("side"),
                                                       sld_info_dict.get(sld_winding).get("multi_term_pos"),
                                                       sld_info_dict.get(sld_winding).get("sld_term_pos")
                                                       )

                    util.convert_to_multiline(mdl, mask_handle, sld_info)


    sld_post_processing(mdl, mask_handle)


def sld_post_processing(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Resize the buses to 4

    for bus_name in ["SLD1_bus", "SLD2_bus", "SLD3_bus", "SLD4_bus"]:
        bus = mdl.get_item(bus_name, parent=comp_handle)
        if bus:
            bus_size_prop = mdl.prop(bus, "bus_size")
            mdl.set_property_value(bus_size_prop, 4)
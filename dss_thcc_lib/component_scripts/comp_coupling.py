import json
import dss_thcc_lib.component_scripts.util as util
import importlib

old_state = {}


def circuit_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:

    """
    # Property Registration
    itm_csnb_type_prop = mdl.prop(container_handle, "itm_csnb_type")
    itm_vsnb_type_prop = mdl.prop(container_handle, "itm_vsnb_type")
    itm_csnb_fixed_prop = mdl.prop(container_handle, "itm_csnb_fixed")
    itm_vsnb_fixed_prop = mdl.prop(container_handle, "itm_vsnb_fixed")
    auto_mode_prop = mdl.prop(container_handle, "auto_mode")
    flip_status_prop = mdl.prop(container_handle, "flip_status")
    n_phases_prop = mdl.prop(container_handle, "n_phases")
    coupling_type_prop = mdl.prop(container_handle, "coupling_type")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_csnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == itm_csnb_type_prop:

        comp_handle = mdl.get_parent(container_handle)
        coupling_handle = mdl.get_item("Coupling", parent=comp_handle)
        mdl.set_property_value(mdl.prop(coupling_handle, "snb_type_i"), new_value)

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_vsnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == itm_vsnb_type_prop:

        comp_handle = mdl.get_parent(container_handle)
        coupling_handle = mdl.get_item("Coupling", parent=comp_handle)
        mdl.set_property_value(mdl.prop(coupling_handle, "snb_type_u"), new_value)

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_csnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == itm_csnb_fixed_prop:

        comp_handle = mdl.get_parent(container_handle)
        coupling_handle = mdl.get_item("Coupling", parent=comp_handle)

        if new_value:
            mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_i"), "true")
        else:
            mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_i"), "false")

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_vsnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == itm_vsnb_fixed_prop:

        comp_handle = mdl.get_parent(container_handle)
        coupling_handle = mdl.get_item("Coupling", parent=comp_handle)

        if new_value:
            mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_u"), "true")
        else:
            mdl.set_property_value(mdl.prop(coupling_handle, "fixed_snb_u"), "false")

    # ------------------------------------------------------------------------------------------------------------------
    #  "auto_mode" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == auto_mode_prop:

        # Change Coupling properties
        comp_handle = mdl.get_parent(container_handle)
        coupling_handle = mdl.get_item("Coupling", parent=comp_handle)
        prop_names = ["R1", "C1", "R2", "L1", "snb_type_i", "snb_type_u"]
        manual_itm_csnb_type = mdl.get_property_disp_value(mdl.prop(container_handle, "itm_csnb_type"))
        manual_itm_vsnb_type = mdl.get_property_disp_value(mdl.prop(container_handle, "itm_vsnb_type"))

        if new_value == "Manual":
            prop_values = ["itm_csnb_r", "itm_csnb_c", "itm_vsnb_r", "itm_vsnb_l", manual_itm_csnb_type, manual_itm_vsnb_type]
        else:
            prop_values = ["itm_csnb_r_auto", "itm_csnb_c_auto", "itm_vsnb_r_auto", "itm_vsnb_l_auto", "none", "none"]
        [mdl.set_property_value(mdl.prop(coupling_handle, pname), value)
         for pname, value in zip(prop_names, prop_values)]

        # Changing Component properties
        if new_value == "Manual":
            mdl.set_property_value(mdl.prop(container_handle, "flip_status"), False)
        else:
            mdl.set_property_value(mdl.prop(container_handle, "itm_csnb_fixed"), True)
            mdl.set_property_value(mdl.prop(container_handle, "itm_vsnb_fixed"), True)

        # Update the Icon
        mdl.refresh_icon(container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "flip_status" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == flip_status_prop:

        # Flip Action
        coupling_type = mdl.get_property_value(coupling_type_prop)
        phases = mdl.get_property_value(n_phases_prop)
        create_coupling_component(mdl, container_handle, coupling_type, phases, force_refactor=True)
        # flip_coupling(mdl, container_handle, new_value)
        # Update the Icon
        mdl.refresh_icon(container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "flip_status" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == n_phases_prop:

        phases = new_value
        coupling_type = mdl.get_property_value(coupling_type_prop)

        create_coupling_component(mdl, container_handle, coupling_type, phases)
        # Updating the icon
        mdl.refresh_icon(container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "coupling_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == coupling_type_prop:

        comp_handle = mdl.get_parent(container_handle)
        coupling_type = new_value
        phases = mdl.get_property_value(n_phases_prop)
        create_coupling_component(mdl, container_handle, coupling_type, phases)
        # Updating the icon
        mdl.refresh_icon(container_handle)


def mask_dialog_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """
    # Property Registration
    auto_mode_prop = mdl.prop(container_handle, "auto_mode")
    itm_csnb_type_prop = mdl.prop(container_handle, "itm_csnb_type")
    itm_vsnb_type_prop = mdl.prop(container_handle, "itm_vsnb_type")

    # ------------------------------------------------------------------------------------------------------------------
    #  SLD exclusive
    # ------------------------------------------------------------------------------------------------------------------
    if mdl.get_name(caller_prop_handle) in ["n_phases", "sld_mode"]:
        phases_prop = mdl.prop(container_handle, "n_phases")
        phases_disp = mdl.get_property_disp_value(phases_prop)
        sld_mode_prop = mdl.prop(container_handle, "sld_mode")
        sld_mode_disp = mdl.get_property_disp_value(sld_mode_prop)
        sld_1ph_pick_prop = mdl.prop(container_handle, "sld_1ph_pick")
        sld_2ph_pick_prop = mdl.prop(container_handle, "sld_2ph_pick")

        if sld_mode_disp in (True, "True"):
            if phases_disp == "1":
                mdl.show_property(sld_1ph_pick_prop)
                mdl.hide_property(sld_2ph_pick_prop)
            elif phases_disp == "2":
                mdl.show_property(sld_2ph_pick_prop)
                mdl.hide_property(sld_1ph_pick_prop)
            else:
                mdl.hide_property(sld_1ph_pick_prop)
                mdl.hide_property(sld_2ph_pick_prop)
        else:
            mdl.hide_property(sld_1ph_pick_prop)
            mdl.hide_property(sld_2ph_pick_prop)

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_disp_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "conf" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == auto_mode_prop:

        csnb_prop_handles = [mdl.prop(container_handle, pname)
                             for pname in ["itm_csnb_type", "itm_csnb_r", "itm_csnb_c"]]
        vsnb_prop_handles = [mdl.prop(container_handle, pname)
                             for pname in ["itm_vsnb_type", "itm_vsnb_r", "itm_vsnb_l"]]

        if new_value == "Manual":
            [mdl.show_property(prop) for prop in csnb_prop_handles + vsnb_prop_handles]
        elif new_value == "Automatic":
            [mdl.hide_property(prop) for prop in csnb_prop_handles + vsnb_prop_handles]

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_csnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == itm_csnb_type_prop:

        prop_names = ["itm_csnb_r", "itm_csnb_c"]
        if new_value == "none":
            [mdl.disable_property(mdl.prop(container_handle, pname)) for pname in prop_names]
        elif new_value == "R1":
            [mdl.enable_property(mdl.prop(container_handle, pname)) for pname in prop_names]
            mdl.disable_property(mdl.prop(container_handle, prop_names[1]))
        elif new_value == "R1-C1":
            [mdl.enable_property(mdl.prop(container_handle, pname)) for pname in prop_names]

    # ------------------------------------------------------------------------------------------------------------------
    #  "itm_vsnb_type" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == itm_vsnb_type_prop:

        prop_names = ["itm_vsnb_r", "itm_vsnb_l"]
        if new_value == "none":
            [mdl.disable_property(mdl.prop(container_handle, pname)) for pname in prop_names]
        elif new_value == "R2":
            [mdl.enable_property(mdl.prop(container_handle, pname)) for pname in prop_names]
            mdl.disable_property(mdl.prop(container_handle, prop_names[1]))
        elif new_value == "R2||L1":
            [mdl.enable_property(mdl.prop(container_handle, pname)) for pname in prop_names]


def define_icon(mdl, container_handle):
    """
    Defines the component icon based on its type

    :param mdl: Schematic API
    :param container_handle: Component Handle
    :return: no return
    """
    phases = mdl.get_property_value(mdl.prop(container_handle, "n_phases"))
    flip = mdl.get_property_value(mdl.prop(container_handle, "flip_status"))
    mode = mdl.get_property_value(mdl.prop(container_handle, "auto_mode"))
    coupling_type = mdl.get_property_value(mdl.prop(container_handle, "coupling_type")).lower()

    sld_mode_prop = mdl.prop(container_handle, "sld_mode")
    sld_mode_disp = mdl.get_property_disp_value(sld_mode_prop)

    if sld_mode_disp in (True, "True"):
        phases = "1"

    f'images/coupling.svg'

    coupling_type = f"images/{coupling_type}_coupling_{phases}ph"
    if flip:
        flip_type = "_flip"
        mdl.set_component_icon_image(container_handle, f"{coupling_type}{flip_type}.svg")
        mdl.disp_component_icon_text(container_handle, "Flipped", relpos_x=0.5, relpos_y=0.95, size=5)
    else:
        mdl.set_component_icon_image(container_handle, f"{coupling_type}.svg")

    if mode == "Automatic":
        mdl.disp_component_icon_text(container_handle, "Auto", relpos_x=0.5, relpos_y=0.08, size=5)


def get_port_const_attributes(phases):
    """

    """
    term_positions = []
    if phases == "3":
        term_positions = [(-16, -32), (-16, 0), (-16, 32), (16, -32), (16, 0), (16, 32.0)]
        comp_positions = [(7600, 7856), (7600, 7952), (7600, 8048), (7872, 7856), (7872, 7952), (7872, 8048)]
    elif phases == "2":
        term_positions = [(-16, -16), (-16, 16), (99, 99), (16, -16), (16, 16), (99, 99)]
        comp_positions = [(7600, 7904), (7600, 8000), (9999, 9999), (7872, 7904), (7872, 8000), (9999, 9999)]
    elif phases == "1":
        term_positions = [(-16, 0), (99, 99), (99, 99), (16, 0), (99, 99), (99, 99)]
        comp_positions = [(7600, 7904), (9999, 9999), (9999, 9999), (7872, 7904), (9999, 9999), (9999, 9999)]

    port_dict = {"A1": {"pos": comp_positions[0], "term_pos": term_positions[0]},
                 "B1": {"pos": comp_positions[1], "term_pos": term_positions[1]},
                 "C1": {"pos": comp_positions[2], "term_pos": term_positions[2]},
                 "A2": {"pos": comp_positions[3], "term_pos": term_positions[3]},
                 "B2": {"pos": comp_positions[4], "term_pos": term_positions[4]},
                 "C2": {"pos": comp_positions[5], "term_pos": term_positions[5]},
                 "Coupling": {"pos": (7744, 8000)}}

    return port_dict


def create_coupling_component(mdl, container_handle, coupling_type, phases, force_refactor=False):

    comp_handle = mdl.get_parent(container_handle)
    # Components Vars
    coupling_handle = mdl.get_item("Coupling", parent=comp_handle)
    comp_port_labels = ["A1", "B1", "C1", "A2", "B2", "C2"]
    comp_port_handles = [mdl.get_item(p_name, item_type="port", parent=comp_handle)
                         for p_name in comp_port_labels]
    ground_handles = [mdl.get_item(gname, parent=comp_handle) for gname in ["gnd1", "gnd2"]]
    ground_term_handles = [mdl.term(ghandle, "node") for ghandle in ground_handles]

    flip = "flip_horizontal" if mdl.get_property_value(mdl.prop(container_handle, "flip_status")) else "flip_none"

    # Component Properties
    coupling_prop_names = ["snb_type_i", "R1", "C1", "snb_type_u", "R2", "L1"]
    coupling_prop_values = [mdl.get_property_disp_value(mdl.prop(coupling_handle, pname))
                            for pname in coupling_prop_names]
    # WorkAround - fixed_snb_i and u are different between Core and Device Couplings. I'll use always true for both

    if phases == "3":
        # Coupling
        coupling_type_full_name = f"Four Phase {coupling_type} Coupling"
        phase_connections = ["a_in", "a_out", "b_in", "b_out", "c_in", "c_out"]
        ground_connections = ["d_in", "d_out"]
        # Ports
        comp_ports = "ABC"

    elif phases == "2":
        # Coupling
        coupling_type_full_name = f"Three Phase {coupling_type} Coupling"
        phase_connections = ["a_in", "a_out", "b_in", "b_out"]
        ground_connections = ["c_in", "c_out"]
        # Ports
        comp_ports = "AB"

    elif phases == "1":
        # Coupling
        coupling_type_full_name = f"Single Phase {coupling_type} Coupling"
        phase_connections = ["a_in", "a_out"]
        ground_connections = ["b_in", "b_out"]
        # Ports
        comp_ports = "A"

    port_attributes = get_port_const_attributes(phases)
    for cnt, port in enumerate(comp_port_handles):
        if port:
            mdl.set_position(port, port_attributes[comp_port_labels[cnt]]["pos"])
            mdl.set_port_properties(port, terminal_position=port_attributes[comp_port_labels[cnt]]["term_pos"])

    # Coupling
    create_delete_ports = [port_phase in comp_ports for port_phase in ["A", "B", "C"]]
    # Creating/Deleting Ports
    new_port_handles = []

    for cnt, action in enumerate(create_delete_ports):
        if action:
            # Upstream Logic
            if not comp_port_handles[cnt]:
                new_port = mdl.create_port(name=comp_port_labels[cnt],
                                           parent=comp_handle,
                                           kind="pe",
                                           direction="in",
                                           position=port_attributes[comp_port_labels[cnt]]["pos"],
                                           terminal_position=port_attributes[comp_port_labels[cnt]]["term_pos"],
                                           hide_name=True)
                new_port_handles.append(new_port)
            else:
                new_port_handles.append(comp_port_handles[cnt])
            # Downstream Logic
            if not comp_port_handles[cnt + 3]:
                new_port = mdl.create_port(name=comp_port_labels[cnt + 3],
                                           parent=comp_handle,
                                           kind="pe",
                                           direction="in",
                                           position=port_attributes[comp_port_labels[cnt + 3]]["pos"],
                                           terminal_position=port_attributes[comp_port_labels[cnt + 3]]["term_pos"],
                                           flip="flip_horizontal",
                                           hide_name=True)
                new_port_handles.append(new_port)
            else:
                new_port_handles.append(comp_port_handles[cnt + 3])
        else:
            # Upstream Logic
            if comp_port_handles[cnt]:
                mdl.delete_item(comp_port_handles[cnt])
            # Downstream Logic
            if comp_port_handles[cnt + 3]:
                mdl.delete_item(comp_port_handles[cnt + 3])

    new_port_handles = new_port_handles + ground_term_handles

    # Coupling
    if (mdl.get_component_type_name(coupling_handle) != coupling_type_full_name) or force_refactor:
        mdl.delete_item(coupling_handle)
        coupling_handle = mdl.create_component(coupling_type_full_name,
                                               name="Coupling",
                                               parent=comp_handle,
                                               position=port_attributes["Coupling"]["pos"],
                                               flip=flip)
        [mdl.set_property_value(mdl.prop(coupling_handle, pname), pvalue)
         for pname, pvalue in zip(coupling_prop_names, coupling_prop_values)]
        # WorkAround
        if "Core" in coupling_type_full_name.split(" "):
            [mdl.set_property_value(mdl.prop(coupling_handle, pname), "true")
             for pname in ["fixed_snb_i", "fixed_snb_u"]]
        else:
            [mdl.set_property_value(mdl.prop(coupling_handle, pname), True)
             for pname in ["fixed_snb_i", "fixed_snb_u"]]

        # Connections
        coupling_connections = phase_connections + ground_connections
        for cnt in range(int(phases) + 1):
            ports = [new_port_handles[idx] for idx in [2 * cnt, 2 * cnt + 1]]
            coupling_port_names = [coupling_connections[idx] for idx in [2 * cnt, 2 * cnt + 1]]
            if flip == "flip_horizontal":
                coupling_port_names = list(reversed(coupling_port_names))
            coupling_port_handle = [mdl.term(coupling_handle, pname) for pname in coupling_port_names]
            for idy in range(2):
                if len(mdl.find_connections(ports[idy], coupling_port_handle[idy])) == 0:
                    mdl.create_connection(ports[idy], coupling_port_handle[idy])


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


def topology_dynamics(mdl, mask_handle, prop_handle):
    """
    This function is called when the user changes the configuration on the mask
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
        define_icon(mdl, mask_handle)
        circuit_dynamics(mdl, mask_handle, prop_handle)

    if calling_prop_name not in ["sld_mode", "init_code"]:

        if old_state:
            current_state = old_state[comp_handle]
        else:
            current_state = new_prop_values

        sld_bus_count = 2

        for sld_idx in range(sld_bus_count):
            sld_name = "SLD" + str(sld_idx+1)
            currently_sld = mdl.get_item(sld_name, parent=comp_handle, item_type="port")
            if currently_sld:
                # The terminal related to the current property hasn't been created yet
                sld_number = {}
                importlib.reload(util)
                phases = current_state.get("n_phases")
                sld_1ph_pick = current_state.get("sld_1ph_pick")
                sld_2ph_pick = current_state.get("sld_2ph_pick")

                multi_port_list = []
                terminal_positions = {}
                sld_term_position = (0, 0)

                if sld_idx == 0:
                    sld_side = "left"
                    port_x = -16
                else:
                    sld_side = "right"
                    port_x = 16
                if phases == "3":
                    multi_port_list = ["A" + str(sld_idx + 1), "B" + str(sld_idx + 1), "C" + str(sld_idx + 1)]
                    terminal_positions = {
                        "A" + str(sld_idx + 1): (port_x, -32),
                        "B" + str(sld_idx + 1): (port_x, 0),
                        "C" + str(sld_idx + 1): (port_x, 32),
                    }
                    sld_term_position = (port_x, 0)
                elif phases == "2":
                    terminal_positions = {
                        "A" + str(sld_idx + 1): (port_x, -16),
                        "B" + str(sld_idx + 1): (port_x, 16),
                    }
                    sld_term_position = (port_x, 0)
                    if sld_2ph_pick == "A and B":
                        multi_port_list = ["A" + str(sld_idx + 1), "B" + str(sld_idx + 1)]
                    elif sld_2ph_pick == "B and C":
                        multi_port_list = [None, "A" + str(sld_idx + 1), "B" + str(sld_idx + 1)]
                    elif sld_2ph_pick == "A and C":
                        multi_port_list = ["A" + str(sld_idx + 1), None, "B" + str(sld_idx + 1)]
                elif phases == "1":
                    terminal_positions = {
                        "A" + str(sld_idx + 1): (port_x, 0),
                    }
                    sld_term_position = (port_x, 0)
                    if sld_1ph_pick == "A":
                        multi_port_list = ["A" + str(sld_idx + 1)]
                    elif sld_1ph_pick == "B":
                        multi_port_list = [None, "A" + str(sld_idx + 1)]
                    elif sld_1ph_pick == "C":
                        multi_port_list = [None, None, "A" + str(sld_idx + 1)]

                sld_number["port_names"] = multi_port_list
                sld_number["side"] = sld_side
                sld_number["multi_term_pos"] = terminal_positions
                sld_number["sld_term_pos"] = sld_term_position

                sld_info = get_sld_conversion_info(mdl, mask_handle, sld_name,
                                                   sld_number.get("port_names"),
                                                   sld_number.get("side"),
                                                   sld_number.get("multi_term_pos"),
                                                   sld_number.get("sld_term_pos")
                                                   )

                util.convert_to_multiline(mdl, mask_handle, sld_info)

        define_icon(mdl, mask_handle)
        circuit_dynamics(mdl, mask_handle, prop_handle)
        old_state[comp_handle] = current_values

    good_for_sld = []
    for prop_name in new_prop_values:
        if prop_name in ["n_phases", "sld_1ph_pick", "sld_2ph_pick"]:
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

        sld_bus_count = 2
        sld_info = []
        for sld_idx in range(sld_bus_count):
            sld_name = "SLD" + str(sld_idx + 1)
            sld_number = {}
            importlib.reload(util)
            phases = new_prop_values.get("n_phases")
            sld_1ph_pick = new_prop_values.get("sld_1ph_pick")
            sld_2ph_pick = new_prop_values.get("sld_2ph_pick")

            multi_port_list = []
            terminal_positions = {}
            sld_term_position = (0, 0)

            if sld_idx == 0:
                sld_side = "left"
                port_x = -16
            else:
                sld_side = "right"
                port_x = 16
            if phases == "3":
                multi_port_list = ["A" + str(sld_idx + 1), "B" + str(sld_idx + 1), "C" + str(sld_idx + 1)]
                terminal_positions = {
                    "A" + str(sld_idx + 1): (port_x, -32),
                    "B" + str(sld_idx + 1): (port_x, 0),
                    "C" + str(sld_idx + 1): (port_x, 32),
                }
                sld_term_position = (port_x, 0)
            elif phases == "2":
                terminal_positions = {
                    "A" + str(sld_idx + 1): (port_x, -16),
                    "B" + str(sld_idx + 1): (port_x, 16),
                }
                sld_term_position = (port_x, 0)
                if sld_2ph_pick == "A and B":
                    multi_port_list = ["A" + str(sld_idx + 1), "B" + str(sld_idx + 1)]
                elif sld_2ph_pick == "B and C":
                    multi_port_list = [None, "A" + str(sld_idx + 1), "B" + str(sld_idx + 1)]
                elif sld_2ph_pick == "A and C":
                    multi_port_list = ["A" + str(sld_idx + 1), None, "B" + str(sld_idx + 1)]
            elif phases == "1":
                terminal_positions = {
                    "A" + str(sld_idx + 1): (port_x, 0),
                }
                sld_term_position = (port_x, 0)
                if sld_1ph_pick == "A":
                    multi_port_list = ["A" + str(sld_idx + 1)]
                elif sld_1ph_pick == "B":
                    multi_port_list = [None, "A" + str(sld_idx + 1)]
                elif sld_1ph_pick == "C":
                    multi_port_list = [None, None, "A" + str(sld_idx + 1)]

            sld_number["port_names"] = multi_port_list
            sld_number["side"] = sld_side
            sld_number["multi_term_pos"] = terminal_positions
            sld_number["sld_term_pos"] = sld_term_position

            sld_info.append(get_sld_conversion_info(mdl, mask_handle, sld_name,
                                                    sld_number.get("port_names"),
                                                    sld_number.get("side"),
                                                    sld_number.get("multi_term_pos"),
                                                    sld_number.get("sld_term_pos")
                                                    )
                            )

        if new_prop_values.get("sld_mode") in (True, "True"):
            for sld_idx in range(sld_bus_count):
                util.convert_to_sld(mdl, mask_handle, sld_info[sld_idx])
        else:
            for sld_idx in range(sld_bus_count):
                sld_name = "SLD" + str(sld_idx + 1)
                currently_sld = mdl.get_item(sld_name, parent=comp_handle, item_type="port")
                if currently_sld:
                    util.convert_to_multiline(mdl, mask_handle, sld_info[sld_idx])

    sld_post_processing(mdl, mask_handle)


def sld_post_processing(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Resize the buses to 4

    for bus_name in ["SLD1_bus", "SLD2_bus"]:
        bus = mdl.get_item(bus_name, parent=comp_handle)
        if bus:
            bus_size_prop = mdl.prop(bus, "bus_size")
            mdl.set_property_value(bus_size_prop, 4)

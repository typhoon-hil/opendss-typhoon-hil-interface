def circuit_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:

    """
    # Property Registration
    grounding_prop = mdl.prop(container_handle, "grounding")
    phases_prop = mdl.prop(container_handle, "phases")

    new_value = None

    if caller_prop_handle:
        new_value = mdl.get_property_value(caller_prop_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "grounding" property code
    # ------------------------------------------------------------------------------------------------------------------
    if caller_prop_handle == grounding_prop:
        comp_handle = mdl.get_parent(container_handle)
        # port_dynamics function to support container component
        port_dynamics(mdl, container_handle, grounding_prop)
        # Connections and Internal Items
        ntag_handle = mdl.get_item("gnd_src", parent=comp_handle, item_type="tag")
        if new_value:
            xpos, ypos = get_port_const_attributes("N")["pos"]
            gnd_handle = mdl.create_component("core/Ground",
                                              name="gnd",
                                              parent=comp_handle,
                                              position=(xpos, ypos+48))
            mdl.create_connection(ntag_handle, mdl.term(gnd_handle, "node"))
        else:
            gnd_handle = mdl.get_item("gnd", parent=comp_handle)
            if gnd_handle:
                mdl.delete_item(gnd_handle)
            nport_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
            if nport_handle:
                if not mdl.find_connections(ntag_handle, nport_handle):
                    mdl.create_connection(ntag_handle, nport_handle)

    # ------------------------------------------------------------------------------------------------------------------
    #  "phases" property code
    # ------------------------------------------------------------------------------------------------------------------
    elif caller_prop_handle == phases_prop:

        comp_handle = mdl.get_parent(container_handle)
        # port_dynamics function to support container component
        port_dynamics(mdl, container_handle, phases_prop)
        # Connections and Internal Items
        phase_names = ["B", "C"]
        port_handles = [mdl.get_item(pname, parent=comp_handle, item_type="port") for pname in ["B1", "C1"]]
        ground_handle = mdl.get_item("gnd_tag", parent=comp_handle, item_type="tag")
        xpos_ref = mdl.get_position(mdl.get_item("InvLeg_A", parent=comp_handle))[0]
        inv_leg_handles = [mdl.get_item(cname, parent=comp_handle) for cname in ["InvLeg_B", "InvLeg_C"]]
        mod_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                       for tname in ["from_modB", "from_modC"]]
        term_mod_handles = [mdl.get_item(tname, parent=comp_handle) for tname in ["term_modB", "term_modC"]]
        imeas_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                         for tname in ["goto_IB", "goto_IC"]]
        ct_imeas_handles = [mdl.get_item(cname, parent=comp_handle) for cname in ["ct_IB", "ct_IC"]]
        vmeas_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                         for tname in ["goto_VB", "goto_VC"]]
        ct_vmeas_handles = [mdl.get_item(cname, parent=comp_handle) for cname in ["ct_VB", "ct_VC"]]
        # Controller
        inv_control_handle = mdl.get_item("InvControl", parent=comp_handle)
        inv_control_pos = mdl.get_position(inv_control_handle)
        vlist_handle = mdl.get_item("Vlist", parent=comp_handle)
        vlist_pos = mdl.get_position(vlist_handle)
        ilist_handle = mdl.get_item("Ilist", parent=comp_handle)
        ilist_pos = mdl.get_position(ilist_handle)
        goto_mod_handles = [mdl.get_item(tname, parent=comp_handle, item_type="tag")
                            for tname in ["mod_vb", "mod_vc"]]
        bus_mod_handle = mdl.get_item("Bus Split mod", parent=comp_handle)

        if new_value == "3":
            # mod_handles
            for cnt, fhandle in enumerate(term_mod_handles):
                if fhandle:
                    mdl.delete_item(fhandle)
            # imeas_handles
            for cnt, ihandle in enumerate(ct_imeas_handles):
                if ihandle:
                    mdl.delete_item(ihandle)
            # vmeas_handles
            for cnt, vhandle in enumerate(ct_vmeas_handles):
                if vhandle:
                    mdl.delete_item(vhandle)
            # inv_legs
            for cnt, leg_handle in enumerate(inv_leg_handles):
                if not leg_handle:
                    ypos = mdl.get_position(port_handles[cnt])[1]
                    leg_handle = mdl.create_component("OpenDSS/Generic Leg Inverter (avg)",
                                                      name=f"InvLeg_{phase_names[cnt]}",
                                                      parent=comp_handle,
                                                      position=[xpos_ref, ypos])
                    mdl.create_connection(mdl.term(leg_handle, "N"), ground_handle)
                    mdl.create_connection(mdl.term(leg_handle, "L"), port_handles[cnt])
                    mdl.create_connection(mdl.term(leg_handle, "mod"), mod_handles[cnt])
                    mdl.create_connection(mdl.term(leg_handle, "Imeas"), imeas_handles[cnt])
                    mdl.create_connection(mdl.term(leg_handle, "Vmeas"), vmeas_handles[cnt])
            # Control
            mdl.set_property_value(mdl.prop(inv_control_handle, "phases"), "3")
            isel_handle = mdl.get_item("ilist_sel", parent=comp_handle)
            if isel_handle:
                mdl.delete_item(isel_handle)
                mdl.create_connection(mdl.term(ilist_handle, "out"), mdl.term(inv_control_handle, "Imeas"))
            vsel_handle = mdl.get_item("vlist_sel", parent=comp_handle)
            if vsel_handle:
                mdl.delete_item(vsel_handle)
                mdl.create_connection(mdl.term(vlist_handle, "out"), mdl.term(inv_control_handle, "Vmeas"))
            ct_mod_handle = mdl.get_item("ct_mod", parent=comp_handle)
            if ct_mod_handle:
                mdl.delete_item(ct_mod_handle)
                mdl.set_property_value(mdl.prop(bus_mod_handle, "outputs"), "3")
                mdl.create_connection(mdl.term(bus_mod_handle, "out2"), goto_mod_handles[1])
        else:
            # inv_legs
            for cnt, leg_handle in enumerate(inv_leg_handles):
                if leg_handle:
                    mdl.delete_item(leg_handle)
            # mod_handles
            for cnt, fhandle in enumerate(mod_handles):
                posx, posy = mdl.get_position(fhandle)
                if not term_mod_handles[cnt]:
                    term_handle = mdl.create_component("core/Termination",
                                                       name=f"term_mod{phase_names[cnt]}",
                                                       parent=comp_handle,
                                                       position=[posx+64, posy])
                    mdl.create_connection(fhandle, mdl.term(term_handle, "in"))
            # imeas_handles
            for cnt, ihandle in enumerate(imeas_handles):
                posx, posy = mdl.get_position(ihandle)
                if not ct_imeas_handles[cnt]:
                    const_handle = mdl.create_component("core/Constant",
                                                        name=f"ct_I{phase_names[cnt]}",
                                                        parent=comp_handle,
                                                        position=[posx-64, posy])
                    mdl.set_property_value(mdl.prop(const_handle, "value"), 0)
                    mdl.set_property_value(mdl.prop(const_handle, "execution_rate"), "ts")
                    mdl.create_connection(mdl.term(const_handle, "out"), ihandle)
            # vmeas_handles
            for cnt, vhandle in enumerate(vmeas_handles):
                posx, posy = mdl.get_position(vhandle)
                if not ct_vmeas_handles[cnt]:
                    const_handle = mdl.create_component("core/Constant",
                                                        name=f"ct_V{phase_names[cnt]}",
                                                        parent=comp_handle,
                                                        position=[posx-64, posy])
                    mdl.set_property_value(mdl.prop(const_handle, "value"), 0)
                    mdl.set_property_value(mdl.prop(const_handle, "execution_rate"), "ts")
                    mdl.create_connection(mdl.term(const_handle, "out"), vhandle)
            # Control
            mdl.set_property_value(mdl.prop(inv_control_handle, "phases"), "1")
            vlist_conn = mdl.find_connections(mdl.term(vlist_handle, "out"), mdl.term(inv_control_handle, "Vmeas"))
            ilist_conn = mdl.find_connections(mdl.term(ilist_handle, "out"), mdl.term(inv_control_handle, "Imeas"))
            if vlist_conn:
                mdl.delete_item(vlist_conn[0])
            if ilist_conn:
                mdl.delete_item(ilist_conn[0])
            vsel_handle = mdl.create_component("core/Bus Selector",
                                               name="vlist_sel",
                                               parent=comp_handle,
                                               position=[vlist_pos[0]+64, vlist_pos[1]])
            mdl.set_property_value(mdl.prop(vsel_handle, "signal_indexes"), "[0]")
            mdl.create_connection(mdl.term(vlist_handle, "out"), mdl.term(vsel_handle, "in"))
            mdl.create_connection(mdl.term(vsel_handle, "out"), mdl.term(inv_control_handle, "Vmeas"))
            isel_handle = mdl.create_component("core/Bus Selector",
                                               name="ilist_sel",
                                               parent=comp_handle,
                                               position=[ilist_pos[0]+64, ilist_pos[1]])
            mdl.set_property_value(mdl.prop(isel_handle, "signal_indexes"), "[0]")
            mdl.create_connection(mdl.term(ilist_handle, "out"), mdl.term(isel_handle, "in"))
            mdl.create_connection(mdl.term(isel_handle, "out"), mdl.term(inv_control_handle, "Imeas"))
            mdl.set_property_value(mdl.prop(bus_mod_handle, "outputs"), "2")
            goto_mod_pos = mdl.get_position(goto_mod_handles[1])
            ct_mod_handle = mdl.create_component("core/Constant",
                                                 name="ct_mod",
                                                 parent=comp_handle,
                                                 position=[goto_mod_pos[0]-128, goto_mod_pos[1]])
            mdl.set_property_value(mdl.prop(ct_mod_handle, "execution_rate"), "ts")
            mdl.create_connection(mdl.term(ct_mod_handle, "out"), goto_mod_handles[1])


def port_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    """
    Ports modification (to support container component)

    :param mdl:
    :param container_handle:
    :param caller_prop_handle:
    :param init:
    :return:
    """

    comp_handle = mdl.get_parent(container_handle)
    prop_name = None
    new_value = None
    if caller_prop_handle:
        prop_name = mdl.get_name(caller_prop_handle)
        new_value = mdl.get_property_value(caller_prop_handle)

    if prop_name == "grounding":
        if new_value:
            nport_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
            if nport_handle:
                mdl.delete_item(nport_handle)
        else:
            nport_handle = mdl.get_item("N", parent=comp_handle, item_type="port")
            if not nport_handle:
                nport_param = get_port_const_attributes("N")
                nport_handle = mdl.create_port(name=nport_param["name"],
                                               parent=comp_handle,
                                               position=nport_param["pos"],
                                               terminal_position=nport_param["term_pos"],
                                               kind="pe",
                                               flip="flip_horizontal")

    elif prop_name == "phases":
        port_names = ["B1", "C1"]
        port_handles = [mdl.get_item(pname, parent=comp_handle, item_type="port") for pname in port_names]
        if new_value == "3":
            for cnt, phandle in enumerate(port_handles):
                if not phandle:
                    port_param = get_port_const_attributes(port_names[cnt])
                    nport_handle = mdl.create_port(name=port_param["name"],
                                                   parent=comp_handle,
                                                   position=port_param["pos"],
                                                   terminal_position=port_param["term_pos"],
                                                   kind="pe",
                                                   flip="flip_horizontal")
        else:
            for cnt, phandle in enumerate(port_handles):
                if phandle:
                    mdl.delete_item(phandle)


def define_icon(mdl, container_handle):
    """
    Defines the component icon based on its type

    :param mdl: Schematic API
    :param container_handle: Component Handle
    :return: no return
    """
    comp_handle = mdl.get_parent(container_handle)
    mask_handle = mdl.get_mask(comp_handle)
    mdl.set_component_icon_image(mask_handle, "images/PVSystem.svg")


def get_port_const_attributes(port_name):
    """

    """
    port_dict = {"A1": {"name": "A1", "pos": (7984, 7984), "term_pos": (40.0, -48.0), "label": "A"},
                 "B1": {"name": "B1", "pos": (7984, 8128), "term_pos": (40.0, -16.0), "label": "B"},
                 "C1": {"name": "C1", "pos": (7984, 8280), "term_pos": (40.0, 16.0), "label": "C"},
                 "N": {"name": "N", "pos": (7984, 8408), "term_pos": (40.0, 48.0), "label": "N"}}

    return port_dict[port_name]


def load_loadshape(mdl, container_handle):
    import os
    import dss_thcc_lib.gui_scripts.load_object as load_obj
    import pathlib
    import json
    import ast

    # Find objects file
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder_path = pathlib.Path(mdlfile_target_folder).joinpath('dss')
    fname = os.path.join(dss_folder_path, 'data', 'general_objects.json')

    loadshape_name_prop = mdl.prop(container_handle, "loadshape_name")
    loadshape_name = mdl.get_property_disp_value(loadshape_name_prop)
    loadshape_name = "" if loadshape_name == "-" else loadshape_name

    obj_type = "LoadShape"

    try:
        with open(fname, 'r') as f:
            obj_dicts = json.load(f)
    except FileNotFoundError:
        obj_dicts = None

    if obj_dicts:
        new_load_window = load_obj.LoadObject(mdl, obj_type, obj_dicts=obj_dicts, starting_object=loadshape_name)
    else:
        new_load_window = load_obj.LoadObject(mdl, obj_type)

    if new_load_window.exec():

        selected_object = new_load_window.selected_object

        obj_dicts = new_load_window.obj_dicts

        # Property handles
        loadshape_prop = mdl.prop(container_handle, "loadshape")
        loadshape_prop_int = mdl.prop(container_handle, "loadshape_int")
        loadshape_time_range_prop = mdl.prop(container_handle, "T_Ts")
        useactual_prop = mdl.prop(container_handle, "useactual")
        loadshape_from_file_prop = mdl.prop(container_handle, "loadshape_from_file")
        loadshape_from_file_path_prop = mdl.prop(container_handle, "loadshape_from_file_path")
        loadshape_from_file_header_prop = mdl.prop(container_handle, "loadshape_from_file_header")
        loadshape_from_file_column_prop = mdl.prop(container_handle, "loadshape_from_file_column")

        selected_obj_dict = obj_dicts.get("loadshapes").get(selected_object)
        loadshape_name = selected_object

        useactual = selected_obj_dict.get("useactual")
        loadshape_from_file = selected_obj_dict.get("csv_file") == "True"
        loadshape_from_file_path = selected_obj_dict.get("csv_path")
        loadshape_from_file_header = selected_obj_dict.get("headers")
        loadshape_from_file_column = selected_obj_dict.get("column")

        selected_obj_dict = obj_dicts.get("loadshapes").get(selected_object)

        npts = selected_obj_dict.get("npts")
        if npts:
            npts = ast.literal_eval(npts)
        hour = selected_obj_dict.get("hour")
        if hour:
            hour = ast.literal_eval(hour)
        interval = selected_obj_dict.get("interval")
        if interval:
            interval = ast.literal_eval(interval)

        if not loadshape_from_file:
            loadshape = selected_obj_dict.get("mult")
        else:
            selected_obj_dict.update({"loadshape_name": selected_object})
            loadshape = str(read_loadshape_from_json(mdl, container_handle, reload_dict=selected_obj_dict))

        if loadshape:
            loadshape = ast.literal_eval(loadshape)

            if interval == 0:  # Check hour points
                if hour:
                    loadshape = loadshape[:npts]
                else:
                    mdl.info("interval property is zero, but hour property is not defined")
            else:
                loadshape = loadshape[:npts]

            mdl.set_property_disp_value(loadshape_prop, str(loadshape))

        mdl.set_property_disp_value(loadshape_name_prop, str(loadshape_name))
        mdl.set_property_disp_value(loadshape_prop_int, str(interval))
        mdl.set_property_disp_value(loadshape_from_file_prop, str(loadshape_from_file))
        mdl.set_property_disp_value(useactual_prop, useactual)
        if interval == 0:
            if hour:
                mdl.set_property_disp_value(loadshape_time_range_prop, str(hour))
        else:
            time_range_str = f"[{', '.join(str(interval * n) for n in range(1, len(loadshape) + 1))}]"
            mdl.set_property_disp_value(loadshape_time_range_prop, time_range_str)
        mdl.set_property_disp_value(loadshape_from_file_path_prop, str(loadshape_from_file_path))
        mdl.set_property_disp_value(loadshape_from_file_header_prop, str(loadshape_from_file_header))
        mdl.set_property_disp_value(loadshape_from_file_column_prop, str(loadshape_from_file_column))


def verify_time_loadshape_sizes(mdl, mask_handle, caller=None):
    import ast

    comp_name = mdl.get_name(mdl.get_parent(mask_handle))

    loadshape_prop = mdl.prop(mask_handle, "loadshape")
    time_prop = mdl.prop(mask_handle, "T_Ts")
    loadshape = mdl.get_property_value(loadshape_prop)

    time_list = ast.literal_eval(mdl.get_property_value(time_prop))
    ls_list = ast.literal_eval(loadshape)

    # Verify matching sizes
    mode = mdl.get_property_value(mdl.prop(mask_handle, "T_mode"))
    if mode == "Time" and time_list and ls_list:
        # The time vector and the loadshape must be the same size
        if not len(ls_list) == len(time_list):
            mdl.info(f"Component {comp_name}: The number of points on the time range "
                     f"({len(time_list)}) and loadshape ({len(ls_list)}) must be equal for correct operation.")
            min_points = min(len(time_list), len(ls_list))
            mdl.info(f"HIL simulation will use the first {min_points} points.")
            if caller == "pre_compile":
                if len(time_list) > len(ls_list):
                    mdl.set_property_value(time_prop, time_list[:min_points])
                elif len(time_list) < len(ls_list):
                    mdl.set_property_value(loadshape_prop, ls_list[:min_points])


def load_xycurve(mdl, container_handle):
    import os
    import dss_thcc_lib.gui_scripts.load_object as load_obj
    # Tirar o importlib depois
    import importlib
    importlib.reload(load_obj)
    import pathlib
    import json
    import ast

    # Find objects file
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder_path = pathlib.Path(mdlfile_target_folder).joinpath('dss')
    fname = os.path.join(dss_folder_path, 'data', 'general_objects.json')

    xycurve_name_prop = mdl.prop(container_handle, "xycurve_name_eff")
    xycurve_name = mdl.get_property_disp_value(xycurve_name_prop)
    #xycurve_name = "" if xycurve_name == "-" else xycurve_name

    obj_type = "XYCurve"

    try:
        with open(fname, 'r') as f:
            obj_dicts = json.load(f)
    except FileNotFoundError:
        obj_dicts = None

    if obj_dicts:
        new_load_window = load_obj.LoadObject(mdl, obj_type, obj_dicts=obj_dicts, starting_object=xycurve_name)
    else:
        new_load_window = load_obj.LoadObject(mdl, obj_type)

    if new_load_window.exec():

        selected_object = new_load_window.selected_object

        obj_dicts = new_load_window.obj_dicts


def set_balanced_fcn(mdl, mask_handle, new_value):
    if new_value == True:
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

        Vn_3ph = mdl.get_property_disp_value(mdl.prop(mask_handle, "Vn_3ph"))
        Sn_3ph = mdl.get_property_disp_value(mdl.prop(mask_handle, "Sn_3ph"))
        phases = mdl.get_property_disp_value(mdl.prop(mask_handle, "phases"))
        pf_mode_3ph = mdl.get_property_disp_value(mdl.prop(mask_handle, "pf_mode_3ph"))
        if not pf_mode_3ph == "Unit":
            mdl.enable_property(mdl.prop(mask_handle, "pf_3ph"))
        pf_3ph = mdl.get_property_disp_value(mdl.prop(mask_handle, "pf_3ph"))

        if phases == "3":
            ph_num = 3
        elif phases == "2":
            ph_num = 2
        elif phases == "1":
            ph_num = 1
        else:
            ph_num = 3

        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VAn'), Vn_3ph + '*1000/(3**0.5)')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VBn'), Vn_3ph + '*1000/(3**0.5)')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VCn'), Vn_3ph + '*1000/(3**0.5)')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VAB'), Vn_3ph + '*1000')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VBC'), Vn_3ph + '*1000')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'VCA'), Vn_3ph + '*1000')
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SAn'), Sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SBn'), Sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SCn'), Sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SAB'), Sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SBC'), Sn_3ph + '*1000/' + str(phases))
        mdl.set_property_disp_value(mdl.prop(mask_handle, 'SCA'), Sn_3ph + '*1000/' + str(phases))
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
        pf_modeA = mdl.get_property_disp_value(mdl.prop(mask_handle, "pf_modeA"))
        if not pf_modeA == "Unit":
            mdl.enable_property(mdl.prop(mask_handle, "pfA"))
        pf_modeB = mdl.get_property_disp_value(mdl.prop(mask_handle, "pf_modeB"))
        if not pf_modeB == "Unit":
            mdl.enable_property(mdl.prop(mask_handle, "pfB"))
        pf_modeC = mdl.get_property_disp_value(mdl.prop(mask_handle, "pf_modeC"))
        if not pf_modeC == "Unit":
            mdl.enable_property(mdl.prop(mask_handle, "pfC"))

        mdl.disable_property(mdl.prop(mask_handle, "Vn_3ph"))
        mdl.disable_property(mdl.prop(mask_handle, "Sn_3ph"))
        mdl.disable_property(mdl.prop(mask_handle, "pf_mode_3ph"))
        mdl.disable_property(mdl.prop(mask_handle, "pf_3ph"))


def pf_mode_fcn(mdl, mask_handle, new_value, phase, comp_pos, jun_pos):
    from typhoon.api.schematic_editor.const import ITEM_COMPONENT, ITEM_CONNECTION, \
        ITEM_JUNCTION

    comp_handle = mdl.get_sub_level_handle(mask_handle)
    R = mdl.get_item("R" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)

    jun1 = mdl.get_item("J" + phase + "1", parent=comp_handle, item_type=ITEM_JUNCTION)
    if not jun1:
        jun1 = mdl.create_junction(name="J" + phase + "1", parent=comp_handle, kind='pe', position=jun_pos)

    if new_value == "Unit":
        L = mdl.get_item("L" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)
        C = mdl.get_item("C" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)

        if L:
            mdl.delete_item(L)
        if C:
            mdl.delete_item(C)

        conn = mdl.get_item("Conn_" + phase, parent=comp_handle, item_type=ITEM_CONNECTION)
        if not conn:
            mdl.create_connection(mdl.term(R, "n_node"), jun1, name="Conn_" + phase)

    elif new_value == "Lead":
        L = mdl.get_item("L" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)
        C = mdl.get_item("C" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)

        if L:
            mdl.delete_item(L)
        if not C:
            C = mdl.create_component("Capacitor", parent=comp_handle, name="C" + phase.lower(), position=comp_pos,
                                     rotation="right")
            mdl.set_property_value(mdl.prop(C, "capacitance"), "C" + phase.lower())

        conn = mdl.get_item("Conn_" + phase, parent=comp_handle, item_type=ITEM_CONNECTION)
        if conn:
            mdl.delete_item(conn)

        conn = mdl.create_connection(mdl.term(C, "n_node"), jun1, name="Conn_" + phase)

        conn0 = mdl.get_item("Conn_" + phase + "0", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not conn0:
            mdl.create_connection(mdl.term(R, "n_node"), mdl.term(C, "p_node"), name="Conn_" + phase + "0")

    else:
        L = mdl.get_item("L" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)
        C = mdl.get_item("C" + phase.lower(), parent=comp_handle, item_type=ITEM_COMPONENT)

        if C:
            mdl.delete_item(C)
        if not L:
            L = mdl.create_component("Inductor", parent=comp_handle, name="L" + phase.lower(), position=comp_pos,
                                     rotation="right")
            mdl.set_property_value(mdl.prop(L, "inductance"), "L" + phase.lower())

        conn = mdl.get_item("Conn_" + phase, parent=comp_handle, item_type=ITEM_CONNECTION)
        if conn:
            mdl.delete_item(conn)

        conn = mdl.create_connection(mdl.term(L, "n_node"), jun1, name="Conn_" + phase)

        conn0 = mdl.get_item("Conn_" + phase + "0", parent=comp_handle, item_type=ITEM_CONNECTION)
        if not conn0:
            mdl.create_connection(mdl.term(R, "n_node"), mdl.term(L, "p_node"), name="Conn_" + phase + "0")


def lock_prop(mdl, comp_handle, property, new_value, locking_value):
    if new_value == locking_value:
        mdl.disable_property(mdl.prop(comp_handle, property))
    else:
        mdl.enable_property(mdl.prop(comp_handle, property))


def conn_type_value_edited_fnc(mdl, container_handle, new_value):
    gnd_prop = mdl.prop(container_handle, "ground_connected")
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


def phase_value_edited_fnc(mdl, container_handle, new_value):
    conn_type_prop = mdl.prop(container_handle, "conn_type")
    conn_type = mdl.get_property_disp_value(conn_type_prop)
    gnd_prop = mdl.prop(container_handle, "ground_connected")
    if new_value == "1":
        if conn_type == "Δ":
            mdl.set_property_disp_value(mdl.prop(container_handle, 'ground_connected'), True)
        mdl.enable_property(mdl.prop(container_handle, "ground_connected"))
        mdl.set_property_disp_value(mdl.prop(container_handle, 'conn_type'), "Y")
        mdl.disable_property(mdl.prop(container_handle, "conn_type"))

    elif new_value == "3":
        mdl.enable_property(mdl.prop(container_handle, "conn_type"))
        if conn_type == "Y":
            mdl.enable_property(mdl.prop(container_handle, "ground_connected"))
        else:
            mdl.set_property_disp_value(mdl.prop(container_handle, 'ground_connected'), False)
            mdl.disable_property(mdl.prop(container_handle, "ground_connected"))

def load_loadshape(mdl, container_handle):
    import os
    import load_object as load_obj
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

        selected_obj_dict = obj_dicts.get("loadshapes").get(selected_object)

        loadshape_name = selected_object
        npts = selected_obj_dict.get("npts")
        if npts:
            npts = ast.literal_eval(npts)
        loadshape = selected_obj_dict.get("mult")
        interval = selected_obj_dict.get("interval")
        if interval:
            interval = ast.literal_eval(interval)
        if loadshape:
            loadshape = ast.literal_eval(loadshape)
        hour = selected_obj_dict.get("hour")
        if hour:
            hour = ast.literal_eval(hour)

        if interval == 0:# Check hour points
            if hour:
                loadshape = loadshape[:npts]
            else:
                mdl.info("interval property is zero, but hour property is not defined")
        else:
            loadshape = loadshape[:npts]

        loadshape_prop = mdl.prop(container_handle, "loadshape")
        loadshape_prop_int = mdl.prop(container_handle, "loadshape_int")
        loadshape_prop_time = mdl.prop(container_handle, "T_Ts")

        mdl.set_property_disp_value(loadshape_name_prop, str(loadshape_name))
        mdl.set_property_disp_value(loadshape_prop, str(loadshape))
        mdl.set_property_disp_value(loadshape_prop_int, str(interval))
        mdl.set_property_value(loadshape_name_prop, str(loadshape_name))
        mdl.set_property_value(loadshape_prop, str(loadshape))
        mdl.set_property_value(loadshape_prop_int, str(interval))

        if interval == 0:
            mdl.set_property_disp_value(loadshape_prop_time, str(hour))
            mdl.set_property_value(loadshape_prop_time, str(hour))


def toggle_frequency_prop(mdl, mask_handle, init=False):
    frequency_prop = mdl.prop(mask_handle, "fn")
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

    frequency_prop = mdl.prop(mask_handle, "fn")
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


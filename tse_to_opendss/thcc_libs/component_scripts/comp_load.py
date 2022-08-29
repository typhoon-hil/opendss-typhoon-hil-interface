import pathlib
import json
import ast
import pandas as pd

got_loadshape_points_list = []

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


def phase_value_changed_fnc(mdl, container_handle, new_value):
    conn_type_prop = mdl.prop(container_handle, "conn_type")
    conn_type = mdl.get_property_disp_value(conn_type_prop)
    if new_value == "1":
        if conn_type == "Δ":
            mdl.set_property_disp_value(mdl.prop(container_handle, 'ground_connected'), True)
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


def phase_value_edited_fnc(mdl, container_handle, new_value):
    load_model_prop = mdl.prop(container_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    if new_value == "3":
        if load_model == "Constant Impedance":
            mdl.enable_property(mdl.prop(container_handle, "conn_type"))
        else:
            mdl.set_property_disp_value(mdl.prop(container_handle, 'conn_type'), "Y")
            mdl.disable_property(mdl.prop(container_handle, "conn_type"))
    else:
        mdl.set_property_disp_value(mdl.prop(container_handle, 'conn_type'), "Y")
        mdl.disable_property(mdl.prop(container_handle, "conn_type"))
        mdl.enable_property(mdl.prop(container_handle, "ground_connected"))


def load_model_value_edited_fnc(mdl, container_handle, new_value):
    conn_type_prop = mdl.prop(container_handle, "conn_type")
    conn_type = mdl.get_property_disp_value(conn_type_prop)

    phases_prop = mdl.prop(container_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    if new_value == "Constant Impedance":
        mdl.set_property_disp_value(mdl.prop(container_handle, 'Pow_ref_s'), "Fixed")
        mdl.disable_property(mdl.prop(container_handle, "Pow_ref_s"))
        mdl.disable_property(mdl.prop(container_handle, "Ts"))
        mdl.disable_property(mdl.prop(container_handle, "Tfast"))
        mdl.disable_property(mdl.prop(container_handle, "CPL_LMT"))
        if phases == "1":
            mdl.disable_property(mdl.prop(container_handle, "conn_type"))
        else:
            mdl.enable_property(mdl.prop(container_handle, "conn_type"))
        if conn_type == "Y":
            mdl.enable_property(mdl.prop(container_handle, "ground_connected"))
    else:
        mdl.enable_property(mdl.prop(container_handle, "Pow_ref_s"))
        mdl.enable_property(mdl.prop(container_handle, "Ts"))
        mdl.enable_property(mdl.prop(container_handle, "Tfast"))
        mdl.enable_property(mdl.prop(container_handle, "CPL_LMT"))
        mdl.set_property_disp_value(mdl.prop(container_handle, 'conn_type'), "Y")
        mdl.disable_property(mdl.prop(container_handle, "conn_type"))
        mdl.enable_property(mdl.prop(container_handle, "ground_connected"))

def load_loadshape(mdl, container_handle):
    import os
    import sys
    import pathlib

    try:
        from tse_to_opendss.tse_to_third_party_tools_converter import tse2tpt
        import tse_to_opendss
    except:
        # If running from development folder instead of installed package
        dss_module_folder = str(pathlib.Path(__file__).parent.parent.parent.parent)
        if not dss_module_folder in sys.path:
            sys.path.append(dss_module_folder)

        from tse_to_opendss.tse_to_third_party_tools_converter import tse2tpt
        import tse_to_opendss

    import tse_to_opendss.thcc_libs.gui_scripts.load_object as load_obj
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
        loadshape_prop_time = mdl.prop(container_handle, "T_Ts")
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
            mdl.set_property_value(loadshape_prop, str(loadshape))

        mdl.set_property_disp_value(loadshape_name_prop, str(loadshape_name))
        mdl.set_property_disp_value(loadshape_prop_int, str(interval))
        mdl.set_property_disp_value(loadshape_from_file_prop, str(loadshape_from_file))
        mdl.set_property_disp_value(useactual_prop, useactual)
        mdl.set_property_value(useactual_prop, useactual)
        mdl.set_property_value(loadshape_name_prop, str(loadshape_name))
        mdl.set_property_value(loadshape_prop_int, str(interval))
        mdl.set_property_value(loadshape_from_file_prop, str(loadshape_from_file))
        mdl.set_property_value(loadshape_from_file_path_prop, str(loadshape_from_file_path))
        mdl.set_property_value(loadshape_from_file_header_prop, str(loadshape_from_file_header))
        mdl.set_property_value(loadshape_from_file_column_prop, str(loadshape_from_file_column))

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

def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    # deleted_ports = []
    created_ports = {}

    conn_type_prop = mdl.prop(mask_handle, "conn_type")
    conn_type = mdl.get_property_disp_value(conn_type_prop)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    ground_connected_prop = mdl.prop(mask_handle, "ground_connected")
    ground_connected = mdl.get_property_disp_value(ground_connected_prop)

    gnd_check = False
    if str(ground_connected) == "True":
        gnd_check = True

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    Pow_ref_s_prop = mdl.prop(mask_handle, "Pow_ref_s")
    Pow_ref_s = mdl.get_property_disp_value(Pow_ref_s_prop)

    # S_Ts_mode_prop = mdl.prop(mask_handle, "S_Ts_mode")
    # mdl.set_property_disp_value(S_Ts_mode_prop, "Manual input")
    # mdl.set_property_value(S_Ts_mode_prop, "Manual input")
    # S_Ts_mode = mdl.get_property_disp_value(S_Ts_mode_prop)

    if phases == "3":
        portA = mdl.get_item("A1", parent=comp_handle, item_type="port")
        portB = mdl.get_item("B1", parent=comp_handle, item_type="port")
        portC = mdl.get_item("C1", parent=comp_handle, item_type="port")

        P_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
        Q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")

        if P_ext:
            mdl.set_port_properties(P_ext, terminal_position=(50, -15))
            created_ports.update({"P_ext": P_ext})
        if Q_ext:
            mdl.set_port_properties(Q_ext, terminal_position=(50, 15))
            created_ports.update({"Q_ext": Q_ext})

        if not portA:
            portA = mdl.create_port(parent=comp_handle, name="A1", direction="out", kind="pe",
                                    terminal_position=(-30, -32),
                                    position=(7802, 7862), rotation="right")
            created_ports.update({"portA": portA})
        else:
            mdl.set_port_properties(portA, terminal_position=(-30, -32))
            created_ports.update({"portA": portA})
        if not portB:
            portB = mdl.create_port(parent=comp_handle, name="B1", direction="out", kind="pe",
                                    terminal_position=(0.0, -32),
                                    position=(7919, 7862), rotation="right")
            created_ports.update({"portB": portB})
        else:
            mdl.set_port_properties(portB, terminal_position=(0.0, -32))
            created_ports.update({"portB": portB})
        if not portC:
            portC = mdl.create_port(parent=comp_handle, name="C1", direction="out", kind="pe",
                                    terminal_position=(30, -32),
                                    position=(8055, 7862), rotation="right")
            created_ports.update({"portC": portC})
        else:
            created_ports.update({"portC": portC})

        junN = mdl.get_item("JN", parent=comp_handle, item_type="junction")
        if not gnd_check:
            if junN:
                if conn_type == "Y":
                    portN = mdl.get_item("N1", parent=comp_handle, item_type="port")
                    if not portN:
                        portN = mdl.create_port(parent=comp_handle, name="N1", direction="out", kind="pe",
                                                terminal_position=(0, 30),
                                                position=(7921, 8384), rotation="left")
                        created_ports.update({"portN": portN})
                    else:
                        created_ports.update({"portN": portN})

    elif phases == "1":
        portA = mdl.get_item("A1", parent=comp_handle, item_type="port")
        portB = mdl.get_item("B1", parent=comp_handle, item_type="port")
        portC = mdl.get_item("C1", parent=comp_handle, item_type="port")

        P_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
        Q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")
        if P_ext:
            mdl.set_port_properties(P_ext, terminal_position=(25, -15))
            created_ports.update({"P_ext": P_ext})
        if Q_ext:
            mdl.set_port_properties(Q_ext, terminal_position=(25, 15))
            created_ports.update({"Q_ext": Q_ext})

        if not portA:
            portA = mdl.create_port(parent=comp_handle, name="A1", direction="out", kind="pe",
                                    terminal_position=(0, -32),
                                    position=(7802, 7862), rotation="right")
            created_ports.update({"portA": portA})
        else:
            mdl.set_port_properties(portA, terminal_position=(0, -32))
            created_ports.update({"portA": portA})
        if gnd_check:
            if portB:
                mdl.delete_item(portB)
                created_ports.pop("portB", None)
        else:
            if not portB:
                portB = mdl.create_port(parent=comp_handle, name="B1", direction="out", kind="pe",
                                        terminal_position=(0, 30),
                                        position=(7919, 7862), rotation="right")
                created_ports.update({"portB": portB})
            else:
                mdl.set_port_properties(portB, terminal_position=(0, 30))
                created_ports.update({"portB": portB})
            portN = mdl.get_item("N1", parent=comp_handle, item_type="port")
            if portN:
                mdl.delete_item(portN)
                created_ports.pop("portN", None)
        if portC:
            mdl.delete_item(portC)
            created_ports.pop("portC", None)

    if conn_type == "Y":
        if not gnd_check:
            portN = mdl.get_item("N1", parent=comp_handle, item_type="port")
            if not portN:
                portN = mdl.create_port(parent=comp_handle, name="N1", direction="out", kind="pe",
                                        terminal_position=(0, 30),
                                        position=(7921, 8384), rotation="left")
                created_ports.update({"portN": portN})
            else:
                created_ports.update({"portN": portN})
    else:
        if load_model == "Constant Impedance":
            portN = mdl.get_item("N1", parent=comp_handle, item_type="port")
            if portN:
                mdl.delete_item(portN)
                created_ports.pop("portN", None)

    if not gnd_check:
        junN = mdl.get_item("JN", parent=comp_handle, item_type="junction")
        if junN:
            portN = mdl.get_item("N1", parent=comp_handle, item_type="port")
            portB = mdl.get_item("B1", parent=comp_handle, item_type="port")
            if phases == "3":
                if not portN:
                    portN = mdl.create_port(parent=comp_handle, name="N1", direction="out", kind="pe",
                                            terminal_position=(0, 30),
                                            position=(7921, 8384), rotation="left")
                    created_ports.update({"portN": portN})
                else:
                    created_ports.update({"portN": portN})
            else:
                if not portB:
                    portB = mdl.create_port(parent=comp_handle, name="B1", direction="out", kind="pe",
                                            terminal_position=(0.0, 30),
                                            position=(7919, 7862), rotation="right")
                    created_ports.update({"portB": portB})
                else:
                    mdl.set_port_properties(portB, terminal_position=(0.0, 30))
                    created_ports.update({"portB": portB})
                if portN:
                    mdl.delete_item(portN)
                    created_ports.pop("portN", None)
        if conn_type == "Δ":
            if load_model == "Constant Impedance":
                portN = mdl.get_item("N1", parent=comp_handle, item_type="port")
                if portN:
                    mdl.delete_item(portN)
                    created_ports.pop("portN", None)

    else:
        portN = mdl.get_item("N1", parent=comp_handle, item_type="port")
        if phases == "1":
            portB = mdl.get_item("B1", parent=comp_handle, item_type="port")
            if portB:
                mdl.delete_item(portB)
                created_ports.pop("portB", None)
        if portN:
            mdl.delete_item(portN)
            created_ports.pop("portN", None)

    if Pow_ref_s == "Fixed":

        P_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
        Q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")
        T_ext = mdl.get_item("T", parent=comp_handle, item_type="port")

        if P_ext:
            mdl.delete_item(P_ext)
            created_ports.pop("P_ext", None)
        if Q_ext:
            mdl.delete_item(Q_ext)
            created_ports.pop("Q_ext", None)
        if T_ext:
            mdl.delete_item(T_ext)
            created_ports.pop("T_ext", None)
    elif Pow_ref_s == "External input":

        P_ext = mdl.get_item("P", parent=comp_handle, item_type="port")

        if not P_ext:
            if phases == "1":
                P_ext = mdl.create_port(parent=comp_handle, name="P", direction="in", kind="sp",
                                        terminal_position=(25, -15),
                                        position=(7936, 8175))
                created_ports.update({"P_ext": P_ext})
            else:
                P_ext = mdl.create_port(parent=comp_handle, name="P", direction="in", kind="sp",
                                        terminal_position=(50, -15),
                                        position=(7936, 8175))
                created_ports.update({"P_ext": P_ext})
        else:
            created_ports.update({"P_ext": P_ext})

        Q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")

        if not Q_ext:
            if phases == "1":
                Q_ext = mdl.create_port(parent=comp_handle, name="Q", direction="in", kind="sp",
                                        terminal_position=(25, 15),
                                        position=(7936, 8240))
                created_ports.update({"Q_ext": Q_ext})
            else:
                Q_ext = mdl.create_port(parent=comp_handle, name="Q", direction="in", kind="sp",
                                        terminal_position=(50, 15),
                                        position=(7936, 8240))
                created_ports.update({"Q_ext": Q_ext})
        else:
            created_ports.update({"Q_ext": Q_ext})

        T_ext = mdl.get_item("T", parent=comp_handle, item_type="port")
        if T_ext:
            mdl.delete_item(T_ext)
            created_ports.pop("T_ext", None)
    else:

        P_ext = mdl.get_item("P", parent=comp_handle, item_type="port")
        Q_ext = mdl.get_item("Q", parent=comp_handle, item_type="port")
        T_ext = mdl.get_item("T", parent=comp_handle, item_type="port")

        if P_ext:
            mdl.delete_item(P_ext)
            created_ports.pop("P_ext", None)
        if Q_ext:
            mdl.delete_item(Q_ext)
            created_ports.pop("Q_ext", None)
        # if S_Ts_mode == "Manual input":
        if not T_ext:
            if phases == "1":
                T_ext = mdl.create_port(parent=comp_handle, name="T", direction="in", kind="sp",
                                        terminal_position=(25, 0),
                                        position=(7400, 8400))
                created_ports.update({"T_ext": T_ext})
            else:
                T_ext = mdl.create_port(parent=comp_handle, name="T", direction="in", kind="sp",
                                        terminal_position=(50, 0),
                                        position=(7400, 8400))
                created_ports.update({"T_ext": T_ext})
        else:
            created_ports.update({"T_ext": T_ext})
        # else:
        #     if T_ext:
        #         mdl.delete_item(T_ext)
        #         created_ports.pop("T_ext", None)

    if load_model == "Constant Power":
        if Pow_ref_s == "Time Series":
            T_ext = mdl.get_item("T", parent=comp_handle, item_type="port")
            # if S_Ts_mode == "Manual input":
            if not T_ext:
                if phases == "1":
                    T_ext = mdl.create_port(parent=comp_handle, name="T", direction="in", kind="sp",
                                            terminal_position=(25, 0),
                                            position=(7740, 8210))
                    created_ports.update({"T_ext": T_ext})
                else:
                    T_ext = mdl.create_port(parent=comp_handle, name="T", direction="in", kind="sp",
                                            terminal_position=(50, 0),
                                            position=(7740, 8210))
                    created_ports.update({"T_ext": T_ext})
            else:
                created_ports.update({"T_ext": T_ext})
            # else:
            #     if T_ext:
            #         mdl.delete_item(T_ext)
            #         created_ports.pop("T_ext", None)

    return created_ports


def connections_dynamics(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)

    conn_type_prop = mdl.prop(mask_handle, "conn_type")
    conn_type = mdl.get_property_disp_value(conn_type_prop)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    ground_connected_prop = mdl.prop(mask_handle, "ground_connected")
    ground_connected = mdl.get_property_disp_value(ground_connected_prop)

    gnd_check = False
    if str(ground_connected) == "True":
        gnd_check = True

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    if conn_type == "Y":
        CIL1 = mdl.get_item("CIL", parent=comp_handle, item_type="component")
        mdl.set_property_value(mdl.prop(CIL1, "conn_type"), "Y")
        mdl.set_property_value(mdl.prop(CIL1, "ground_connected"), True)
        mdl.set_property_value(mdl.prop(CIL1, "ground_connected"), False)
        connNCIL = mdl.get_item("Conn_AN", parent=comp_handle, item_type="component")
        junN = mdl.get_item("JN", parent=comp_handle, item_type="junction")

        if not junN:
            junN = mdl.create_junction(name='JN', parent=comp_handle, kind='pe',
                                       position=(7921, 8326))
        if not connNCIL:
            mdl.create_connection(mdl.term(CIL1, "N"), junN, name="Conn_AN")

        if not gnd_check:
            gnd1 = mdl.get_item("gndc", parent=comp_handle, item_type="component")
            if gnd1:
                mdl.delete_item(gnd1)
            if junN:
                if phases == "3":
                    connN0 = mdl.get_item("Conn_N0", parent=comp_handle, item_type="connection")
                    if not connN0:
                        mdl.create_connection(junN, created_ports.get("portN"), name="Conn_N0")

    else:
        CIL1 = mdl.get_item("CIL", parent=comp_handle, item_type="component")
        mdl.set_property_value(mdl.prop(CIL1, "conn_type"), "Δ")


def connections_gnd_dynamics(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)

    conn_type_prop = mdl.prop(mask_handle, "conn_type")
    conn_type = mdl.get_property_disp_value(conn_type_prop)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    ground_connected_prop = mdl.prop(mask_handle, "ground_connected")
    ground_connected = mdl.get_property_disp_value(ground_connected_prop)

    gnd_check = False
    if str(ground_connected) == "True":
        gnd_check = True

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    if not gnd_check:
        junN = mdl.get_item("JN", parent=comp_handle, item_type="junction")
        gnd1 = mdl.get_item("gndc", parent=comp_handle, item_type="component")
        if gnd1:
            mdl.delete_item(gnd1)
        if junN:
            connBN = mdl.get_item("ConnB1N", parent=comp_handle, item_type="connection")
            tagNN = mdl.get_item("TagNN", parent=comp_handle, item_type="tag")
            tagBN = mdl.get_item("TagBN", parent=comp_handle, item_type="tag")
            if phases == "3":
                if tagNN:
                    mdl.delete_item(tagNN)
                connN0 = mdl.get_item("Conn_N0", parent=comp_handle, item_type="connection")
                portN = created_ports.get("portN")
                if portN:
                    if not connN0:
                        mdl.create_connection(junN, portN, name="Conn_N0")
            else:
                if tagBN:
                    mdl.delete_item(tagBN)
                tagBN = mdl.create_tag("BN", name="TagBN", parent=comp_handle, scope="local",
                                       kind="pe", rotation="left", position=(7960, 7944))
                if not connBN:
                    mdl.create_connection(created_ports.get("portB"), tagBN, name="ConnB1N")
                if not tagNN:
                    tagNN = mdl.create_tag("BN", name="TagNN", parent=comp_handle, scope="local",
                                           kind="pe", rotation="left", position=(7960, 8384))
                connBN0 = mdl.get_item("Conn_BN0", parent=comp_handle, item_type="connection")
                if not connBN0:
                    mdl.create_connection(junN, tagNN, name="Conn_BN0")
        if conn_type == "Δ":
            if load_model == "Constant Impedance":
                if tagNN:
                    mdl.delete_item(tagNN)
    else:
        tagNN = mdl.get_item("TagNN", parent=comp_handle, item_type="tag")
        gnd1 = mdl.get_item("gndc", parent=comp_handle, item_type="component")
        junN = mdl.get_item("JN", parent=comp_handle, item_type="junction")
        if phases == "1":
            tagBN = mdl.get_item("TagBN", parent=comp_handle, item_type="tag")
            if tagBN:
                mdl.delete_item(tagBN)
        if tagNN:
            mdl.delete_item(tagNN)
        if junN:
            if not gnd1:
                gnd1 = mdl.create_component("src_ground", parent=comp_handle, name="gndc", position=(7921, 8344))
            connG = mdl.get_item("Conn_G", parent=comp_handle, item_type="connection")
            if not connG:
                mdl.create_connection(mdl.term(gnd1, "node"), junN, name="Conn_G")


def connections_phases_dynamics(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)

    conn_type_prop = mdl.prop(mask_handle, "conn_type")
    conn_type = mdl.get_property_disp_value(conn_type_prop)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    ground_connected_prop = mdl.prop(mask_handle, "ground_connected")
    ground_connected = mdl.get_property_disp_value(ground_connected_prop)

    gnd_check = False
    if str(ground_connected) == "True":
        gnd_check = True

    phases_prop = mdl.prop(mask_handle, "phases")
    phases = mdl.get_property_disp_value(phases_prop)

    if phases == "3":
        CIL1 = mdl.get_item("CIL", parent=comp_handle, item_type="component")
        CPL1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
        if mdl.is_enabled(CIL1):
            if load_model == "Constant Impedance":
                mdl.set_property_value(mdl.prop(CIL1, "phases"), "3")
        if mdl.is_enabled(CPL1):
            if load_model == "Constant Power":
                mdl.set_property_value(mdl.prop(CPL1, "phases"), "3")
        connACPL = mdl.get_item("ConnA1CPL", parent=comp_handle, item_type="connection")
        connBCPL = mdl.get_item("ConnB1CPL", parent=comp_handle, item_type="connection")
        connCCPL = mdl.get_item("ConnC1CPL", parent=comp_handle, item_type="connection")
        connACIL = mdl.get_item("ConnA1CIL", parent=comp_handle, item_type="connection")
        connBCIL = mdl.get_item("ConnB1CIL", parent=comp_handle, item_type="connection")
        connCCIL = mdl.get_item("ConnC1CIL", parent=comp_handle, item_type="connection")
        tagAP = mdl.get_item("TagA1", parent=comp_handle, item_type="tag")
        tagBP = mdl.get_item("TagB1", parent=comp_handle, item_type="tag")
        tagCP = mdl.get_item("TagC1", parent=comp_handle, item_type="tag")
        tagACIL = mdl.get_item("TagA2", parent=comp_handle, item_type="tag")
        tagBCIL = mdl.get_item("TagB2", parent=comp_handle, item_type="tag")
        tagCCIL = mdl.get_item("TagC2", parent=comp_handle, item_type="tag")
        tagACPL = mdl.get_item("TagA3", parent=comp_handle, item_type="tag")
        tagBCPL = mdl.get_item("TagB3", parent=comp_handle, item_type="tag")
        tagCCPL = mdl.get_item("TagC3", parent=comp_handle, item_type="tag")
        tagBN = mdl.get_item("TagBN", parent=comp_handle, item_type="tag")
        tagNN = mdl.get_item("TagNN", parent=comp_handle, item_type="tag")

        if tagBN:
            mdl.delete_item(tagBN)
        if tagNN:
            mdl.delete_item(tagNN)
        if not tagBP:
            tagBP = mdl.create_tag("B1", name="TagB1", parent=comp_handle, scope="local",
                                   kind="pe", rotation="left", position=(7920, 7944))
        if not tagCP:
            tagCP = mdl.create_tag("C1", name="TagC1", parent=comp_handle, scope="local",
                                   kind="pe", rotation="left", position=(8056, 7944))
        if load_model == "Constant Impedance":
            if not tagACIL:
                tagACIL = mdl.create_tag("A1", name="TagA2", parent=comp_handle, scope="local",
                                         kind="pe", rotation="right", position=(7694, 8088))
            if not tagBCIL:
                tagBCIL = mdl.create_tag("B1", name="TagB2", parent=comp_handle, scope="local",
                                         kind="pe", rotation="right", position=(7758, 8088))
            if not tagCCIL:
                tagCCIL = mdl.create_tag("C1", name="TagC2", parent=comp_handle, scope="local",
                                         kind="pe", rotation="right", position=(7823, 8088))
            if not connACIL:
                mdl.create_connection(mdl.term(CIL1, "A1"), tagACIL, name="ConnA1CIL")
            if not connBCIL:
                mdl.create_connection(mdl.term(CIL1, "B1"), tagBCIL, name="ConnB1CIL")
            if not connCCIL:
                mdl.create_connection(mdl.term(CIL1, "C1"), tagCCIL, name="ConnC1CIL")
        elif load_model == "Constant Power":
            if not tagACPL:
                tagACPL = mdl.create_tag("A1", name="TagA3", parent=comp_handle, scope="local",
                                         kind="pe", rotation="right", position=(8000, 8088))
            if not tagBCPL:
                tagBCPL = mdl.create_tag("B1", name="TagB3", parent=comp_handle, scope="local",
                                         kind="pe", rotation="right", position=(8063, 8088))
            if not tagCCPL:
                tagCCPL = mdl.create_tag("C1", name="TagC3", parent=comp_handle, scope="local",
                                         kind="pe", rotation="right", position=(8127, 8088))
            if not connACPL:
                mdl.create_connection(mdl.term(CPL1, "A1"), tagACPL, name="ConnA1CPL")
            if not connBCPL:
                mdl.create_connection(mdl.term(CPL1, "B1"), tagBCPL, name="ConnB1CPL")
            if not connCCPL:
                mdl.create_connection(mdl.term(CPL1, "C1"), tagCCPL, name="ConnC1CPL")

        connAP = mdl.get_item("ConnA1P", parent=comp_handle, item_type="connection")
        connBP = mdl.get_item("ConnB1P", parent=comp_handle, item_type="connection")
        connCP = mdl.get_item("ConnC1P", parent=comp_handle, item_type="connection")

        if not connAP:
            mdl.create_connection(created_ports.get("portA"), tagAP, name="ConnA1P")
        if not connBP:
            mdl.create_connection(created_ports.get("portB"), tagBP, name="ConnB1P")
        if not connCP:
            mdl.create_connection(created_ports.get("portC"), tagCP, name="ConnC1P")

        junN = mdl.get_item("JN", parent=comp_handle, item_type="junction")
        gnd1 = mdl.get_item("gndc", parent=comp_handle, item_type="component")
        if not gnd_check:
            if gnd1:
                mdl.delete_item(gnd1)
            if conn_type == "Y":
                if junN:
                    connN0 = mdl.get_item("Conn_N0", parent=comp_handle, item_type="connection")
                    if not connN0:
                        mdl.create_connection(junN, created_ports.get("portN"), name="Conn_N0")

    elif phases == "1":

        CIL1 = mdl.get_item("CIL", parent=comp_handle, item_type="component")
        CPL1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
        if mdl.is_enabled(CIL1):
            if load_model == "Constant Impedance":
                mdl.set_property_value(mdl.prop(CIL1, "phases"), "1")
        if mdl.is_enabled(CPL1):
            if load_model == "Constant Power":
                mdl.set_property_value(mdl.prop(CPL1, "phases"), "1")
        connACPL = mdl.get_item("ConnA1CPL", parent=comp_handle, item_type="connection")
        connACIL = mdl.get_item("ConnA1CIL", parent=comp_handle, item_type="connection")
        connAP = mdl.get_item("ConnA1P", parent=comp_handle, item_type="connection")
        tagAP = mdl.get_item("TagA1", parent=comp_handle, item_type="tag")
        tagBP = mdl.get_item("TagB1", parent=comp_handle, item_type="tag")
        tagCP = mdl.get_item("TagC1", parent=comp_handle, item_type="tag")
        tagACIL = mdl.get_item("TagA2", parent=comp_handle, item_type="tag")
        tagBCIL = mdl.get_item("TagB2", parent=comp_handle, item_type="tag")
        tagCCIL = mdl.get_item("TagC2", parent=comp_handle, item_type="tag")
        tagACPL = mdl.get_item("TagA3", parent=comp_handle, item_type="tag")
        tagBCPL = mdl.get_item("TagB3", parent=comp_handle, item_type="tag")
        tagCCPL = mdl.get_item("TagC3", parent=comp_handle, item_type="tag")
        tagBN = mdl.get_item("TagBN", parent=comp_handle, item_type="tag")
        tagNN = mdl.get_item("TagNN", parent=comp_handle, item_type="tag")

        if load_model == "Constant Power":
            tagACPL = mdl.get_item("TagA3", parent=comp_handle, item_type="tag")
            if not tagACPL:
                tagACPL = mdl.create_tag("A1", name="TagA3", parent=comp_handle, scope="local",
                                         kind="pe", rotation="right", position=(8000, 8088))
            if not connACPL:
                mdl.create_connection(mdl.term(CPL1, "A1"), tagACPL, name="ConnA1CPL")
        elif load_model == "Constant Impedance":
            tagACIL = mdl.get_item("TagA2", parent=comp_handle, item_type="tag")
            if not tagACIL:
                tagACIL = mdl.create_tag("A1", name="TagA2", parent=comp_handle, scope="local",
                                         kind="pe", rotation="right", position=(7694, 8088))
            if not connACIL:
                mdl.create_connection(mdl.term(CIL1, "A1"), tagACIL, name="ConnA1CIL")
        if not connAP:
            mdl.create_connection(created_ports.get("portA"), tagAP, name="ConnA1P")
        if gnd_check:
            if tagBP:
                mdl.delete_item(tagBP)
            if tagBN:
                mdl.delete_item(tagBN)
            if tagNN:
                mdl.delete_item(tagNN)
        else:
            if tagBP:
                mdl.delete_item(tagBP)
            if tagBN:
                mdl.delete_item(tagBN)
            tagBN = mdl.create_tag("BN", name="TagBN", parent=comp_handle, scope="local",
                                   kind="pe", rotation="left", position=(7960, 7944))
            connBN = mdl.get_item("ConnB1N", parent=comp_handle, item_type="connection")
            if not connBN:
                mdl.create_connection(created_ports.get("portB"), tagBN, name="ConnB1N")
            tagNN = mdl.get_item("TagNN", parent=comp_handle, item_type="tag")
            if not tagNN:
                tagNN = mdl.create_tag("BN", name="TagNN", parent=comp_handle, scope="local",
                                       kind="pe", rotation="left", position=(7960, 8384))
            connBN0 = mdl.get_item("Conn_BN0", parent=comp_handle, item_type="connection")
            junN = mdl.get_item("JN", parent=comp_handle, item_type="junction")
            if not connBN0:
                mdl.create_connection(junN, tagNN, name="Conn_BN0")
        if tagCP:
            mdl.delete_item(tagCP)
        if tagBCPL:
            mdl.delete_item(tagBCPL)
        if tagCCPL:
            mdl.delete_item(tagCCPL)
        if tagBCIL:
            mdl.delete_item(tagBCIL)
        if tagCCIL:
            mdl.delete_item(tagCCIL)


def connections_pow_ref_dynamics(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)

    Pow_ref_s_prop = mdl.prop(mask_handle, "Pow_ref_s")
    Pow_ref_s = mdl.get_property_disp_value(Pow_ref_s_prop)

    # S_Ts_mode_prop = mdl.prop(mask_handle, "S_Ts_mode")
    # mdl.set_property_disp_value(S_Ts_mode_prop, "Manual input")
    # mdl.set_property_value(S_Ts_mode_prop, "Manual input")
    # S_Ts_mode = mdl.get_property_disp_value(S_Ts_mode_prop)


    if Pow_ref_s == "Fixed":
        CPL1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
        TSmdl = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
        Ts_select = mdl.get_item("T_switch", parent=comp_handle, item_type="component")
        Ts_select1 = mdl.get_item("Constant1", parent=comp_handle, item_type="component")
        mdl.set_property_value(mdl.prop(TSmdl, "P_mode"), "Manual input")
        mdl.disable_items(TSmdl)
        mdl.disable_items(Ts_select)
        mdl.disable_items(Ts_select1)
        mdl.set_property_value(mdl.prop(CPL1, "kP_inp"), "Fixed")
        mdl.set_property_value(mdl.prop(CPL1, "kQ_inp"), "Fixed")

        conn_TsP_int = mdl.get_item("ConnTsP", parent=comp_handle, item_type="connection")
        conn_TsQ_int = mdl.get_item("ConnTsQ", parent=comp_handle, item_type="connection")

        if conn_TsP_int:
            mdl.delete_item(conn_TsP_int)
        if conn_TsQ_int:
            mdl.delete_item(conn_TsQ_int)

    elif Pow_ref_s == "External input":
        CPL1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
        mdl.set_property_value(mdl.prop(CPL1, "kP_inp"), "Variable input")
        mdl.set_property_value(mdl.prop(CPL1, "kQ_inp"), "Variable input")

        P_inp = mdl.get_item("CPL", parent=comp_handle, item_type="component")
        conn_P_int = mdl.get_item("connP", parent=comp_handle, item_type="connection")

        conn_TsP_int = mdl.get_item("ConnTsP", parent=comp_handle, item_type="connection")
        conn_TsQ_int = mdl.get_item("ConnTsQ", parent=comp_handle, item_type="connection")

        if conn_TsP_int:
            mdl.delete_item(conn_TsP_int)
        if conn_TsQ_int:
            mdl.delete_item(conn_TsQ_int)

        if conn_P_int:
            mdl.delete_item(conn_P_int)

        mdl.create_connection(mdl.term(P_inp, "P_set"), created_ports.get("P_ext"), "ConnP")

        conn_Q_int = mdl.get_item("connQ", parent=comp_handle, item_type="connection")
        if conn_Q_int:
            mdl.delete_item(conn_Q_int)

        mdl.create_connection(mdl.term(P_inp, "Q_set"), created_ports.get("Q_ext"), "ConnQ")

        TSmdl = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
        Ts_select = mdl.get_item("T_switch", parent=comp_handle, item_type="component")
        Ts_select1 = mdl.get_item("Constant1", parent=comp_handle, item_type="component")
        mdl.set_property_value(mdl.prop(TSmdl, "P_mode"), "Manual input")
        mdl.disable_items(TSmdl)
        mdl.disable_items(Ts_select)
        mdl.disable_items(Ts_select1)
    else:
        CPL1 = mdl.get_item("CPL", parent=comp_handle, item_type="component")
        mdl.set_property_value(mdl.prop(CPL1, "kP_inp"), "Variable input")
        mdl.set_property_value(mdl.prop(CPL1, "kQ_inp"), "Variable input")

        P_inp = mdl.get_item("CPL", parent=comp_handle, item_type="component")
        conn_P_int = mdl.get_item("connP", parent=comp_handle, item_type="connection")
        conn_Q_int = mdl.get_item("connQ", parent=comp_handle, item_type="connection")
        conn_Ts_in = mdl.get_item("ConnTs", parent=comp_handle, item_type="connection")

        if conn_P_int:
            mdl.delete_item(conn_P_int)
        if conn_Q_int:
            mdl.delete_item(conn_Q_int)

        TSmdl = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
        Ts_select = mdl.get_item("T_switch", parent=comp_handle, item_type="component")
        Ts_select1 = mdl.get_item("Constant1", parent=comp_handle, item_type="component")
        mdl.enable_items(TSmdl)
        mdl.enable_items(Ts_select)
        mdl.enable_items(Ts_select1)
        # if S_Ts_mode == "Manual input":
        mdl.set_property_value(mdl.prop(TSmdl, "P_mode"), "Manual input")
        if not conn_Ts_in:
            mdl.create_connection(mdl.term(Ts_select, "T"), created_ports.get("T_ext"), "ConnTs")
        # else:
        #     mdl.set_property_value(mdl.prop(TSmdl, "P_mode"), "Loop cycle")

        conn_TsP_int = mdl.get_item("ConnTsP", parent=comp_handle, item_type="connection")
        conn_TsQ_int = mdl.get_item("ConnTsQ", parent=comp_handle, item_type="connection")

        if not conn_TsP_int:
            mdl.create_connection(mdl.term(P_inp, "P_set"), mdl.term(TSmdl, "P"), "ConnTsP")
        if not conn_TsQ_int:
            mdl.create_connection(mdl.term(P_inp, "Q_set"), mdl.term(TSmdl, "Q"), "ConnTsQ")


def connections_ts_mode_dynamics(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)

    load_model_prop = mdl.prop(mask_handle, "load_model")
    load_model = mdl.get_property_disp_value(load_model_prop)

    Pow_ref_s_prop = mdl.prop(mask_handle, "Pow_ref_s")
    Pow_ref_s = mdl.get_property_disp_value(Pow_ref_s_prop)

    # S_Ts_mode_prop = mdl.prop(mask_handle, "S_Ts_mode")
    # mdl.set_property_disp_value(S_Ts_mode_prop, "Manual input")
    # mdl.set_property_value(S_Ts_mode_prop, "Manual input")
    # S_Ts_mode = mdl.get_property_disp_value(S_Ts_mode_prop)

    if load_model == "Constant Power":
        if Pow_ref_s == "Time Series":
            TSmdl = mdl.get_item("TS_module", parent=comp_handle, item_type="component")
            conn_Ts_in = mdl.get_item("ConnTs", parent=comp_handle, item_type="connection")
            # if S_Ts_mode == "Manual input":
            mdl.set_property_value(mdl.prop(TSmdl, "P_mode"), "Manual input")
            if not conn_Ts_in:
                mdl.create_connection(mdl.term(TSmdl, "T"), created_ports.get("T_ext"), "ConnTs")
            # else:
            #     mdl.set_property_value(mdl.prop(TSmdl, "P_mode"), "Loop cycle")


def get_all_circuit_loads(mdl, mask_handle, parent_comp=None):
    component_list = []
    if parent_comp:  # Component inside a subsystem (recursive function)
        all_components = mdl.get_items(parent_comp)
    else:  # Top level call
        all_components = mdl.get_items()

    for comp in all_components:
        try:
            type_name = mdl.get_component_type_name(comp)
            if type_name and type_name == "Load":
                component_list.append(comp)
            elif not type_name:  # Component is a subsystem
                component_list.extend(get_all_circuit_loads(mdl, mdl.get_mask(comp), parent_comp=comp))
        except:
            # Some components (such as ports and connections) cannot be used with
            # get_component_type_name
            pass
    # Return the list of component handles
    return component_list


def restore_all_loads_points(mdl, mask_handle):
    global got_loadshape_points_list

    # Return all components (including inside subsystems)
    all_loads = get_all_circuit_loads(mdl, mask_handle)
    got_loadshape_points_list = []
    for load in all_loads:
        if load not in got_loadshape_points_list:
            load_mask_handle = mdl.get_mask(load)
            read_loadshape_from_json(mdl, load_mask_handle)

def read_loadshape_from_json(mdl, mask_handle, reload_dict=None):
    global got_loadshape_points_list

    comp_handle = mdl.get_parent(mask_handle)

    try:
        current_points = ast.literal_eval(mdl.get_property_disp_value(mdl.prop(mask_handle, "loadshape")))
    except:
        current_points = []
    useactual = mdl.get_property_disp_value(mdl.prop(mask_handle, "useactual"))
    interval = mdl.get_property_disp_value(mdl.prop(mask_handle, "loadshape_int"))

    if not reload_dict:
        loadshape_name = mdl.get_property_disp_value(mdl.prop(mask_handle, "loadshape_name"))
        loadshape_from_file = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file")) == "True"
        loadshape_from_file_header = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_header")) == "True"
        loadshape_from_file_column = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_column"))
        loadshape_from_file_path = mdl.get_property_value(mdl.prop(mask_handle, "loadshape_from_file_path"))
    else:
        loadshape_name = reload_dict.get("loadshape_name")
        loadshape_from_file = reload_dict.get("csv_file") == "True"
        loadshape_from_file_header = reload_dict.get("headers") == "True"
        loadshape_from_file_column = reload_dict.get("column")
        loadshape_from_file_path = reload_dict.get("csv_path")

    model_path = pathlib.Path(mdl.get_model_file_path())

    if model_path:
        filename = model_path.stem
        data_folder_path = model_path.parent.joinpath(filename + " Target files").joinpath('dss').joinpath("data")
        general_objects_json = data_folder_path.joinpath(f"general_objects.json")
        if general_objects_json.is_file():
            with open(general_objects_json, 'r') as f:
                general_objects_dict = json.load(f)
            loadshape_points = general_objects_dict.get("loadshapes", {}).get(loadshape_name, {}).get("mult", [])
            if loadshape_from_file:
                if pathlib.Path(loadshape_from_file_path).is_file():
                    with open(pathlib.Path(loadshape_from_file_path), 'r', encoding='utf-8-sig') as ls_f:
                        if loadshape_from_file_header:
                            table = pd.read_csv(ls_f)
                            table = table.fillna(0)
                        else:
                            table = pd.read_csv(ls_f, header=None)
                            table = table.fillna(0)
                        loadshape_points = list(table.iloc[:, int(loadshape_from_file_column) - 1])
                    mdl.set_property_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
                    mdl.set_property_disp_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
                else:
                    mdl.error(f"Could not find the CSV file '{loadshape_from_file_path}'."
                              f" Please edit or choose a new LoadShape.", context=mdl.get_parent(mask_handle))
                if loadshape_name not in general_objects_dict.get("loadshapes"):
                    with open(general_objects_json, 'w') as f:
                        new_loadshape_dict = {
                            "npts": str(len(current_points)),
                            "mult": "[]",
                            "interval": interval,
                            "interval_unit": "h",
                            "hour": "",
                            "useactual": str(useactual),
                            "csv_file": str(loadshape_from_file),
                            "csv_path": loadshape_from_file_path,
                            "headers": str(loadshape_from_file_header),
                            "column": loadshape_from_file_column
                        }
                        general_objects_dict.get("loadshapes")[loadshape_name] = new_loadshape_dict
                        f.write(json.dumps(general_objects_dict, indent=4))
            elif not loadshape_points:
                new_loadshape_dict = {
                    "npts": str(len(current_points)),
                    "mult": str(current_points),
                    "interval": interval,
                    "interval_unit": "h",
                    "hour": "",
                    "useactual": str(useactual),
                    "csv_file": str(loadshape_from_file),
                    "csv_path": loadshape_from_file_path,
                    "headers": str(loadshape_from_file_header),
                    "column": loadshape_from_file_column
                }

                general_objects_dict.get("loadshapes")[loadshape_name] = new_loadshape_dict
                with open(general_objects_json, 'w') as f:
                    f.write(json.dumps(general_objects_dict, indent=4))
            else:
                mdl.set_property_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
                mdl.set_property_disp_value(mdl.prop(mask_handle, "loadshape"), loadshape_points)
        else:
            loadshape_points = str(current_points)
            if not data_folder_path.is_dir():
                data_folder_path.mkdir(parents=True)
            with open(general_objects_json, 'w') as f:
                new_loadshape_dict = {
                    "npts": str(len(current_points)),
                    "mult": str(current_points),
                    "interval": interval,
                    "interval_unit": "h",
                    "hour": "",
                    "useactual": str(useactual),
                    "csv_file": str(loadshape_from_file),
                    "csv_path": loadshape_from_file_path,
                    "headers": str(loadshape_from_file_header),
                    "column": loadshape_from_file_column
                }
                f.write(json.dumps({"loadshapes": {loadshape_name: new_loadshape_dict}}, indent=4))

    if comp_handle not in got_loadshape_points_list:
        got_loadshape_points_list.append(comp_handle)

    return loadshape_points


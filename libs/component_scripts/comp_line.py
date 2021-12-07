import os, sys
import numpy as np
import ast

# OpenDSS converter path
try:
    opendss_converter_path = os.environ['TYPHOON_OPENDSS_INTERFACE']
except:
    raise Exception("The TYPHOON_OPENDSS_INTERFACE system environment variable could not be found. " \
                    "Make sure Control Center is restarted after running install.bat in the opendss_integration folder.")

if not opendss_converter_path in sys.path:
    sys.path.append(opendss_converter_path)


def show_hide_param_inputs(mdl, container_handle, new_value, mode=None):
    mask_handle = container_handle
    comp_handle = mdl.get_parent(mask_handle)

    mode = mdl.get_property_value(mdl.prop(container_handle, "obj_mode"))

    if new_value == "Symmetrical":
        hide_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix", "coupling"]
        show_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "coupling"]
        enable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
        disable_params = []
    elif new_value == "Matrix":
        hide_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0", "coupling"]
        show_params = ["xmatrix", "rmatrix", "cmatrix", "coupling"]
        enable_params = ["xmatrix", "rmatrix", "cmatrix"]
        disable_params = []
    elif new_value == "LineCode":
        if mdl.get_property_disp_value(mdl.prop(mask_handle, "selected_object")):
            if mode == "matrix":
                show_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix", "coupling"]
                hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "coupling"]
            elif mode == "symmetrical":
                show_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0", "coupling"]
                hide_params = ["xmatrix", "rmatrix", "cmatrix", "coupling"]
            else:
                show_params = ["Load", "selected_object", "coupling"]
                hide_params = ["coupling"]
        else:
            show_params = ["Load", "selected_object", "coupling"]
            hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix", "coupling"]

        enable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]  # Workaround
        disable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]
    elif new_value == "LineGeometry":
        if mdl.get_property_disp_value(mdl.prop(mask_handle, "selected_object")):
            if mode == "matrix":
                show_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix", "coupling"]
                hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "coupling"]
            elif mode == "symmetrical":
                show_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0", "coupling"]
                hide_params = ["xmatrix", "rmatrix", "cmatrix", "coupling"]
            else:
                show_params = ["Load", "selected_object", "coupling"]
                hide_params = ["coupling"]
        else:
            show_params = ["Load", "selected_object", "coupling"]
            hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix", "coupling"]
        show_params = ["Load", "selected_object", "coupling"]
        enable_params = []
        disable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]

    for p in hide_params:
        if p:
            mdl.hide_property(mdl.prop(comp_handle, p))
    for p in show_params:
        if p:
            mdl.show_property(mdl.prop(comp_handle, p))
    for p in enable_params:
        if p:
            mdl.enable_property(mdl.prop(comp_handle, p))
    for p in disable_params:
        if p:
            mdl.disable_property(mdl.prop(comp_handle, p))


def load_line_parameters(mdl, container_handle):
    import os
    import load_object as load_obj
    import pathlib
    import json

    # Find objects file
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder_path = pathlib.Path(mdlfile_target_folder).joinpath('dss')
    fname = os.path.join(dss_folder_path, 'data', 'general_objects.json')

    input_type_prop = mdl.prop(container_handle, "input_type")
    obj_type = mdl.get_property_disp_value(input_type_prop)
    selected_object_prop = mdl.prop(container_handle, "selected_object")
    selected_object = mdl.get_property_disp_value(selected_object_prop)

    if obj_type == "LineCode":
        getname = "linecodes"
    elif obj_type == "LineGeometry":
        getname = "linegeometries"
    obj_dicts = {getname: {}}

    try:
        with open(fname, 'r') as f:
            obj_dicts = json.load(f)
    except FileNotFoundError:
        obj_dicts = None

    if obj_dicts:
        new_load_window = load_obj.LoadObject(mdl, obj_type, obj_dicts=obj_dicts, starting_object=selected_object)
    else:
        new_load_window = load_obj.LoadObject(mdl, obj_type)

    if new_load_window.exec():
        selected_object = new_load_window.selected_object
        selected_object_prop = mdl.prop(container_handle, "selected_object")
        mdl.set_property_disp_value(selected_object_prop, selected_object)
        mdl.set_property_value(selected_object_prop, selected_object)

        obj_dicts = new_load_window.obj_dicts

        selected_obj_dict = obj_dicts.get(getname).get(selected_object)

        mode = selected_obj_dict.get("mode")
        if mode == "matrix":
            param_conversion_dict = {
                "rmatrix": selected_obj_dict.get("rmatrix"),
                "xmatrix": selected_obj_dict.get("xmatrix"),
                "cmatrix": selected_obj_dict.get("cmatrix")
            }
            for param in ["rmatrix", "xmatrix", "cmatrix"]:
                param_prop = mdl.prop(container_handle, param)
                value = param_conversion_dict.get(param)
                mdl.set_property_disp_value(param_prop, value)
                mdl.set_property_value(param_prop, value)
        elif mode == "symmetrical":
            param_conversion_dict = {
                "R1": selected_obj_dict.get("r1"),
                "R0": selected_obj_dict.get("r0"),
                "dC1": selected_obj_dict.get("c1"),
                "dC0": selected_obj_dict.get("c0"),
                "X1": selected_obj_dict.get("x1"),
                "X0": selected_obj_dict.get("x0")
            }
            for param in ["R1", "R0", "dC1", "dC0", "X1", "X0"]:
                param_prop = mdl.prop(container_handle, param)
                value = param_conversion_dict.get(param)
                mdl.set_property_disp_value(param_prop, value)
                mdl.set_property_value(param_prop, value)
        mdl.set_property_value(mdl.prop(container_handle, "obj_mode"), mode)
        show_hide_param_inputs(mdl, container_handle, obj_type)

        matrix_props = ['rmatrix', 'xmatrix', 'cmatrix']
        for mat_name in ['rmatrix', 'xmatrix', 'cmatrix']:
            mat_prop = mdl.prop(container_handle, mat_name)
            mat = mdl.get_property_disp_value(mat_prop)
            try:
                if type(ast.literal_eval(mat)) == list:
                    matrix_props.remove(mat_name)
            except:
                pass

        convert_matrix_to_hil_format(mdl, container_handle, matrix_props)

def convert_matrix_to_hil_format(mdl, container_handle, matrix_props):
    global hil_format
    comp_handle = mdl.get_parent(container_handle)
    import re

    hil_matrices = {}
    prop_dict = {'rmatrix': 'd_R', 'xmatrix': 'd_X', 'cmatrix': 'd_C'}
    for mat_name in matrix_props:
        mat_prop = mdl.prop(container_handle, mat_name)
        mat = mdl.get_property_disp_value(mat_prop)
        if re.match('[^\n\|\s]+', mat):
            re_str = '([+-]?[0-9]+[.]?[0-9]*[eE]?[+-]?[0-9]*|[+-]?[0-9]*[.]?[0-9]+[eE]?[+-]?[0-9]*)'
            matrix_elements = re.findall(re_str, mat)

            if mat_name == 'cmatrix':
                for idx, _ in enumerate(matrix_elements):
                    float_val = float(matrix_elements[idx])*1e-9
                    matrix_elements[idx] = '{: .4e}'.format(float_val)

            if not mat.count('|') == 2:
                raise Exception(f"Matrix definition on {mdl.get_name(comp_handle)} is not supported (not 3x3)")

            hil_format = []
            for idx in range(0, 9, 3):
                new_row = ", ".join(matrix_elements[idx:idx + 3])
                hil_format.append(new_row)

            hil_matrices[mat_name] = f'[[{"], [".join(hil_format)}]]'

    for mat_name in ['rmatrix', 'xmatrix', 'cmatrix']:
        if mat_name in matrix_props:
            mdl.set_property_value(mdl.prop(container_handle, prop_dict.get(mat_name)),
                                   hil_matrices[mat_name])
        else:
            mat_prop = mdl.prop(container_handle, mat_name)
            mdl.set_property_value(mdl.prop(container_handle, prop_dict.get(mat_name)),
                                   mdl.get_property_disp_value(mat_prop))
            if mat_name == 'cmatrix':
                prop_handle = mdl.prop(container_handle, "d_C")
                cap_array = np.array(mdl.get_property_value(prop_handle)) * 1e-9
                mdl.set_property_value(prop_handle, cap_array.tolist())

def configure_cable(mdl, container_handle):

    comp_handle = mdl.get_parent(container_handle)
    mode = mdl.get_property_value(mdl.prop(container_handle, "obj_mode"))
    input_type = mdl.get_property_value(mdl.prop(container_handle, "input_type"))
    Length = mdl.get_property_value(mdl.prop(container_handle, "Length"))
    BaseFreq = mdl.get_property_value(mdl.prop(container_handle, "BaseFreq"))
    w = 2 * np.pi * BaseFreq
    transmission_line = mdl.get_item("TL", parent=comp_handle)

    mdl.set_property_value(mdl.prop(container_handle, "Length"), Length)
    mdl.set_property_value(mdl.prop(container_handle, "Len"), Length)
    mdl.set_property_value(mdl.prop(container_handle, "Fr"), BaseFreq)

    if input_type == "Symmetrical" or (input_type == "LineCode" and mode == "symmetrical"):

        R0 = mdl.get_property_value(mdl.prop(container_handle, "R0"))
        R1 = mdl.get_property_value(mdl.prop(container_handle, "R1"))
        X0 = mdl.get_property_value(mdl.prop(container_handle, "X0"))
        X1 = mdl.get_property_value(mdl.prop(container_handle, "X1"))
        dC0 = mdl.get_property_value(mdl.prop(container_handle, "dC0"))
        dC1 = mdl.get_property_value(mdl.prop(container_handle, "dC1"))
        L1 = X1 / w
        L0 = X0 / w
        C1 = dC1 * 1e-9
        C0 = dC0 * 1e-9

        coupling = mdl.get_property_value(mdl.prop(container_handle, "coupling"))
        if not coupling == "None":

            Rseq = np.array(
                [[R0, 0, 0],
                 [0, R1, 0],
                 [0, 0, R1]])
            Xseq = np.array(
                [[X0, 0, 0],
                 [0, X1, 0],
                 [0, 0, X1]])

            Zseq = Rseq + 1j * Xseq

            [R0n, R1n, X0n, X1n, Xcoup] = compute_sequence_values(mdl, container_handle, Zseq, "symmetrical")
            Lcoup = Xcoup / w * Length
            L1n = X1n / w
            L0n = X0n / w
            comp_handle = mdl.get_parent(container_handle)
            coup = mdl.get_item("CC", parent=comp_handle, item_type="masked_component")
            if coup:
                cc_inductance_prop = mdl.prop(coup, "inductance")
                mdl.set_property_value(cc_inductance_prop, Lcoup)
                mdl.info(f'Setting {mdl.get_name(comp_handle)}\'s coupling inductance to {"{:.4e}".format(Lcoup)}H')
            d_R = [[R0n, 0, 0], [0, R1n, 0], [0, 0, R1n]]
            d_L = [[L0n, 0, 0], [0, L1n, 0], [0, 0, L1n]]
            d_C = [[C0, 0, 0], [0, C1, 0], [0, 0, C1]]
        else:
            d_R = [[R0, 0, 0], [0, R1, 0], [0, 0, R1]]
            d_L = [[L0, 0, 0], [0, L1, 0], [0, 0, L1]]
            d_C = [[C0, 0, 0], [0, C1, 0], [0, 0, C1]]

        mdl.set_property_value(mdl.prop(container_handle, "d_R"), d_R)
        mdl.set_property_value(mdl.prop(container_handle, "d_L"), d_L)
        mdl.set_property_value(mdl.prop(container_handle, "d_C"), d_C)
        mdl.set_property_value(mdl.prop(container_handle, "C1"), C1)
        mdl.set_property_value(mdl.prop(container_handle, "C0"), C0)
        mdl.set_property_value(mdl.prop(transmission_line, "model_def"), "Sequence")
        mdl.set_property_value(mdl.prop(transmission_line, "Length_metric"), "Length")
        mdl.set_property_value(mdl.prop(transmission_line, "Frequency"), "BaseFreq")
        mdl.set_property_value(mdl.prop(transmission_line, "R_sequence_metric"), d_R)
        mdl.set_property_value(mdl.prop(transmission_line, "L_sequence_metric"), d_L)
        mdl.set_property_value(mdl.prop(transmission_line, "C_sequence_metric"), d_C)


    elif input_type == "Matrix" or (input_type == "LineCode" and mode == "matrix"):

        matrix_props = ['rmatrix', 'xmatrix', 'cmatrix']
        for mat_name in ['rmatrix', 'xmatrix', 'cmatrix']:
            mat_prop = mdl.prop(container_handle, mat_name)
            mat = mdl.get_property_disp_value(mat_prop)
            try:
                evaluated = ast.literal_eval(mat)
                if type(evaluated) == list:
                    matrix_props.remove(mat_name)
            except:
                pass

        convert_matrix_to_hil_format(mdl, container_handle, matrix_props)

        # Convert to inductance
        Xarray = np.array(mdl.get_property_value(mdl.prop(container_handle, "d_X")))
        BaseFreq = mdl.get_property_value(mdl.prop(container_handle, "BaseFreq"))
        w = 2 * np.pi * BaseFreq
        Larray = Xarray/w
        mdl.set_property_value(mdl.prop(container_handle, "d_L"), Larray.tolist())

        # RLC model
        mdl.set_property_value(mdl.prop(transmission_line, "model_def"), "RLC")
        mdl.set_property_value(mdl.prop(transmission_line, "Length_metric"), "Length")
        mdl.set_property_value(mdl.prop(transmission_line, "Frequency"), "BaseFreq")
        mdl.set_property_value(mdl.prop(transmission_line, "R_metric"), d_R)
        mdl.set_property_value(mdl.prop(transmission_line, "L_metric"), d_L)
        mdl.set_property_value(mdl.prop(transmission_line, "C_metric"), d_C)

        coupling = mdl.get_property_value(mdl.prop(container_handle, "coupling"))
        if not coupling == "None":
            mdl.info("Coupling not implemented for matrix-type parameters")

    mdl.set_property_value(mdl.prop(container_handle, "Length"), Length)
    mdl.set_property_value(mdl.prop(container_handle, "Len"), Length)
    mdl.set_property_value(mdl.prop(container_handle, "Fr"), BaseFreq)

def compute_sequence_values(mdl, mask_handle, Zseq, mode):

    Length = mdl.get_property_value(mdl.prop(mask_handle, "Length"))
    BaseFreq = mdl.get_property_value(mdl.prop(mask_handle, "BaseFreq"))
    w = 2 * np.pi * BaseFreq

    alpha = complex(np.cos(-120.0 * np.pi / 180.0), np.sin(-120.0 * np.pi / 180.0))
    A = np.matrix([[1, 1, 1],
                   [1, alpha ** 2.0, alpha],
                   [1, alpha, alpha ** 2.0]])  # sequence to phase components transf. matrix
    Zabc = np.dot(np.dot(A, Zseq), A.I)
    Rabc = Zabc.real
    Xabc = Zabc.imag
    Xabc_min = min(np.diag(Xabc))
    digits = 10

    X_ratio = 1e-3
    Xcoup = X_ratio * Xabc_min

    if Xcoup / w * Length > 100e-6:
        Xcoup = 100e-6*w/Length
    elif Xcoup / w * Length < 1e-6:
        Xcoup = 1e-6*w/Length

    Xcoup_abc = Xcoup * np.eye(3)
    Xabcn = Xabc - Xcoup_abc
    Zabc = Rabc + 1j * Xabcn
    Zseq = np.dot(np.dot(A.I, Zabc), A).round(digits)
    Rseq = Zseq.real
    Xseq = Zseq.imag

    R0 = Rseq[0, 0]
    R1 = Rseq[1, 1]
    X0 = Xseq[0, 0]
    X1 = Xseq[1, 1]

    if mode == "symmetrical":
        return [R0, R1, X0, X1, Xcoup]
    elif mode == "matrix":
        return [Rseq, Xseq, Xcoup]

def toggle_coupling(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Inner components
    coupling = mdl.get_item("CC", parent=comp_handle)
    transmission_line = mdl.get_item("TL", parent=comp_handle)
    port_A1 = mdl.get_item("A1", parent=comp_handle, item_type="port")
    port_B1 = mdl.get_item("B1", parent=comp_handle, item_type="port")
    port_C1 = mdl.get_item("C1", parent=comp_handle, item_type="port")
    port_A2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
    port_B2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
    port_C2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
    port_N = mdl.get_item("N", parent=comp_handle, item_type="port")
    connTLN = mdl.get_item("ConnTLN1", parent=comp_handle, item_type="connection")
    portN2 = mdl.get_item("N2", parent=comp_handle, item_type="port")

    coupling_prop = mdl.prop(comp_handle, "coupling")
    coupling_type = mdl.get_property_value(coupling_prop)
    dCp = mdl.prop(comp_handle, "dC1")
    dCp_value = mdl.get_property_value(dCp)
    dCz = mdl.prop(comp_handle, "dC0")
    dCz_value = mdl.get_property_value(dCz)
    RL_active = 0

    if str(dCp_value) == "0" and str(dCz_value) == "0":
        mdl.delete_item(mdl.find_connections(port_A1)[0])
        mdl.delete_item(mdl.find_connections(port_B1)[0])
        mdl.delete_item(mdl.find_connections(port_C1)[0])
        mdl.delete_item(mdl.find_connections(port_A2)[0])
        mdl.delete_item(mdl.find_connections(port_B2)[0])
        mdl.delete_item(mdl.find_connections(port_C2)[0])
        if port_N:
            mdl.delete_item(port_N)
        RL_active = 1
        mdl.set_property_value(mdl.prop(transmission_line, "model"), "RL coupled")
        mdl.create_connection(port_A1, mdl.term(transmission_line, "a_in"))
        mdl.create_connection(port_B1, mdl.term(transmission_line, "b_in"))
        mdl.create_connection(port_C1, mdl.term(transmission_line, "c_in"))
        if coupling:
            mdl.create_connection(port_A2, mdl.term(coupling, "a_out"))
            mdl.create_connection(port_B2, mdl.term(coupling, "b_out"))
            mdl.create_connection(port_C2, mdl.term(coupling, "c_out"))
        else:
            mdl.create_connection(port_A2, mdl.term(transmission_line, "a_out"))
            mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
            mdl.create_connection(port_C2, mdl.term(transmission_line, "c_out"))
    else:
        mdl.delete_item(mdl.find_connections(port_A1)[0])
        mdl.delete_item(mdl.find_connections(port_B1)[0])
        mdl.delete_item(mdl.find_connections(port_C1)[0])
        mdl.delete_item(mdl.find_connections(port_A2)[0])
        mdl.delete_item(mdl.find_connections(port_B2)[0])
        mdl.delete_item(mdl.find_connections(port_C2)[0])
        if not port_N:
            port_N = mdl.create_port(
                name="N",
                parent=comp_handle,
                kind="pe",
                terminal_position=("bottom", "left"),
                position=(7728, 8144)
            )
        RL_active = 0
        mdl.set_property_value(mdl.prop(transmission_line, "model"), "PI")
        mdl.create_connection(port_A1, mdl.term(transmission_line, "a_in"))
        mdl.create_connection(port_B1, mdl.term(transmission_line, "b_in"))
        mdl.create_connection(port_C1, mdl.term(transmission_line, "c_in"))
        # mdl.delete_item(mdl.find_connections(port_N)[0])
        if coupling:
            mdl.create_connection(port_A2, mdl.term(coupling, "a_out"))
            mdl.create_connection(port_B2, mdl.term(coupling, "b_out"))
            mdl.create_connection(port_C2, mdl.term(coupling, "c_out"))
        else:
            mdl.create_connection(port_A2, mdl.term(transmission_line, "a_out"))
            mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
            mdl.create_connection(port_C2, mdl.term(transmission_line, "c_out"))
        if not connTLN:
            mdl.create_connection(port_N, mdl.term(transmission_line, "gnd"), name="ConnTLN1")

    if coupling_type == "None":
        if coupling:
            mdl.delete_item(coupling)
            if portN2:
                mdl.delete_item(portN2)
            # mdl.delete_item(mdl.get_item("N2", parent=comp_handle, item_type="port"))
            mdl.create_connection(port_A2, mdl.term(transmission_line, "a_out"))
            mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
            mdl.create_connection(port_C2, mdl.term(transmission_line, "c_out"))
    elif coupling_type == "Device coupling" or coupling_type == "Core coupling":
        if coupling:  # If there is a coupling of a different type, delete it
            mdl.delete_item(coupling)

        else:
            # Connections
            mdl.delete_item(mdl.find_connections(port_A2)[0])
            mdl.delete_item(mdl.find_connections(port_B2)[0])
            mdl.delete_item(mdl.find_connections(port_C2)[0])

        if coupling_type == "Device coupling":
            if RL_active == 0:
                coup_component_type = "core/Four Phase TLM Device Coupling"
            else:
                coup_component_type = "core/Three Phase TLM Device Coupling"
        elif coupling_type == "Core coupling":
            if RL_active == 0:
                coup_component_type = "core/Four Phase TLM Core Coupling"
            else:
                coup_component_type = "core/Three Phase TLM Core Coupling"

        portN2 = mdl.get_item("N2", parent=comp_handle, item_type="port")

        if RL_active == 1:
            if portN2:
                mdl.delete_item(portN2)
        else:
            if not portN2:
                portN2 = mdl.create_port(
                    name="N2",
                    parent=comp_handle,
                    kind="pe",
                    terminal_position=("bottom", "right"),
                    position=(8008, 8224),
                    rotation="down"
                )

        try:
            coup = mdl.create_component(
                coup_component_type,
                name="CC",
                parent=comp_handle,
                position=(7944, 8082)
            )
        except:
            mdl.create_connection(port_A2, mdl.term(transmission_line, "a_out"))
            mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
            mdl.create_connection(port_C2, mdl.term(transmission_line, "c_out"))
            mdl.delete_item(portN2)
            mdl.info("It was not possible to create the Device Coupling because the component is not" +
                       " available in the library. Make sure the HIL device model and configuration are properly set.")
            mdl.set_property_value(coupling_prop, "Core coupling")
        else:
            mdl.create_connection(port_A2, mdl.term(coup, "a_out"))
            mdl.create_connection(port_B2, mdl.term(coup, "b_out"))
            mdl.create_connection(port_C2, mdl.term(coup, "c_out"))
            if RL_active == 0:
                mdl.create_connection(portN2, mdl.term(coup, "d_out"))
            mdl.create_connection(mdl.term(coup, "a_in"), mdl.term(transmission_line, "a_out"))
            mdl.create_connection(mdl.term(coup, "b_in"), mdl.term(transmission_line, "b_out"))
            mdl.create_connection(mdl.term(coup, "c_in"), mdl.term(transmission_line, "c_out"))
            if RL_active == 0:
                mdl.create_connection(mdl.term(coup, "d_in"), mdl.term(transmission_line, "gnd"))

    else:  # Old model was loaded
        mdl.set_property_value(coupling_prop, "None")

def toggle_frequency_prop(mdl, mask_handle, init=False):
    frequency_prop = mdl.prop(mask_handle, "BaseFreq")
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

    frequency_prop = mdl.prop(mask_handle, "BaseFreq")
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

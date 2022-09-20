import numpy as np
import ast
import re


def show_hide_param_inputs(mdl, container_handle, new_value, mode=None):
    mask_handle = container_handle
    comp_handle = mdl.get_parent(mask_handle)

    mode = mdl.get_property_value(mdl.prop(container_handle, "obj_mode"))
    phase_num = mdl.get_property_value(mdl.prop(container_handle, "phases"))

    if new_value == "Symmetrical":
        hide_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix"]
        show_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
        enable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
        disable_params = []
    elif new_value == "Matrix":
        hide_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0"]
        show_params = ["xmatrix", "rmatrix", "cmatrix"]
        enable_params = ["xmatrix", "rmatrix", "cmatrix"]
        disable_params = []
    elif new_value == "LineCode":
        if mdl.get_property_disp_value(mdl.prop(mask_handle, "selected_object")):
            if mode == "matrix":
                show_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix"]
                hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "coupling"]
            elif mode == "symmetrical":
                show_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0"]
                hide_params = ["xmatrix", "rmatrix", "cmatrix"]
            else:
                show_params = ["Load", "selected_object"]
                hide_params = []
        else:
            show_params = ["Load", "selected_object"]
            hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]

        enable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]  # Workaround
        disable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]
    elif new_value == "LineGeometry":
        if mdl.get_property_disp_value(mdl.prop(mask_handle, "selected_object")):
            if mode == "matrix":
                show_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix"]
                hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
            elif mode == "symmetrical":
                show_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0"]
                hide_params = ["xmatrix", "rmatrix", "cmatrix"]
            else:
                show_params = ["Load", "selected_object"]
                hide_params = []
        else:
            show_params = ["Load", "selected_object"]
            hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]
        show_params = ["Load", "selected_object"]
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


def show_hide_param_phases(mdl, container_handle, new_value, mode=None):
    mask_handle = container_handle
    comp_handle = mdl.get_parent(mask_handle)

    mode = mdl.get_property_value(mdl.prop(container_handle, "obj_mode"))
    input_type = mdl.get_property_disp_value(mdl.prop(container_handle, "input_type"))

    if input_type == "Symmetrical":
        hide_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix"]
        show_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
        enable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
        disable_params = []
    elif input_type == "Matrix":
        hide_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0"]
        show_params = ["xmatrix", "rmatrix", "cmatrix"]
        enable_params = ["xmatrix", "rmatrix", "cmatrix"]
        disable_params = []
    elif input_type == "LineCode":
        if mdl.get_property_disp_value(mdl.prop(mask_handle, "selected_object")):
            if mode == "matrix":
                show_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix"]
                hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
            elif mode == "symmetrical":
                show_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0"]
                hide_params = ["xmatrix", "rmatrix", "cmatrix"]
            else:
                show_params = ["Load", "selected_object"]
                hide_params = []
        else:
            show_params = ["Load", "selected_object"]
            hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]

        enable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]  # Workaround
        disable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]
    # elif input_type == "LineGeometry":
    #     if mdl.get_property_disp_value(mdl.prop(mask_handle, "selected_object")):
    #         if mode == "matrix":
    #             show_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix", "coupling"]
    #             hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "coupling"]
    #         elif mode == "symmetrical":
    #             show_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0", "coupling"]
    #             hide_params = ["xmatrix", "rmatrix", "cmatrix", "coupling"]
    #         else:
    #             show_params = ["Load", "selected_object", "coupling"]
    #             hide_params = ["coupling"]
    #     else:
    #         show_params = ["Load", "selected_object", "coupling"]
    #         hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix", "coupling"]
    #     show_params = ["Load", "selected_object", "coupling"]
    #     enable_params = []
    #     disable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]

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
    import sys
    import pathlib

    try:
        from tse_to_opendss.tse2tpt_base_converter import tse2tpt
        import tse_to_opendss
    except:
        # If running from development folder instead of installed package
        dss_module_folder = str(pathlib.Path(__file__).parent.parent.parent.parent)
        if not dss_module_folder in sys.path:
            sys.path.append(dss_module_folder)

        from tse_to_opendss.tse2tpt_base_converter import tse2tpt
        import tse_to_opendss

    import tse_to_opendss.thcc_libs.gui_scripts.load_object as load_obj

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
                "phases": selected_obj_dict.get("nphases"),
                "rmatrix": selected_obj_dict.get("rmatrix"),
                "xmatrix": selected_obj_dict.get("xmatrix"),
                "cmatrix": selected_obj_dict.get("cmatrix")
            }
            for param in ["phases", "rmatrix", "xmatrix", "cmatrix"]:
                param_prop = mdl.prop(container_handle, param)
                value = param_conversion_dict.get(param)
                value = "" if not value else value
                mdl.set_property_disp_value(param_prop, value)
                mdl.set_property_value(param_prop, value)
        elif mode == "symmetrical":
            param_conversion_dict = {
                "R1": selected_obj_dict.get("r1"),
                "R0": selected_obj_dict.get("r0"),
                "dC1": selected_obj_dict.get("c1"),
                "dC0": selected_obj_dict.get("c0"),
                "X1": selected_obj_dict.get("x1"),
                "X0": selected_obj_dict.get("x0"),
                "phases": "3"
            }
            for param in ["R1", "R0", "dC1", "dC0", "X1", "X0", "phases"]:
                param_prop = mdl.prop(container_handle, param)
                value = param_conversion_dict.get(param)
                value = "" if not value else value
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

    comp_handle = mdl.get_parent(container_handle)
    phases = mdl.prop(container_handle, "phases")
    phase_num = int(mdl.get_property_value(phases))
    import re

    hil_matrices = {}
    prop_dict = {'rmatrix': 'd_R', 'xmatrix': 'd_X', 'cmatrix': 'd_C'}
    for mat_name in matrix_props:
        mat_prop = mdl.prop(container_handle, mat_name)
        mat = mdl.get_property_disp_value(mat_prop)

        mod_mat = mat.strip(" [](){}\"\'")
        matrix_rows = mod_mat.split("|")

        dummy_matrix = "["
        for row_number in range(len(matrix_rows) - 1):
            dummy_matrix += f'[{matrix_rows[row_number].strip()}], '
        dummy_matrix += f'[{matrix_rows[-1].strip()}]]'
        dummy_matrix = re.sub(r"[\s,]+", ", ", dummy_matrix)
        try:
            evaluated_matrix = ast.literal_eval(dummy_matrix)

        except ValueError:
            raise Exception(f"Invalid matrix input on {comp_handle}, {mat_name}")

        # truncate number of lines and the size of the last line to the number of phases
        if len(evaluated_matrix) > phase_num:
            mdl.warning(f"The matrix {mat_name} on {mdl.get_name(comp_handle)} was truncated in rows to the number"
                        f" of phases. The last row was also truncated to the number of phases",
                        context=mdl.prop(comp_handle, mat_name))
            evaluated_matrix = evaluated_matrix[:phase_num]
            evaluated_matrix[-1] = evaluated_matrix[-1][:phase_num]

        # Check if the matrix input is on the lower triangular form
        if not all([len(row) >= n + 1 for n, row in enumerate(evaluated_matrix)]):
            raise Exception(
                f"One or more rows of the matrix {mat_name} on {mdl.get_name(comp_handle)} have dimension "
                f"that does not match with the minimum entries required for a lower triangular matrix.",
                context=mdl.prop(comp_handle, mat_name))
        elif any([len(row) < len(evaluated_matrix[-1]) for row in evaluated_matrix]):
            # Assume lower triangular matrix form
            if any([len(row) > n + 1 for n, row in enumerate(evaluated_matrix)]):
                # report row truncation to the lower triangular form
                mdl.warning(f"Due to the row dimensions, the matrix \"{mat_name}\" on {mdl.get_name(comp_handle)} "
                            f"is assumed to be writen on the lower triangular form, but one or more rows have "
                            f"dimension greater than the number of entries required by the lower triangular form. "
                            f"Truncating the rows of the final matrix",
                            context=mdl.prop(comp_handle, mat_name))
            for i in range(phase_num - 1):
                # Drop all entries above the matrix diagonal
                row = evaluated_matrix[i][:i + 1]
                for j in range(i, phase_num - 1):
                    # add the entries below the diagonal to the symmetrical places above the diagonal
                    row.append(evaluated_matrix[j + 1][i])
                # overwrite original row with the new full row
                evaluated_matrix[i] = row
        elif any([len(row) > phase_num for row in evaluated_matrix]):
            # report row truncation to number of phases
            mdl.warning(f"The matrix \"{mat_name}\" on {mdl.get_name(comp_handle)} contains one or more rows "
                        f"with dimension greater than the number of phases. Truncating the rows to "
                        f"the number of phases",
                        context=mdl.prop(comp_handle, mat_name))
            # Truncate the matrix row size to contain a number of entries equal to the number of phases
            for i in range(phase_num):
                evaluated_matrix[i] = evaluated_matrix[i][:phase_num]

        if mat_name == "cmatrix":
            # Convert cmatrix unit from nF to F
            evaluated_matrix = [[item * 1e-9 for item in row] for row in evaluated_matrix]

        if len(evaluated_matrix) == 1:
            # make the list into a single bracket list (instead of a list of list)
            evaluated_matrix = evaluated_matrix[0]

        dummy_matrix = str(evaluated_matrix)
        hil_matrices[mat_name] = dummy_matrix

    for mat_name in ['rmatrix', 'xmatrix', 'cmatrix']:
        if mat_name in matrix_props:
            mdl.set_property_value(mdl.prop(container_handle, prop_dict.get(mat_name)),
                                   hil_matrices.get(mat_name))
        else:
            if mat_name == 'cmatrix':
                prop_handle = mdl.prop(container_handle, "d_C")
                cap_array = np.array(mdl.get_property_value(prop_handle)) * 1e-9
                mdl.set_property_value(prop_handle, cap_array.tolist())
            else:
                mat_prop = mdl.prop(container_handle, mat_name)
                mdl.set_property_value(mdl.prop(container_handle, prop_dict.get(mat_name)),
                                       mdl.get_property_disp_value(mat_prop))


def configure_cable(mdl, container_handle):

    comp_handle = mdl.get_parent(container_handle)
    mode = mdl.get_property_value(mdl.prop(container_handle, "obj_mode"))
    input_type = mdl.get_property_value(mdl.prop(container_handle, "input_type"))
    Length = mdl.get_property_value(mdl.prop(container_handle, "Length"))
    BaseFreq = mdl.get_property_value(mdl.prop(container_handle, "BaseFreq"))
    phase_num = mdl.get_property_value(mdl.prop(container_handle, "phases"))
    w = 2 * np.pi * BaseFreq
    transmission_line = mdl.get_item("TL", parent=comp_handle)
    pi_section = mdl.get_item("pisec", parent=comp_handle)

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

    elif input_type == "Matrix" or (input_type == "LineCode" and mode == "matrix"):
        # Convert matrix inputs to python format
        matrix_props = ['rmatrix', 'xmatrix', 'cmatrix']

        convert_matrix_to_hil_format(mdl, container_handle, matrix_props)

        if phase_num == "1":
            # R1 = mdl.get_property_value(mdl.prop(container_handle, "R1"))
            # X1 = mdl.get_property_value(mdl.prop(container_handle, "X1"))
            # dC1 = mdl.get_property_value(mdl.prop(container_handle, "dC1"))
            R1 = mdl.get_property_value(mdl.prop(container_handle, "d_R"))
            X1 = mdl.get_property_value(mdl.prop(container_handle, "d_X"))
            C1 = mdl.get_property_value(mdl.prop(container_handle, "d_C"))

            L1 = X1 / w

            R1_one = R1 * Length
            L1_one = L1 * Length
            C1_one = C1 * Length

            mdl.set_property_value(mdl.prop(pi_section, "R"), R1_one)
            mdl.set_property_value(mdl.prop(pi_section, "L"), L1_one)
            mdl.set_property_value(mdl.prop(pi_section, "C"), C1_one)
            mdl.set_property_value(mdl.prop(container_handle, "C1"), C1)
            mdl.set_property_value(mdl.prop(container_handle, "d_L"), L1_one)
        else:
            # Convert Xarray to inductance
            Xarray = np.array(mdl.get_property_value(mdl.prop(container_handle, "d_X")))
            Larray = Xarray/w
            mdl.set_property_value(mdl.prop(container_handle, "d_L"), Larray.tolist())

            # RLC model
            mdl.set_property_value(mdl.prop(transmission_line, "model_def"), "RLC")
            mdl.set_property_value(mdl.prop(transmission_line, "Length_metric"), "Length")
            mdl.set_property_value(mdl.prop(transmission_line, "Frequency"), "BaseFreq")

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


def toggle_coupling(mdl, mask_handle, created_ports):
    comp_handle = mdl.get_parent(mask_handle)

    # Inner components
    coupling = mdl.get_item("CC", parent=comp_handle)
    transmission_line = mdl.get_item("TL", parent=comp_handle)
    pi_section = mdl.get_item("pisec", parent=comp_handle)

    port_N = mdl.get_item("N", parent=comp_handle, item_type="port")
    portN2 = mdl.get_item("N2", parent=comp_handle, item_type="port")

    input_type_prop = mdl.prop(comp_handle, "input_type")
    input_type = mdl.get_property_value(input_type_prop)
    mode_prop = mdl.prop(comp_handle, "obj_mode")
    mode = mdl.get_property_value(mode_prop)
    phases_prop = mdl.prop(comp_handle, "phases")
    phase_num = mdl.get_property_value(phases_prop)

    if phase_num == "1":
        num_phases = "2"
    else:
        num_phases = phase_num
    coupling_prop = mdl.prop(comp_handle, "coupling")
    coupling_type = mdl.get_property_value(coupling_prop)
    dCp = mdl.prop(comp_handle, "dC1")
    dCp_value = mdl.get_property_value(dCp)
    dCz = mdl.prop(comp_handle, "dC0")
    dCz_value = mdl.get_property_value(dCz)
    RL_active = 0
    RL_section = 0

    if not phase_num == "1":
        if input_type == "Matrix" or (input_type == "LineCode" and mode == "matrix"):
            cmtx_prop = mdl.prop(comp_handle, "cmatrix")
            cmtx = mdl.get_property_disp_value(cmtx_prop)
            cmtx_sum = 0
            if re.match(r'[^\n\|\s]+', cmtx):
                re_str = '([+-]?[0-9]+[.]?[0-9]*[eE]?[+-]?[0-9]*|[+-]?[0-9]*[.]?[0-9]+[eE]?[+-]?[0-9]*)'
                cmtx_elements = re.findall(re_str, cmtx)
            for idx, _ in enumerate(cmtx_elements):
                cmtx_sum = cmtx_sum + float(cmtx_elements[idx])

            if cmtx_sum == 0:
                RL_section = 1
            else:
                RL_section = 0
        else:
            dCp = mdl.prop(comp_handle, "dC1")
            dCp_value = mdl.get_property_value(dCp)
            dCz = mdl.prop(comp_handle, "dC0")
            dCz_value = mdl.get_property_value(dCz)
            if str(dCp_value) == "0" and str(dCz_value) == "0":
                RL_section = 1
            else:
                RL_section = 0

    if input_type == "Matrix" or (input_type == "LineCode" and mode == "matrix"):
        mdl.set_property_value(mdl.prop(transmission_line, "model_def"), "RLC")
        mdl.set_property_value(mdl.prop(transmission_line, "num_of_phases"), num_phases)
    else:
        mdl.set_property_value(mdl.prop(transmission_line, "num_of_phases"), num_phases)

    ###########
    conn1phin = mdl.get_item("Conn_1ph_gnd_in", parent=comp_handle, item_type="connection")
    conn1phout = mdl.get_item("Conn_1ph_gnd_out", parent=comp_handle, item_type="connection")

    if phase_num == "3":
        if conn1phin:
            mdl.delete_item(conn1phin)
        if conn1phout:
            mdl.delete_item(conn1phout)
    elif phase_num == "2":
        if conn1phin:
            mdl.delete_item(conn1phin)
        if conn1phout:
            mdl.delete_item(conn1phout)

    port_A2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
    port_B2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
    port_C2 = mdl.get_item("C2", parent=comp_handle, item_type="port")

    if coupling_type == "None":
        if coupling:
            mdl.delete_item(coupling)
            if portN2:
                mdl.delete_item(portN2)

            mdl.create_connection(port_A2, mdl.term(transmission_line, "a_out"))
            if phase_num == "1":
                conn1phout = mdl.get_item("Conn_1ph_gnd_out", parent=comp_handle, item_type="connection")
                if not conn1phout:
                    mdl.create_connection(port_N, mdl.term(transmission_line, "b_out"), name="Conn_1ph_gnd_out")
            elif phase_num == "2":
                mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
            elif phase_num == "3":
                mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
                mdl.create_connection(port_C2, mdl.term(transmission_line, "c_out"))
    elif coupling_type == "Device coupling" or coupling_type == "Core coupling":
        if coupling:  # If there is a coupling of a different type, delete it
            mdl.delete_item(coupling)

        else:
            # Connections
            if port_A2:
                if not len(mdl.find_connections(port_A2)) == 0:
                    mdl.delete_item(mdl.find_connections(port_A2)[0])

            if port_B2:
                if not len(mdl.find_connections(port_B2)) == 0:
                    mdl.delete_item(mdl.find_connections(port_B2)[0])

            if port_C2:
                if not len(mdl.find_connections(port_C2)) == 0:
                    mdl.delete_item(mdl.find_connections(port_C2)[0])

        if coupling_type == "Device coupling":
            if RL_active == 0:
                coup_component_type = "core/Four Phase TLM Device Coupling"
                if phase_num == "2":
                    coup_component_type = "core/Three Phase TLM Device Coupling"
                elif phase_num == "1":
                    coup_component_type = "core/Single Phase TLM Device Coupling"
            else:
                coup_component_type = "core/Three Phase TLM Device Coupling"
                if phase_num == "2":
                    coup_component_type = "core/Single Phase TLM Device Coupling"
                elif phase_num == "1":
                    coup_component_type = "core/Single Phase TLM Device Coupling"
        elif coupling_type == "Core coupling":
            if RL_active == 0:
                coup_component_type = "core/Four Phase TLM Core Coupling"
                if phase_num == "2":
                    coup_component_type = "core/Three Phase TLM Core Coupling"
                elif phase_num == "1":
                    coup_component_type = "core/Single Phase TLM Core Coupling"
            else:
                coup_component_type = "core/Three Phase TLM Core Coupling"
                if phase_num == "2":
                    coup_component_type = "core/Single Phase TLM Core Coupling"
                elif phase_num == "1":
                    coup_component_type = "core/Single Phase TLM Core Coupling"

        portN2 = mdl.get_item("N2", parent=comp_handle, item_type="port")

        try:
            coup = mdl.create_component(
                coup_component_type,
                name="CC",
                parent=comp_handle,
                position=(7944, 8082)
            )
        except:
            mdl.create_connection(port_A2, mdl.term(transmission_line, "a_out"))
            if phase_num == "1":
                conn1phout = mdl.get_item("Conn_1ph_gnd_out", parent=comp_handle, item_type="connection")
                if not conn1phout:
                    mdl.create_connection(port_N, mdl.term(transmission_line, "b_out"), name="Conn_1ph_gnd_out")
            elif phase_num == "2":
                mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
            elif phase_num == "3":
                mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
                mdl.create_connection(port_C2, mdl.term(transmission_line, "c_out"))
            mdl.delete_item(portN2)
            mdl.info("It was not possible to create the Device Coupling because the component is not" +
                       " available in the library. Make sure the HIL device model and configuration are properly set.")
            mdl.set_property_value(coupling_prop, "Core coupling")
        else:
            mdl.create_connection(port_A2, mdl.term(coup, "a_out"))
            if phase_num == "2":
                mdl.create_connection(port_B2, mdl.term(coup, "b_out"))
            elif phase_num == "3":
                mdl.create_connection(port_B2, mdl.term(coup, "b_out"))
                mdl.create_connection(port_C2, mdl.term(coup, "c_out"))

            if RL_active == 0:
                if phase_num == "3":
                    mdl.create_connection(portN2, mdl.term(coup, "d_out"))
                elif phase_num == "2":
                    mdl.create_connection(portN2, mdl.term(coup, "c_out"))
                elif phase_num == "1":
                    mdl.create_connection(portN2, mdl.term(coup, "b_out"))

            mdl.create_connection(mdl.term(coup, "a_in"), mdl.term(transmission_line, "a_out"))
            if phase_num == "1":
                mdl.create_connection(mdl.term(coup, "b_in"), mdl.term(transmission_line, "b_out"))
            elif phase_num == "2":
                mdl.create_connection(mdl.term(coup, "b_in"), mdl.term(transmission_line, "b_out"))
            elif phase_num == "3":
                mdl.create_connection(mdl.term(coup, "b_in"), mdl.term(transmission_line, "b_out"))
                mdl.create_connection(mdl.term(coup, "c_in"), mdl.term(transmission_line, "c_out"))

            if RL_active == 0 and mdl.get_property_value(mdl.prop(transmission_line, "model")) == "PI":
                if phase_num == "3":
                    mdl.create_connection(mdl.term(coup, "d_in"), mdl.term(transmission_line, "gnd"))
                elif phase_num == "2":
                    mdl.create_connection(mdl.term(coup, "c_in"), mdl.term(transmission_line, "gnd"))
                elif phase_num == "1":
                    mdl.create_connection(mdl.term(coup, "b_in"), mdl.term(transmission_line, "gnd"))
            elif RL_active == 0 and mdl.get_property_value(mdl.prop(transmission_line, "model")) == "RL coupled":
                if phase_num == "3":
                    mdl.create_connection(mdl.term(coup, "d_in"), port_N, name="ConnTLN2")
                elif phase_num == "2":
                    mdl.create_connection(mdl.term(coup, "c_in"), port_N, name="ConnTLN2")
                elif phase_num == "1":
                    mdl.create_connection(mdl.term(coup, "b_in"), port_N, name="ConnTLN2")

    else:  # Old model was loaded
        mdl.set_property_value(coupling_prop, "None")

    port_A1 = mdl.get_item("A1", parent=comp_handle, item_type="port")
    port_B1 = mdl.get_item("B1", parent=comp_handle, item_type="port")
    port_C1 = mdl.get_item("C1", parent=comp_handle, item_type="port")
    port_A2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
    port_B2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
    port_C2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
    coup = mdl.get_item("CC", parent=comp_handle)

    if RL_section == 1:
        if port_A1 and port_A2:
            if not len(mdl.find_connections(port_A1)) == 0:
                for xx in mdl.find_connections(port_A1):
                    mdl.delete_item(xx)
            if not len(mdl.find_connections(port_A2)) == 0:
                for xx in mdl.find_connections(port_A2):
                    mdl.delete_item(xx)

        if port_B1 and port_B2:
            if not len(mdl.find_connections(port_B1)) == 0:
                mdl.delete_item(mdl.find_connections(port_B1)[0])
            if not len(mdl.find_connections(port_B2)) == 0:
                mdl.delete_item(mdl.find_connections(port_B2)[0])

        if port_C1 and port_C2:
            if not len(mdl.find_connections(port_C1)) == 0:
                mdl.delete_item(mdl.find_connections(port_C1)[0])
            if not len(mdl.find_connections(port_C2)) == 0:
                mdl.delete_item(mdl.find_connections(port_C2)[0])

        if phase_num == "1":
            if not port_N:
                port_N = created_ports.get("N")

        mode_toggle = 0
        if mdl.get_property_value(mdl.prop(transmission_line, "model")) == "PI":
            mode_toggle = 1
        mdl.set_property_value(mdl.prop(transmission_line, "model"), "RL coupled")
        mdl.create_connection(port_A1, mdl.term(transmission_line, "a_in"))
        if phase_num == "2":
            mdl.create_connection(port_B1, mdl.term(transmission_line, "b_in"))
        elif phase_num == "3":
            mdl.create_connection(port_B1, mdl.term(transmission_line, "b_in"))
            mdl.create_connection(port_C1, mdl.term(transmission_line, "c_in"))
        if coup:
            connTLN2 = mdl.get_item("ConnTLN2", parent=comp_handle, item_type="connection")
            if connTLN2:
                mdl.delete_item(connTLN2)

            mdl.create_connection(port_A2, mdl.term(coup, "a_out"))
            if mode_toggle == 1:
                mdl.create_connection(mdl.term(transmission_line, "a_out"), mdl.term(coup, "a_in"))
            if phase_num == "2":
                mdl.create_connection(port_B2, mdl.term(coup, "b_out"))
                mdl.create_connection(port_N, mdl.term(coup, "c_in"), name="ConnTLN2")
                if mode_toggle == 1:
                    mdl.create_connection(mdl.term(transmission_line, "b_out"), mdl.term(coup, "b_in"))
            elif phase_num == "3":
                mdl.create_connection(port_B2, mdl.term(coup, "b_out"))
                mdl.create_connection(port_C2, mdl.term(coup, "c_out"))
                mdl.create_connection(port_N, mdl.term(coup, "d_in"), name="ConnTLN2")
                if mode_toggle == 1:
                    mdl.create_connection(mdl.term(transmission_line, "b_out"), mdl.term(coup, "b_in"))
                    mdl.create_connection(mdl.term(transmission_line, "c_out"), mdl.term(coup, "c_in"))

        else:
            mdl.create_connection(port_A2, mdl.term(transmission_line, "a_out"))
            if phase_num == "2":
                mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
            elif phase_num == "3":
                mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
                mdl.create_connection(port_C2, mdl.term(transmission_line, "c_out"))

    else:
        if port_A1 and port_A2:
            if not len(mdl.find_connections(port_A1)) == 0:
                for xx in mdl.find_connections(port_A1):
                    mdl.delete_item(xx)
            if not len(mdl.find_connections(port_A2)) == 0:
                for xx in mdl.find_connections(port_A2):
                    mdl.delete_item(xx)

        if port_B1 and port_B2:
            if not len(mdl.find_connections(port_B1)) == 0:
                mdl.delete_item(mdl.find_connections(port_B1)[0])
            if not len(mdl.find_connections(port_B2)) == 0:
                mdl.delete_item(mdl.find_connections(port_B2)[0])

        if port_C1 and port_C2:
            if not len(mdl.find_connections(port_C1)) == 0:
                mdl.delete_item(mdl.find_connections(port_C1)[0])
            if not len(mdl.find_connections(port_C2)) == 0:
                mdl.delete_item(mdl.find_connections(port_C2)[0])
        if not port_N:
            port_N = created_ports.get("N")

        mode_toggle = 0
        if mdl.get_property_value(mdl.prop(transmission_line, "model")) == "RL coupled":
            mode_toggle = 1

        mdl.set_property_value(mdl.prop(transmission_line, "model"), "PI")
        mdl.create_connection(port_A1, mdl.term(transmission_line, "a_in"))
        if phase_num == "2":
            mdl.create_connection(port_B1, mdl.term(transmission_line, "b_in"))
        elif phase_num == "3":
            mdl.create_connection(port_B1, mdl.term(transmission_line, "b_in"))
            mdl.create_connection(port_C1, mdl.term(transmission_line, "c_in"))
        if coup:
            mdl.create_connection(port_A2, mdl.term(coup, "a_out"))
            if mode_toggle == 1:
                mdl.create_connection(mdl.term(transmission_line, "a_out"), mdl.term(coup, "a_in"))
            if phase_num == "2":
                mdl.create_connection(port_B2, mdl.term(coup, "b_out"))
                if mode_toggle == 1:
                    mdl.create_connection(mdl.term(transmission_line, "b_out"), mdl.term(coup, "b_in"))
            elif phase_num == "3":
                mdl.create_connection(port_B2, mdl.term(coup, "b_out"))
                mdl.create_connection(port_C2, mdl.term(coup, "c_out"))
                if mode_toggle == 1:
                    mdl.create_connection(mdl.term(transmission_line, "b_out"), mdl.term(coup, "b_in"))
                    mdl.create_connection(mdl.term(transmission_line, "c_out"), mdl.term(coup, "c_in"))
        else:
            mdl.create_connection(port_A2, mdl.term(transmission_line, "a_out"))
            if phase_num == "2":
                mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
            elif phase_num == "3":
                mdl.create_connection(port_B2, mdl.term(transmission_line, "b_out"))
                mdl.create_connection(port_C2, mdl.term(transmission_line, "c_out"))
        connTLN = mdl.get_item("ConnTLN1", parent=comp_handle, item_type="connection")
        if not connTLN:
            mdl.create_connection(port_N, mdl.term(transmission_line, "gnd"), name="ConnTLN1")

    conn1pha1 = mdl.get_item("Conn1phA1", parent=comp_handle, item_type="connection")
    conn1pha2 = mdl.get_item("Conn1phA2", parent=comp_handle, item_type="connection")
    conn1phN = mdl.get_item("Conn1phN", parent=comp_handle, item_type="connection")
    conn1phN2 = mdl.get_item("Conn1phN2", parent=comp_handle, item_type="connection")
    if conn1pha1:
        mdl.delete_item(conn1pha1)
    if conn1pha2:
        mdl.delete_item(conn1pha2)
    if conn1phN:
        mdl.delete_item(conn1phN)
    if conn1phN2:
        mdl.delete_item(conn1phN2)
    if phase_num == "1":
        if port_N:
            mdl.create_connection(mdl.term(pi_section, "N"), port_N, name="Conn1phN")

        mdl.create_connection(mdl.term(pi_section, "A1"), port_A1, name="Conn1phA1")
        if coup:
            mdl.create_connection(mdl.term(pi_section, "A2"), mdl.term(coup, "a_in"), name="Conn1phA2")
            mdl.create_connection(mdl.term(pi_section, "N"), mdl.term(coup, "b_in"), name="Conn1phN2")
        else:
            mdl.create_connection(mdl.term(pi_section, "A2"), port_A2, name="Conn1phA2")
        mdl.enable_items(pi_section)
        mdl.disable_items(transmission_line)
    else:
        mdl.enable_items(transmission_line)
        mdl.disable_items(pi_section)


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


def port_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)
    deleted_ports = []
    created_ports = {}

    phases_prop = mdl.prop(comp_handle, "phases")
    phase_num = mdl.get_property_value(phases_prop)

    port_A1 = mdl.get_item("A1", parent=comp_handle, item_type="port")
    port_B1 = mdl.get_item("B1", parent=comp_handle, item_type="port")
    port_C1 = mdl.get_item("C1", parent=comp_handle, item_type="port")
    port_A2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
    port_B2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
    port_C2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
    port_N = mdl.get_item("N", parent=comp_handle, item_type="port")
    portN2 = mdl.get_item("N2", parent=comp_handle, item_type="port")

    input_type_prop = mdl.prop(comp_handle, "input_type")
    input_type = mdl.get_property_value(input_type_prop)
    coupling_prop = mdl.prop(comp_handle, "coupling")
    coupling_type = mdl.get_property_value(coupling_prop)
    mode_prop = mdl.prop(comp_handle, "obj_mode")
    mode = mdl.get_property_value(mode_prop)
    RL_section = 0

    if not phase_num == "1":
        if input_type == "Matrix" or (input_type == "LineCode" and mode == "matrix"):
            cmtx_prop = mdl.prop(comp_handle, "cmatrix")
            cmtx = mdl.get_property_disp_value(cmtx_prop)
            cmtx_sum = 0
            if re.match(r'[^\n\|\s]+', cmtx):
                re_str = '([+-]?[0-9]+[.]?[0-9]*[eE]?[+-]?[0-9]*|[+-]?[0-9]*[.]?[0-9]+[eE]?[+-]?[0-9]*)'
                cmtx_elements = re.findall(re_str, cmtx)
            for idx, _ in enumerate(cmtx_elements):
                cmtx_sum = cmtx_sum + float(cmtx_elements[idx])

            if cmtx_sum == 0:
                RL_section = 1
            else:
                RL_section = 0
        else:
            dCp = mdl.prop(comp_handle, "dC1")
            dCp_value = mdl.get_property_value(dCp)
            dCz = mdl.prop(comp_handle, "dC0")
            dCz_value = mdl.get_property_value(dCz)
            if str(dCp_value) == "0" and str(dCz_value) == "0":
                RL_section = 1
            else:
                RL_section = 0

    if phase_num == "3":
        if not port_B1:
            port_B1 = mdl.create_port(
                name="B1",
                parent=comp_handle,
                kind="pe",
                terminal_position=(-32, 0),
                position=(7512, 8032)
            )
            created_ports.update({"B1": port_B1})
        if not port_B2:
            port_B2 = mdl.create_port(
                name="B2",
                parent=comp_handle,
                kind="pe",
                terminal_position=(32, 0),
                position=(8008, 8032)
            )
            created_ports.update({"B2": port_B2})
        if not port_C1:
            port_C1 = mdl.create_port(
                name="C1",
                parent=comp_handle,
                kind="pe",
                terminal_position=(-32, 32),
                position=(7512, 8088)
            )
            created_ports.update({"C1": port_C1})
        if not port_C2:
            port_C2 = mdl.create_port(
                name="C2",
                parent=comp_handle,
                kind="pe",
                terminal_position=(32, 32),
                position=(8008, 8128)
            )
            created_ports.update({"C2": port_C2})
    elif phase_num == "2":
        if port_C1:
            deleted_ports.append(mdl.get_name(port_C1))
            mdl.delete_item(port_C1)
        if port_C2:
            deleted_ports.append(mdl.get_name(port_C2))
            mdl.delete_item(port_C2)
        if not port_B1:
            port_B1 = mdl.create_port(
                name="B1",
                parent=comp_handle,
                kind="pe",
                terminal_position=(-32, 0),
                position=(7512, 8032)
            )
            created_ports.update({"B1": port_B1})
        if not port_B2:
            port_B2 = mdl.create_port(
                name="B2",
                parent=comp_handle,
                kind="pe",
                terminal_position=(32, 0),
                position=(8008, 8032)
            )
            created_ports.update({"B2": port_B2})
    elif phase_num == "1":
        if port_B1:
            deleted_ports.append(mdl.get_name(port_B1))
            mdl.delete_item(port_B1)
        if port_B2:
            deleted_ports.append(mdl.get_name(port_B2))
            mdl.delete_item(port_B2)
        if port_C1:
            deleted_ports.append(mdl.get_name(port_C1))
            mdl.delete_item(port_C1)
        if port_C2:
            deleted_ports.append(mdl.get_name(port_C2))
            mdl.delete_item(port_C2)

    if coupling_type == "Device coupling" or coupling_type == "Core coupling":

        if not portN2:
            portN2 = mdl.create_port(
                name="N2",
                parent=comp_handle,
                kind="pe",
                terminal_position=("bottom", "right"),
                position=(8008, 8224),
                rotation="down"
            )
        created_ports.update({"N2": portN2})

    if RL_section == 1:
        if phase_num == "1":
            if not port_N:
                port_N = mdl.create_port(
                    name="N",
                    parent=comp_handle,
                    kind="pe",
                    terminal_position=("bottom", "left"),
                    position=(7728, 8144)
                )
                created_ports.update({"N": port_N})
    else:
        if not port_N:
            port_N = mdl.create_port(
                name="N",
                parent=comp_handle,
                kind="pe",
                terminal_position=("bottom", "left"),
                position=(7728, 8144)
            )
            created_ports.update({"N": port_N})


    # Relocate ports
    mdl.refresh_icon(comp_handle)
    if caller_prop_handle and mdl.get_name(caller_prop_handle) == "phases":
        if phase_num == "3":
            mdl.set_port_properties(port_A1, terminal_position=(-32, -32))
            mdl.set_port_properties(port_A2, terminal_position=(32, -32))
            mdl.set_port_properties(port_B1, terminal_position=(-32, 0))
            mdl.set_port_properties(port_B2, terminal_position=(32, 0))
            mdl.set_port_properties(port_C1, terminal_position=(-32, 32))
            mdl.set_port_properties(port_C2, terminal_position=(32, 32))
            if port_N:
                mdl.set_port_properties(port_N, terminal_position=("bottom", "left"))
            if portN2:
                mdl.set_port_properties(portN2, terminal_position=("bottom", "right"))
        elif phase_num == "2":
            mdl.set_port_properties(port_A1, terminal_position=(-32, -16))
            mdl.set_port_properties(port_A2, terminal_position=(32, -16))
            mdl.set_port_properties(port_B1, terminal_position=(-32, 16))
            mdl.set_port_properties(port_B2, terminal_position=(32, 16))
            if port_N:
                mdl.set_port_properties(port_N, terminal_position=("bottom", "left"))
            if portN2:
                mdl.set_port_properties(portN2, terminal_position=("bottom", "right"))
        elif phase_num == "1":
            mdl.set_port_properties(port_A1, terminal_position=(-32, 0))
            mdl.set_port_properties(port_A2, terminal_position=(32, 0))
            if port_N:
                mdl.set_port_properties(port_N, terminal_position=("bottom", "left"))
            if portN2:
                mdl.set_port_properties(portN2, terminal_position=("bottom", "right"))
        else:
            mdl.set_port_properties(port_A1, terminal_position=(-32, -32))
            mdl.set_port_properties(port_A2, terminal_position=(32, -32))
            mdl.set_port_properties(port_B1, terminal_position=(-32, 0))
            mdl.set_port_properties(port_B2, terminal_position=(32, 0))
            mdl.set_port_properties(port_C1, terminal_position=(-32, 32))
            mdl.set_port_properties(port_C2, terminal_position=(32, 32))
            if port_N:
                mdl.set_port_properties(port_N, terminal_position=("bottom", "left"))
            if portN2:
                mdl.set_port_properties(portN2, terminal_position=("bottom", "right"))

    return created_ports, deleted_ports


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)

    mode = mdl.get_property_value(mdl.prop(mask_handle, "obj_mode"))
    input_type = mdl.get_property_disp_value(mdl.prop(mask_handle, "input_type"))
    phases = mdl.get_property_disp_value(mdl.prop(mask_handle, "phases"))

    if input_type == "Symmetrical":
        hide_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix"]
        show_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
        enable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
        disable_params = []

        mdl.set_property_disp_value(mdl.prop(mask_handle, 'phases'), "3")
        mdl.disable_property(mdl.prop(mask_handle, "phases"))

    elif input_type == "Matrix":
        hide_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0"]
        show_params = ["xmatrix", "rmatrix", "cmatrix"]
        enable_params = ["xmatrix", "rmatrix", "cmatrix"]
        disable_params = []
        mdl.enable_property(mdl.prop(mask_handle, "phases"))
    elif input_type == "LineCode":
        if mdl.get_property_disp_value(mdl.prop(mask_handle, "selected_object")):
            if mode == "matrix":
                show_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix"]
                hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
            elif mode == "symmetrical":
                show_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0"]
                hide_params = ["xmatrix", "rmatrix", "cmatrix"]
            else:
                show_params = ["Load", "selected_object"]
                hide_params = []
        else:
            show_params = ["Load", "selected_object"]
            hide_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]

        enable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]  # Workaround
        disable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]
        mdl.enable_property(mdl.prop(mask_handle, "phases"))
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

    toggle_frequency_prop(mdl, mask_handle, init=False)


def define_icon(mdl, mask_handle):
    phases = mdl.get_property_value(mdl.prop(mask_handle, "phases"))

    if phases == "3":
        mdl.set_component_icon_image(mask_handle, 'images/transmission_line.svg')
    elif phases == "2":
        mdl.set_component_icon_image(mask_handle, 'images/transmission_line_2.svg')
    elif phases == "1":
        mdl.set_component_icon_image(mask_handle, 'images/transmission_line_1.svg')
    else:
        mdl.set_component_icon_image(mask_handle, 'images/transmission_line.svg')

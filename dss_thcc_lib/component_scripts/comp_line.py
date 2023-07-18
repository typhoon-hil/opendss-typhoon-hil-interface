import numpy as np
import ast
import re


def load_line_parameters(mdl, container_handle):
    import os
    #import sys
    import pathlib

    # try:
    #from tse_to_opendss.tse2tpt_base_converter import tse2tpt
    #import tse_to_opendss
    # except:
        # If running from development folder instead of installed package
        # dss_module_folder = str(pathlib.Path(__file__).parent.parent.parent.parent)
        # if not dss_module_folder in sys.path:
        #     sys.path.append(dss_module_folder)
        #
        # from tse_to_opendss.tse2tpt_base_converter import tse2tpt
        # import tse_to_opendss

    import dss_thcc_lib.gui_scripts.load_object as load_obj

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
                if param == "phases":
                    if not value:
                        mdl.warning("The linecode selected doesn't have the number of phases defined. "
                                    "Assuming three-phase.", context=param_prop)
                        value = 3
                else:
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
        mask_dialog_dynamics(mdl, container_handle, obj_type)

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
        try:
            mat = str(mdl.get_ns_var(mdl.get_property_value(mat_prop)))
        except:
            mat = str(mdl.get_property_value(mat_prop))

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
            raise mdl.error(
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

    mdl.info("-------------------")
    mdl.info(f"{mdl.get_name(comp_handle)=}")
    for mat_name in ['rmatrix', 'xmatrix', 'cmatrix']:
        if mat_name in matrix_props:
            mdl.info(f"setting {mat_name} to {hil_matrices.get(mat_name)}")
            mdl.set_property_value(mdl.prop(container_handle, prop_dict.get(mat_name)),
                                   hil_matrices.get(mat_name))
        else:
            mdl.info("not in matrix_props")
            if mat_name == 'cmatrix':
                prop_handle = mdl.prop(container_handle, "d_C")
                cap_array = np.array(mdl.get_property_value(prop_handle)) * 1e-9
                list_cap_array = cap_array.tolist()
                mdl.info(f"setting cap to {list_cap_array}")
                mdl.set_property_value(prop_handle, cap_array.tolist())
            else:
                mat_prop = mdl.prop(container_handle, mat_name)
                mdl.info(f"setting {mat_name} to {mdl.get_property_disp_value(mat_prop)}")
                mdl.set_property_value(mdl.prop(container_handle, prop_dict.get(mat_name)),
                                       mdl.get_property_disp_value(mat_prop))


def configure_cable(mdl, container_handle):

    comp_handle = mdl.get_parent(container_handle)
    mode = mdl.get_property_value(mdl.prop(container_handle, "obj_mode"))
    input_type = mdl.get_property_value(mdl.prop(container_handle, "input_type"))
    length = mdl.get_property_value(mdl.prop(container_handle, "Length"))
    basefreq = mdl.get_property_value(mdl.prop(container_handle, "baseFreq"))
    w = 2 * np.pi * basefreq
    transmission_line = mdl.get_item("TL", parent=comp_handle)

    mdl.set_property_value(mdl.prop(container_handle, "Length"), length)
    mdl.set_property_value(mdl.prop(container_handle, "Len"), length)
    mdl.set_property_value(mdl.prop(container_handle, "Fr"), basefreq)

    if input_type == "Symmetrical" or (input_type == "LineCode" and mode == "symmetrical"):

        r0 = mdl.get_property_value(mdl.prop(container_handle, "R0"))
        r1 = mdl.get_property_value(mdl.prop(container_handle, "R1"))
        x0 = mdl.get_property_value(mdl.prop(container_handle, "X0"))
        x1 = mdl.get_property_value(mdl.prop(container_handle, "X1"))
        dc0 = mdl.get_property_value(mdl.prop(container_handle, "dC0"))
        dc1 = mdl.get_property_value(mdl.prop(container_handle, "dC1"))
        l1 = x1 / w
        l0 = x0 / w
        c1 = dc1 * 1e-9
        c0 = dc0 * 1e-9

        coupling = mdl.get_property_value(mdl.prop(container_handle, "coupling"))
        if not coupling == "None":

            rseq = np.array(
                [[r0, 0, 0],
                 [0, r1, 0],
                 [0, 0, r1]])
            xseq = np.array(
                [[x0, 0, 0],
                 [0, x1, 0],
                 [0, 0, x1]])

            zseq = rseq + 1j * xseq

            [r0n, r1n, x0n, x1n, xcoup] = compute_sequence_values(mdl, container_handle, zseq, "symmetrical")
            lcoup = xcoup / w * length
            l1n = x1n / w
            l0n = x0n / w
            comp_handle = mdl.get_parent(container_handle)
            coup = mdl.get_item("CC", parent=comp_handle, item_type="masked_component")
            if coup:
                cc_inductance_prop = mdl.prop(coup, "inductance")
                mdl.set_property_value(cc_inductance_prop, lcoup)
                mdl.info(f'Setting {mdl.get_name(comp_handle)}\'s coupling inductance to {"{:.4e}".format(lcoup)}H')
            d_r = [[r0n, 0, 0], [0, r1n, 0], [0, 0, r1n]]
            d_l = [[l0n, 0, 0], [0, l1n, 0], [0, 0, l1n]]
            d_c = [[c0, 0, 0], [0, c1, 0], [0, 0, c1]]
        else:
            d_r = [[r0, 0, 0], [0, r1, 0], [0, 0, r1]]
            d_l = [[l0, 0, 0], [0, l1, 0], [0, 0, l1]]
            d_c = [[c0, 0, 0], [0, c1, 0], [0, 0, c1]]

        mdl.set_property_value(mdl.prop(container_handle, "d_R"), d_r)
        mdl.set_property_value(mdl.prop(container_handle, "d_L"), d_l)
        mdl.set_property_value(mdl.prop(container_handle, "d_C"), d_c)
        mdl.set_property_value(mdl.prop(container_handle, "C1"), c1)
        mdl.set_property_value(mdl.prop(container_handle, "C0"), c0)
        mdl.set_property_value(mdl.prop(transmission_line, "model_def"), "Sequence")
        mdl.set_property_value(mdl.prop(transmission_line, "Length_metric"), "Length")
        mdl.set_property_value(mdl.prop(transmission_line, "Frequency"), "baseFreq")

    elif input_type == "Matrix" or (input_type == "LineCode" and mode == "matrix"):
        # Convert matrix inputs to python format
        matrix_props = ['rmatrix', 'xmatrix', 'cmatrix']

        convert_matrix_to_hil_format(mdl, container_handle, matrix_props)

        xarray = np.array(mdl.get_property_value(mdl.prop(container_handle, "d_X")))
        larray = xarray / w
        mdl.set_property_value(mdl.prop(container_handle, "d_L"), larray.tolist())

        # RLC model
        mdl.set_property_value(mdl.prop(transmission_line, "model_def"), "RLC")
        mdl.set_property_value(mdl.prop(transmission_line, "Length_metric"), "Length")
        mdl.set_property_value(mdl.prop(transmission_line, "Frequency"), "baseFreq")

        coupling = mdl.get_property_value(mdl.prop(container_handle, "coupling"))
        if not coupling == "None":
            mdl.info("Coupling not implemented for matrix-type parameters")

    mdl.set_property_value(mdl.prop(container_handle, "Length"), length)
    mdl.set_property_value(mdl.prop(container_handle, "Len"), length)
    mdl.set_property_value(mdl.prop(container_handle, "Fr"), basefreq)


def compute_sequence_values(mdl, mask_handle, zseq, mode):

    length = mdl.get_property_value(mdl.prop(mask_handle, "Length"))
    basefreq = mdl.get_property_value(mdl.prop(mask_handle, "baseFreq"))
    w = 2 * np.pi * basefreq

    alpha = complex(np.cos(-120.0 * np.pi / 180.0), np.sin(-120.0 * np.pi / 180.0))
    a_matrix = np.matrix([[1, 1, 1],
                          [1, alpha ** 2.0, alpha],
                          [1, alpha, alpha ** 2.0]])  # sequence to phase components transf. matrix
    zabc = np.dot(np.dot(a_matrix, zseq), a_matrix.I)
    rabc = zabc.real
    xabc = zabc.imag
    xabc_min = min(np.diag(xabc))
    digits = 10

    x_ratio = 1e-3
    xcoup = x_ratio * xabc_min

    if xcoup / w * length > 100e-6:
        xcoup = 100e-6 * w / length
    elif xcoup / w * length < 1e-6:
        xcoup = 1e-6 * w / length

    xcoup_abc = xcoup * np.eye(3)
    xabcn = xabc - xcoup_abc
    zabc = rabc + 1j * xabcn
    zseq = np.dot(np.dot(a_matrix.I, zabc), a_matrix).round(digits)
    rseq = zseq.real
    xseq = zseq.imag

    r0 = rseq[0, 0]
    r1 = rseq[1, 1]
    x0 = xseq[0, 0]
    x1 = xseq[1, 1]

    if mode == "symmetrical":
        return [r0, r1, x0, x1, xcoup]
    elif mode == "matrix":
        return [rseq, xseq, xcoup]


def toggle_coupling(mdl, mask_handle, created_ports):
    """
    This function manages all important connections when changes are made to the number of phases, coupling presence
    and type and/or transmission line model (PI or RL coupled).
    """

    comp_handle = mdl.get_parent(mask_handle)

    # getting item and property handlers
    coup = mdl.get_item("CC", parent=comp_handle)
    transmission_line = mdl.get_item("TL", parent=comp_handle)
    port_a1 = mdl.get_item("A1", parent=comp_handle, item_type="port")
    port_b1 = mdl.get_item("B1", parent=comp_handle, item_type="port")
    port_c1 = mdl.get_item("C1", parent=comp_handle, item_type="port")
    port_a2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
    port_b2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
    port_c2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
    port_n1 = mdl.get_item("N1", parent=comp_handle, item_type="port")
    port_n2 = mdl.get_item("N2", parent=comp_handle, item_type="port")
    ground1 = mdl.get_item("G1", parent=comp_handle, item_type="component")
    ground2 = mdl.get_item("G2", parent=comp_handle, item_type="component")

    port_pair_list = [(port_a1, port_a2),
                      (port_b1, port_b2),
                      (port_c1, port_c2),
                      (port_n1, port_n2)]

    input_type_prop = mdl.prop(comp_handle, "input_type")
    mode_prop = mdl.prop(comp_handle, "obj_mode")
    phases_prop = mdl.prop(comp_handle, "phases")
    coupling_prop = mdl.prop(comp_handle, "coupling")

    input_type = mdl.get_property_value(input_type_prop)
    mode = mdl.get_property_value(mode_prop)
    phase_num = mdl.get_property_value(phases_prop)
    coupling_type = mdl.get_property_value(coupling_prop)

    rl_section = 0

    # evaluates the cmatrix property and analyze if the line should have the capacitors (PI model) or not
    if input_type == "Matrix" or (input_type == "LineCode" and mode == "matrix"):
        cmtx_prop = mdl.prop(comp_handle, "cmatrix")
        try:
            cmtx = str(mdl.get_ns_var(mdl.get_property_value(cmtx_prop)))
        except:
            cmtx = str(mdl.get_property_value(cmtx_prop))

        mod_mat = cmtx.strip(" [](){}\"\'")
        matrix_rows = mod_mat.split("|")

        dummy_matrix = "["
        for row_number in range(len(matrix_rows) - 1):
            dummy_matrix += f'[{matrix_rows[row_number].strip()}], '
        dummy_matrix += f'[{matrix_rows[-1].strip()}]]'
        dummy_matrix = re.sub(r"[\s,]+", ", ", dummy_matrix)
        try:
            evaluated_matrix = ast.literal_eval(dummy_matrix)
            if not np.any(np.matrix(evaluated_matrix)):
                rl_section = 1
            else:
                rl_section = 0

        except ValueError:
            mdl.info((f"It wasn't possible to evaluate the property {mdl.get_name(cmtx_prop)} on the Line"
                      f" {mdl.get_name(comp_handle)}: {cmtx}. \n Check if the property exists on the init script "
                      f"and click on the 'Validate Model' button to update the namespace."
                      f"Since the evaluation failed, the Line will be set to the PI model"))

    # evalues the positive and zero sequence capacitance values and analyze if the line should have capaciors (PI model)
    else:
        dcp = mdl.prop(comp_handle, "dC1")
        dcp_value = mdl.get_property_value(dcp)
        dcz = mdl.prop(comp_handle, "dC0")
        dcz_value = mdl.get_property_value(dcz)
        if str(dcp_value) == "0" and str(dcz_value) == "0":
            rl_section = 1
        else:
            rl_section = 0

    # All the configuration to the inner line are known at this point. Passing them down.
    if input_type == "Matrix" or (input_type == "LineCode" and mode == "matrix"):
        mdl.set_property_value(mdl.prop(transmission_line, "model_def"), "RLC")
        mdl.set_property_value(mdl.prop(transmission_line, "num_of_phases"), phase_num)
    else:
        mdl.set_property_value(mdl.prop(transmission_line, "num_of_phases"), phase_num)

    if rl_section == 0:
        mdl.set_property_value(mdl.prop(transmission_line, "model"), "PI")
    else:
        mdl.set_property_value(mdl.prop(transmission_line, "model"), "RL coupled")

    ###########
    if coupling_type == "None":
        if coup:
            mdl.delete_item(coup)

        if ground2:
            mdl.delete_item(ground2)

        if rl_section == 0:
            if ground1:
                if not len(mdl.find_connections(mdl.term(ground1, "node"))) == 0:
                    for xx in mdl.find_connections(mdl.term(ground1, "node")):
                        mdl.delete_item(xx)
            else:
                ground1 = mdl.create_component("core/Ground",
                                               name="G1",
                                               parent=comp_handle,
                                               position=(7742, 8278),
                                               rotation="up")
            mdl.create_connection(mdl.term(transmission_line, "gnd"), mdl.term(ground1, "node"))
        elif ground1:
            mdl.delete_item(ground1)

        for port_pair, phase_id in zip(port_pair_list, ["a", "b", "c", "d"]):
            if port_pair[0] and port_pair[1]:
                if not len(mdl.find_connections(port_pair[0])) == 0:
                    mdl.delete_item(mdl.find_connections(port_pair[0])[0])
                if not len(mdl.find_connections(port_pair[1])) == 0:
                    mdl.delete_item(mdl.find_connections(port_pair[1])[0])

                mdl.create_connection(port_pair[0], mdl.term(transmission_line, f"{phase_id}_in"))
                mdl.create_connection(port_pair[1], mdl.term(transmission_line, f"{phase_id}_out"))
    elif ((coupling_type == "Device coupling") or (coupling_type == "Core coupling")) and (int(phase_num) < 4):
        if coup:  # If there is a coupling of a different type, delete it
            mdl.delete_item(coup)

        # Delete connections between ports and transmission line to later place a coupling
        for port_pair, phase_id in zip(port_pair_list, ["a", "b", "c", "n"]):
            if port_pair[0] and port_pair[1]:
                if not len(mdl.find_connections(port_pair[0])) == 0:
                    mdl.delete_item(mdl.find_connections(port_pair[0])[0])
                if not len(mdl.find_connections(port_pair[1])) == 0:
                    mdl.delete_item(mdl.find_connections(port_pair[1])[0])
        # identify which coupling type to use
        coup_trnslt_dict = {"1":  "Single",
                            "2": "Three",
                            "3": "Four",
                            "Core coupling": "Core",
                            "Device coupling": "Device"}
        coup_component_type = f"core/{coup_trnslt_dict[phase_num]} Phase TLM {coup_trnslt_dict[coupling_type]} Coupling"

        try:
            # create the requested coupling
            coup = mdl.create_component(
                coup_component_type,
                name="CC",
                parent=comp_handle,
                position=(7944, 8082)
            )

        except RuntimeError:
            # Can't create coupling, most likely because the selected HIL device doesn't support Device Couplings
            # Recreate connections between line and ports
            for port_pair, phase_id in zip(port_pair_list, ["a", "b", "c", "n"]):
                if port_pair[0] and port_pair[1]:
                    mdl.create_connection(port_pair[0], mdl.term(transmission_line, f"{phase_id}_in"))
                    mdl.create_connection(port_pair[1], mdl.term(transmission_line, f"{phase_id}_out"))

            mdl.delete_item(ground2)

            mdl.info("It was not possible to create the Device Coupling because the component is not" +
                     " available in the library. Make sure the HIL device model and configuration are properly set."
                     "\n No couplings will be applied.")
            mdl.set_property_value(coupling_prop, "None")
        else:
            if ground1:
                if not len(mdl.find_connections(mdl.term(ground1, "node"))) == 0:
                    for xx in mdl.find_connections(mdl.term(ground1, "node")):
                        mdl.delete_item(xx)
            else:
                ground1 = mdl.create_component("core/Ground",
                                               name="G1",
                                               parent=comp_handle,
                                               position=(7742, 8278),
                                               rotation="up")

            if ground2:
                if not len(mdl.find_connections(mdl.term(ground2, "node"))) == 0:
                    for xx in mdl.find_connections(mdl.term(ground2, "node")):
                        mdl.delete_item(xx)
            else:
                ground2 = mdl.create_component("core/Ground",
                                               name="G2",
                                               parent=comp_handle,
                                               position=(8008, 8278),
                                               rotation="up")

            # If line is in PI model, connect port_N to the inner transmission line ground
            if rl_section == 0:
                mdl.create_connection(mdl.term(transmission_line, "gnd"), mdl.term(ground1, "node"))

            coup_conn_dict = {"1": {"conn_term_pair_list": [(port_a1, port_a2),
                                                            (ground1, ground2)],
                                    "phase_id_list": ["a", "b"]},
                              "2": {"conn_term_pair_list": [(port_a1, port_a2),
                                                            (port_b1, port_b2),
                                                            (ground1, ground2)],
                                    "phase_id_list": ["a", "b", "c"]},
                              "3": {"conn_term_pair_list": [(port_a1, port_a2),
                                                            (port_b1, port_b2),
                                                            (port_c1, port_c2),
                                                            (ground1, ground2)],
                                    "phase_id_list": ["a", "b", "c", "d"]}}

            # Create all connections through the coupling
            for conn_term_pair, phase_id in zip(coup_conn_dict[phase_num]["conn_term_pair_list"],
                                                coup_conn_dict[phase_num]["phase_id_list"]):
                if conn_term_pair != coup_conn_dict[phase_num]["conn_term_pair_list"][-1]:
                    mdl.create_connection(conn_term_pair[0], mdl.term(transmission_line, f"{phase_id}_in"))
                    mdl.create_connection(mdl.term(coup, f"{phase_id}_in"),
                                          mdl.term(transmission_line, f"{phase_id}_out"))
                    mdl.create_connection(conn_term_pair[1], mdl.term(coup, f"{phase_id}_out"))
                else:
                    mdl.create_connection(mdl.term(coup, f"{phase_id}_in"), mdl.term(conn_term_pair[0], "node"))
                    mdl.create_connection(mdl.term(conn_term_pair[1], "node"), mdl.term(coup, f"{phase_id}_out"))
    else:  # Old model was loaded
        mdl.set_property_value(coupling_prop, "None")


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

    phases_prop = mdl.prop(comp_handle, "phases")
    phase_num = mdl.get_property_value(phases_prop)

    port_a1 = mdl.get_item("A1", parent=comp_handle, item_type="port")
    port_b1 = mdl.get_item("B1", parent=comp_handle, item_type="port")
    port_c1 = mdl.get_item("C1", parent=comp_handle, item_type="port")
    port_a2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
    port_b2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
    port_c2 = mdl.get_item("C2", parent=comp_handle, item_type="port")
    port_n1 = mdl.get_item("N1", parent=comp_handle, item_type="port")
    port_n2 = mdl.get_item("N2", parent=comp_handle, item_type="port")

    coupling_prop = mdl.prop(comp_handle, "coupling")
    coupling_type = mdl.get_property_value(coupling_prop)

    hide_term_list = [port_a1, port_a2]

    if int(phase_num) > 1:
        if not port_b1:
            port_b1 = mdl.create_port(
                name="B1",
                parent=comp_handle,
                kind="pe",
                terminal_position=(-32, 0),
                position=(7512, 8032),
                rotation="up"
            )
            created_ports.update({"B1": port_b1})
        if not port_b2:
            port_b2 = mdl.create_port(
                name="B2",
                parent=comp_handle,
                kind="pe",
                terminal_position=(32, 0),
                position=(8008, 8032),
                rotation="down"
            )
            created_ports.update({"B2": port_b2})

        hide_term_list.extend([port_b1, port_b2])

    if int(phase_num) > 2:
        if not port_c1:
            port_c1 = mdl.create_port(
                name="C1",
                parent=comp_handle,
                kind="pe",
                terminal_position=(-32, 32),
                position=(7512, 8088),
                rotation="up"
            )
            created_ports.update({"C1": port_c1})
        if not port_c2:
            port_c2 = mdl.create_port(
                name="C2",
                parent=comp_handle,
                kind="pe",
                terminal_position=(32, 32),
                position=(8008, 8128),
                rotation="down"
            )
            created_ports.update({"C2": port_c2})

        hide_term_list.extend([port_c1, port_c2])

    if int(phase_num) > 3:
        if not port_n1:
            port_n1 = mdl.create_port(
                name="N1",
                parent=comp_handle,
                kind="pe",
                terminal_position=(-32, 48),
                position=(7512, 8144),
                rotation="up"
            )
            created_ports.update({"N1": port_n1})
        if not port_n2:
            port_n2 = mdl.create_port(
                name="N2",
                parent=comp_handle,
                kind="pe",
                terminal_position=(32, 48),
                position=(8008, 8224),
                rotation="down"
            )
            created_ports.update({"N2": port_n2})

        hide_term_list.extend([port_n1, port_n2])

    [mdl.set_port_properties(port_handle, hide_term_label=True) for port_handle in hide_term_list]

    if int(phase_num) <= 3:
        if port_n1:
            deleted_ports.append(mdl.get_name(port_n1))
            mdl.delete_item(port_n1)
        if port_n2:
            deleted_ports.append(mdl.get_name(port_n2))
            mdl.delete_item(port_n2)

    if int(phase_num) <= 2:
        if port_c1:
            deleted_ports.append(mdl.get_name(port_c1))
            mdl.delete_item(port_c1)
        if port_c2:
            deleted_ports.append(mdl.get_name(port_c2))
            mdl.delete_item(port_c2)

    if int(phase_num) <= 1:
        if port_b1:
            deleted_ports.append(mdl.get_name(port_b1))
            mdl.delete_item(port_b1)
        if port_b2:
            deleted_ports.append(mdl.get_name(port_b2))
            mdl.delete_item(port_b2)

    # Relocate ports
    mdl.refresh_icon(comp_handle)
    if caller_prop_handle and mdl.get_name(caller_prop_handle) == "phases":
        if phase_num == "4":
            mdl.set_port_properties(port_a1, terminal_position=(-32, -48))
            mdl.set_port_properties(port_a2, terminal_position=(32, -48))
            mdl.set_port_properties(port_b1, terminal_position=(-32, -16))
            mdl.set_port_properties(port_b2, terminal_position=(32, -16))
            mdl.set_port_properties(port_c1, terminal_position=(-32, 16))
            mdl.set_port_properties(port_c2, terminal_position=(32, 16))
            mdl.set_port_properties(port_n1, terminal_position=(-32, 48))
            mdl.set_port_properties(port_n2, terminal_position=(32, 48))
        elif phase_num == "3":
            mdl.set_port_properties(port_a1, terminal_position=(-32, -32))
            mdl.set_port_properties(port_a2, terminal_position=(32, -32))
            mdl.set_port_properties(port_b1, terminal_position=(-32, 0))
            mdl.set_port_properties(port_b2, terminal_position=(32, 0))
            mdl.set_port_properties(port_c1, terminal_position=(-32, 32))
            mdl.set_port_properties(port_c2, terminal_position=(32, 32))
        elif phase_num == "2":
            mdl.set_port_properties(port_a1, terminal_position=(-32, -16))
            mdl.set_port_properties(port_a2, terminal_position=(32, -16))
            mdl.set_port_properties(port_b1, terminal_position=(-32, 16))
            mdl.set_port_properties(port_b2, terminal_position=(32, 16))
        elif phase_num == "1":
            mdl.set_port_properties(port_a1, terminal_position=(-32, 0))
            mdl.set_port_properties(port_a2, terminal_position=(32, 0))

    return created_ports, deleted_ports


def mask_dialog_dynamics(mdl, mask_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(mask_handle)

    mode = mdl.get_property_value(mdl.prop(mask_handle, "obj_mode"))
    input_type = mdl.get_property_disp_value(mdl.prop(mask_handle, "input_type"))
    phase_num = mdl.get_property_disp_value(mdl.prop(mask_handle, "phases"))
    hide_params = []
    show_params = []
    enable_params = []
    disable_params = []

    if input_type == "Symmetrical":
        hide_params = ["Load", "selected_object", "xmatrix", "rmatrix", "cmatrix"]
        show_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
        enable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0"]
        disable_params = ["phases"]

        if caller_prop_handle and (caller_prop_handle != mdl.prop(mask_handle, "phases")):
            mdl.set_property_disp_value(mdl.prop(mask_handle, 'phases'), "3")

    elif input_type == "Matrix":
        hide_params = ["Load", "selected_object", "R1", "R0", "dC1", "dC0", "X1", "X0"]
        show_params = ["xmatrix", "rmatrix", "cmatrix"]
        enable_params = ["xmatrix", "rmatrix", "cmatrix", "phases"]
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

        enable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix", "phases"]  # Workaround
        disable_params = ["R1", "R0", "dC1", "dC0", "X1", "X0", "xmatrix", "rmatrix", "cmatrix"]

    if phase_num == "4":
        disable_params.append("coupling")
        mdl.set_property_disp_value(mdl.prop(mask_handle, "coupling"), "None")
    else:
        enable_params.append("coupling")

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

    mdl.set_component_icon_image(mask_handle, f'images/transmission_line_{phases}.svg')

import os, pathlib

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QFileDialog, QWidget
import numpy as np
import re
from math import log10, floor
import ast
import itertools

# Append commands dialog
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(718, 465)
        self.gridLayout_4 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.text_edit = QtWidgets.QTextEdit(Dialog)
        self.text_edit.setObjectName("text_edit")
        self.gridLayout_4.addWidget(self.text_edit, 1, 0, 1, 1)
        self.text_edit_2 = QtWidgets.QTextEdit(Dialog)
        self.text_edit_2.setObjectName("text_edit_2")
        self.gridLayout_4.addWidget(self.text_edit_2, 3, 0, 1, 1)
        self.label_commands = QtWidgets.QLabel(Dialog)
        self.label_commands.setObjectName("label_commands")
        self.gridLayout_4.addWidget(self.label_commands, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.locate_button = QtWidgets.QPushButton(Dialog)
        self.locate_button.setEnabled(True)
        self.locate_button.setMinimumSize(QtCore.QSize(120, 0))
        self.locate_button.setObjectName("locate_button")
        self.verticalLayout.addWidget(self.locate_button)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.ok_button = QtWidgets.QPushButton(Dialog)
        self.ok_button.setObjectName("ok_button")
        self.verticalLayout.addWidget(self.ok_button)
        self.cancel_button = QtWidgets.QPushButton(Dialog)
        self.cancel_button.setObjectName("cancel_button")
        self.verticalLayout.addWidget(self.cancel_button)
        self.gridLayout_4.addLayout(self.verticalLayout, 1, 1, 3, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout_4.addWidget(self.label, 2, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Append DSS commands"))
        self.label_commands.setText(_translate("Dialog", "Before the solution"))
        self.locate_button.setText(_translate("Dialog", "Locate .dss files"))
        self.ok_button.setText(_translate("Dialog", "OK"))
        self.cancel_button.setText(_translate("Dialog", "Cancel"))
        self.label.setText(_translate("Dialog", "After the solution"))


class AppendDialog(QDialog, Ui_Dialog):

    def __init__(self, mdl):
        super().__init__()
        self.setupUi(self)

        # 'Before solving' is the default selected text edit box
        self.selected_textedit = self.text_edit

        # Get the path to the target files folder
        mdlfile = mdl.get_model_file_path()
        mdlfile_name = pathlib.Path(mdlfile).stem
        mdlfile_folder = pathlib.Path(mdlfile).parents[0]
        mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
        self.dss_folder_path = pathlib.Path(mdlfile_target_folder).joinpath('dss')

        self.load_appended_commands_file()

        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.save_append_file)
        self.locate_button.clicked.connect(self.load_dss_files)
        self.text_edit.selectionChanged.connect(self.set_selected_textedit)
        self.text_edit_2.selectionChanged.connect(self.set_selected_textedit)

    def set_selected_textedit(self):
        self.selected_textedit = self.sender()

    def load_appended_commands_file(self):
        fname = os.path.join(self.dss_folder_path, 'data', 'appended_commands.tse2dss')
        if os.path.isfile(fname):
            with open(fname, 'r') as f:
                text_lines = f.readlines()
                text_1_lines = []
                text_2_lines = []
                flag_text2 = False
                for line in text_lines:
                    if not flag_text2:
                        if not "!After solving!" in line:
                            text_1_lines.append(line)
                        else:
                            flag_text2 = True
                    else:
                        text_2_lines.append(line)

                self.text_edit.append("\n".join(text_1_lines))
                self.text_edit_2.append("\n".join(text_2_lines))

    def write_redirects(self, file_names):
        if len(file_names) > 1:
            self.selected_textedit.append("""<body>
                                <h4 style='color:green;'>!Make sure the redirected files are correctly ordered</h2>""")
        for f in file_names:
            self.selected_textedit.append(f'redirect "{f}"')

    def load_dss_files(self):

        filter = "DSS (*.dss)"
        file_name = QtGui.QFileDialog()
        file_name.setFileMode(QFileDialog.ExistingFiles)
        located_files = file_name.getOpenFileNames(self, "Select DSS files", "C:\Program Files\OpenDSS\Examples",
                                                   filter)

        self.write_redirects(located_files[0])

    def save_append_file(self):
        import os

        fname = os.path.join(self.dss_folder_path, 'data', 'appended_commands.tse2dss')
        fname_before_plain = os.path.join(self.dss_folder_path, 'data', 'appended_commands_before.dss')
        fname_after_plain = os.path.join(self.dss_folder_path, 'data', 'appended_commands_after.dss')
        with open(fname, 'w') as f:
            f.write(self.text_edit.toHtml())
            f.write("\n!After solving!")
            f.write(self.text_edit_2.toHtml())
        with open(fname_before_plain, 'w') as f:
            f.write(self.text_edit.toPlainText())
        with open(fname_after_plain, 'w') as f:
            f.write(self.text_edit_2.toPlainText())
        self.accept()


class FileDialog(QWidget):
    def __init__(self, mdl, item_handle):
        super().__init__()
        self.title = 'Save the Model File'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.mdl = mdl
        self.item_handle = item_handle
        self.comp_handle = mdl.get_sub_level_handle(item_handle)

    def save_file(self):
        return False

def append_commands(mdl, mask_handle):
    new_diag = AppendDialog(mdl)
    new_diag.exec()


def sim_with_opendss(mdl, mask_handle):
    try:
        comp_handle = mdl.get_parent(mask_handle)
    except:
        mdl.info(
            "If this SimDSS component was copied from another model, please save and reload this model or add a new SimDSS from the Library Explorer.")
        raise Exception()

    import opendssdirect as dss

    # try:
    from tse_to_opendss.tse2tpt_base_converter import tse2tpt
    import tse_to_opendss
    # except:
    #     # If running from development folder instead of installed package
    #     dss_module_folder = str(pathlib.Path(__file__).parent.parent.parent.parent)
    #     if not dss_module_folder in sys.path:
    #         sys.path.append(dss_module_folder)
    #
    #     from tse_to_opendss.tse2tpt_base_converter import tse2tpt
    #     import tse_to_opendss

    mdlfile = mdl.get_model_file_path()

    if mdlfile:
        mdl.export_model_to_json()
    else:
        save_dialog = FileDialog(mdl, mask_handle)
        mdlfile = save_dialog.save_file()
        if not mdlfile:
            raise Exception("The model must be saved to allow the OpenDSS simulation")

    # Get the path to the exported JSON
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder = mdlfile_target_folder.joinpath('dss')
    json_file_path = mdlfile_target_folder.joinpath(mdlfile_name + '.json')
    dss_file = mdlfile_target_folder.joinpath(dss_folder).joinpath(mdlfile_name + '_master.dss')

    # Simulation parameters
    sim_parameters = {}
    sim_parameters["sim_mode"] = mdl.get_property_disp_value(mdl.prop(comp_handle, "sim_mode"))
    sim_parameters["algorithm"] = mdl.get_property_disp_value(mdl.prop(comp_handle, "algorithm"))
    sim_parameters["voltagebases"] = mdl.get_property_disp_value(mdl.prop(comp_handle, "voltagebases"))
    sim_parameters["basefrequency"] = mdl.get_property_disp_value(mdl.prop(comp_handle, "baseFreq"))
    sim_parameters["maxiter"] = mdl.get_property_disp_value(mdl.prop(comp_handle, "maxiter"))
    sim_parameters["miniterations"] = mdl.get_property_disp_value(mdl.prop(comp_handle, "miniterations"))
    sim_parameters["loadmodel"] = mdl.get_property_disp_value(mdl.prop(comp_handle, "loadmodel"))
    sim_parameters["stepsize"] = mdl.get_property_disp_value(mdl.prop(comp_handle, "tsstp"))
    sim_parameters["number"] = mdl.get_property_disp_value(mdl.prop(comp_handle, "tspoints"))

    if tse2tpt.start_conversion(json_file_path, tse_to_opendss, simulation_parameters=sim_parameters):
        # Compile dss model
        comp_result = dss.utils.run_command(f'Compile "{str(dss_file)}"')
        mdl.info(f"Converting and solving {str(mdlfile_name)}...")
        stat_prop = mdl.prop(mask_handle, 'sim_status')
        counter_prop = mdl.prop(mask_handle, 'sim_counter')
        cur_count = int(mdl.get_property_value(counter_prop))
        mdl.set_property_value(counter_prop, str(cur_count + 1))
        if not comp_result:
            mdl.set_property_value(stat_prop, f"Sim{cur_count + 1} complete")
            mdl.info("Done.")

        else:
            mdl.set_property_value(stat_prop, f"Sim{cur_count + 1} failed")
            mdl.error(str(comp_result), context=comp_handle)


def run_command(mdl, mask_handle):
    import opendssdirect as dss
    from pathlib import Path

    command_prop = mdl.prop(mask_handle, "command")
    command = mdl.get_property_disp_value(command_prop)

    file_path = mdl.get_model_file_path()
    filename = Path(file_path).stem

    data_folder_path = pathlib.Path(file_path).parent.joinpath(f'{filename} Target files', 'dss', 'data')
    output_folder_path = pathlib.Path(file_path).parent.joinpath(f'{filename} Target files', 'dss', 'output')

    if command.strip()[:4].lower() == 'show' or command.strip()[:6].lower() == 'export':
        dss.Text.Command(f'set Datapath = "{output_folder_path}"')

    dss.Basic.AllowEditor(1)
    comm_result = dss.utils.run_command(f"{command}")
    if not comm_result:
        mdl.info(f"Ran the following command: {command}.")
    else:
        mdl.info(f"Command line output: {comm_result}")
    dss.Basic.AllowEditor(0)

    dss.Text.Command(f'set Datapath = "{data_folder_path}"')

    return comm_result


def command_buttons(mdl, mask_handle, prop_handle):
    import opendssdirect as dss
    from pathlib import Path
    import subprocess

    dss.Basic.AllowEditor(0)
    prop_name = mdl.get_name(prop_handle)

    file_path = mdl.get_model_file_path()
    filename = Path(file_path).stem

    data_folder_path = pathlib.Path(file_path).parent.joinpath(f'{filename} Target files', 'dss', 'data')
    output_folder_path = pathlib.Path(file_path).parent.joinpath(f'{filename} Target files', 'dss', 'output')

    output_file_dict = {
        'voltages LN': "_VLN.txt",
        'voltages LL': "_VLL.txt",
        'voltages LN Nodes': "_VLN_Node.txt",
        'voltages LN Elements': "_VLN_elem.txt",
        'voltages LL Nodes': "_VLL_Node.txt",
        'currents Seq': "_Curr_Seq.txt",
        'currents Elem': "_Curr_Elem.txt",
        'currents Elem Resid': "_Curr_Elem.txt",
        'powers kVA': "_Power_seq_kVA.txt",
        'powers MVA': "_Power_seq_MVA.txt",
        'powers kVA Elem': "_Power_elem_kVA.txt",
        'powers MVA Elem': "_Power_elem_MVA.txt",
        'Buses': "_Buses.txt",
        'Elements': "_Elements.txt",
        'Generators': "_Generators.txt",
        'Losses': "_Losses.txt",
    }

    if prop_name == "show_v":
        combo_prop_handle = mdl.prop(mask_handle, "voltages")
        general_comm = "voltages "
    elif prop_name == "show_c":
        combo_prop_handle = mdl.prop(mask_handle, "currents")
        general_comm = "currents "
    elif prop_name == "show_p":
        combo_prop_handle = mdl.prop(mask_handle, "powers")
        general_comm = "powers "
    elif prop_name == "show_misc":
        combo_prop_handle = mdl.prop(mask_handle, "misc")
        general_comm = ""

    subcommand = mdl.get_property_disp_value(combo_prop_handle)
    command = f"{general_comm}{subcommand}"

    dss.Text.Command(f'set Datapath = "{output_folder_path}"')
    dss.Text.Command('show ' + command)
    dss.Text.Command(f'set Datapath = "{data_folder_path}"')
    txt_file_suffix = f'{output_file_dict[command]}'
    txt_file_path = output_folder_path.joinpath(filename + txt_file_suffix)
    subprocess.Popen(['notepad.exe', str(txt_file_path)], shell=True)


def report(mdl, mask_handle, mode="snap"):
    try:
        import tse_to_opendss
        import dss_thcc_lib.extra.auto_report.power_flow_report as pf_rep
        import dss_thcc_lib.extra.auto_report.fault_report as fault_rep
        import dss_thcc_lib.extra.auto_report.comp_data_report as comp_rep
        import dss_thcc_lib.extra.auto_report.time_series_report as ts_rep

        mdlfile = mdl.get_model_file_path()

        if mode == "snap":
            rep_successful = pf_rep.generate_report(mdlfile)
        elif mode == "fault":
            rep_successful = fault_rep.generate_report(mdlfile)
        if not rep_successful[0]:
            mdl.info(rep_successful[1])

    except:
        mdl.info("Make sure to successfully run an OpenDSS simulation before printing a report.")
        return


def set_basefrequency_ns_var(mdl, mask_handle):
    basefreq = mdl.get_property_value(mdl.prop(mask_handle, "baseFreq"))
    mdl.set_ns_var("simdss_basefreq", basefreq)


def define_icon(mdl, mask_handle):
    mdl.set_component_icon_image(mask_handle, 'images/dss_logo.svg')


def run_stability_analysis(mdl, mask_handle):
    import opendssdirect as dss

    if len(get_all_dss_elements(mdl, comp_type=["Coupling"])) == 0:
        mdl.info("There are no DSS Coupling elements in the model.")
        return

    debug = False
    stability_data = {}

    window_report = 90
    mdl.info(f"Running the Power Flow")
    sim_with_opendss(mdl, mask_handle)
    # Get the path to the exported JSON
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder = mdlfile_target_folder.joinpath('dss')
    dss_file = mdlfile_target_folder.joinpath(dss_folder).joinpath(mdlfile_name + '_master.dss')

    stability_data.update({"dss_folder": dss_folder})
    stability_data.update({"mdlfile_name": mdlfile_name})

    # Initial settings
    # TODO: Create a function to estimate the time step if it is on "auto" mode
    if mdl.get_model_property_value("simulation_time_step") == "auto":
        mdl.info("The simulation time step is currently configured as auto. 10us will be used for this analysis")
        ts = 10e-6
    else:
        ts = float(mdl.get_model_property_value("simulation_time_step"))
    if not mdl.get_model_property_value("cpl_stb"):
        mdl.info("Enabling the THCC Core Coupling Stability Analysis.")
        mdl.set_model_property_value("cpl_stb", True)
    if not mdl.get_model_property_value("ground_scope_core"):
        mdl.info("Setting the Ground component scope to core.")
        mdl.set_model_property_value("ground_scope_core", True)

    stability_data.update({"ts": ts})

    # Getting all switches/contactors
    tse_sw_elements = []
    dss_sw_elements = []
    initial_condition = []
    for switch_handle in get_all_dss_elements(mdl, comp_type=["Controlled Switch"]):
        tse_sw_elements.append(switch_handle)
        dss_sw_elements.append(f"LINE.{mdl.get_name(switch_handle)}")
        initial_condition.append(1 if mdl.get_property_value(mdl.prop(switch_handle, "initial_state")) == "on" else 0)

    # Get the original power flow at the Coupling Elements
    dss.run_command(f'Compile "{dss_file}"')

    # Add switches from the Storage Components
    for storage_handle in get_all_dss_elements(mdl, comp_type=["Storage"]):
        tse_sw_elements.append(storage_handle)
        storage_dss_name = mdl.get_fqn(storage_handle).replace(".", "_").upper()
        dss_sw_elements.append(f"LINE.{storage_dss_name}")
        initial_condition.append(0)
        # Creating the switch on the DSS model
        dss.Circuit.SetActiveElement(f"STORAGE.{storage_dss_name}")
        storage_bus = dss.Properties.Value("bus1")
        dss.Properties.Value("bus1", f"aux_{storage_bus}")
        line_aux_prop = {}
        line_aux_prop["bus1"] = f"{storage_bus}"
        line_aux_prop["bus2"] = f"aux_{storage_bus}"
        line_aux_prop["phases"] = 3
        line_aux_prop["r1"] = 1e-6
        line_aux_prop["x1"] = 1e-6
        line_aux_prop["c1"] = 0
        line_aux_prop["r0"] = 1e-6
        line_aux_prop["x0"] = 1e-6
        line_aux_prop["c0"] = 0
        params = [f'{param}={line_aux_prop.get(param)}' for param in line_aux_prop]
        cmd_string = "new" + f" LINE.{storage_dss_name} " + " ".join(params)
        mdl.info(cmd_string) if debug else None
        dss.run_command(cmd_string)
        dss.run_command("calcv")

    sw_gen = [(0, 1) for _ in range(len(dss_sw_elements))]
    sw_comb = [comb for comb in itertools.product(*sw_gen)]

    pf_results = {}
    if tse_sw_elements:
        stability_data.update({"switches": tse_sw_elements})
        stability_data.update({"initial_sw_states": tuple(initial_condition)})
        for cnt, comb in enumerate(sw_comb):
            for idx, sw_element in enumerate(dss_sw_elements):
                dss.Circuit.SetActiveElement(sw_element)
                if comb[idx] == 0:
                    dss.CktElement.Open(0, 0)
                    dss.CktElement.Open(1, 0)
                elif comb[idx] == 1:
                    dss.CktElement.Close(0, 0)
                    dss.CktElement.Close(1, 0)
            pf_results.update({comb: get_pf_results(mdl, dss)})
    else:
        sw_comb = ["no_sw"]
        stability_data.update({"switches": []})
        pf_results["no_sw"] = get_pf_results(mdl, dss)
        stability_data.update({"initial_sw_states": "no_sw"})
    # dss.run_command(f'Compile "{dss_file}"')  # Reset the dss file

    # Compensation Stage (Changing DSS properties to follow the THCC approach)
    restore_names_dict = {}
    dss_to_thcc_compensation(mdl, dss, "Bus", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Coupling", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Load", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Line", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Vsource", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Manual Switch", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Controlled Switch", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Three-Phase Transformer", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Storage", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Generator", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Fault", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "VSConverter", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Isource", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "Single-Phase Transformer", ts, restore_names_dict)
    dss_to_thcc_compensation(mdl, dss, "PV System", ts, restore_names_dict)

    tse_cpl_elements = []
    dss_cpl_elements = []
    for coupling_handle in get_all_dss_elements(mdl, comp_type=["Coupling"]):
        tse_cpl_elements.append(coupling_handle)
        dss_cpl_elements.append(f"LINE.{mdl.get_name(coupling_handle)}")

    if dss_cpl_elements:
        mdl.info("\nOpenDSS Coupling Assistance started...")
        all_report_data = {}
        stability_data.update({"couplings": tse_cpl_elements})

        for idx_el, element in enumerate(dss_cpl_elements):
            tse_name = mdl.get_name(tse_cpl_elements[idx_el])
            stability_data[tse_name] = {}
            # Report Vars
            report_cpl_data = {}
            report_cpl_data["name"] = tse_name

            case_data = {}
            if tse_sw_elements:
                for count, comb in enumerate(sw_comb):
                    for idx, sw_element in enumerate(dss_sw_elements):
                        dss.Circuit.SetActiveElement(sw_element)
                        if comb[idx] == 0:
                            dss.CktElement.Open(0, 0)
                            dss.CktElement.Open(1, 0)
                        elif comb[idx] == 1:
                            dss.CktElement.Close(0, 0)
                            dss.CktElement.Close(1, 0)
                    r1, r2, bus1, bus2, freq = get_zsc_impedances(mdl, mask_handle, dss, element, "matrix", ts)
                    case_data[comb] = {}
                    case_data[comb].update({"r1": r1, "r2": r2})
                    # Retrieve the Power flow data
                    case_data[comb].update({"power_flow": pf_results[comb][tse_name]})
            else:
                r1, r2, bus1, bus2, freq = get_zsc_impedances(mdl, mask_handle, dss, element, "matrix", ts)
                case_data["no_sw"] = {"r1": r1, "r2": r2}
                # Retrieve the Power flow data
                case_data["no_sw"].update({"power_flow": pf_results["no_sw"][tse_name]})
                mdl.info("----")

            stability_data[tse_name].update(case_data)
            stability_data[tse_name].update({"bus1": bus1, "bus2": bus2, "freq": freq})

            cpl_bus1 = stability_data[tse_name].get("bus1")
            cpl_bus2 = stability_data[tse_name].get("bus2")
            cpl_freq = stability_data[tse_name].get("freq")
            mode = mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "auto_mode"))
            if mode == "Manual":
                # Vars
                report_cpl_data["mode"] = "Manual"

                # Snubbers
                current_side_snubber = True
                voltage_side_snubber = True
                itm_csnb_type = mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_type"))
                itm_vsnb_type = mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_type"))
                if itm_csnb_type == "none":
                    r1_snb = 1e12
                    current_side_snubber = False
                    report_cpl_data["csnb_value"] = f"none"
                    report_cpl_data["csnb_impedance"] = 0
                elif itm_csnb_type == "R1":
                    r1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_r")))
                    r1_snb = r1_cc_snb
                    report_cpl_data["csnb_value"] = f"R1={sc_notation(r1_cc_snb)}Ω"
                    report_cpl_data["csnb_impedance"] = r1_cc_snb + 0*1j
                elif itm_csnb_type == "R1-C1":
                    r1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_r")))
                    c1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_c")))
                    r1_snb = r1_cc_snb + ts/c1_cc_snb
                    report_cpl_data["csnb_value"] = f"R1={sc_notation(r1_cc_snb)}Ω, C1={sc_notation(c1_cc_snb)}F"
                    report_cpl_data["csnb_impedance"] = r1_cc_snb - (1/(2*np.pi*cpl_freq*c1_cc_snb))*1j

                if itm_vsnb_type == "none":
                    r2_snb = 0
                    voltage_side_snubber = False
                    report_cpl_data["vsnb_value"] = f"none"
                    report_cpl_data["vsnb_impedance"] = 0
                elif itm_vsnb_type == "R2":
                    r2_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_r")))
                    r2_snb = r2_cc_snb
                    report_cpl_data["vsnb_value"] = f"R2={sc_notation(r2_cc_snb)}Ω"
                    report_cpl_data["vsnb_impedance"] = r2_cc_snb + 0*1j
                elif itm_vsnb_type == "R2||L1":
                    r2_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_r")))
                    l1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_l")))
                    l1_cc_snb_r = (1/ts)*l1_cc_snb
                    r2_snb = r2_cc_snb*l1_cc_snb_r/(r2_cc_snb+l1_cc_snb_r)
                    report_cpl_data["vsnb_value"] = f"R2={sc_notation(r2_cc_snb)}Ω, L1={sc_notation(l1_cc_snb)}H"
                    report_cpl_data["vsnb_impedance"] = (r2_cc_snb*(2*np.pi*cpl_freq*l1_cc_snb)*1j) / (r2_cc_snb+(2*np.pi*cpl_freq*l1_cc_snb)*1j)

                cs_top_conflict, vs_topconflict = check_topological_conflicts(mdl, dss, tse_cpl_elements[idx_el], restore_names_dict)
                topological_status_msg = "No"
                topological_conflict_msg = []

                if len(cs_top_conflict) > 0:
                    topological_status_msg = "Yes"
                    topological_conflict_msg.append(
                        f"- There are topological conflicts between {mdl.get_name(tse_cpl_elements[idx_el])} and {', '.join(cs_top_conflict)}."
                        f"\n  Please, considers to use a snubber at the current source side of the {mdl.get_name(tse_cpl_elements[idx_el])}")

                if len(vs_topconflict) > 0:
                    topological_status_msg = "Yes"
                    topological_conflict_msg.append(
                        f"- There are topological conflicts between {mdl.get_name(tse_cpl_elements[idx_el])} and {', '.join(vs_topconflict)}."
                        f"\n  Please, considers to use a snubber at the voltage source side of the {mdl.get_name(tse_cpl_elements[idx_el])}")

                report_cpl_data['topological_status_msg'] = topological_status_msg
                report_cpl_data["top_conflicts"] = topological_conflict_msg

                # Stability Check
                for count, comb in enumerate(sw_comb):
                    r1_fixed = [rdss*r1_snb/(rdss + r1_snb) for rdss in stability_data[tse_name][comb].get("r1")]
                    r2_fixed = [rdss + r2_snb for rdss in stability_data[tse_name][comb].get("r2")]
                    mdl.info(f"{r1_fixed=}") if debug else None
                    mdl.info(f"{r2_fixed=}") if debug else None
                    stability_data[tse_name][comb].update({"r1_fixed": r1_fixed})
                    stability_data[tse_name][comb].update({"r2_fixed": r2_fixed})
                    z_ratio = [_r1/_r2 for _r1, _r2 in zip(r1_fixed, r2_fixed)]
                    cpl_stable = []
                    cpl_msg = []
                    for z in z_ratio:
                        if z > 1.1:
                            cpl_stable.append(0)
                            # stability_data[tse_name][comb].update({"stability": "unstable"})
                            # mdl.info(f"Stability Info: {mdl.get_name(tse_cpl_elements[idx_el])} is unstable.\n")
                            cpl_msg = f"- A flip on the {report_cpl_data['name']} might solve this issue."
                            report_cpl_data["stability"] = "unstable"
                            report_cpl_data["stability_tip"] = cpl_msg
                        elif 0.9 < z < 1.1:
                            cpl_stable.append(2)
                            # mdl.info(f"Stability Info: {mdl.get_name(tse_cpl_elements[idx_el])} is around stability border.\n")
                            # stability_data[tse_name][comb].update({"stability": "around stability border"})
                            report_cpl_data["stability"] = "around stability border"
                            if z >= 1.0:
                                cpl_msg = f"- A flip on the {report_cpl_data['name']} and an increase in its snubbers might solve this issue might solve this issue."
                                report_cpl_data['stability_tip'] = cpl_msg
                                # stability_data[tse_name][comb].update({"stability_tip": msg})
                            else:
                                cpl_msg = f"- An increase in the {report_cpl_data['name']}'s snubbers might solve this issue."
                                report_cpl_data['stability_tip'] = cpl_msg
                                # stability_data[tse_name][comb].update({"stability_tip": msg})
                        else:
                            cpl_stable.append(1)
                            # mdl.info(f"Stability Info: {mdl.get_name(tse_cpl_elements[idx_el])} is stable.\n")
                            stability_data[tse_name][comb].update({"stability": "stable"})
                            report_cpl_data["stability"] = "stable"
                        stability_data[tse_name][comb].update({"stability_tip": cpl_msg})

                    stability_data[tse_name].update({"report_cpl": report_cpl_data})
                    stability_data[tse_name][comb].update({"stability": cpl_stable})

            elif mode == "Automatic":
                report_cpl_data["mode"] = "Automatic"

                # Set the initial_state as reference for the flip operations
                ini_state = stability_data.get("initial_sw_states")
                r1_cpl = stability_data.get(tse_name).get(ini_state).get("r1")
                r2_cpl = stability_data.get(tse_name).get(ini_state).get("r2")
                flip_status = mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "flip_status"))
                if flip_status:
                    r1_cpl, r2_cpl = r2_cpl, r1_cpl
                z_ratio = [rth1/rth2 for rth1, rth2 in zip(r1_cpl, r2_cpl)]

                cpl_stable = []
                flip_candidate = 0
                for z in z_ratio:
                    if z > 1.1:
                        cpl_stable.append(0)
                        flip_candidate += 1
                    elif 0.9 < z < 1.1:
                        cpl_stable.append(2)
                        if z >= 1:
                            flip_candidate += 1
                    else:
                        cpl_stable.append(1)
                if flip_candidate > 1:
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "flip_status"), not flip_status)
                    report_cpl_data["stability_tip"] = f"- Flip action done."
                stability_data[tse_name][ini_state].update({"stability": cpl_stable})

                flip_status = mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "flip_status"))
                for count, comb in enumerate(sw_comb):
                    _r1 = stability_data.get(tse_name).get(comb).get("r1")
                    _r2 = stability_data.get(tse_name).get(comb).get("r2")
                    if flip_status:
                        _r1, _r2 = _r2, _r1
                        cpl_bus1, cpl_bus2 = cpl_bus2, cpl_bus1
                        stability_data.get(tse_name).get(comb).update({"stability_tip": f"- Flip action done."})
                    stability_data.get(tse_name).get(comb).update({"r1_fixed": _r1})
                    stability_data.get(tse_name).get(comb).update({"r2_fixed": _r2})
                    stability_data.get(tse_name).update({"bus1": cpl_bus1})
                    stability_data.get(tse_name).update({"bus2": cpl_bus2})

                # Snubbers Evaluation
                for count, comb in enumerate(sw_comb):
                    set_snubber = False
                    max_power = 1e-6 + 1e-6*1j  # For compute the snubber impedance
                    max_current = 1e-6 + 1e-6*1j
                    max_voltage = 1e-6 + 1e-6*1j
                    # Stability
                    r1_cpl = stability_data.get(tse_name).get(comb).get("r1_fixed")
                    r2_cpl = stability_data.get(tse_name).get(comb).get("r2_fixed")
                    z_ratio = [rth1 / rth2 for rth1, rth2 in zip(r1_cpl, r2_cpl)]
                    cpl_stable = []
                    for z in z_ratio:
                        if z > 1.1:
                            cpl_stable.append(0)
                            set_snubber = True
                        elif 0.9 < z > 1.1:
                            cpl_stable.append(2)
                            set_snubber = True
                        else:
                            cpl_stable.append(1)
                    stability_data[tse_name][comb].update({"stability": cpl_stable})
                    # Power
                    pf_data = stability_data.get(f"{tse_name}").get(comb).get(f"power_flow")
                    phases = int(len(pf_data.get("power")) / 2 / 2)
                    for idx in range(phases):
                        pf_power_aux = pf_data.get("power")[2 * idx] + pf_data.get("power")[2 * idx + 1] * 1j
                        pf_current_aux = pf_data.get("current")[2 * idx] + pf_data.get("current")[2 * idx + 1] * 1j
                        pf_voltage_aux = pf_data.get("voltage")[2 * idx] + pf_data.get("voltage")[2 * idx + 1] * 1j
                        if round(np.absolute(pf_power_aux), 3) > round(np.absolute(max_power), 3):
                            max_power = pf_power_aux
                            max_current = pf_current_aux
                            max_voltage = pf_voltage_aux

                if set_snubber:
                    internal_cpl_handle = mdl.get_item("Coupling", parent=tse_cpl_elements[idx_el])
                    factor = 0.01
                    # Current Source Side
                    csnb_z = np.absolute(max_voltage)**2/(np.absolute(max_power)*factor)
                    csnb_c = 1 / (2*np.pi*cpl_freq*csnb_z)
                    csnb_r = ts / csnb_c
                    csnb_req = csnb_r + (ts/csnb_c)
                    mdl.set_property_value(mdl.prop(internal_cpl_handle, "snb_type_i"), "R1-C1")
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_r_auto"), csnb_r)
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_c_auto"), csnb_c)
                    report_cpl_data["csnb_value"] = f"R1={sc_notation(csnb_r)}Ω, C1={sc_notation(csnb_c)}F"
                    report_cpl_data["csnb_impedance"] = csnb_r - (1/(2*np.pi*cpl_freq*csnb_c))*1j
                    # Voltage Source Side
                    vsnb_z = np.absolute(max_voltage)*factor/np.absolute(max_current)
                    vsnb_l = vsnb_z / (2*np.pi*cpl_freq)
                    vsnb_r = vsnb_l / ts
                    vsnb_req = vsnb_r*(1/ts)*vsnb_l / (vsnb_r + (1/ts)*vsnb_l)
                    mdl.set_property_value(mdl.prop(internal_cpl_handle, "snb_type_u"), "R2||L1")
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_r_auto"), vsnb_r)
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_l_auto"), vsnb_l)
                    report_cpl_data["vsnb_value"] = f"R2={sc_notation(vsnb_r)}Ω, L1={sc_notation(vsnb_l)}H"
                    report_cpl_data["vsnb_impedance"] = (vsnb_r*(2*np.pi*cpl_freq*vsnb_l)*1j) / (vsnb_r+(2*np.pi*cpl_freq*vsnb_l)*1j)
                else:
                    internal_cpl_handle = mdl.get_item("Coupling", parent=tse_cpl_elements[idx_el])
                    # Current Source Side
                    csnb_r = 1e6
                    csnb_req = csnb_r
                    mdl.set_property_value(mdl.prop(internal_cpl_handle, "snb_type_i"), "R1")
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_r_auto"), csnb_r)
                    report_cpl_data["csnb_value"] = f"R1={sc_notation(csnb_r)}Ω"
                    report_cpl_data["csnb_impedance"] = csnb_r + 0*1j
                    # Voltage Source Side
                    vsnb_r = 1e-3
                    vsnb_req = vsnb_r
                    mdl.set_property_value(mdl.prop(internal_cpl_handle, "snb_type_u"), "R2")
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_r_auto"), vsnb_r)
                    report_cpl_data["vsnb_value"] = f"R2={sc_notation(vsnb_r)}Ω"
                    report_cpl_data["vsnb_impedance"] = vsnb_r + 0*1j

                # Adding snubbers influence
                for count, comb in enumerate(sw_comb):
                    r1_new = [_r1*csnb_req/(_r1+csnb_req) for _r1 in stability_data.get(tse_name).get(comb).get("r1_fixed")]
                    r2_new = [_r2 + vsnb_req for _r2 in stability_data.get(tse_name).get(comb).get("r2_fixed")]
                    stability_data.get(tse_name).get(comb).update({"r1_fixed": r1_new})
                    stability_data.get(tse_name).get(comb).update({"r2_fixed": r2_new})

                report_cpl_data['topological_status_msg'] = "No"
                stability_data[tse_name].update({"report_cpl": report_cpl_data})

        mdl.info(f"- Detailed stability report saved on: {stability_data['dss_folder']}\stability_report.txt")
        detailed_report(mdl, stability_data)
        mdl.info(f"\nSummary Report:")
        summary_report(mdl, stability_data)
        mdl.info("-"*window_report)
        mdl.info("Stability analysis Completed.")
        dss.run_command(f'Compile "{dss_file}"')
    else:
        stability_data.update({"couplings": []})


def get_all_dss_elements(mdl, comp_type, parent_comp=None):

    component_list = []
    if parent_comp:  # Component inside a subsystem (recursive function)
        all_components = mdl.get_items(parent_comp)
    else:  # Top level call
        all_components = mdl.get_items()

    for comp in all_components:
        try:
            type_name = mdl.get_component_type_name(comp)
            if type_name and type_name in comp_type and mdl.is_enabled(comp):
                component_list.append(comp)
            elif not type_name:  # Component is a subsystem
                component_list.extend(get_all_dss_elements(mdl, [mdl.get_mask(comp)], parent_comp=comp))
        except:
            # Some components (such as ports and connections) cannot be used with
            # get_component_type_name
            pass
    # Return the list of component handles
    return component_list


def get_zsc_impedances(mdl, mask_handle, dss, coupling_line, mode, ts):

    freq = float(mdl.get_property_value(mdl.prop(mask_handle, "baseFreq")))
    scale_l = (1/ts)/(2*np.pi*freq)  # Use as "scale_l*X"
    scale_c = ts*(2*np.pi*freq)  # Use as "scale_c*Xc"
    debug = False

    if mode == "matrix":

        dss.run_command("Solve Mode=FaultStudy")
        dss.run_command("calcv")
        dss.Circuit.SetActiveElement(coupling_line)
        bus = [bus_name for bus_name in dss.CktElement.BusNames()]
        bus1 = bus[0]
        bus2 = bus[1]

        # I should to remove the reactors created during the compensation stage
        dss.run_command("calcv")
        dss.Circuit.SetActiveBus(bus1.split(".")[0])
        bus1_snb_list = []
        bus2_snb_list = []
        pce_pde = dss.Bus.AllPCEatBus() + dss.Bus.AllPDEatBus()
        for connected_element in pce_pde:
            reactor_match = re.match(r"^REACTOR.(.+)_([VC])(?:SIDE_snb\d$)", connected_element, re.IGNORECASE)
            if reactor_match:
                if reactor_match.group(1).lower() == coupling_line.split(".")[-1].lower():
                    bus1_snb_list.append(connected_element)

        dss.run_command("calcv")
        dss.Circuit.SetActiveBus(bus2.split(".")[0])
        pce_pde = dss.Bus.AllPCEatBus() + dss.Bus.AllPDEatBus()
        for connected_element in pce_pde:
            reactor_match = re.match(r"^REACTOR.(.+)_([VC])(?:SIDE_snb\d$)", connected_element, re.IGNORECASE)
            if reactor_match:
                if reactor_match.group(1).lower() == coupling_line.split(".")[-1].lower():
                    bus2_snb_list.append(connected_element)

        [dss.run_command(f"{pde}.enabled=no") for pde in bus1_snb_list]
        [dss.run_command(f"{pde}.enabled=no") for pde in bus2_snb_list]

        dss.run_command("Solve Mode=FaultStudy")
        # Thevenin Impedances
        # Bus1
        dss.run_command("calcv")
        dss.Circuit.SetActiveBus(bus1.split(".")[0])
        dss.Bus.ZscRefresh()
        zsc_matrix = [round(elem, 6) for elem in dss.Bus.ZscMatrix()]
        #zsc_matrix = [elem for elem in dss.Bus.ZscMatrix()]
        n_phases = int(np.sqrt(len(zsc_matrix)/2))
        rsc_array = np.array(zsc_matrix[0::2])
        xsc_array = np.array(zsc_matrix[1::2])
        rsc_matrix = rsc_array.reshape(n_phases, n_phases)
        xsc_matrix = xsc_array.reshape(n_phases, n_phases)
        mdl.info(f"{coupling_line}") if debug else None
        mdl.info("Current Side") if debug else None
        mdl.info(f"{rsc_matrix=}") if debug else None
        mdl.info(f"{xsc_matrix=}") if debug else None
        zsc1 = [float(z) for z in dss.Bus.Zsc1()]
        zsc0 = [float(z) for z in dss.Bus.Zsc0()]
        mdl.info(f"{zsc1=}") if debug else None
        mdl.info(f"{zsc0=}") if debug else None
        thil_sc = np.zeros(len(rsc_array))
        for idx in range(len(rsc_array)):
            r_aux = rsc_array[idx]
            x_aux = xsc_array[idx]
            if xsc_array[idx] >= 0:
                thil_sc[idx] = r_aux + scale_l * x_aux
            else:
                thil_sc[idx] = r_aux + scale_c * x_aux
        thil_sc_matrix = thil_sc.reshape(n_phases, n_phases)
        mdl.info(f"{thil_sc_matrix=}") if debug else None
        # Current sources ITM uses self impedance
        r1 = []
        for idx in range(n_phases):
            r1.append(thil_sc_matrix[idx, idx])

        # Bus2
        dss.run_command("calcv")
        dss.Circuit.SetActiveBus(bus2.split(".")[0])
        dss.Bus.ZscRefresh()
        zsc_matrix = [round(elem, 6) for elem in dss.Bus.ZscMatrix()]
        #zsc_matrix = [elem for elem in dss.Bus.ZscMatrix()]
        n_phases = int(np.sqrt(len(zsc_matrix)/2))
        rsc_array = np.array(zsc_matrix[0::2])
        xsc_array = np.array(zsc_matrix[1::2])
        rsc_matrix = rsc_array.reshape(n_phases, n_phases)
        xsc_matrix = xsc_array.reshape(n_phases, n_phases)
        mdl.info("Voltage Side") if debug else None
        mdl.info(f"{rsc_matrix=}") if debug else None
        mdl.info(f"{xsc_matrix=}") if debug else None
        zsc1 = [float(z) for z in dss.Bus.Zsc1()]
        zsc0 = [float(z) for z in dss.Bus.Zsc0()]
        mdl.info(f"{zsc1=}") if debug else None
        mdl.info(f"{zsc0=}") if debug else None

        thil_sc = np.zeros(len(rsc_array))
        for idx in range(len(rsc_array)):
            r_aux = rsc_array[idx]
            x_aux = xsc_array[idx]
            if x_aux >= 0:
                thil_sc[idx] = r_aux + scale_l * x_aux
            else:
                thil_sc[idx] = r_aux + scale_c * x_aux
        thil_sc_matrix = thil_sc.reshape(n_phases, n_phases)
        mdl.info(f"{thil_sc_matrix=}") if debug else None
        # Voltage sources ITM uses kron reduction
        r2 = []
        for idx in range(n_phases):
            # resistance
            k = thil_sc_matrix[idx, idx]
            l = np.array([thil_sc_matrix[idx, yvec] for yvec in range(n_phases) if yvec != idx]).reshape(1, n_phases-1)
            lt = np.array([thil_sc_matrix[xvec, idx] for xvec in range(n_phases) if xvec != idx]).reshape(n_phases-1, 1)
            m = np.array([thil_sc_matrix[xvec, yvec]
                          for xvec in range(n_phases) if xvec != idx
                          for yvec in range(n_phases) if yvec != idx]).reshape(n_phases-1, n_phases-1)
            try:
                r2.append(k - np.dot(np.dot(l, np.linalg.inv(m)), lt)[0, 0])
            except:
                r2.append(0)

        # I should to add the reactors created during the compensation stage
        [dss.run_command(f"{pde}.enabled=yes") for pde in bus1_snb_list]
        [dss.run_command(f"{pde}.enabled=yes") for pde in bus2_snb_list]
        #[mdl.info(f"{pde}.enabled=yes") for pde in bus1_snb_list]
        #[mdl.info(f"{pde}.enabled=yes") for pde in bus2_snb_list]

        dss.run_command("calcv")
        dss.run_command("Solve Mode=Snap")
        #mdl.info(f"[{r1[0]}, {r2[0]}]")if debug else None
        mdl.info(f"{r1=}") if debug else None
        mdl.info(f"{r2=}") if debug else None

    return r1, r2, bus1, bus2, freq


def dss_to_thcc_compensation(mdl, dss, element_type, ts, restore_dict):

    debug = False

    if element_type == "Bus":
        # Add Snubbers of the Three-Phase Meters
        mdl.info("Bus Compensation Stage...") if debug else None
        for bus_handle in get_all_dss_elements(mdl, comp_type=["Bus"]):
            bus_name = mdl.get_fqn(bus_handle).replace(".", "_").upper()
            mdl.info(f"Bus: {bus_name}") if debug else None

            if mdl.get_item("meter_3ph", parent=bus_handle):
                snb_prop = {}
                snb_prop["bus1"] = f"{bus_name}.1.2.3"
                snb_prop["phases"] = 3
                snb_prop["R"] = 1e5
                snb_prop["X"] = 1e-9
                params = [f'{param}={snb_prop.get(param)}' for param in snb_prop]
                cmd_string = "new" + f" REACTOR.{bus_name}_meter_snb " + " ".join(params)
                mdl.info(cmd_string) if debug else None
                dss.run_command(cmd_string)
                dss.run_command("calcv")

    elif element_type == "Vsource":
        # Convert to pure resistive impedance
        mdl.info("Vsource Compensation Stage...") if debug else None
        for vsource_handle in get_all_dss_elements(mdl, comp_type=["Vsource"]):
            dss_vsource_name = mdl.get_fqn(vsource_handle).replace(".", "_").upper()
            mdl.info(f"Vsource: {dss_vsource_name}") if debug else None
            dss.Circuit.SetActiveElement(f"VSOURCE.{dss_vsource_name}")

            freq = float(dss.Properties.Value("frequency"))
            scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
            r1 = float(dss.Properties.Value("R1"))
            r0 = float(dss.Properties.Value("R0"))
            x1 = float(dss.Properties.Value("X1"))
            x0 = float(dss.Properties.Value("X0"))

            r1_new = r1 + x1 * scale_l
            x1_new = 1e-6
            r0_new = r0 + x0 * scale_l
            x0_new = 1e-6
            dss.Properties.Value("R1", str(r1_new))
            dss.Properties.Value("R0", str(r0_new))
            dss.Properties.Value("X1", str(x1_new))
            dss.Properties.Value("X0", str(x0_new))
            dss.run_command("calcv")

    elif element_type == "Line":
        # Convert to pure resistive impedance
        mdl.info("Line Compensation Stage...") if debug else None
        for line_handle in get_all_dss_elements(mdl, comp_type=["Line"]):
            dss_line_name = mdl.get_fqn(line_handle).replace(".", "_").upper()
            mdl.info(f"Line: {dss_line_name}") if debug else None
            dss.Circuit.SetActiveElement(f"LINE.{dss_line_name}")

            freq = float(dss.Solution.Frequency())
            scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
            scale_c = ts * (2 * np.pi * freq)  # Use as "scale_c*Xc"

            rmatrix = dss.Lines.RMatrix()
            xmatrix = dss.Lines.XMatrix()
            cmatrix = dss.Lines.CMatrix()
            n_phases = int(np.sqrt(len(rmatrix)))

            rmatrix_compensated = np.zeros(len(rmatrix))
            xmatrix_compensated = np.zeros(len(rmatrix))
            cmatrix_compensated = np.zeros(len(rmatrix))
            for idx in range(len(rmatrix)):
                rmatrix_compensated[idx] = rmatrix[idx] + scale_l * xmatrix[idx]
                xmatrix_compensated[idx] = 1e-6
                cmatrix_compensated[idx] = 0

            rmatrix_compensated = rmatrix_compensated.reshape(n_phases, n_phases)
            xmatrix_compensated = xmatrix_compensated.reshape(n_phases, n_phases)
            cmatrix_compensated = cmatrix_compensated.reshape(n_phases, n_phases)
            dss.Lines.RMatrix(rmatrix_compensated)
            dss.Lines.XMatrix(xmatrix_compensated)
            dss.Lines.CMatrix(cmatrix_compensated)

            # Reshaping for debug purposes
            rmatrix = np.array(rmatrix).reshape(n_phases, n_phases)
            xmatrix = np.array(xmatrix).reshape(n_phases, n_phases)
            cmatrix = np.array(cmatrix).reshape(n_phases, n_phases)
            mdl.info(f"{rmatrix=}") if debug else None
            mdl.info(f"{xmatrix=}") if debug else None
            mdl.info(f"{cmatrix=}") if debug else None
            mdl.info(f"{rmatrix_compensated=}") if debug else None

            # Creating the capacitors as reactors (only resistive values)
            # TODO Check how to convert mutual capacitors to the resistive branch (getting only the self value)
            bus1, bus2 = [bus_name.split(".")[0] for bus_name in dss.CktElement.BusNames()]
            bus1_nodes, bus2_nodes = [bus_name.split(".")[1:] for bus_name in dss.CktElement.BusNames()]
            for idx in bus1_nodes:
                pos = int(idx)-1
                if cmatrix[pos, pos] > 0:
                    snb1_prop = {}
                    req_cap = ts / (1e-9*cmatrix[pos, pos]/2)
                    snb1_prop["bus1"] = f"{bus1}.{idx}"
                    snb1_prop["phases"] = 1
                    snb1_prop["R"] = req_cap
                    snb1_prop["X"] = 1e-9
                    params = [f'{param}={snb1_prop.get(param)}' for param in snb1_prop]
                    cmd_string = "new" + f" REACTOR.{dss_line_name}_CAP1_snb{idx} " + " ".join(params)
                    mdl.info(cmd_string) if debug else None
                    dss.run_command(cmd_string)

                    snb2_prop = {}
                    snb2_prop["bus1"] = f"{bus2}.{idx}"
                    snb2_prop["phases"] = 1
                    snb2_prop["R"] = req_cap
                    snb2_prop["X"] = 1e-9
                    params = [f'{param}={snb2_prop.get(param)}' for param in snb2_prop]
                    cmd_string = "new" + f" REACTOR.{dss_line_name}_CAP2_snb{idx} " + " ".join(params)
                    mdl.info(cmd_string) if debug else None
                    dss.run_command(cmd_string)

                dss.run_command("calcv")

    elif element_type == "Load":
        # Convert to pure resistive impedance
        mdl.info("Load Compensation Stage...") if debug else None
        for load_handle in get_all_dss_elements(mdl, comp_type=["Load"]):
            dss_load_name = mdl.get_fqn(load_handle).replace(".", "_").upper()
            mdl.info(f"Load: {dss_load_name}") if debug else None
            dss.Circuit.SetActiveElement(f"LOAD.{dss_load_name}")

            model = int(dss.Properties.Value("model"))
            kv = float(dss.Properties.Value("kV"))
            pf = float(dss.Properties.Value("pf"))
            kva = float(dss.Properties.Value("KVA"))
            freq = float(dss.Properties.Value("basefreq"))
            conn = dss.Properties.Value("conn")
            scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
            scale_c = ts * (2 * np.pi * freq)  # Use as "scale_c*Xc"
            mdl.info(f"{kv=}") if debug else None
            mdl.info(f"{kva=}") if debug else None
            if model in [2]:
                # Constant Impedance
                z_load = 1e3 * kv * kv / kva
                r_load = z_load * np.abs(pf)
                if pf > 0:
                    l_load = z_load * ((1 - pf ** 2) ** 0.5) / (2 * np.pi * freq)
                    r_eq = r_load + (1 / ts) * l_load
                else:
                    c_load = 1 / (z_load * 2 * np.pi * freq * ((1 - np.abs(pf) ** 2) ** 0.5))
                    r_eq = r_load + (ts / c_load)

            elif model in [1, 8]:
                # Constant Power or ZIP
                # Equations from the CPL component
                rsnb = 30 * (1e3 * kv * kv / (1.66 * kva))
                csnb = 1 / (1 * rsnb * 2 * np.pi * freq)
                rsnb = rsnb / 15
                # Those resistances are in parallel from the THCC viewpoint
                r_eq = rsnb * (ts / csnb) / (rsnb + (ts / csnb))

            p_load = 1e6 * kv * kv / r_eq
            dss.Properties.Value("kvar", f"{0}")
            dss.Properties.Value("kW", f"{p_load/1e3}")

            mdl.info(f"{dss.Properties.Value('kvar')=}") if debug else None
            mdl.info(f"{dss.Properties.Value('kW')=}") if debug else None
            mdl.info(f"{dss.Properties.Value('pf')=}") if debug else None

            # WorkAround for Yz loads (The coupling gets 4 phases instead 3)
            load_bus = dss.Properties.Value('bus1').split(".")[0]
            load_nodes = dss.Properties.Value('bus1').split(".")[1:]
            if "4" in load_nodes:
                load_nodes.remove("4")
                dss.CktElement.Enabled(False)
                load_rneut = float(dss.Properties.Value("Rneut"))
                load_xneut = float(dss.Properties.Value("Xneut"))
                if load_rneut != -1:
                    if load_xneut >= 0:
                        rneut_eq = load_rneut + scale_l*load_xneut
                    else:
                        rneut_eq = load_rneut + scale_c * load_xneut
                else:
                    rneut_eq = 1e9

                for load_ph in load_nodes:
                    snb1_prop = {}
                    snb1_prop["bus1"] = f"{load_bus}.{load_ph}"
                    snb1_prop["bus2"] = f"aux1_{load_bus}.4"
                    snb1_prop["phases"] = 1
                    snb1_prop["R"] = r_eq
                    snb1_prop["X"] = 1e-9
                    params = [f'{param}={snb1_prop.get(param)}' for param in snb1_prop]
                    cmd_string = "new" + f" REACTOR.{dss_load_name.upper()}_ph{load_ph} " + " ".join(params)
                    restore_dict[f" REACTOR.{dss_load_name.upper()}_ph{load_ph} "] = f"LOAD.{dss_load_name.upper()}"
                    mdl.info(cmd_string) if debug else None
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")

                snb2_prop = {}
                snb2_prop["bus1"] = f"aux1_{load_bus}.4"
                snb2_prop["bus2"] = f"aux2_{load_bus}.0"
                snb2_prop["phases"] = 1
                snb2_prop["R"] = rneut_eq
                snb2_prop["X"] = 1e-9
                params = [f'{param}={snb2_prop.get(param)}' for param in snb2_prop]
                cmd_string = "new" + f" REACTOR.{dss_load_name.upper()}_ph{load_ph}_gnd " + " ".join(params)
                mdl.info(cmd_string) if debug else None
                dss.run_command(cmd_string)
                dss.run_command("calcv")

            # WorkAround for delta loads (dss needs a connection to the ground to performs the matrix inversion)
            if conn == "delta":
                for load_ph in load_nodes:
                    snb3_prop = {}
                    snb3_prop["bus1"] = f"{load_bus}.{load_ph}"
                    snb3_prop["bus2"] = f"aux2_{load_bus}.0"
                    snb3_prop["phases"] = 1
                    snb3_prop["R"] = 1e9
                    snb3_prop["X"] = 1e-9
                    params = [f'{param}={snb3_prop.get(param)}' for param in snb3_prop]
                    cmd_string = "new" + f" REACTOR.{dss_load_name.upper()}_{load_ph}_delta " + " ".join(params)
                    mdl.info(cmd_string) if debug else None
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")

    elif element_type == "Coupling":
        # Add Snubbers to the both sides of the Coupling (Those should be removed during its stability analysis stage)
        mdl.info("Coupling Compensation Stage...") if debug else None
        for coupling_handle in get_all_dss_elements(mdl, comp_type=["Coupling"]):
            # Opening DSS Line
            dss_coupling_name = mdl.get_fqn(coupling_handle).replace(".", "_").upper()
            mdl.info(f"Coupling: {dss_coupling_name}") if debug else None
            dss.Circuit.SetActiveElement(f"LINE.{dss_coupling_name}")

            dss.CktElement.Open(0, 0)
            bus1, bus2 = [bus_name.split(".")[0] for bus_name in dss.CktElement.BusNames()]
            bus1_nodes, bus2_nodes = [bus_name.split(".")[1:] for bus_name in dss.CktElement.BusNames()]
            if not mdl.get_property_value(mdl.prop(coupling_handle, "flip_status")):
                bus_current_side = bus1
                nodes_current_side = bus1_nodes
                bus_voltage_side = bus2
                nodes_voltage_side = bus2_nodes
            else:
                bus_current_side = bus2
                nodes_current_side = bus2_nodes
                bus_voltage_side = bus1
                nodes_voltage_side = bus1_nodes

            # Creating the Snubbers
            mode = mdl.get_property_value(mdl.prop(coupling_handle, "auto_mode"))
            itm_csnb_type = mdl.get_property_value(mdl.prop(coupling_handle, "itm_csnb_type"))
            itm_vsnb_type = mdl.get_property_value(mdl.prop(coupling_handle, "itm_vsnb_type"))
            if mode == "Automatic":
                req_cside = 50e6
                req_vside = 0
            elif mode == "Manual":
                if itm_csnb_type == "none":
                    req_cside = 50e6
                elif itm_csnb_type == "R1":
                    req_cside = mdl.get_property_value(mdl.prop(coupling_handle, "itm_csnb_r"))
                elif itm_csnb_type == "R1-C1":
                    rsnb = mdl.get_property_value(mdl.prop(coupling_handle, "itm_csnb_r"))
                    r_csnb = ts/mdl.get_property_value(mdl.prop(coupling_handle, "itm_csnb_c"))
                    req_cside = rsnb + r_csnb

                if itm_vsnb_type == "none":
                    req_vside = 1e-6
                elif itm_vsnb_type == "R2":
                    req_vside = mdl.get_property_value(mdl.prop(coupling_handle, "itm_vsnb_r"))
                elif itm_vsnb_type == "R2||L1":
                    rsnb = mdl.get_property_value(mdl.prop(coupling_handle, "itm_vsnb_r"))
                    r_lsnb = (1/ts)*mdl.get_property_value(mdl.prop(coupling_handle, "itm_vsnb_l"))
                    req_vside = rsnb*r_lsnb/(rsnb+r_lsnb)

            for idx in nodes_current_side:
                snb_prop = {}
                snb_prop["bus1"] = f"{bus_current_side}.{idx}"
                snb_prop["phases"] = 1
                snb_prop["R"] = req_cside
                snb_prop["X"] = 1e-9
                params = [f'{param}={snb_prop.get(param)}' for param in snb_prop]
                cmd_string = "new" + f" REACTOR.{dss_coupling_name}_CSIDE_SNB{idx} " + " ".join(params)
                mdl.info(cmd_string) if debug else None
                dss.run_command(cmd_string)
                restore_dict.update({f"REACTOR.{dss_coupling_name}_CSIDE_SNB{idx}": f"LINE.{dss_coupling_name}"})
            for idx in nodes_voltage_side:
                snb_prop = {}
                snb_prop["bus1"] = f"{bus_voltage_side}.{idx}"
                snb_prop["phases"] = 1
                snb_prop["R"] = req_vside
                snb_prop["X"] = 1e-6
                params = [f'{param}={snb_prop.get(param)}' for param in snb_prop]
                cmd_string = "new" + f" REACTOR.{dss_coupling_name}_VSIDE_SNB{idx} " + " ".join(params)
                mdl.info(cmd_string) if debug else None
                dss.run_command(cmd_string)
                restore_dict.update({f"REACTOR.{dss_coupling_name}_VSIDE_SNB{idx}": f"LINE.{dss_coupling_name}"})

    elif element_type == "Three-Phase Transformer":
        # Flip the Transformers (to match the core side)
        # Convert the leakage impedance into transmission lines in both sides of the inverter
        # The connection of the transmission lines is according to the connection type of the transformer
        mdl.info("Three-Phase Transformer Compensation Stage...") if debug else None
        for trf_handle in get_all_dss_elements(mdl, comp_type=["Three-Phase Transformer"]):
            dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
            mdl.info(f"Transformer: {dss_trf_name}") if debug else None

            # dss.run_command("calcv")
            dss.Transformers.Name(dss_trf_name)
            bus1, bus2 = [bus_name for bus_name in dss.CktElement.BusNames()]
            freq = float(dss.Properties.Value("basefreq"))
            scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
            scale_c = ts * (2 * np.pi * freq)

            # TODO Assuming two windigs for now (print a message if there is more than 2 windings)
            vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
            pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
            conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
            zbase = [1e3 * volt * volt / pot for volt, pot in zip(vbase, pbase)]
            if conn1 == "Δ":
                zbase[0] = zbase[0]*3
            if conn2 == "Δ":
                zbase[1] = zbase[1]*3
            mdl.info(f"{zbase=}") if debug else None
            xarray = [1e-2 * xval for xval in mdl.get_property_value(mdl.prop(trf_handle, "XArray"))]
            # Windings
            dss.Transformers.Xhl(1e-3)
            dss.Properties.Value("ppm_antifloat", "0.005")

            dss.Transformers.Wdg(1)
            rw1 = 1e-2 * dss.Transformers.R() * zbase[0]
            rw1_eq = rw1 + scale_l * xarray[0] * zbase[0]
            rw1_rneut = float(dss.Properties.Value("Rneut"))
            rw1_xneut = float(dss.Properties.Value("Xneut"))
            mdl.info(f"{rw1=}") if debug else None
            mdl.info(f"{rw1_eq=}") if debug else None
            dss.Transformers.R(100 * rw1_eq / zbase[0])

            dss.Transformers.Wdg(2)
            rw2 = 1e-2 * dss.Transformers.R() * zbase[1]
            rw2_eq = rw2 + scale_l * xarray[1] * zbase[1]
            rw2_rneut = float(dss.Properties.Value("Rneut"))
            rw2_xneut = float(dss.Properties.Value("Xneut"))
            dss.Transformers.R(100 * rw2_eq / zbase[1])
            mdl.info(f"{rw2=}") if debug else None
            mdl.info(f"{rw2_eq=}") if debug else None
            dss.run_command("calcv")

            noloadloss = 1e-2 * float(dss.Properties.Value("%noloadloss"))
            imag = 1e-2 * float(dss.Properties.Value("%imag"))

            # Compensation Stage
            dss.Transformers.Name(dss_trf_name)
            mdl.info(f"{dss.CktElement.Name()}") if debug else None
            dss.Transformers.Wdg(1)
            dss.Properties.Value("bus", f"isolated{bus1}")
            dss.Transformers.Wdg(2)
            dss.Properties.Value("bus", f"isolated{bus2}")
            # dss.CktElement.Enabled(False)  # Maybe DSS Bug. Disabled PD Elements are shown in allPDEElements function
            dss.CktElement.Open(0, 0)
            dss.CktElement.Open(1, 0)

            bus1 = bus1.split('.')[0]
            bus2 = bus2.split('.')[0]
            int_bus1 = f"int{bus1}"
            int_bus2 = f"int{bus2}"
            trf_names = ["t1", "t2", "t3"]
            if conn1 == "Δ":
                pri_nodes = ["1.2", "2.3", "3.1"]
                pri_kv = vbase[0]
            else:
                pri_nodes = ["1.4", "2.4", "3.4"]
                pri_kv = vbase[0]/np.sqrt(3)

            if conn2 == "Δ":
                sec_nodes = ["1.2", "2.3", "3.1"]
                sec_kv = vbase[1]
            else:
                sec_nodes = ["1.4", "2.4", "3.4"]
                sec_kv = vbase[1]/np.sqrt(3)

            pri_rmatrix = f"({rw1_eq} | 0 1e-6)"
            sec_rmatrix = f"({rw2_eq} | 0 1e-6)"
            xmatrix = f"(1e-6 | 0 1e-6)"
            cmatrix = f"(0 | 0 0)"

            core_loss = 0
            if noloadloss != 0 or imag != 0:
                try:
                    rloss = (1 / noloadloss) * zbase[1]
                except ZeroDivisionError:
                    rloss = 1e15
                try:
                    xmag = (1 / imag) * zbase[1]
                    rmag = scale_l * xmag
                except ZeroDivisionError:
                    rmag = 1e15

                rcore = rloss * rmag / (rloss + rmag)
                core_loss = 100*(zbase[1]/rcore)
                mdl.info(f"{core_loss=}") if debug else None

            for idx in range(3):
                trafo_prop = {}
                trafo_prop["Buses"] = f"[{int_bus2}_{trf_names[idx]}.1.2, {int_bus1}_{trf_names[idx]}.1.2]"
                trafo_prop["KVs"] = f"[{sec_kv}, {pri_kv}]"
                trafo_prop["KVAs"] = f"[{pbase[0]/3}, {pbase[1]/3}]"
                trafo_prop["XHL"] = "1e-4"
                trafo_prop["%Rs"] = "[0.1, 0.1]"
                trafo_prop["%noloadloss"] = core_loss
                trafo_prop["%imag"] = "0"
                trafo_prop["phases"] = "1"
                trafo_prop["ppm_antifloat"] = "0.005"
                params = [f'{param}={trafo_prop.get(param)}' for param in trafo_prop]
                cmd_string = "new" + f" TRANSFORMER.{dss_trf_name}_{trf_names[idx]} " + " ".join(params)
                mdl.info(cmd_string) if debug else None
                dss.run_command(cmd_string)
                dss.run_command("calcv")
                dss.Transformers.Wdg(1)
                dss.Properties.Value("Rneut", "-1")
                dss.Properties.Value("Xneut", "0")
                dss.Transformers.Wdg(2)
                dss.Properties.Value("Rneut", "-1")
                dss.Properties.Value("Xneut", "0")

                if conn1 == "Δ":
                    line_pri_prop = {}
                    line_pri_prop["bus1"] = f"{int_bus1}_{trf_names[idx]}.1.2"
                    line_pri_prop["bus2"] = f"{bus1}.{pri_nodes[idx]}"
                    line_pri_prop["phases"] = 2
                    line_pri_prop["rmatrix"] = pri_rmatrix
                    line_pri_prop["xmatrix"] = xmatrix
                    line_pri_prop["cmatrix"] = cmatrix
                    params = [f'{param}={line_pri_prop.get(param)}' for param in line_pri_prop]
                    cmd_string = "new" + f" LINE.{dss_trf_name}_{trf_names[idx]}_pricomp " + " ".join(params)
                    mdl.info(cmd_string) if debug else None
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")
                    restore_dict[
                        f"LINE.{dss_trf_name.upper()}_{trf_names[idx].upper()}_PRICOMP"] = f"TRANSFORMER.{dss_trf_name.upper()}"
                else:
                    line_pri_prop = {}
                    line_pri_prop["bus1"] = f"{int_bus1}_{trf_names[idx]}.1"
                    line_pri_prop["bus2"] = f"{bus1}.{pri_nodes[idx].split('.')[0]}"
                    line_pri_prop["phases"] = 1
                    line_pri_prop["R"] = rw1_eq
                    line_pri_prop["X"] = 1e-6
                    params = [f'{param}={line_pri_prop.get(param)}' for param in line_pri_prop]
                    cmd_string = "new" + f" REACTOR.{dss_trf_name}_{trf_names[idx]}_pricomp " + " ".join(params)
                    mdl.info(cmd_string) if debug else None
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")
                    restore_dict[f"REACTOR.{dss_trf_name.upper()}_{trf_names[idx].upper()}_PRICOMP"] = f"TRANSFORMER.{dss_trf_name.upper()}"

                    line_pri_neutral_prop = {}
                    line_pri_neutral_prop["bus1"] = f"{int_bus1}_{trf_names[idx]}.2"
                    line_pri_neutral_prop["bus2"] = f"auxZ_{bus1}.4"
                    line_pri_neutral_prop["phases"] = 1
                    line_pri_neutral_prop["R"] = 1e-6
                    line_pri_neutral_prop["X"] = 1e-6
                    params = [f'{param}={line_pri_neutral_prop.get(param)}' for param in line_pri_neutral_prop]
                    cmd_string = "new" + f" REACTOR.{dss_trf_name}_{trf_names[idx]}_prineutr " + " ".join(params)
                    mdl.info(cmd_string) if debug else None
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")

                if conn2 == "Δ":
                    line_sec_prop = {}
                    line_sec_prop["bus1"] = f"{int_bus2}_{trf_names[idx]}.1.2"
                    line_sec_prop["bus2"] = f"{bus2}.{sec_nodes[idx]}"
                    line_sec_prop["phases"] = 2
                    line_sec_prop["rmatrix"] = sec_rmatrix
                    line_sec_prop["xmatrix"] = xmatrix
                    line_sec_prop["cmatrix"] = cmatrix
                    params = [f'{param}={line_sec_prop.get(param)}' for param in line_sec_prop]
                    cmd_string = "new" + f" LINE.{dss_trf_name}_{trf_names[idx]}_seccomp " + " ".join(params)
                    mdl.info(cmd_string) if debug else None
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")
                    restore_dict[
                        f"LINE.{dss_trf_name.upper()}_{trf_names[idx].upper()}_SECCOMP"] = f"TRANSFORMER.{dss_trf_name.upper()}"
                else:
                    line_sec_prop = {}
                    line_sec_prop["bus1"] = f"{int_bus2}_{trf_names[idx]}.1"
                    line_sec_prop["bus2"] = f"{bus2}.{sec_nodes[idx].split('.')[0]}"
                    line_sec_prop["phases"] = 1
                    line_sec_prop["R"] = rw2_eq
                    line_sec_prop["X"] = 1e-6
                    params = [f'{param}={line_sec_prop.get(param)}' for param in line_sec_prop]
                    cmd_string = "new" + f" REACTOR.{dss_trf_name}_{trf_names[idx]}_seccomp " + " ".join(params)
                    mdl.info(cmd_string) if debug else None
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")
                    restore_dict[f"REACTOR.{dss_trf_name.upper()}_{trf_names[idx].upper()}_SECCOMP"] = f"TRANSFORMER.{dss_trf_name.upper()}"

                    line_sec_neutral_prop = {}
                    line_sec_neutral_prop["bus1"] = f"{int_bus2}_{trf_names[idx]}.2"
                    line_sec_neutral_prop["bus2"] = f"auxZ_{bus2}.4"
                    line_sec_neutral_prop["phases"] = 1
                    line_sec_neutral_prop["R"] = 1e-6
                    line_sec_neutral_prop["X"] = 1e-6
                    params = [f'{param}={line_sec_neutral_prop.get(param)}' for param in line_sec_neutral_prop]
                    cmd_string = "new" + f" REACTOR.{dss_trf_name}_{trf_names[idx]}_secneutr " + " ".join(params)
                    mdl.info(cmd_string) if debug else None
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")

            if conn1 != "Δ":
                if rw1_rneut != -1:
                    if rw1_xneut >= 0:
                        rw1_neut_eq = rw1_rneut + scale_l * rw1_xneut
                    else:
                        rw1_neut_eq = rw1_rneut + scale_c * rw1_xneut
                else:
                    rw1_neut_eq = 1e15

                snb1_prop = {}
                snb1_prop["bus1"] = f"auxZ_{bus1}.4"
                snb1_prop["bus2"] = f"{bus1}.0"
                snb1_prop["phases"] = 1
                snb1_prop["R"] = rw1_neut_eq
                snb1_prop["X"] = 1e-9
                params = [f'{param}={snb1_prop.get(param)}' for param in snb1_prop]
                cmd_string = "new" + f" REACTOR.{dss_trf_name.upper()}_zn1 " + " ".join(params)
                mdl.info(cmd_string) if debug else None
                dss.run_command(cmd_string)
                dss.run_command("calcv")

            if conn2 != "Δ":

                if rw2_rneut != -1:
                    if rw2_xneut >= 0:
                        rw2_neut_eq = rw2_rneut + scale_l * rw2_xneut
                    else:
                        rw2_neut_eq = rw2_rneut + scale_c * rw2_xneut
                else:
                    rw2_neut_eq = 1e15

                snb2_prop = {}
                snb2_prop["bus1"] = f"auxZ_{bus2}.4"
                snb2_prop["bus2"] = f"{bus2}.0"
                snb2_prop["phases"] = 1
                snb2_prop["R"] = rw2_neut_eq
                snb2_prop["X"] = 1e-9
                params = [f'{param}={snb2_prop.get(param)}' for param in snb2_prop]
                cmd_string = "new" + f" REACTOR.{dss_trf_name.upper()}_zn2 " + " ".join(params)
                mdl.info(cmd_string) if debug else None
                dss.run_command(cmd_string)
                dss.run_command("calcv")

    elif element_type in ["Manual Switch", "Controlled Switch"]:
        for swt_handle in get_all_dss_elements(mdl, comp_type=["Manual Switch", "Controlled Switch"]):
            dss_swt_name = mdl.get_fqn(swt_handle).replace(".", "_").upper()
            dss.Circuit.SetActiveElement(f"LINE.{dss_swt_name}")
            dss.Lines.C1(0)
            dss.Lines.C0(0)
            dss.Lines.X0(1e-3)
            dss.Lines.X1(1e-3)
            dss.Lines.R0(1e-3)
            dss.Lines.R1(1e-3)
            dss.run_command("calcv")
            restore_dict.update({f"LINE.{dss_swt_name.upper()}": f"SWITCH.{dss_swt_name.upper()}"})

    elif element_type == "Storage":
        # Disable the Storage and create Three Reactors (L and C filter branches, and meter snubbers)
        mdl.info("Storage Compensation Stage...") if debug else None
        for storage_handle in get_all_dss_elements(mdl, comp_type=["Storage"]):
            dss_storage_name = mdl.get_fqn(storage_handle).replace(".", "_").upper()
            mdl.info(f"Storage: {dss_storage_name}") if debug else None
            dss.Circuit.SetActiveElement(f"STORAGE.{dss_storage_name}")

            storage_bus = "".join(dss.Properties.Value("bus1").split("aux_")[1:])
            # Disabling the default storage
            dss.CktElement.Enabled(False)

            # Capacitive Filter (connected after the contactor) - Without the ground
            inv_rf = mdl.get_property_value(mdl.prop(storage_handle, "inv_rf"))
            inv_cf = mdl.get_property_value(mdl.prop(storage_handle, "inv_cf"))
            req_cap = inv_rf + ts / inv_cf
            snb_prop = {}
            snb_prop["bus1"] = f"aux_{storage_bus.split('.')[0]}"
            snb_prop["bus2"] = f"aux2_{storage_bus.split('.')[0]}.4.4.4"
            snb_prop["phases"] = 3
            snb_prop["R"] = req_cap
            snb_prop["X"] = 1e-9
            params = [f'{param}={snb_prop.get(param)}' for param in snb_prop]
            cmd_string = "new" + f" REACTOR.{dss_storage_name}_cf " + " ".join(params)
            mdl.info(cmd_string) if debug else None
            dss.run_command(cmd_string)
            dss.run_command("calcv")

            # Inductive Filter (connected after the contactor) - Without the ground
            inv_r = mdl.get_property_value(mdl.prop(storage_handle, "inv_r"))
            inv_l = mdl.get_property_value(mdl.prop(storage_handle, "inv_l"))
            req_ind = inv_r + (1/ts)*inv_l
            snb_prop = {}
            snb_prop["bus1"] = f"aux_{storage_bus.split('.')[0]}"
            snb_prop["bus2"] = f"aux2_{storage_bus.split('.')[0]}.4.4.4"
            snb_prop["phases"] = 3
            snb_prop["R"] = req_ind
            snb_prop["X"] = 1e-9
            params = [f'{param}={snb_prop.get(param)}' for param in snb_prop]
            cmd_string = "new" + f" REACTOR.{dss_storage_name}_lf " + " ".join(params)
            mdl.info(cmd_string) if debug else None
            dss.run_command(cmd_string)
            dss.run_command("calcv")

            # Meter Filter (connected before the contactor) - Grounded
            meter_handle = mdl.get_item("Three-phase Meter1", parent=storage_handle)
            if meter_handle:
                snb_r = mdl.get_property_value(mdl.prop(meter_handle, "R"))
                snb_prop = {}
                snb_prop["bus1"] = f"{storage_bus.split('.')[0]}"
                snb_prop["phases"] = 3
                snb_prop["R"] = snb_r
                snb_prop["X"] = 1e-9
                params = [f'{param}={snb_prop.get(param)}' for param in snb_prop]
                cmd_string = "new" + f" REACTOR.{dss_storage_name}_meter " + " ".join(params)
                mdl.info(cmd_string) if debug else None
                dss.run_command(cmd_string)
                dss.run_command("calcv")

    elif element_type == "Generator":
        # Disable the Generator and create One Reactor (Generator Impedance)
        mdl.info("Generator Compensation Stage...") if debug else None
        for generator_handle in get_all_dss_elements(mdl, comp_type=["Generator"]):
            dss_generator_name = mdl.get_fqn(generator_handle).replace(".", "_").upper()
            mdl.info(f"Generator: {dss_generator_name}") if debug else None
            dss.Circuit.SetActiveElement(f"GENERATOR.{dss_generator_name}")
            generator_bus = dss.Properties.Value("bus1").split(".")[0]

            # Disabling the default storage
            dss.CktElement.Enabled(False)

            freq = mdl.get_property_value(mdl.prop(generator_handle, "baseFreq"))
            ws = 2 * np.pi * freq
            kv = mdl.get_property_value(mdl.prop(generator_handle, "kv"))
            kva = mdl.get_property_value(mdl.prop(generator_handle, "kVA"))
            xd = mdl.get_property_value(mdl.prop(generator_handle, "Xd"))
            xdp = mdl.get_property_value(mdl.prop(generator_handle, "Xdp"))
            xdpp = mdl.get_property_value(mdl.prop(generator_handle, "Xdpp"))
            # Equations from the generator source code
            z_base = 1e3 * (kv * kv / kva)
            rs = 0.01 * z_base
            lmd = xd * z_base / ws
            lls = 0.05 * lmd
            llfd = (((xdp * z_base / ws) - lls) * lmd) / (lmd - ((xdp * z_base / ws) - lls))
            llkd = (((xdpp * z_base / ws) - lls) * llfd) / (llfd - ((xdpp * z_base / ws) - lls))
            lmzd = 1 / (1 / lmd + 1 / llkd + 1 / llfd)

            req_gen = rs + (1/ts) * (lls + lmzd)
            snb_prop = {}
            snb_prop["bus1"] = f"{generator_bus}"
            snb_prop["bus2"] = f"Genaux_{generator_bus}.4.4.4"
            snb_prop["phases"] = 3
            snb_prop["R"] = req_gen
            snb_prop["X"] = 1e-9
            params = [f'{param}={snb_prop.get(param)}' for param in snb_prop]
            cmd_string = "new" + f" REACTOR.{dss_generator_name}_z " + " ".join(params)
            mdl.info(cmd_string) if debug else None
            dss.run_command(cmd_string)
            dss.run_command("calcv")

    elif element_type == "Fault":
        mdl.info("Fault Compensation Stage...") if debug else None
        fault_elements = get_all_dss_elements(mdl, comp_type=["Fault"])
        if fault_elements:
            mdl.info("The current version of the MPA doesn't support Fault elements."
                     "The results might not be trustable.")

    elif element_type == "VSConverter":
        mdl.info("VSConverter Compensation Stage...") if debug else None
        fault_elements = get_all_dss_elements(mdl, comp_type=["VSConverter"])
        if fault_elements:
            mdl.info("The current version of the MPA doesn't support VSConverter elements."
                     "The results might not be trustable.")

    elif element_type == "Isource":
        mdl.info("Isource Compensation Stage...") if debug else None
        fault_elements = get_all_dss_elements(mdl, comp_type=["Isource"])
        if fault_elements:
            mdl.info("The current version of the MPA doesn't support Isource elements."
                     "The results might not be trustable.")

    elif element_type == "Single-Phase Transformer":
        mdl.info("Single-Phase Transformer Compensation Stage...") if debug else None
        fault_elements = get_all_dss_elements(mdl, comp_type=["Single-Phase Transformer"])
        if fault_elements:
            mdl.info("The current version of the MPA doesn't support Single-Phase Transformer elements."
                     "The results might not be trustable.")

    elif element_type == "PV System":
        # Disable the Generator and create One Reactor (Generator Impedance)
        mdl.info("PVSystem Compensation Stage...") if debug else None
        for pv_handle in get_all_dss_elements(mdl, comp_type=["PV System"]):
            dss_pv_name = mdl.get_fqn(pv_handle).replace(".", "_").upper()
            mdl.info(f"PVSystem: {pv_handle}") if debug else None
            dss.Circuit.SetActiveElement(f"PVSYSTEM.{dss_pv_name}")
            pv_bus = dss.Properties.Value("bus1")
            pv_phases = int(dss.Properties.Value("phases"))
            connection = mdl.get_property_value(mdl.prop(pv_handle, "connection"))
            filter_type = mdl.get_property_value(mdl.prop(pv_handle, "filter_type"))

            # Not considering the non-Ideal Switch (resistance is very slow)
            if filter_type == "L":
                rl1_resistance = mdl.get_property_value(mdl.prop(pv_handle, "rl1_resistance"))
                rl1_inductance = mdl.get_property_value(mdl.prop(pv_handle, "rl1_inductance"))
                mdl.info(f"{rl1_resistance=}")
                mdl.info(f"{rl1_inductance=}")
                r_pv = rl1_resistance + (1 / ts) * rl1_inductance
            elif filter_type == "LC":
                rl1_resistance = mdl.get_property_value(mdl.prop(pv_handle, "rl1_resistance"))
                rl1_inductance = mdl.get_property_value(mdl.prop(pv_handle, "rl1_inductance"))
                rc_resistance = mdl.get_property_value(mdl.prop(pv_handle, "rc_resistance"))
                rc_capacitance = mdl.get_property_value(mdl.prop(pv_handle, "rc_capacitance"))
                rl1_eq = rl1_resistance + (1 / ts) * rl1_inductance
                rc_eq = rc_resistance + ts / rc_capacitance
                r_pv = rl1_eq * rc_eq / (rl1_eq + rc_eq)
            elif filter_type == "LCL":
                rl1_resistance = mdl.get_property_value(mdl.prop(pv_handle, "rl1_resistance"))
                rl1_inductance = mdl.get_property_value(mdl.prop(pv_handle, "rl1_inductance"))
                rc_resistance = mdl.get_property_value(mdl.prop(pv_handle, "rc_resistance"))
                rc_capacitance = mdl.get_property_value(mdl.prop(pv_handle, "rc_capacitance"))
                rl2_resistance = mdl.get_property_value(mdl.prop(pv_handle, "rl2_resistance"))
                rl2_inductance = mdl.get_property_value(mdl.prop(pv_handle, "rl2_inductance"))
                rl1_eq = rl1_resistance + (1 / ts) * rl1_inductance
                rc_eq = rc_resistance + ts / rc_capacitance
                rl2_eq = rl2_resistance + (1 / ts) * rl2_inductance
                r_pv = (rl1_eq * rc_eq / (rl1_eq + rc_eq)) + rl2_eq

            if pv_phases == 3:
                bus1_pv = pv_bus
                bus2_pv = pv_bus.split(".")[0] + ".0.0.0"
            else:
                if connection == "Y":
                    bus1_pv = pv_bus
                    bus2_pv = pv_bus.split(".")[0] + ".0"
                else:
                    bus1_pv = f"{pv_bus.split('.')[0]}.{pv_bus.split('.')[1]}"
                    bus2_pv = f"{pv_bus.split('.')[0]}.{pv_bus.split('.')[2]}"

            dss.CktElement.Enabled(False)
            # Creating an equivalent PV
            pv_req_prop = {}
            pv_req_prop["bus1"] = bus1_pv
            pv_req_prop["bus2"] = bus2_pv
            pv_req_prop["phases"] = pv_phases
            pv_req_prop["R"] = r_pv
            pv_req_prop["X"] = 1e-9
            params = [f'{param}={pv_req_prop.get(param)}' for param in pv_req_prop]
            cmd_string = "new" + f" REACTOR.{dss_pv_name}_eq " + " ".join(params)
            mdl.info(cmd_string) if debug else None
            dss.run_command(cmd_string)
            dss.run_command("calcv")
            restore_dict[f"REACTOR.{dss_pv_name.upper()}_EQ"] = f"PVSystem.{dss_pv_name.upper()}"

            #mdl.info(f"{dss.CktElement.AllPropertyNames()=}")
            #mdl.info(f"{pv_bus=}")


def sc_notation(val, num_decimals=2, exponent_pad=2):
    exponent_template = "{:0>%d}" % exponent_pad
    mantissa_template = "{:.%df}" % num_decimals

    order_of_magnitude = floor(log10(abs(val)))
    nearest_lower_third = 3 * (order_of_magnitude // 3)
    adjusted_mantissa = val * 10 ** (-nearest_lower_third)
    adjusted_mantissa_string = mantissa_template.format(adjusted_mantissa)
    adjusted_exponent_string = "+-"[nearest_lower_third < 0] + exponent_template.format(abs(nearest_lower_third))
    if int(adjusted_exponent_string) == 0:
        factor = " "
    elif int(adjusted_exponent_string) == 3:
        factor = " k"
    elif int(adjusted_exponent_string) == 6:
        factor = " M"
    elif int(adjusted_exponent_string) == 9:
        factor = " G"
    elif int(adjusted_exponent_string) == -3:
        factor = " m"
    elif int(adjusted_exponent_string) == -6:
        factor = " µ"
    elif int(adjusted_exponent_string) == -9:
        factor = " p"
    else:
        factor = "e" + f"{int(adjusted_exponent_string)}"

    return adjusted_mantissa_string + factor


def get_pf_results(mdl, dss):

    pf_results = {}
    tse_cpl_elements = []
    dss_cpl_elements = []
    for coupling_handle in get_all_dss_elements(mdl, comp_type="Coupling"):
        tse_cpl_elements.append(coupling_handle)
        dss_cpl_elements.append(f"LINE.{mdl.get_name(coupling_handle)}")

    dss.run_command("Calcv")
    dss.run_command("Solve Mode=Snap")

    if dss_cpl_elements:
        for idx_el, element in enumerate(dss_cpl_elements):
            cpl_results = {}
            dss.Circuit.SetActiveElement(element)
            nodes = dss.Properties.Value("bus1").split(".")[1:]
            cpl_results["power"] = [float(power) for power in dss.CktElement.Powers()]
            cpl_results["current"] = [float(current) for current in dss.CktElement.Currents()]
            cpl_results["voltage"] = [float(voltage) for voltage in dss.CktElement.Voltages()]
            pf_results.update({f"{mdl.get_name(tse_cpl_elements[idx_el])}": cpl_results})

    return pf_results


def format_report_line(original_string, new_string, ini_pos, sub_item=False):

    original_char_list = [char for char in original_string]
    new_char_list = [char for char in new_string]
    num_car = len(new_char_list)
    for cnt, idx in enumerate(range(ini_pos, ini_pos+num_car)):
        original_char_list[idx] = new_string[cnt]

    if sub_item:
        original_char_list[0] = " "
        original_char_list[1] = "-"

    return "".join(original_char_list)


def detailed_report(mdl, stability_data):

    window_report = 120
    file_name = f"{stability_data['dss_folder']}\stability_report.txt"

    with open(file_name, mode="w", encoding="utf-8") as file:
        file.write(f"Stability Report for {stability_data.get('mdlfile_name')}\n")
        file.write(f"Time Step: {sc_notation(stability_data.get('ts'))}s\n")
        n_cpls = len(stability_data.get('couplings'))
        cpl_names = []
        for cpl in stability_data.get('couplings'):
            cpl_names.append(mdl.get_name(cpl))
        if n_cpls > 0:
            file.write(f"Couplings: {n_cpls} ({', '.join(cpl_names)})\n")
        else:
            file.write(f"Couplings: {n_cpls}\n")
        n_sw = len(stability_data.get('switches'))
        sw_names = []
        for sw in stability_data.get('switches'):
            sw_names.append(mdl.get_name(sw))
        if n_sw > 0:
            file.write(f"Switches: {n_sw} ({', '.join(sw_names)})\n")
        else:
            file.write(f"Switches: {n_sw}\n")

        if n_sw > 0:
            sw_gen = [(0, 1) for _ in range(n_sw)]
            sw_comb = [comb for comb in itertools.product(*sw_gen)]
        else:
            sw_comb = ["no_sw"]

        for count_cpl, cpl in enumerate(stability_data.get("couplings")):
            coupling = mdl.get_name(cpl)
            bus1 = stability_data.get(f"{coupling}").get("bus1")
            bus2 = stability_data.get(f"{coupling}").get("bus2")
            cpl_data = stability_data.get(f"{coupling}").get("report_cpl")
            file.write("\n")
            msg = f"{cpl_data['name']} Element"
            file.write(format_report_line("-" * window_report, msg, int((window_report - len(msg)) / 2)))
            file.write("\n")
            file.write(f"Operational Mode: {cpl_data['mode']}\n")
            file.write(f"Snubbers Parameterization:\n")
            file.write(f"- Current Source Side: {cpl_data.get('csnb_value')}\n")
            file.write(f"- Voltage Source Side: {cpl_data.get('vsnb_value')}\n")
            file.write(f"Topological Conflicts: {cpl_data.get('topological_status_msg')}\n")
            if cpl_data['topological_status_msg'] == "Yes":
                for msg in cpl_data['top_conflicts']:
                    file.write(f"{msg}\n")
            for count_comb, comb in enumerate(sw_comb):
                pf_data = stability_data.get(f"{coupling}").get(comb).get(f"power_flow")
                if comb != "no_sw":
                    sw_pos = []
                    for count_sw, sw in enumerate(comb):
                        if sw == 1:
                            sw_pos.append(f"{sw_names[count_sw]}=Close")
                        else:
                            sw_pos.append(f"{sw_names[count_sw]}=Open")
                    ini_state = " (initial state)" if comb == stability_data.get("initial_sw_states") else ""
                    msg = f"--- Switch Condition{ini_state}: {'|'.join(sw_pos)} ---"
                    file.write(format_report_line(" "*window_report, msg, int((window_report - len(msg)) / 2)))
                    file.write("\n")
                file.write(f"Power Flow data at the Coupling:\n")
                phases = int(len(pf_data.get("power")) / 2 / 2)
                power_msg = format_report_line(f"{'': <{window_report}}", "", 0, sub_item=True)
                current_msg = format_report_line(f"{'': <{window_report}}", "", 0, sub_item=True)
                voltage_msg = format_report_line(f"{'': <{window_report}}", "", 0, sub_item=True)
                for idx in range(phases):
                    pf_power_aux = pf_data.get("power")
                    pf_current_aux = pf_data.get("current")[2*idx] + pf_data.get("current")[2*idx+1]*1j
                    pf_voltage_aux = pf_data.get("voltage")[2*idx] + pf_data.get("voltage")[2*idx+1]*1j
                    msg = f"S{bus1.split('.')[1 + idx]}= {abs(round(pf_power_aux[2 * idx], 3))} + j{abs(round(pf_power_aux[2 * idx + 1], 3))} kVA"
                    power_msg = format_report_line(power_msg, msg, 30*idx + 3)
                    msg = f"I{bus1.split('.')[1 + idx]}= {round(np.absolute(pf_current_aux), 3)} A < {round(np.angle(pf_current_aux, deg=True),2)}°"
                    current_msg = format_report_line(current_msg, msg, 30*idx + 3)
                    msg = f"V{bus1.split('.')[1 + idx]}= {round(np.absolute(pf_voltage_aux)*1e-3, 3)} kV < {round(np.angle(pf_voltage_aux, deg=True), 2)}°"
                    voltage_msg = format_report_line(voltage_msg, msg, 30*idx + 3)
                file.write(f"{power_msg}\n")
                file.write(f"{current_msg}\n")
                file.write(f"{voltage_msg}\n")

                file.write(f"Stability Data (ITM):\n")
                r1_aux = stability_data.get(f"{coupling}").get(comb).get(f"r1_fixed")
                r2_aux = stability_data.get(f"{coupling}").get(comb).get(f"r2_fixed")
                stability_aux = stability_data.get(f"{coupling}").get(comb).get(f"stability")
                for idx in range(phases):
                    if stability_aux[idx] == 0:
                        stability_results = "**UNSTABLE**"
                    elif stability_aux[idx] == 2:
                        stability_results = "**BORDER**"
                    else:
                        stability_results = "**STABLE**"
                    msg = f"- Phase{bus1.split('.')[1 + idx]}: r1={sc_notation(r1_aux[idx])}Ω,  r2={sc_notation(r2_aux[idx])}Ω {stability_results}"
                    file.write(f"{msg}\n")
                if stability_data.get(f"{coupling}").get(comb).get(f"stability_tip"):
                    file.write(stability_data.get(f"{coupling}").get(comb).get(f"stability_tip"))
                    file.write("\n")


def summary_report(mdl, stability_data):

    window_report = 90
    n_sw = len(stability_data.get('switches'))
    sw_names = []
    for sw in stability_data.get('switches'):
        sw_names.append(mdl.get_name(sw))

    if n_sw > 0:
        sw_gen = [(0, 1) for _ in range(n_sw)]
        sw_comb = [comb for comb in itertools.product(*sw_gen)]
    else:
        sw_comb = ["no_sw"]

    for cpl_handle in stability_data.get("couplings"):
        cpl_name = mdl.get_name(cpl_handle)
        cpl_data = stability_data.get(f"{cpl_name}").get("report_cpl")
        mdl.info(" ")
        msg = f"{cpl_data['name']} Element"
        mdl.info(format_report_line("-"*window_report, msg, int((window_report - len(msg)) / 2)))
        mdl.info(f"Operational Mode: {cpl_data['mode']}")
        mdl.info(f"Topological Conflicts: {cpl_data['topological_status_msg']}") if cpl_data["mode"] == "Manual" else None
        if cpl_data['topological_status_msg'] == "Yes":
            for msg in cpl_data['top_conflicts']:
                mdl.info(msg)

        mdl.info(f"Snubbers Parameterization:")
        max_current = 1e-6 + 1e-6*1j  # For compute line drop voltage
        max_voltage = 1e-6 + 1e-6*1j  # For compute snubber power
        for count_comb, comb in enumerate(sw_comb):
            pf_data = stability_data.get(f"{cpl_name}").get(comb).get(f"power_flow")
            phases = int(len(pf_data.get("power")) / 2 / 2)
            for idx in range(phases):
                pf_current_aux = pf_data.get("current")[2*idx] + pf_data.get("current")[2*idx+1]*1j
                pf_voltage_aux = pf_data.get("voltage")[2*idx] + pf_data.get("voltage")[2*idx+1]*1j
                if round(np.absolute(pf_current_aux), 3) > max_current:
                    max_current = pf_current_aux
                if round(np.absolute(pf_voltage_aux), 3) > max_voltage:
                    max_voltage = pf_voltage_aux
        if cpl_data['csnb_value'] == "none":
            mdl.info(f"- Current Source Side: {cpl_data['csnb_value']}")
        else:
            snubber_power = max_voltage*np.conj(max_voltage)/(cpl_data["csnb_impedance"])
            if np.imag(snubber_power) != 0:
                mdl.info(f"- Current Source Side: {cpl_data['csnb_value']} (maximum snubber power: {sc_notation(np.real(snubber_power))}W + j{sc_notation(np.imag(snubber_power))}var)")
            else:
                mdl.info(f"- Current Source Side: {cpl_data['csnb_value']} (maximum snubber power: {sc_notation(np.real(snubber_power))}W)")
        if cpl_data['vsnb_value'] == "none":
            mdl.info(f"- Voltage Source Side: {cpl_data['vsnb_value']}")
        else:
            line_drop_voltage = max_current * cpl_data["vsnb_impedance"]
            line_loss = np.real(max_current*np.conj(max_current)*cpl_data["vsnb_impedance"])
            mdl.info(f"- Voltage Source Side: {cpl_data['vsnb_value']} (maximum drop voltage {sc_notation(np.absolute(line_drop_voltage))}V, and maximum loss {sc_notation(line_loss)}W)")

        stability_results = "stable"
        unst_comb = []
        for count_comb, comb in enumerate(sw_comb):
            aux_cpl_data = stability_data.get(f"{cpl_name}").get(comb)
            if any([x != 1 for x in aux_cpl_data.get("stability")]):
                stability_results = "unstable"
                if comb != "no_sw":
                    sw_pos = []
                    for count_sw, sw in enumerate(comb):
                        if sw == 1:
                            sw_pos.append(f"{sw_names[count_sw]}=Close")
                        else:
                            sw_pos.append(f"{sw_names[count_sw]}=Open")
                    unst_comb.append(f"{'|'.join(sw_pos)}")
        if stability_results == "stable":
            mdl.info(f"Stability Check: {cpl_data['name']} is {stability_results}")
        else:
            if comb != "no_sw":
               mdl.info(f"Stability Check: {cpl_data['name']} is {stability_results} for {', '.join(unst_comb)} switches combinations.")
               mdl.info(f"Stability tips can be found on the detailed report")
            else:
                mdl.info(f"Stability Check: {cpl_data['name']} is {stability_results}")
                if cpl_data.get("stability_tip"):
                    mdl.info(f"{cpl_data['stability_tip']}")


def check_topological_conflicts(mdl, dss, cpl_handle, restore_names_dict):

    cpl_mode = mdl.get_property_value(mdl.prop(cpl_handle, "auto_mode"))
    cpl_name = mdl.get_fqn(cpl_handle).replace(".", "_").upper()
    dss.Circuit.SetActiveElement(f"LINE.{cpl_name}")

    dss_tse_dict_handles = {}
    supported_components = ["Bus", "Line", "Generator", "Vsource", "Capacitor Bank",
                            "Three-Phase Transformer", "Single-Phase Transformer", "PV System"]
    for comp_handle in get_all_dss_elements(mdl, comp_type=supported_components):
        comp_name = mdl.get_fqn(comp_handle).replace(".", "_").upper()
        dss_tse_dict_handles.update({f"{comp_name}": comp_handle})

    cs_bus = [dss.Properties.Value("bus1").upper().split(".")[0]]
    vs_bus = [dss.Properties.Value("bus2").upper().split(".")[0]]
    if mdl.get_property_value(mdl.prop(cpl_handle, "flip_status")):
        cs_bus, vs_bus = vs_bus, cs_bus

    # Current Source Side
    cs_topological_components = []
    cpl_csnb_type = mdl.get_property_value(mdl.prop(cpl_handle, "itm_csnb_type"))
    has_cs_snb = cpl_csnb_type != "none" or cpl_mode != "Manual"   # Skip the process if is in auto-mode
    has_bus_snb = False
    bus_meter_handle = mdl.get_item("meter_3ph", parent=dss_tse_dict_handles[cs_bus[0].upper()])
    if bus_meter_handle:
        has_bus_snb = not mdl.get_property_value(mdl.prop(bus_meter_handle, "remove_snubber"))

    connected_elem = []
    if (not has_cs_snb) and (not has_bus_snb):

        dss.Circuit.SetActiveBus(cs_bus[0])
        connected_elem += [elem.upper() for elem in dss.Bus.AllPDEatBus()]
        connected_elem += [elem.upper() for elem in dss.Bus.AllPCEatBus()]

        # Fixing the names
        for idx, elem in enumerate(connected_elem.copy()):
            # Restore the names from the compensation stage
            if restore_names_dict.get(elem):
                connected_elem[idx] = restore_names_dict.get(elem)
            # Add new buses due to the contactors connection
            if connected_elem[idx].split(".")[0] == "SWITCH":
                dss.Circuit.SetActiveElement(f"LINE.{''.join(elem.split('.')[1:])}")
                aux_bus1 = dss.Properties.Value("bus1").split(".")[0].upper()
                aux_bus2 = dss.Properties.Value("bus2").split(".")[0].upper()
                if aux_bus1 in cs_bus:
                    cs_bus.append(aux_bus2)
                else:
                    cs_bus.append(aux_bus1)

        # Check the new connections
        for sw_bus in cs_bus[1:]:
            dss.Circuit.SetActiveBus(sw_bus)
            connected_elem += [elem.upper() for elem in dss.Bus.AllPDEatBus()]
            connected_elem += [elem.upper() for elem in dss.Bus.AllPCEatBus()]

        for idx, elem in enumerate(connected_elem.copy()):
            # Restore the names from the compensation stage
            if restore_names_dict.get(elem):
                connected_elem[idx] = restore_names_dict.get(elem)

        # Removing duplicated elements and the coupling itself
        connected_elem = list(set(connected_elem))
        connected_elem.remove(f"LINE.{cpl_name}")

        for elem in connected_elem:
            elem_type = elem.split(".")[0]
            elem_name = "".join(elem.split(".")[1:])
            elem_handle = dss_tse_dict_handles.get(elem_name)
            if elem_handle:
                elem_fqn = mdl.get_fqn(elem_handle)

            if elem_type in ["VSOURCE", "GENERATOR", "PVSystem"]:
                cs_topological_components.append(elem_fqn)
            # Transformer Check
            if elem_type in ["TRANSFORMER"]:
                cs_topological_components.append(elem_fqn)
            # Line Check
            if elem_type in ["LINE"]:
                dss.Circuit.SetActiveElement(elem)
                if dss.Lines.C1 == 0 and dss.Lines.C0() == 0:
                    cs_topological_components.append(elem_fqn)

    # Voltage Source Side
    vs_topological_components = []
    cpl_vsnb_type = mdl.get_property_value(mdl.prop(cpl_handle, "itm_vsnb_type"))
    has_vs_snb = cpl_vsnb_type != "none" and cpl_mode != "Manual"   # Skip the process if is in auto-mode

    connected_elem = []
    if not has_vs_snb:

        dss.Circuit.SetActiveBus(vs_bus[0])
        connected_elem += [elem.upper() for elem in dss.Bus.AllPDEatBus()]
        connected_elem += [elem.upper() for elem in dss.Bus.AllPCEatBus()]

        # Fixing the names
        for idx, elem in enumerate(connected_elem.copy()):
            # Restore the names from the compensation stage
            if restore_names_dict.get(elem):
                connected_elem[idx] = restore_names_dict.get(elem)
            # Add new buses due to the contactors connection
            if connected_elem[idx].split(".")[0] == "SWITCH":
                dss.Circuit.SetActiveElement(f"LINE.{''.join(elem.split('.')[1:])}")
                aux_bus1 = dss.Properties.Value("bus1").split(".")[0].upper()
                aux_bus2 = dss.Properties.Value("bus2").split(".")[0].upper()
                if aux_bus1 in vs_bus:
                    vs_bus.append(aux_bus2)
                else:
                    vs_bus.append(aux_bus1)

        # Check the new connections
        for sw_bus in vs_bus[1:]:
            dss.Circuit.SetActiveBus(sw_bus)
            connected_elem += [elem.upper() for elem in dss.Bus.AllPDEatBus()]
            connected_elem += [elem.upper() for elem in dss.Bus.AllPCEatBus()]

        for idx, elem in enumerate(connected_elem.copy()):
            # Restore the names from the compensation stage
            if restore_names_dict.get(elem):
                connected_elem[idx] = restore_names_dict.get(elem)

        # Removing duplicated elements and the coupling itself
        connected_elem = list(set(connected_elem))
        connected_elem.remove(f"LINE.{cpl_name}")

        for elem in connected_elem:
            elem_type = elem.split(".")[0]
            elem_name = "".join(elem.split(".")[1:])
            elem_handle = dss_tse_dict_handles.get(elem_name)
            if elem_handle:
                elem_fqn = mdl.get_fqn(elem_handle)

            # Line Check
            if elem_type in ["LINE"]:
                dss.Circuit.SetActiveElement(elem)
                if dss.Lines.C1 != 0 and dss.Lines.C0() != 0:
                    vs_topological_components.append(elem_fqn)

            # Capacitor Check
            if elem_type in ["CAPACITOR"]:
                vs_topological_components.append(elem_fqn)

    return cs_topological_components, vs_topological_components


def run_auto_partitioning(mdl, mask_handle):

    import opendssdirect as dss
    import networkx as nx
    import matplotlib.pyplot as plt
    from sklearn.cluster import SpectralClustering

    debug = True

    reset_auto_partitioning(mdl, mask_handle)

    circ_graph = nx.Graph()

    mdl.info(f"Running the Power Flow")
    sim_with_opendss(mdl, mask_handle)
    # Get the path to the exported JSON
    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem
    mdlfile_folder = pathlib.Path(mdlfile).parents[0]
    mdlfile_target_folder = mdlfile_folder.joinpath(mdlfile_name + ' Target files')
    dss_folder = mdlfile_target_folder.joinpath('dss')
    dss_file = mdlfile_target_folder.joinpath(dss_folder).joinpath(mdlfile_name + '_master.dss')

    # Load DSS
    dss.run_command(f'Compile "{dss_file}"')
    dss.Solution.Solve()
    dss.run_command("calcv")
    dss.run_command("calcincmatrix")

    incmatrix = dss.Solution.IncMatrix()
    incmatrix_cols = dss.Solution.IncMatrixCols()
    incmatrix_rows = dss.Solution.IncMatrixRows()
    rows_index = np.array(incmatrix[0:-2:3])
    cols_index = np.array(incmatrix[1:-1:3])
    vals = np.array(incmatrix[2::3])
    circ_matrix = np.zeros((len(rows_index), len(cols_index)))
    for cnt in range(int((len(incmatrix)-1)/3)):
        i = int(rows_index[cnt])
        j = int(cols_index[cnt])
        circ_matrix[i][j] = vals[cnt]

    mdl.info(f"{incmatrix=}") if debug else None
    mdl.info(f"{incmatrix_cols=}") if debug else None
    mdl.info(f"{incmatrix_rows=}") if debug else None
    mdl.info(f"{circ_matrix=}") if debug else None

    # Pensar em uma estratégia para formar os grafos

    # Create Nodes using bus elements
    pos_bus = {}
    for cnt, bus in enumerate(incmatrix_cols):
        circ_graph.add_node(cnt, bus_name=bus)
        mdl.info(f"Add Node {cnt}: {bus}") if debug else None
        # Getting position (initial/simple logic)
        bus_handle = mdl.get_item(bus)
        bus_position_x = (mdl.get_position(bus_handle)[0] / 8192 - 1) * 200
        bus_position_y = (mdl.get_position(bus_handle)[1] / 8192 - 1)
        pos_bus.update({cnt: (bus_position_x, bus_position_y)})

    # Create Edges
    for j in range(len(incmatrix_cols)):
        bus_from_name = incmatrix_cols[j]
        bus_from_num = j
        for i in range(len(incmatrix_rows)):
            pd_name = incmatrix_rows[i]
            if circ_matrix[i][j] == 1:
                for aux_j in range(len(incmatrix_cols)):
                    if circ_matrix[i][aux_j] == -1:
                        bus_to_name = incmatrix_cols[aux_j]
                        bus_to_num = aux_j
                        mdl.info(f"Create Node {pd_name} between {bus_from_name} - {bus_to_name}") if debug else None
                        circ_graph.add_edge(bus_from_num, bus_to_num, element=pd_name)

    edge_labels = nx.get_edge_attributes(circ_graph, name="element")
    node_labels = nx.get_node_attributes(circ_graph, name="bus_name")

    # Convert the graph to its adjacency matrix
    adj_matrix = nx.adjacency_matrix(circ_graph).toarray()
    num_partitions = 3

    # Use spectral clustering to perform balanced partitioning
    sc = SpectralClustering(n_clusters=num_partitions, affinity='precomputed', random_state=0)
    labels = sc.fit_predict(adj_matrix)
    mdl.info(f"{labels=}")

    partitioned_graphs = []
    for i in range(num_partitions):
        subgraph_nodes = [node for node, label in enumerate(labels) if label == i]
        subgraph = circ_graph.subgraph(subgraph_nodes)
        partitioned_graphs.append(subgraph)

    # You now have the partitioned subgraphs in the `partitioned_graphs` list
    for i, subgraph in enumerate(partitioned_graphs):
        mdl.info(f"Partition {i + 1}: Nodes {subgraph.nodes()}")

    # Getting Interface Edges
    mdl.info(f"Interface Edges")
    interface_edges = []
    edge_config = {}
    for i, subgraph in enumerate(partitioned_graphs):
        cpl_id = 0
        for node in subgraph.nodes():
            neighbors = circ_graph.neighbors(node)
            for neighbor in neighbors:
                mdl.info(f"{node=} - {neighbor=}")
                if neighbor not in partitioned_graphs[i].nodes():
                    edge = circ_graph[node][neighbor]["element"]
                    if edge not in interface_edges:
                        cpl_id = cpl_id + 1
                        interface_edges.append(edge)
                        edge_config.update({f"{edge}": {"from_id": cpl_id, "to_id": cpl_id + 1}})

    for cpl_element, config in edge_config.items():
        cpl_name = cpl_element.split(".")[-1]
        cpl_handle = mdl.get_item(cpl_name)
        if cpl_handle:
            if mdl.get_property_value(mdl.prop(cpl_handle, "enable_partitioning")):
                mdl.set_property_value(mdl.prop(cpl_handle, "coupling_type"), "Core")


    # Figure
    fig, ax = plt.subplots(2, 1)
    ax = ax.flat
    nx.draw(circ_graph, pos=pos_bus, ax=ax[0])
    nx.draw_networkx_labels(circ_graph, pos=pos_bus, ax=ax[0], labels=node_labels, verticalalignment="bottom")
    #nx.draw_networkx_edge_labels(circ_graph, pos=pos_bus, edge_labels=edge_labels, verticalalignment="top", label_pos=0.5)

    #options = {"edgecolors": "tab:gray", "node_size": 800, "alpha": 0.9}
    colors = ["tab:red", "tab:blue", "tab:green", "tab:cyan", "tab:magenta", "tab:black"]
    nx.draw(circ_graph, pos=pos_bus, ax=ax[1], label=True)
    nx.draw_networkx_labels(circ_graph, pos=pos_bus, ax=ax[1], labels=node_labels, verticalalignment="bottom")
    for i, subgraph in enumerate(partitioned_graphs):
        mdl.info(f"Partition {i + 1}: Nodes {subgraph.nodes()}")
        nx.draw_networkx_nodes(circ_graph,  pos=pos_bus, ax=ax[1], nodelist=partitioned_graphs[i], node_color=colors[i], label=True)
        #nx.draw_networkx_nodes(circ_graph,  pos=pos_bus, ax=ax[1], nodelist=partitioned_graphs[1], node_color="tab:blue")

    plt.show()


def reset_auto_partitioning(mdl, mask_handle):

    for int_cpl_handle in get_all_dss_elements(mdl, comp_type=["Line", "Three-Phase Transformer"]):

        mdl.set_property_value(mdl.prop(int_cpl_handle, "coupling_type"), "None")

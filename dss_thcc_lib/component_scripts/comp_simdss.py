import os, pathlib
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QFileDialog, QWidget
import numpy as np
import re
from math import log10, floor
import ast

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

    mdl.info(f"{dss.__path__=}")

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
    sim_parameters["basefrequency"] = mdl.get_property_disp_value(mdl.prop(comp_handle, "basefrequency"))
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
            if mdl.get_property_value(mdl.prop(mask_handle, "stability_analysis")):
                run_stability_analysis(mdl, mask_handle, dss_file)

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
    basefreq = mdl.get_property_value(mdl.prop(mask_handle, "basefrequency"))
    mdl.set_ns_var("simdss_basefreq", basefreq)


def define_icon(mdl, mask_handle):
    mdl.set_component_icon_image(mask_handle, 'images/dss_logo.svg')


def run_stability_analysis(mdl, mask_handle, dss_file):
    import opendssdirect as dss

    # Initial settings
    # TODO: Create a function to estimate the time step if it is on "auto" mode
    if mdl.get_model_property_value("simulation_time_step") == "auto":
        mdl.info("The simulation time step is currently configured as auto. 10us will be used for this analysis")
        ts = 10e-6
    else:
        ts = float(mdl.get_model_property_value("simulation_time_step"))

    dss.run_command(f'Compile "{dss_file}"')
    # TODO: Get the original power flow at the Coupling Elements

    # Compensation Stage (Changing DSS properties to follow the THCC approach)
    dss = dss_to_thcc_compensation(mdl, dss, "Coupling", ts)
    dss = dss_to_thcc_compensation(mdl, dss, "Load", ts)
    dss = dss_to_thcc_compensation(mdl, dss, "Line", ts)
    dss = dss_to_thcc_compensation(mdl, dss, "Vsource", ts)
    dss = dss_to_thcc_compensation(mdl, dss, "Manual Switch", ts)
    dss = dss_to_thcc_compensation(mdl, dss, "Three-Phase Transformer", ts)

    tse_cpl_elements = []
    dss_cpl_elements = []
    for coupling_handle in get_all_dss_elements(mdl, comp_type="Coupling"):
        tse_cpl_elements.append(coupling_handle)
        dss_cpl_elements.append(f"LINE.{mdl.get_name(coupling_handle)}")

    if dss_cpl_elements:
        mdl.info("\nOpenDSS Coupling Assistance started...")
        for idx_el, element in enumerate(dss_cpl_elements):
            report_data = {}

            report_data["name"] = mdl.get_name(tse_cpl_elements[idx_el])
            # mdl.info(f"----- {mdl.get_name(tse_cpl_elements[idx_el])} Element -----")

            r1, r2, bus1, bus2 = get_zsc_impedances(mdl, mask_handle, dss, element, "matrix", ts)
            mode = mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "auto_mode"))
            if mode == "Manual":
                report_data["mode"] = "Manual"
                # mdl.info("Operational Mode: Manual")
                # Snubbers
                current_side_snubber = True
                voltage_side_snubber = True
                itm_csnb_type = mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_type"))
                itm_vsnb_type = mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_type"))
                if itm_csnb_type == "none":
                    r1_snb = 1e12
                    current_side_snubber = False
                    report_data["csnb_value"] = f"none"
                elif itm_csnb_type == "R1":
                    r1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_r")))
                    r1_snb = r1_cc_snb
                    report_data["csnb_value"] = f"R1={sc_notation(r1_cc_snb)}Ω"
                elif itm_csnb_type == "R1-C1":
                    r1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_r")))
                    c1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_c")))
                    r1_snb = r1_cc_snb + ts/c1_cc_snb
                    report_data["csnb_value"] = f"R1={sc_notation(r1_cc_snb)}Ω, C1={sc_notation(c1_cc_snb)}F"

                if itm_vsnb_type == "none":
                    r2_snb = 0
                    voltage_side_snubber = False
                    report_data["vsnb_value"] = f"none"
                elif itm_vsnb_type == "R2":
                    r2_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_r")))
                    r2_snb = r2_cc_snb
                    report_data["vsnb_value"] = f"R2={sc_notation(r2_cc_snb)}Ω"
                elif itm_vsnb_type == "R2||L1":
                    r2_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_r")))
                    l1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_l")))
                    l1_cc_snb_r = (1/ts)*l1_cc_snb
                    r2_snb = r2_cc_snb*l1_cc_snb_r/(r2_cc_snb+l1_cc_snb_r)
                    report_data["vsnb_value"] = f"R2={sc_notation(r2_cc_snb)}Ω, L1={sc_notation(l1_cc_snb)}H"

                # Check Topological Conflicts
                topological_status_msg = "No"
                topological_conflict = False
                topological_conflict_msg = []
                # Current Side
                dss.Circuit.SetActiveBus(bus1)
                pde_connected = [item.upper() for item in dss.Bus.AllPDEatBus()]
                pde_connected.remove(element.upper())
                pce_connected = [item.upper() for item in dss.Bus.AllPCEatBus()]

                for pde in pde_connected:
                    if pde.split(".")[0] in ["LINE", "TRANSFORMER"] and not current_side_snubber:
                        topological_conflict = True
                        topological_status_msg = "Yes"
                        aux_element = pde.split(".")[1]
                        topological_conflict_msg.append(f"- There are topological conflicts between {mdl.get_name(tse_cpl_elements[idx_el])} and {aux_element}."
                                                        f" Please, considers to use a snubber at the current source side of the {mdl.get_name(tse_cpl_elements[idx_el])}")

                for pce in pce_connected:
                    if pce.split(".")[0] in ["VSOURCE"] and not current_side_snubber:
                        topological_conflict = True
                        topological_status_msg = "Yes"
                        aux_element = pce.split(".")[1]
                        topological_conflict_msg.append(f"- There are topological conflicts between {mdl.get_name(tse_cpl_elements[idx_el])} and {aux_element}."
                                                        f" Please, considers to use a snubber at the current source side of the {mdl.get_name(tse_cpl_elements[idx_el])}")

                # Voltage Side
                dss.Circuit.SetActiveBus(bus2)
                pde_connected = [item.upper() for item in dss.Bus.AllPDEatBus()]
                pde_connected.remove(element.upper())

                for idx, pde in enumerate(pde_connected):
                    if pde.split(".")[0] in ["LINE"]:
                        dss.Circuit.SetActiveElement(pde_connected[idx])
                        if dss.Lines.C1() != 0.0 and not voltage_side_snubber:
                            topological_conflict = True
                            topological_status_msg = "Yes"
                            aux_element = pde.split(".")[1]
                            topological_conflict_msg.append(f"- There are topological conflicts between {mdl.get_name(tse_cpl_elements[idx_el])} and {aux_element}."
                                                            f" Please, considers to use a snubber at the voltage source side of the {mdl.get_name(tse_cpl_elements[idx_el])}")
                    if pde.split(".")[0] in ["CAPACITOR"] and not voltage_side_snubber:
                        topological_conflict = True
                        topological_status_msg = "Yes"
                        aux_element = pde.split(".")[1]
                        topological_conflict_msg.append(f"- There are topological conflicts between {mdl.get_name(tse_cpl_elements[idx_el])} and {aux_element}."
                                                        f" Please, considers to use a snubber at the voltage source side of the {mdl.get_name(tse_cpl_elements[idx_el])}")

                report_data["top_conflicts"] = topological_conflict_msg
                # mdl.info(f"Topological Conflicts: {topological_status_msg}")

                if topological_conflict:
                    for msg in topological_conflict_msg:
                        pass
                        # mdl.info(msg)
                        # mdl.warning(msg, kind=f"Coupling Element: {mdl.get_name(coupling_handle)}", context=mask_handle)

                # Stability Check
                r1_fixed = [rdss*r1_snb/(rdss + r1_snb) for rdss in r1]
                r2_fixed = [rdss + r2_snb for rdss in r2]
                z_ratio = [r1/r2 for r1, r2 in zip(r1_fixed, r2_fixed)]
                if any([z > 1.1 for z in z_ratio]):
                    # mdl.info(f"Stability Info: {mdl.get_name(tse_cpl_elements[idx_el])} is unstable.\n")
                    report_data["stability"] = "unstable"
                    report_data['stability_tip'] = f"- A flip on the {report_data['name']} might solve this issue."
                elif any([(0.9 < z < 1.1) for z in z_ratio]):
                    # mdl.info(f"Stability Info: {mdl.get_name(tse_cpl_elements[idx_el])} is around stability border.\n")
                    report_data["stability"] = "around stability border"
                    if any([ z >= 1.0 for z in z_ratio]):
                        report_data['stability_tip'] = f"- A flip on the {report_data['name']} and an increase in its snubbers might solve this issue might solve this issue."
                    else:
                        report_data['stability_tip'] = f"- An increase in the {report_data['name']}'s snubbers might solve this issue."
                else:
                    # mdl.info(f"Stability Info: {mdl.get_name(tse_cpl_elements[idx_el])} is stable.\n")
                    report_data["stability"] = "stable"

                """
                for ph in range(len(r1_fixed)):
                    #mdl.info(f"{[r1_fixed[ph], r2_fixed[ph]]}")
                    if r1_fixed[ph] >= r2_fixed[ph]:
                        mdl.info(f"Stability Info: {mdl.get_name(tse_cpl_elements[idx_el])}.{ph} is unstable.")
                        # msg = f"Coupling element {mdl.get_name(coupling_handle)} is unstable."
                        # mdl.warning(msg, kind='General warning', context=coupling_handle)
                    else:
                        # msg = f"Coupling element {mdl.get_name(coupling_handle)} is stable."
                        # mdl.info(msg, context=coupling_handle)
                        mdl.info(f"Stability Info: {mdl.get_name(tse_cpl_elements[idx_el])}.{ph} is stable.")
                """
                # Report for Manual Mode
                mdl.info(f"----- {report_data['name']} Element -----")
                mdl.info(f"Operational Mode: {report_data['mode']}")
                mdl.info(f"Snubbers Parameterization:")
                mdl.info(f"- Current Source Side: {report_data['csnb_value']}")
                mdl.info(f"- Current Source Side: {report_data['vsnb_value']}")
                mdl.info(f"Topological Conflicts: {topological_status_msg}")
                if topological_status_msg == "Yes":
                    for msg in topological_conflict_msg:
                        pass
                        mdl.info(msg)
                mdl.info(f"Stability Check: {report_data['name']} is {report_data['stability']}")
                if report_data["stability"] != "stable":
                    mdl.info(f"{report_data['stability_tip']}")
                mdl.info(" ")

            elif mode == "Automatic":
                report_data["mode"] = "Automatic"
                #mdl.info("Operational Mode: Automatic")

                # mdl.info(f"Element Actions:")
                # Stability Check
                flip_status = mdl.get_property_value(mdl.prop(tse_cpl_elements[idx_el], "flip_status"))
                # TODO The logic has not considered the phases individually yet
                if flip_status:
                    r1, r2 = r2, r1
                    bus1, bus2 = bus2, bus1

                z_ratio = [rth1/rth2 for rth1, rth2 in zip(r1, r2)]
                if any([z > 1.1 for z in z_ratio]):
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "flip_status"), not flip_status)
                    report_data["stability_tip"] = f"- Horizontal flip done."
                    report_data["stability"] = "stable"
                elif any([(0.9 < z < 1.1) for z in z_ratio]):
                    if any([z >= 1.0 for z in z_ratio]):
                        report_data["stability_tip"] = f"- Horizontal flip done."
                        report_data["stability"] = "TODO: Work on the parameterization"
                    else:
                        report_data["stability"] = "TODO: Work on the parameterization"
                else:
                    report_data["stability"] = "stable"

                # Current Side
                dss.Circuit.SetActiveBus(bus1)
                pde_connected = [item.upper() for item in dss.Bus.AllPDEatBus()]
                pde_connected.remove(element.upper())
                pce_connected = [item.upper() for item in dss.Bus.AllPCEatBus()]
                topological_conflict = False
                for pde in pde_connected:
                    if pde.split(".")[0] in ["LINE", "TRANSFORMER"]:
                        topological_conflict = True
                for pce in pce_connected:
                    if pce.split(".")[0] in ["VSOURCE"]:
                        topological_conflict = True

                if topological_conflict:
                    mdl.info(tse_cpl_elements[idx_el])
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_type"), "R1")
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_csnb_r_auto"), "1e6")
                    report_data["csnb_value"] = f"R1={sc_notation(1e6)}Ω"
                    # mdl.info(f"  - Added Snubber in Current Source Side: R1 = 1e6 Ω")
                else:
                    report_data["csnb_value"] = f"none"

                # Voltage Side
                dss.Circuit.SetActiveBus(bus2)
                pde_connected = [item.upper() for item in dss.Bus.AllPDEatBus()]
                pde_connected.remove(element.upper())
                topological_conflict = False
                for idx, pde in enumerate(pde_connected):
                    if pde.split(".")[0] in ["LINE"]:
                        dss.Circuit.SetActiveElement(pde_connected[idx])
                        if dss.Lines.C1() != 0.0:
                            topological_conflict = True
                    if pde.split(".")[0] in ["CAPACITOR"]:
                        topological_conflict = True

                if topological_conflict:
                    mdl.info(tse_cpl_elements[idx_el])
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_type"), "R2")
                    mdl.set_property_value(mdl.prop(tse_cpl_elements[idx_el], "itm_vsnb_r_auto"), "1e-3")
                    report_data["vsnb_value"] = f"R2={sc_notation(1e-3)}Ω"
                    # mdl.info(f"  - Added Snubber in Voltage Source Side: R2 = 1e-3 Ω")
                else:
                    report_data["vsnb_value"] = f"none"

                # Report for Automatic Mode
                mdl.info(f"----- {report_data['name']} Element -----")
                mdl.info(f"Operational Mode: {report_data['mode']}")
                mdl.info(f"Snubbers Parameterization:")
                mdl.info(f"- Current Source Side: {report_data['csnb_value']}")
                mdl.info(f"- Current Source Side: {report_data['vsnb_value']}")
                mdl.info(f"Topological Conflicts: None")
                mdl.info(f"Stability Check: {report_data['name']} is {report_data['stability']}")
                if report_data.get("stability_tip"):
                    mdl.info(f"{report_data['stability_tip']}")
                mdl.info(" ")

        mdl.info("-----")
        mdl.info("Stability analysis Completed.")


def get_all_dss_elements(mdl, comp_type, parent_comp=None):

    component_list = []
    if parent_comp:  # Component inside a subsystem (recursive function)
        all_components = mdl.get_items(parent_comp)
    else:  # Top level call
        all_components = mdl.get_items()

    for comp in all_components:
        try:
            type_name = mdl.get_component_type_name(comp)
            if type_name and type_name == comp_type and mdl.is_enabled(comp):
                component_list.append(comp)
            elif not type_name:  # Component is a subsystem
                component_list.extend(get_all_dss_elements(mdl, mdl.get_mask(comp), parent_comp=comp))
        except:
            # Some components (such as ports and connections) cannot be used with
            # get_component_type_name
            pass
    # Return the list of component handles
    return component_list


def get_zsc_impedances(mdl, mask_handle, dss, coupling_line, mode, ts):

    freq = float(mdl.get_property_value(mdl.prop(mask_handle, "basefrequency")))
    scale_l = (1/ts)/(2*np.pi*freq)  # Use as "scale_l*X"
    scale_c = ts*(2*np.pi*freq)  # Use as "scale_c*Xc"
    debug = True

    if mode == "matrix":

        dss.run_command("Solve Mode=FaultStudy")
        dss.run_command("calcv")
        dss.Circuit.SetActiveElement(coupling_line)
        bus = [bus_name.split(".")[0] for bus_name in dss.CktElement.BusNames()]
        bus1 = bus[0]
        bus2 = bus[1]

        # I should to remove the reactors created during the compensation stage
        dss.run_command("calcv")
        dss.Circuit.SetActiveBus(bus1)
        bus1_snb_list = []
        bus2_snb_list = []
        pce_pde = dss.Bus.AllPCEatBus() + dss.Bus.AllPDEatBus()
        for connected_element in pce_pde:
            reactor_match = re.match(r"^REACTOR.(.+)_([VC])(?:SIDE_snb\d$)", connected_element, re.IGNORECASE)
            if reactor_match:
                if reactor_match.group(1).lower() == coupling_line.split(".")[-1].lower():
                    bus1_snb_list.append(connected_element)

        dss.run_command("calcv")
        dss.Circuit.SetActiveBus(bus2)
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
        dss.Circuit.SetActiveBus(bus1)
        dss.Bus.ZscRefresh()
        zsc_matrix = [round(elem, 6) for elem in dss.Bus.ZscMatrix()]
        #zsc_matrix = [elem for elem in dss.Bus.ZscMatrix()]
        #zsc_matrix = dss.Bus.ZscMatrix()
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
        dss.Circuit.SetActiveBus(bus2)
        dss.Bus.ZscRefresh()
        zsc_matrix = [round(elem, 6) for elem in dss.Bus.ZscMatrix()]
        #zsc_matrix = [elem for elem in dss.Bus.ZscMatrix()]
        # zsc_matrix = dss.Bus.ZscMatrix()
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

        if True:
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
        else:
            r2 = []
            r2_sc = []
            x2_sc = []
            for idx in range(n_phases):
                # resistance
                k = rsc_matrix[idx, idx]
                l = np.array([rsc_matrix[idx, yvec] for yvec in range(n_phases) if yvec != idx]).reshape(1,n_phases - 1)
                lt = np.array([rsc_matrix[xvec, idx] for xvec in range(n_phases) if xvec != idx]).reshape(n_phases - 1,1)
                m = np.array([rsc_matrix[xvec, yvec]
                              for xvec in range(n_phases) if xvec != idx
                              for yvec in range(n_phases) if yvec != idx]).reshape(n_phases - 1, n_phases - 1)
                try:
                    r2_sc.append(k - np.dot(np.dot(l, np.linalg.inv(m)), lt)[0, 0])
                except:
                    r2_sc.append(0)
                # reactance
                k = xsc_matrix[idx, idx]
                l = np.array([xsc_matrix[idx, yvec] for yvec in range(n_phases) if yvec != idx]).reshape(1,
                                                                                                         n_phases - 1)
                lt = np.array([xsc_matrix[xvec, idx] for xvec in range(n_phases) if xvec != idx]).reshape(n_phases - 1,
                                                                                                          1)
                m = np.array([xsc_matrix[xvec, yvec]
                              for xvec in range(n_phases) if xvec != idx
                              for yvec in range(n_phases) if yvec != idx]).reshape(n_phases - 1, n_phases - 1)
                try:
                    x2_sc.append(k - np.dot(np.dot(l, np.linalg.inv(m)), lt)[0, 0])
                except:
                    x2_sc.append(0)
            for idx in range(n_phases):
                if x2_sc[idx] >= 0:
                    r2x = (1 / ts) * x2_sc[idx] / (2 * np.pi * freq)
                else:
                    r2x = (ts) / (x2_sc[idx] * 2 * np.pi * freq)
                #mdl.info(f"{r2_sc[idx]=}")
                #mdl.info(f"{r2x=}")
                r_eq = r2_sc[idx] + r2x
                r2.append(r_eq)

        # I should to add the reactors created during the compensation stage
        [dss.run_command(f"{pde}.enabled=yes") for pde in bus1_snb_list]
        [dss.run_command(f"{pde}.enabled=yes") for pde in bus2_snb_list]
        #[mdl.info(f"{pde}.enabled=yes") for pde in bus1_snb_list]
        #[mdl.info(f"{pde}.enabled=yes") for pde in bus2_snb_list]

        dss.run_command("calcv")
        dss.run_command("Solve Mode=Snap")
        mdl.info(f"[{r1[0]}, {r2[0]}]")if debug else None

    return r1, r2, bus1, bus2


def dss_to_thcc_compensation(mdl, dss, element_type, ts):

    debug = True

    if element_type == "Load":
        for load_handle in get_all_dss_elements(mdl, comp_type="Load"):
            # Getting THCC properties
            #mdl.info(load_handle)
            conn_type = mdl.get_property_value(mdl.prop(load_handle, "conn_type"))
            voltage = float(mdl.get_property_value(mdl.prop(load_handle, "Vn_3ph")))
            voltage = voltage*np.sqrt(3) if conn_type == "Δ" else voltage
            pf_mode = mdl.get_property_value(mdl.prop(load_handle, "pf_mode_3ph"))
            pf = float(mdl.get_property_value(mdl.prop(load_handle, "pf_3ph")))
            phases = float(mdl.get_property_value(mdl.prop(load_handle, "phases")))
            power = float(mdl.get_property_value(mdl.prop(load_handle, "Sn_3ph"))) * 3 / phases
            freq = float(mdl.get_property_value(mdl.prop(load_handle, "fn")))
            # Disabling DSS Load and getting its properties
            dss_load_name = mdl.get_fqn(load_handle).replace(".", "_").upper()
            dss.Circuit.SetActiveElement(f"LOAD.{dss_load_name}")
            #mdl.info(f"set LOAD.{dss_load_name}")
            #mdl.info(dss.CktElement.Name())
            bus = dss.CktElement.BusNames()[0].split(".")[0]
            nodes = dss.CktElement.BusNames()[0].split(".")[1:]
            # dss.CktElement.Enabled = 0
            dss.run_command(f"Load.{dss_load_name}.enabled=no")
            #mdl.info(f"Load.{dss_load_name}.enabled=no")
            #mdl.info(dss.CktElement.Name())
            if mdl.get_property_value(mdl.prop(load_handle, "load_model")) in ["Constant Power", "Constant Z,I,P"]:
                # Creating new loads
                cpl_handle = mdl.get_item("CPL", parent=load_handle)
                cpl_phase_handle = [mdl.get_item(cname, parent=cpl_handle) for cname in ["CPLA", "CPLB", "CPLC"]]
                for idx, cpl in enumerate(cpl_phase_handle):
                    if cpl:
                        load_p = {}
                        load_q = {}
                        load_eq = {}
                        VLL = 1e3*voltage/np.sqrt(3)
                        SS = 1e3*power/3
                        # Navid Equations
                        rsnb = (30 * (VLL * VLL / (1.66 * SS)))
                        csnb = 1 / (1 * rsnb * 2 * np.pi * freq)
                        rsnb = rsnb/15
                        # Those resistances are in parallel from the THCC viewpoint
                        req = rsnb*(ts/csnb)/(rsnb+ts/csnb)
                        #mdl.info(f"req{dss_load_name}={req}")
                        # mdl.info(f"{req=}")
                        snubber_p = 1e-3*(VLL*VLL/rsnb)
                        snubber_q = 1e-3*(VLL*VLL*2*np.pi*freq*csnb)
                        snubber_eq = 1e-3*(VLL*VLL/req)
                        # mdl.info(f"{snubber_eq=}")
                        load_p["Bus1"] = bus + f".{nodes[idx]}"
                        load_p["kW"] = snubber_p
                        load_p["kvar"] = 0
                        load_p["model"] = 2
                        load_p["kV"] = 1e-3*VLL
                        load_p["phases"] = 1
                        params = [f'{param}={load_p.get(param)}' for param in load_p]
                        cmd_string = "new" + f" Load.{dss_load_name}_P{idx+1} " + " ".join(params)
                        #mdl.info(cmd_string)
                        #dss.run_command(cmd_string)
                        load_q["Bus1"] = bus + f".{nodes[idx]}"
                        load_q["kW"] = 0
                        load_q["kvar"] = -1*snubber_q
                        load_q["model"] = 2
                        load_q["kV"] = 1e-3*VLL
                        load_q["phases"] = 1
                        params = [f'{param}={load_q.get(param)}' for param in load_q]
                        cmd_string = "new" + f" Load.{dss_load_name}_Q{idx+1} " + " ".join(params)
                        #mdl.info(cmd_string)
                        #dss.run_command(cmd_string)
                        load_eq["Bus1"] = bus + f".{nodes[idx]}"
                        load_eq["kW"] = snubber_eq
                        load_eq["kvar"] = 0
                        load_eq["model"] = 2
                        load_eq["kV"] = 1e-3 * VLL
                        load_eq["phases"] = 1
                        params = [f'{param}={load_eq.get(param)}' for param in load_eq]
                        cmd_string = "new" + f" Load.{dss_load_name}_EQ{idx + 1} " + " ".join(params)
                        #mdl.info(cmd_string)
                        dss.run_command(cmd_string)

                        #mdl.info(dss.CktElement.Name())
            else:
                load_eq = {}
                VLL = 1e3 * voltage / np.sqrt(3)
                SS = 1e3 * power / 3
                if pf_mode == "Unit":
                    R = (VLL ** 2) / SS
                    req = R
                elif pf_mode == "Lag":
                    Z = (VLL ** 2) / SS
                    R = pf * Z
                    L = Z * ((1 - pf ** 2) ** 0.5) / (2 * np.pi * freq)
                    req = R + (1/ts)*L
                else:
                    Z = (VLL ** 2) / SS
                    R = pf * Z
                    C = 1 / (Z * 2 * np.pi * freq * ((1 - pf ** 2) ** 0.5))
                    req = R + (ts/C)
                for idx in nodes:
                    mdl.info(f"{req=}")
                    load_eq["Bus1"] = bus + f".{idx}"
                    load_eq["kW"] = 1e-3*VLL*VLL/req
                    load_eq["kvar"] = 0
                    load_eq["model"] = 2
                    load_eq["phases"] = 1
                    load_eq["kV"] = 1e-3 * VLL
                    params = [f'{param}={load_eq.get(param)}' for param in load_eq]
                    cmd_string = "new" + f" Load.{dss_load_name}_EQ{idx} " + " ".join(params)
                    #mdl.info(cmd_string)
                    dss.run_command(cmd_string)

    elif element_type == "Coupling":
        for coupling_handle in get_all_dss_elements(mdl, comp_type="Coupling"):
            # Opening DSS Line
            dss_coupling_name = mdl.get_fqn(coupling_handle).replace(".", "_").upper()
            dss.Circuit.SetActiveElement(f"LINE.{dss_coupling_name}")
            # Ways to disabling the coupling
            dss.CktElement.Open(0, 0)
            # dss.run_command(f"Open LINE.{dss_coupling_name}")
            # dss.run_command(f"LINE.{dss_coupling_name}.enabled=no")

            #
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
                cmd_string = "new" + f" REACTOR.{dss_coupling_name}_CSIDE_snb{idx} " + " ".join(params)
                #mdl.info(cmd_string)
                dss.run_command(cmd_string)
            for idx in nodes_voltage_side:
                snb_prop = {}
                snb_prop["bus1"] = f"{bus_voltage_side}.{idx}"
                snb_prop["phases"] = 1
                snb_prop["R"] = req_vside
                snb_prop["X"] = 1e-6
                params = [f'{param}={snb_prop.get(param)}' for param in snb_prop]
                cmd_string = "new" + f" REACTOR.{dss_coupling_name}_VSIDE_snb{idx} " + " ".join(params)
                #mdl.info(cmd_string)
                dss.run_command(cmd_string)

    elif element_type == "Line":
        for line_handle in get_all_dss_elements(mdl, comp_type="Line"):
            dss_line_name = mdl.get_fqn(line_handle).replace(".", "_").upper()
            #mdl.info(f"{dss_line_name=}")
            dss.Circuit.SetActiveElement(f"LINE.{dss_line_name}")
            rmatrix = dss.Lines.RMatrix()
            xmatrix = dss.Lines.XMatrix()
            cmatrix = dss.Lines.CMatrix()
            freq = float(dss.Solution.Frequency())
            n_phases = int(np.sqrt(len(rmatrix)))
            rmatrix_compensated = np.zeros(len(rmatrix))
            xmatrix_compensated = np.zeros(len(rmatrix))
            cmatrix_compensated = np.zeros(len(rmatrix))
            for idx in range(len(rmatrix)):
                rmatrix_compensated[idx] = rmatrix[idx] + (1/ts)*xmatrix[idx]/(2*np.pi*freq)
                xmatrix_compensated[idx] = 1e-6
                cmatrix_compensated[idx] = cmatrix[idx]

            rmatrix_compensated = rmatrix_compensated.reshape(n_phases, n_phases)
            xmatrix_compensated = xmatrix_compensated.reshape(n_phases, n_phases)
            cmatrix_compensated = cmatrix_compensated.reshape(n_phases, n_phases)

            rmatrix = np.array(rmatrix).reshape(n_phases, n_phases)
            xmatrix = np.array(xmatrix).reshape(n_phases, n_phases)
            cmatrix = np.array(cmatrix).reshape(n_phases, n_phases)

            #mdl.info(f"{rmatrix=}")
            #mdl.info(f"{xmatrix=}")
            #mdl.info(f"{cmatrix=}")
            #mdl.info(f"{rmatrix_compensated=}")
            #mdl.info(f"{xmatrix_compensated=}")
            #mdl.info(f"{cmatrix_compensated=}")

            dss.Lines.RMatrix(rmatrix_compensated)
            dss.Lines.XMatrix(xmatrix_compensated)
            dss.Lines.CMatrix(cmatrix_compensated)

            # Creating the capacitors as reactors (only resistive values)
            bus1, bus2 = [bus_name.split(".")[0] for bus_name in dss.CktElement.BusNames()]
            bus1_nodes, bus2_nodes = [bus_name.split(".")[1:] for bus_name in dss.CktElement.BusNames()]
            for idx in bus1_nodes:
                pos = int(idx)-1
                if cmatrix[pos, pos] > 0:
                    snb1_prop = {}
                    req_cap = ts / (1e-9*cmatrix[pos, pos]/2)
                    #mdl.info(f"{req_cap=}")
                    snb1_prop["bus1"] = f"{bus1}.{idx}"
                    snb1_prop["phases"] = 1
                    snb1_prop["R"] = req_cap
                    snb1_prop["X"] = 1e-9
                    params = [f'{param}={snb1_prop.get(param)}' for param in snb1_prop]
                    cmd_string = "new" + f" REACTOR.{dss_line_name}_CAP1_snb{idx} " + " ".join(params)
                    #mdl.info(cmd_string)
                    dss.run_command(cmd_string)
                    snb2_prop = {}
                    snb2_prop["bus1"] = f"{bus2}.{idx}"
                    snb2_prop["phases"] = 1
                    snb2_prop["R"] = req_cap
                    snb2_prop["X"] = 1e-9
                    params = [f'{param}={snb2_prop.get(param)}' for param in snb2_prop]
                    cmd_string = "new" + f" REACTOR.{dss_line_name}_CAP2_snb{idx} " + " ".join(params)
                    #mdl.info(cmd_string)
                    dss.run_command(cmd_string)
                dss.run_command("calcv")

    elif element_type == "Vsource":
        for vsource_handle in get_all_dss_elements(mdl, comp_type="Vsource"):
            dss_vsource_name = mdl.get_fqn(vsource_handle).replace(".", "_").upper()
            dss.Circuit.SetActiveElement(f"VSOURCE.{dss_vsource_name}")
            #mdl.info(dss.CktElement.Name())
            #mdl.info(dss.CktElement.AllPropertyNames())
            freq = float(dss.Properties.Value("frequency"))
            scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
            r1 = float(dss.Properties.Value("R1"))
            r0 = float(dss.Properties.Value("R0"))
            x1 = float(dss.Properties.Value("X1"))
            x0 = float(dss.Properties.Value("X0"))
            # r1, x1 = [float(prop_value) for prop_value in ast.literal_eval(dss.Properties.Value("Z1"))]
            # r0, x0 = [float(prop_value) for prop_value in ast.literal_eval(dss.Properties.Value("Z0"))]

            r1_new = r1 + x1*scale_l
            x1_new = 1e-6
            r0_new = r0 + x0*scale_l
            x0_new = 1e-6
            #mdl.info("Vsource")
            #mdl.info(f"{r1_new=}")
            #mdl.info(f"{r0_new=}")
            dss.Properties.Value("R1", str(r1_new))
            dss.Properties.Value("R0", str(r0_new))
            dss.Properties.Value("X1", str(x1_new))
            dss.Properties.Value("X0", str(x0_new))

            #cmd_string = f"VSOURCE.{dss_vsource_name}.Z1 = [{r1_new}, {x1_new}]"
            #mdl.info(cmd_string)
            #dss.run_command(cmd_string)
            #dss.run_command("calcv")
            #cmd_string = f"VSOURCE.{dss_vsource_name}.Z0 = [{r0_new}, {x0_new}]"
            #mdl.info(cmd_string)
            #dss.run_command(cmd_string)
            dss.run_command("calcv")

            #r1_new, x1_new = [float(prop_value) for prop_value in ast.literal_eval(dss.Properties.Value("Z1"))]
            #r0_new, x0_new = [float(prop_value) for prop_value in ast.literal_eval(dss.Properties.Value("Z0"))]
            #mdl.info(f"{r1_new=}")
            #mdl.info(f"{x1_new=}")
            #mdl.info(f"{r0_new=}")
            #mdl.info(f"{x0_new=}")

    elif element_type == "Three-Phase Transformer":

        method = 8

        if method == 0:
            for trf_handle in get_all_dss_elements(mdl, comp_type="Three-Phase Transformer"):

                dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
                dss.run_command("calcv")
                dss.Transformers.Name(dss_trf_name)
                bus1, bus2 = [bus_name for bus_name in dss.CktElement.BusNames()]
                #mdl.info(dss.CktElement.AllPropertyNames())
                freq = float(dss.Properties.Value("basefreq"))
                scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
                # Assuming two windigs for now
                vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
                pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
                trf_ratio = vbase[0] / vbase[1]
                conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
                zbase = [1e3*volt*volt/pot for volt, pot in zip(vbase, pbase)]
                xarray = [1e-2*xval for xval in mdl.get_property_value(mdl.prop(trf_handle, "XArray"))]
                #mdl.info(f"{zbase=}")
                #mdl.info(f"{xarray=}")
                # Windings
                #dss.Transformers.Xhl(1e-5)
                dss.Properties.Value("ppm_antifloat", "0.5")
                #dss.Properties.Value("%normhkVA", "1000")
                #dss.Properties.Value("%emerghkVA", "1050")
                #dss.Transformers.Xhl(1e-3)
                dss.Transformers.Wdg(1)
                rw1_delta = bool(dss.Transformers.IsDelta())
                L1_trafo = xarray[0] * zbase[0] / (2 * np.pi * freq)
                #mdl.info(f"{L1_trafo=}")
                rw1 = 1e-2*dss.Transformers.R()*zbase[0]
                rw1_eq = rw1 + scale_l*xarray[0]*zbase[0]
                dss.run_command("calcv")
                #mdl.info(f"{rw1=}")
                #mdl.info(f"{rw1_eq=}")
                dss.Transformers.R(1e-3)  # I'll consider the R1 on the XHL
                dss.Transformers.kV(vbase[1])
                dss.Properties.Value("bus", f"{bus2}")
                dss.Transformers.IsDelta(True if conn2 != "Y" else False)

                dss.Transformers.Wdg(2)
                rw2_delta = bool(dss.Transformers.IsDelta())
                L2_trafo = xarray[1] * zbase[1] / (2 * np.pi * freq)
                #mdl.info(f"{L2_trafo=}")
                rw2 = 1e-2*dss.Transformers.R()*zbase[1]
                # rw2_eq = rw2 + scale_l * xarray[1] * zbase[1]
                rw2_eq = scale_l*xarray[1]*zbase[1] # I wont consider the R2 on the XHL
                rw2_eq = rw2_eq*(trf_ratio**2)
                #mdl.info(f"{rw2=}")
                #mdl.info(f"{rw2_eq=}")

                xhl_thil = (rw1_eq + rw2_eq)*ts*2*np.pi*freq
                #mdl.info(f"{xhl_thil=}")

                dss.Transformers.kV(vbase[0])
                dss.Properties.Value("bus", f"{bus1}")
                dss.Transformers.IsDelta(True if conn1 != "Y" else False)

                dss.Transformers.Xhl(100*xhl_thil/zbase[0])

                #mdl.info(dss.Properties.Name())
                #dss.Properties.Value("%imag", "100")



                dss.run_command("calcv")

                # Core
                #dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
                #dss.Properties.Value("ppm_antifloat", "1")
                #dss.run_command("calcv")
                noloadloss = 1e-2*float(dss.Properties.Value("%noloadloss"))
                imag = 1e-2*float(dss.Properties.Value("%imag"))
                #mdl.info(f"load loss is {dss.Properties.Value('%noloadloss')}")
                #mdl.info(f"{noloadloss=}")
                #mdl.info(f"{imag=}")

                ## Teste 50 - Incluindo rloss no segundo enrolamento

                """
                # Work Around (Make an Equivalent Transformer)
                #dss.Transformers.Name(dss_trf_name)
                #dss.CktElement.Name()
                #dss.CktElement.Enabled(False)
                #dss.run_command(f"TRANSFORMER.{dss_trf_name}.enabled=no")
                #dss.CktElement.Open(1,1)
                int_bus = f"intBus_{dss_trf_name}.1.2.3"
                # Primary Side
                prim_prop = {}
                prim_prop["bus1"] = f"{bus1}"
                prim_prop["bus2"] = f"{int_bus}"
                prim_prop["phases"] = 3
                prim_prop["R1"] = rw1_eq
                prim_prop["R0"] = 1000*rw1_eq if (rw1_delta or rw2_delta) else rw1_eq
                prim_prop["R0"] = rw1_eq
                prim_prop["X1"] = 1e-9
                prim_prop["X0"] = 1000*rw1_eq if (rw1_delta or rw2_delta) else 1e-9
                prim_prop["C1"] = 0
                prim_prop["C0"] = 0
                params = [f'{param}={prim_prop.get(param)}' for param in prim_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_eqPrim " + " ".join(params)
                mdl.info(cmd_string)
                #dss.run_command(cmd_string)
                # Secondary Side
                sec_prop = {}
                sec_prop["bus1"] = f"{int_bus}"
                sec_prop["bus2"] = f"{bus2}"
                sec_prop["phases"] = 3
                sec_prop["R1"] = rw2_eq
                sec_prop["R0"] = 1000*rw2_eq if (rw1_delta or rw2_delta) else rw2_eq
                sec_prop["R0"] = rw2_eq
                sec_prop["X1"] = 1e-9
                sec_prop["X0"] = 1000*rw2_eq if (rw1_delta or rw2_delta) else 1e-9
                sec_prop["C1"] = 0
                sec_prop["C0"] = 0
                params = [f'{param}={sec_prop.get(param)}' for param in sec_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_eqSeq " + " ".join(params)
                mdl.info(cmd_string)
                #dss.run_command(cmd_string)
                """

                if noloadloss != 0 or imag != 0:
                    try:
                        #rloss = 1e3*vbase[1]*vbase[1]/(noloadloss*pbase[1])
                        rloss = (1/noloadloss)*zbase[0]
                    except:
                        rloss = 1e15
                    try:
                        xmag = (1/imag)*zbase[0]
                        rmag = scale_l * xmag # (1/ts)*(xmag/(2*np.pi*freq))
                    except:
                        rmag = 1e15

                    #dss.Properties.Value("%noloadloss", str(100*noloadloss/(1e3/pbase[0])))
                    #dss.Properties.Value("%imag", "0")
                    #dss.Properties.Value("%noloadloss", "1")
                    rcore = rloss*rmag/(rloss+rmag)
                    mdl.info(f"{rloss=}")
                    mdl.info(f"{rmag=}")
                    mdl.info(f"{rcore=}")
                    rw2_eq = rcore*rw2_eq/(rcore+rw2_eq)
                    xhl = (rw1_eq + rw2_eq)
                    xhl_thil = xhl * ts * 2 * np.pi * freq
                    dss.Transformers.Xhl(100*xhl_thil/zbase[0])

                    # DSS
                    rloss_new = 1e3 * vbase[1] * vbase[1] / (noloadloss * pbase[1])
                    ploss_old = noloadloss * pbase[1]/2

                    ploss_new = ploss_old / 1e3
                    #dss.Properties.Value("%noloadloss", f"{100*ploss_new}")
                    #dss.Transformers.Wdg(2)
                    #dss.Transformers.R(100 * req_22)
                    #mdl.info(dss.Transformers.R())

                    #core_prop = {}
                    #core_prop["bus1"] = f"{bus1}"
                    #core_prop["phases"] = 3
                    #core_prop["R"] = req
                    #core_prop["X"] = 1e-9
                    #params = [f'{param}={core_prop.get(param)}' for param in core_prop]
                    #cmd_string = "new" + f" REACTOR.{dss_trf_name}_EQCORE" + " ".join(params)
                    #dss.run_command(cmd_string)
                    #dss.Transformers.Name(dss_trf_name)
                    #cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = 0"
                    #dss.run_command(cmd_string)
                    #cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = 0"
                    #dss.run_command(cmd_string)

                    #noloadloss_eq = 100*(1e3*vbase[1]*vbase[1]/req)/pbase[1]
                    #mdl.info(f"{noloadloss_eq=}")
                    #dss.run_command("calcv")
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = {noloadloss_eq}"
                    #dss.run_command(cmd_string)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = {1e-4}"
                    #dss.run_command(cmd_string)

                    #dss.Properties.Value("%noloadloss", str(noloadloss_eq))
                    #mdl.info(cmd_string)
                    #dss.run_command(cmd_string)
                    #mdl.info(dss.Transformers.Name())
                    #dss.Properties.Value("%imag", "1e-5")
                    #mdl.info(cmd_string)
                    #dss.run_command(cmd_string)
                    #mdl.info(dss.Transformers.Name())
                    dss.run_command("calcv")

                # ppm_antifloat
                #dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
                #dss.Properties.Value("ppm_antifloat", "0.01")
                #dss.run_command("calcv")

        elif method == 1:
            for trf_handle in get_all_dss_elements(mdl, comp_type="Three-Phase Transformer"):

                dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
                dss.run_command("calcv")
                dss.Transformers.Name(dss_trf_name)
                bus1, bus2 = [bus_name for bus_name in dss.CktElement.BusNames()]
                freq = float(dss.Properties.Value("basefreq"))
                scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
                # Assuming two windigs for now
                vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
                pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
                trf_ratio = vbase[0] / vbase[1]
                mdl.info(f"{trf_ratio=}")
                conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
                zbase = [1e3 * volt * volt / pot for volt, pot in zip(vbase, pbase)]
                xarray = [1e-2 * xval for xval in mdl.get_property_value(mdl.prop(trf_handle, "XArray"))]
                # Windings
                dss.Transformers.Xhl(1e-5)
                dss.Properties.Value("ppm_antifloat", "1.0")

                dss.Transformers.Wdg(1)
                mdl.info(f"wdg{dss.Transformers.Wdg()}")
                rw1 = 1e-2 * dss.Transformers.R() * zbase[0]
                rw1_eq = rw1 + scale_l * xarray[0] * zbase[0]
                dss.Transformers.R(100 * rw1_eq / zbase[0])
                dss.run_command("calcv")
                mdl.info(f"{rw1=}")
                mdl.info(f"{rw1_eq=}")

                dss.Transformers.Wdg(2)
                rw2 = 1e-2 * dss.Transformers.R() * zbase[1]
                rw2_eq = rw2 + scale_l * xarray[1] * zbase[1]
                dss.Transformers.R(100*rw2_eq/zbase[1])
                mdl.info(f"{rw2=}")
                mdl.info(f"{rw2_eq=}")
                dss.run_command("calcv")

                # Changing the windings
                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(1)
                dss.Properties.Value("bus", f"{bus2}")
                dss.Transformers.kV(vbase[1])
                dss.Transformers.R(100*rw2_eq/zbase[1])
                dss.Transformers.IsDelta(True if conn2 != "Y" else False)

                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(2)
                dss.Properties.Value("bus", f"{bus1}")
                dss.Transformers.kV(vbase[0])
                dss.Transformers.R(100*rw1_eq/zbase[0])
                dss.Transformers.IsDelta(True if conn1 != "Y" else False)
                dss.run_command("calcv")


                noloadloss = 1e-2 * float(dss.Properties.Value("%noloadloss"))
                imag = 1e-2 * float(dss.Properties.Value("%imag"))

                #dss.Properties.Value("%noloadloss", f"{100*noloadloss}")
                #dss.Properties.Value("%imag", f"{100*imag}")

                if noloadloss != 0 or imag != 0:
                    try:
                        # rloss = 1e3*vbase[1]*vbase[1]/(noloadloss*pbase[1])
                        rloss = (1 / noloadloss) * zbase[0]
                    except:
                        rloss = 1e15
                    try:
                        xmag = (1 / imag) * zbase[0]
                        rmag = scale_l * xmag  # (1/ts)*(xmag/(2*np.pi*freq))
                    except:
                        rmag = 1e15

                    rcore = rloss * rmag / (rloss + rmag)

                    # Tentative: Apply a compensation of the OPENDSS Circuit (core is on the terminal side)
                    r1 = rw1_eq
                    r2 = rw2_eq*trf_ratio**2
                    core_middle = r1 + r2*rcore/(r2+rcore)
                    core_end = (r1+r2)*rcore/(r1+r2+rcore)
                    loss_mult = core_end/core_middle

                    rw1_new = rw1_eq*rcore/(rw1_eq+rcore)
                    dss.Transformers.Name(dss_trf_name)
                    dss.Transformers.Wdg(2)
                    dss.Transformers.R(100 * rw1_new / zbase[0])
                    # 25 is a alleatory factor :)
                    dss.Properties.Value("%noloadloss", f"{5*(zbase[0]/rcore)}")
                    dss.Properties.Value("%imag", f"0")
                    #dss.Transformers.Name(dss_trf_name)
                    #dss.Transformers.Wdg(1)
                    #dss.Transformers.R(100 * rw2_new / zbase[1])

                    # DSS
                    #rloss_new = 1e3 * vbase[1] * vbase[1] / (noloadloss * pbase[1])
                    #ploss_old = noloadloss * pbase[1] / 2

                    #ploss_new = ploss_old / 1e3
                    # dss.Properties.Value("%noloadloss", f"{100*ploss_new}")
                    # dss.Transformers.Wdg(2)
                    # dss.Transformers.R(100 * req_22)
                    # mdl.info(dss.Transformers.R())

                    # core_prop = {}
                    # core_prop["bus1"] = f"{bus1}"
                    # core_prop["phases"] = 3
                    # core_prop["R"] = req
                    # core_prop["X"] = 1e-9
                    # params = [f'{param}={core_prop.get(param)}' for param in core_prop]
                    # cmd_string = "new" + f" REACTOR.{dss_trf_name}_EQCORE" + " ".join(params)
                    # dss.run_command(cmd_string)
                    # dss.Transformers.Name(dss_trf_name)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = 0"
                    # dss.run_command(cmd_string)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = 0"
                    # dss.run_command(cmd_string)

                    # noloadloss_eq = 100*(1e3*vbase[1]*vbase[1]/req)/pbase[1]
                    # mdl.info(f"{noloadloss_eq=}")
                    # dss.run_command("calcv")
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = {noloadloss_eq}"
                    # dss.run_command(cmd_string)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = {1e-4}"
                    # dss.run_command(cmd_string)

                    # dss.Properties.Value("%noloadloss", str(noloadloss_eq))
                    # mdl.info(cmd_string)
                    # dss.run_command(cmd_string)
                    # mdl.info(dss.Transformers.Name())
                    # dss.Properties.Value("%imag", "1e-5")
                    # mdl.info(cmd_string)
                    # dss.run_command(cmd_string)
                    # mdl.info(dss.Transformers.Name())
                    dss.run_command("calcv")

                # ppm_antifloat
                # dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
                # dss.Properties.Value("ppm_antifloat", "0.01")
                # dss.run_command("calcv")

        elif method == 2:
            for trf_handle in get_all_dss_elements(mdl, comp_type="Three-Phase Transformer"):

                dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
                dss.Transformers.Name(dss_trf_name)
                bus1, bus2 = [bus_name for bus_name in dss.CktElement.BusNames()]
                freq = float(dss.Properties.Value("basefreq"))
                scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
                # Assuming two windigs for now
                vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
                pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
                trf_ratio = vbase[0] / vbase[1]
                conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
                zbase = [1e3*volt*volt/pot for volt, pot in zip(vbase, pbase)]
                xarray = [1e-2*xval for xval in mdl.get_property_value(mdl.prop(trf_handle, "XArray"))]
                dss.Transformers.Xhl(1e-6)
                dss.Properties.Value("ppm_antifloat", "1.0")
                # Windings
                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(1)
                rw1_delta = bool(dss.Transformers.IsDelta())
                L1_trafo = xarray[0] * zbase[0] / (2 * np.pi * freq)
                rw1 = 1e-2*dss.Transformers.R()*zbase[0]
                rw1_eq = rw1 + scale_l*xarray[0]*zbase[0]

                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(2)
                rw2_delta = bool(dss.Transformers.IsDelta())
                L2_trafo = xarray[1] * zbase[1] / (2 * np.pi * freq)
                mdl.info(f"{L2_trafo=}")
                rw2 = 1e-2*dss.Transformers.R()*zbase[1]
                rw2_eq = rw2 + scale_l * xarray[1] * zbase[1]
                rw2_eq = scale_l*xarray[1]*zbase[1]
                rw2_eq = rw2_eq*(trf_ratio**2)

                # Changing the windings

                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(1)
                dss.Properties.Value("bus", f"int_{bus2}")
                dss.Transformers.R(1e-3)
                dss.Transformers.kV(vbase[1])
                dss.Transformers.IsDelta(True if conn2 != "Y" else False)
                sec_prop = {}
                sec_prop["bus1"] = f"{bus2}"
                sec_prop["bus2"] = f"int_{bus2}"
                sec_prop["phases"] = "3"
                sec_prop["R"] = f"{rw1_eq}"
                sec_prop["X"] = 1e-3
                params = [f'{param}={sec_prop.get(param)}' for param in sec_prop]
                cmd_string = "new" + f" REACTOR.{dss_trf_name}_sec " + " ".join(params)
                dss.run_command(cmd_string)
                mdl.info(cmd_string)

                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(2)
                dss.Properties.Value("bus", f"int_{bus1}")
                dss.Transformers.R(1e-3)
                dss.Transformers.kV(vbase[0])
                dss.Transformers.IsDelta(True if conn1 != "Y" else False)
                core_prop = {}
                core_prop["bus1"] = f"{bus1}"
                core_prop["bus2"] = f"int_{bus1}"
                core_prop["phases"] = "3"
                core_prop["R"] = f"{rw2_eq}"
                core_prop["X"] = 1e-3
                params = [f'{param}={core_prop.get(param)}' for param in core_prop]
                cmd_string = "new" + f" REACTOR.{dss_trf_name}_prim " + " ".join(params)
                mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                # Core
                #dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
                #dss.Properties.Value("ppm_antifloat", "1")
                #dss.run_command("calcv")
                dss.Transformers.Name(dss_trf_name)
                noloadloss = 1e-2*float(dss.Properties.Value("%noloadloss"))
                imag = 1e-2*float(dss.Properties.Value("%imag"))

                if noloadloss != 0 or imag != 0:
                    try:
                        #rloss = 1e3*vbase[1]*vbase[1]/(noloadloss*pbase[1])
                        rloss = (1/noloadloss)*zbase[0]
                    except:
                        rloss = 1e15
                    try:
                        xmag = (1/imag)*zbase[0]
                        rmag = scale_l * xmag # (1/ts)*(xmag/(2*np.pi*freq))
                    except:
                        rmag = 1e15

                    #dss.Properties.Value("%noloadloss", str(100*noloadloss/(1e3/pbase[0])))
                    #dss.Properties.Value("%imag", "0")
                    #dss.Properties.Value("%noloadloss", "1")
                    asdasdasda
                    rcore = rloss*rmag/(rloss+rmag)
                    mdl.info(f"{rloss=}")
                    mdl.info(f"{rmag=}")
                    mdl.info(f"{rcore=}")
                    rw2_eq = rcore*rw2_eq/(rcore+rw2_eq)
                    xhl = (rw1_eq + rw2_eq)
                    xhl_thil = xhl * ts * 2 * np.pi * freq
                    dss.Transformers.Xhl(100*xhl_thil/zbase[0])

                    # DSS
                    rloss_new = 1e3 * vbase[1] * vbase[1] / (noloadloss * pbase[1])
                    ploss_old = noloadloss * pbase[1]/2

                    ploss_new = ploss_old / 1e3
                    #dss.Properties.Value("%noloadloss", f"{100*ploss_new}")
                    #dss.Transformers.Wdg(2)
                    #dss.Transformers.R(100 * req_22)
                    #mdl.info(dss.Transformers.R())

                    #core_prop = {}
                    #core_prop["bus1"] = f"{bus1}"
                    #core_prop["phases"] = 3
                    #core_prop["R"] = req
                    #core_prop["X"] = 1e-9
                    #params = [f'{param}={core_prop.get(param)}' for param in core_prop]
                    #cmd_string = "new" + f" REACTOR.{dss_trf_name}_EQCORE" + " ".join(params)
                    #dss.run_command(cmd_string)
                    #dss.Transformers.Name(dss_trf_name)
                    #cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = 0"
                    #dss.run_command(cmd_string)
                    #cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = 0"
                    #dss.run_command(cmd_string)

                    #noloadloss_eq = 100*(1e3*vbase[1]*vbase[1]/req)/pbase[1]
                    #mdl.info(f"{noloadloss_eq=}")
                    #dss.run_command("calcv")
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = {noloadloss_eq}"
                    #dss.run_command(cmd_string)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = {1e-4}"
                    #dss.run_command(cmd_string)

                    #dss.Properties.Value("%noloadloss", str(noloadloss_eq))
                    #mdl.info(cmd_string)
                    #dss.run_command(cmd_string)
                    #mdl.info(dss.Transformers.Name())
                    #dss.Properties.Value("%imag", "1e-5")
                    #mdl.info(cmd_string)
                    #dss.run_command(cmd_string)
                    #mdl.info(dss.Transformers.Name())
                    dss.run_command("calcv")

                # ppm_antifloat
                #dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
                #dss.Properties.Value("ppm_antifloat", "0.01")
                #dss.run_command("calcv")

        elif method == 3:
            for trf_handle in get_all_dss_elements(mdl, comp_type="Three-Phase Transformer"):

                dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
                dss.Transformers.Name(dss_trf_name)
                bus1, bus2 = [bus_name for bus_name in dss.CktElement.BusNames()]
                freq = float(dss.Properties.Value("basefreq"))
                scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
                # Assuming two windigs for now
                vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
                pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
                trf_ratio = vbase[0] / vbase[1]
                conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
                zbase = [1e3*volt*volt/pot for volt, pot in zip(vbase, pbase)]
                xarray = [1e-2*xval for xval in mdl.get_property_value(mdl.prop(trf_handle, "XArray"))]
                # Windings
                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(1)
                rw1_delta = bool(dss.Transformers.IsDelta())
                L1_trafo = xarray[0] * zbase[0] / (2 * np.pi * freq)
                rw1 = 1e-2*dss.Transformers.R()*zbase[0]
                rw1_eq = rw1 + scale_l*xarray[0]*zbase[0]
                mdl.info(f"{rw1=}")
                mdl.info(f"{rw1_eq=}")

                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(2)
                rw2_delta = bool(dss.Transformers.IsDelta())
                L2_trafo = xarray[1] * zbase[1] / (2 * np.pi * freq)
                mdl.info(f"{L2_trafo=}")
                rw2 = 1e-2*dss.Transformers.R()*zbase[1]
                rw2_eq = rw2 + scale_l * xarray[1] * zbase[1]
                #rw2_eq = scale_l*xarray[1]*zbase[1]
                rw2_eq = rw2_eq*(trf_ratio**2)
                mdl.info(f"{rw2=}")
                mdl.info(f"{rw2_eq=}")

                # Changing the windings
                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Xhl(1e-3)
                dss.Properties.Value("ppm_antifloat", "1.0")
                mdl.info(dss.CktElement.Name())
                dss.Transformers.Wdg(1)
                dss.Properties.Value("bus", f"int_{bus2}")
                dss.Transformers.R(0)
                dss.Transformers.kV(vbase[1])
                dss.Transformers.IsDelta(True if conn2 != "Y" else False)
                mdl.info(f"Sec is delta? {True if conn2 != 'Y' else False}")
                sec_prop = {}
                sec_prop["bus1"] = f"int_{bus2}"
                sec_prop["bus2"] = f"{bus2}"
                sec_prop["phases"] = 3
                sec_prop["R1"] = rw1_eq
                sec_prop["R0"] = rw1_eq
                sec_prop["X1"] = 1e-3
                sec_prop["X0"] = 1e-3
                sec_prop["C1"] = 0
                sec_prop["C0"] = 0
                params = [f'{param}={sec_prop.get(param)}' for param in sec_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_sec " + " ".join(params)
                dss.run_command(cmd_string)
                mdl.info(cmd_string)

                dss.Transformers.Name(dss_trf_name)
                mdl.info(dss.CktElement.Name())
                dss.Transformers.Wdg(2)
                dss.Properties.Value("bus", f"int_{bus1}")
                dss.Transformers.R(0)
                dss.Transformers.kV(vbase[0])
                dss.Transformers.IsDelta(True if conn1 != "Y" else False)
                mdl.info(f"Pri is delta? {True if conn1 != 'Y' else False}")
                prim_prop = {}
                prim_prop["bus1"] = f"{bus1}"
                prim_prop["bus2"] = f"int_{bus1}"
                prim_prop["phases"] = 3
                prim_prop["R1"] = rw2_eq
                prim_prop["R0"] = rw2_eq
                prim_prop["X1"] = 1e-3
                prim_prop["X0"] = 1e-3
                prim_prop["C1"] = 0
                prim_prop["C0"] = 0
                params = [f'{param}={prim_prop.get(param)}' for param in prim_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_prim " + " ".join(params)
                dss.run_command(cmd_string)
                mdl.info(cmd_string)
                dss.run_command("calcv")

                # Core
                #dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
                #dss.Properties.Value("ppm_antifloat", "1")
                #dss.run_command("calcv")
                dss.Transformers.Name(dss_trf_name)
                noloadloss = 1e-2*float(dss.Properties.Value("%noloadloss"))
                imag = 1e-2*float(dss.Properties.Value("%imag"))

                if noloadloss != 0 or imag != 0:
                    try:
                        #rloss = 1e3*vbase[1]*vbase[1]/(noloadloss*pbase[1])
                        rloss = (1/noloadloss)*zbase[0]
                    except:
                        rloss = 1e15
                    try:
                        xmag = (1/imag)*zbase[0]
                        rmag = scale_l * xmag # (1/ts)*(xmag/(2*np.pi*freq))
                    except:
                        rmag = 1e15

                    #dss.Properties.Value("%noloadloss", str(100*noloadloss/(1e3/pbase[0])))
                    #dss.Properties.Value("%imag", "0")
                    #dss.Properties.Value("%noloadloss", "1")
                    asdasdasda
                    rcore = rloss*rmag/(rloss+rmag)
                    #mdl.info(f"{rloss=}")
                    #mdl.info(f"{rmag=}")
                    #mdl.info(f"{rcore=}")
                    rw2_eq = rcore*rw2_eq/(rcore+rw2_eq)
                    xhl = (rw1_eq + rw2_eq)
                    xhl_thil = xhl * ts * 2 * np.pi * freq
                    dss.Transformers.Xhl(100*xhl_thil/zbase[0])

                    # DSS
                    rloss_new = 1e3 * vbase[1] * vbase[1] / (noloadloss * pbase[1])
                    ploss_old = noloadloss * pbase[1]/2

                    ploss_new = ploss_old / 1e3
                    #dss.Properties.Value("%noloadloss", f"{100*ploss_new}")
                    #dss.Transformers.Wdg(2)
                    #dss.Transformers.R(100 * req_22)
                    #mdl.info(dss.Transformers.R())

                    #core_prop = {}
                    #core_prop["bus1"] = f"{bus1}"
                    #core_prop["phases"] = 3
                    #core_prop["R"] = req
                    #core_prop["X"] = 1e-9
                    #params = [f'{param}={core_prop.get(param)}' for param in core_prop]
                    #cmd_string = "new" + f" REACTOR.{dss_trf_name}_EQCORE" + " ".join(params)
                    #dss.run_command(cmd_string)
                    #dss.Transformers.Name(dss_trf_name)
                    #cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = 0"
                    #dss.run_command(cmd_string)
                    #cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = 0"
                    #dss.run_command(cmd_string)

                    #noloadloss_eq = 100*(1e3*vbase[1]*vbase[1]/req)/pbase[1]
                    #mdl.info(f"{noloadloss_eq=}")
                    #dss.run_command("calcv")
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = {noloadloss_eq}"
                    #dss.run_command(cmd_string)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = {1e-4}"
                    #dss.run_command(cmd_string)

                    #dss.Properties.Value("%noloadloss", str(noloadloss_eq))
                    #mdl.info(cmd_string)
                    #dss.run_command(cmd_string)
                    #mdl.info(dss.Transformers.Name())
                    #dss.Properties.Value("%imag", "1e-5")
                    #mdl.info(cmd_string)
                    #dss.run_command(cmd_string)
                    #mdl.info(dss.Transformers.Name())
                    dss.run_command("calcv")

                # ppm_antifloat
                #dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
                #dss.Properties.Value("ppm_antifloat", "0.01")
                #dss.run_command("calcv")

        elif method == 4:
            for trf_handle in get_all_dss_elements(mdl, comp_type="Three-Phase Transformer"):

                dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
                dss.run_command("calcv")
                dss.Transformers.Name(dss_trf_name)
                bus1, bus2 = [bus_name for bus_name in dss.CktElement.BusNames()]
                freq = float(dss.Properties.Value("basefreq"))
                scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
                # Assuming two windigs for now
                vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
                pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
                trf_ratio = vbase[0] / vbase[1]
                #mdl.info(f"{trf_ratio=}")
                conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
                zbase = [1e3 * volt * volt / pot for volt, pot in zip(vbase, pbase)]
                xarray = [1e-2 * xval for xval in mdl.get_property_value(mdl.prop(trf_handle, "XArray"))]
                # Windings
                dss.Transformers.Xhl(1e-5)
                dss.Properties.Value("ppm_antifloat", "0.0")

                dss.Transformers.Wdg(1)
                #mdl.info(f"wdg{dss.Transformers.Wdg()}")
                rw1 = 1e-2 * dss.Transformers.R() * zbase[0]
                rw1_eq = rw1 + scale_l * xarray[0] * zbase[0]
                dss.Transformers.R(100 * rw1_eq / zbase[0])
                dss.run_command("calcv")
                #mdl.info(f"{rw1=}")
                #mdl.info(f"{rw1_eq=}")

                dss.Transformers.Wdg(2)
                rw2 = 1e-2 * dss.Transformers.R() * zbase[1]
                rw2_eq = rw2 + scale_l * xarray[1] * zbase[1]
                dss.Transformers.R(100 * rw2_eq / zbase[1])
                #mdl.info(f"{rw2=}")
                #mdl.info(f"{rw2_eq=}")
                dss.run_command("calcv")

                # Changing the windings
                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(1)
                dss.Properties.Value("bus", f"int_{bus2}")
                dss.Transformers.kV(vbase[1])
                dss.Transformers.R(0)
                dss.Transformers.IsDelta(True if conn2 != "Y" else False)

                if conn2 != "Y":
                    #mdl.info("DELTA")
                    #mdl.info(f"Rw2/3")
                    rw2_eq = rw2_eq/3
                    rw2_r0 = rw2_eq
                    rw2_x0 = -1e-4
                    rw2_x1 = -1e-4
                    dss.Properties.Value("ppm_antifloat", "0.05")
                    if conn1 == "Y":
                        rw2_eq = rw2_eq / np.sqrt(3)
                else:
                    #mdl.info("Y")
                    rw2_eq = rw2_eq
                    rw2_r0 = rw2_eq
                    rw2_x0 = -1e-4
                    rw2_x1 = -1e-4
                    if conn1 != "Y":
                        #mdl.info(f"Rw2 * sqrt(3)")
                        rw2_eq = rw2_eq * np.sqrt(3)
                        rw2_r0 = rw2_eq

                prim_prop = {}
                prim_prop["bus1"] = f"int_{bus2}"
                prim_prop["bus2"] = f"{bus2}"
                prim_prop["phases"] = 3
                prim_prop["R1"] = rw2_eq
                prim_prop["R0"] = rw2_r0
                prim_prop["X1"] = rw2_x1
                prim_prop["X0"] = rw2_x0
                prim_prop["C1"] = 0
                prim_prop["C0"] = 0
                params = [f'{param}={prim_prop.get(param)}' for param in prim_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_pri " + " ".join(params)
                #mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(2)
                dss.Properties.Value("bus", f"int_{bus1}")
                dss.Transformers.kV(vbase[0])
                dss.Transformers.R(1e-3)
                dss.Transformers.IsDelta(True if conn1 != "Y" else False)
                if conn1 != "Y":
                    #mdl.info("DELTA")
                    #mdl.info(f"RW1/3")
                    rw1_eq = rw1_eq*(1/3)
                    rw1_r0 = rw1_eq
                    rw1_x0 = 1e-5
                    rw1_x1 = 1e-5
                    dss.Properties.Value("ppm_antifloat", "0.05")
                else:
                    #mdl.info("Y")
                    rw1_eq = rw1_eq
                    rw1_r0 = rw1_eq
                    rw1_x0 = 1e-6
                    rw1_x1 = 1e-6

                sec_prop = {}
                sec_prop["bus1"] = f"int_{bus1}"
                sec_prop["bus2"] = f"{bus1}"
                sec_prop["phases"] = 3
                sec_prop["R1"] = rw1_eq
                sec_prop["R0"] = rw1_r0
                sec_prop["X1"] = rw1_x1
                sec_prop["X0"] = rw1_x0
                sec_prop["C1"] = 0
                sec_prop["C0"] = 0
                params = [f'{param}={sec_prop.get(param)}' for param in sec_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_sec " + " ".join(params)
                #mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                dss.Transformers.Name(dss_trf_name)
                noloadloss = 1e-2 * float(dss.Properties.Value("%noloadloss"))
                imag = 1e-2 * float(dss.Properties.Value("%imag"))
                #mdl.info("transformer connections")
                #mdl.info(dss.CktElement.BusNames())

                # dss.Properties.Value("%noloadloss", f"{100*noloadloss}")
                # dss.Properties.Value("%imag", f"{100*imag}")

                if noloadloss != 0 or imag != 0:
                    try:
                        # rloss = 1e3*vbase[1]*vbase[1]/(noloadloss*pbase[1])
                        rloss = (1 / noloadloss) * zbase[0]
                    except:
                        rloss = 1e15
                    try:
                        xmag = (1 / imag) * zbase[0]
                        rmag = scale_l * xmag  # (1/ts)*(xmag/(2*np.pi*freq))
                    except:
                        rmag = 1e15

                    rcore = rloss * rmag / (rloss + rmag)

                    # Tentative: Apply a compensation of the OPENDSS Circuit (core is on the terminal side)
                    r1 = rw1_eq
                    r2 = rw2_eq * trf_ratio ** 2
                    core_middle = r1 + r2 * rcore / (r2 + rcore)
                    core_end = (r1 + r2) * rcore / (r1 + r2 + rcore)
                    loss_mult = core_end / core_middle

                    rw1_new = rw1_eq * rcore / (rw1_eq + rcore)
                    #dss.Transformers.Name(dss_trf_name)
                    #dss.Transformers.Wdg(2)
                    #dss.Transformers.R(100 * rw1_new / zbase[0])
                    # 25 is a alleatory factor :)
                    #dss.Properties.Value("%noloadloss", f"{5 * (zbase[0] / rcore)}")
                    #dss.Properties.Value("%imag", f"0")
                    # dss.Transformers.Name(dss_trf_name)
                    # dss.Transformers.Wdg(1)
                    # dss.Transformers.R(100 * rw2_new / zbase[1])

                    # DSS
                    # rloss_new = 1e3 * vbase[1] * vbase[1] / (noloadloss * pbase[1])
                    # ploss_old = noloadloss * pbase[1] / 2

                    # ploss_new = ploss_old / 1e3
                    # dss.Properties.Value("%noloadloss", f"{100*ploss_new}")
                    # dss.Transformers.Wdg(2)
                    # dss.Transformers.R(100 * req_22)
                    # mdl.info(dss.Transformers.R())

                    # core_prop = {}
                    # core_prop["bus1"] = f"{bus1}"
                    # core_prop["phases"] = 3
                    # core_prop["R"] = req
                    # core_prop["X"] = 1e-9
                    # params = [f'{param}={core_prop.get(param)}' for param in core_prop]
                    # cmd_string = "new" + f" REACTOR.{dss_trf_name}_EQCORE" + " ".join(params)
                    # dss.run_command(cmd_string)
                    # dss.Transformers.Name(dss_trf_name)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = 0"
                    # dss.run_command(cmd_string)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = 0"
                    # dss.run_command(cmd_string)

                    # noloadloss_eq = 100*(1e3*vbase[1]*vbase[1]/req)/pbase[1]
                    # mdl.info(f"{noloadloss_eq=}")
                    # dss.run_command("calcv")
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = {noloadloss_eq}"
                    # dss.run_command(cmd_string)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = {1e-4}"
                    # dss.run_command(cmd_string)

                    # dss.Properties.Value("%noloadloss", str(noloadloss_eq))
                    # mdl.info(cmd_string)
                    # dss.run_command(cmd_string)
                    # mdl.info(dss.Transformers.Name())
                    # dss.Properties.Value("%imag", "1e-5")
                    # mdl.info(cmd_string)
                    # dss.run_command(cmd_string)
                    # mdl.info(dss.Transformers.Name())
                    dss.run_command("calcv")

                # ppm_antifloat
                # dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
                # dss.Properties.Value("ppm_antifloat", "0.01")
                # dss.run_command("calcv")

        elif method == 5:
            for trf_handle in get_all_dss_elements(mdl, comp_type="Three-Phase Transformer"):

                dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
                if dss_trf_name in ['TREAL3', 'TREAL4', 'TDEBUG3', 'TDEBUG4']:
                    return dss
                dss.run_command("calcv")
                dss.Transformers.Name(dss_trf_name)
                bus1, bus2 = [bus_name for bus_name in dss.CktElement.BusNames()]
                freq = float(dss.Properties.Value("basefreq"))
                scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
                # Assuming two windigs for now
                vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
                pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
                trf_ratio = vbase[0] / vbase[1]
                #mdl.info(f"{trf_ratio=}")
                conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
                zbase = [1e3 * volt * volt / pot for volt, pot in zip(vbase, pbase)]
                if conn1 != "Y":
                    zbase[0] = zbase[0]*3
                if conn2 != "Y":
                    zbase[1] = zbase[1]*3
                xarray = [1e-2 * xval for xval in mdl.get_property_value(mdl.prop(trf_handle, "XArray"))]
                # Windings
                dss.Transformers.Xhl(1e-3)
                dss.Properties.Value("ppm_antifloat", "0.0")

                dss.Transformers.Wdg(1)
                rw1 = 1e-2 * dss.Transformers.R() * zbase[0]
                rw1_eq = rw1 + scale_l * xarray[0] * zbase[0]
                dss.Transformers.R(100 * rw1_eq / zbase[0])
                dss.run_command("calcv")
                mdl.info(f"{rw1=}") if debug else None
                mdl.info(f"{rw1_eq=}") if debug else None

                dss.Transformers.Wdg(2)
                rw2 = 1e-2 * dss.Transformers.R() * zbase[1]
                rw2_eq = rw2 + scale_l * xarray[1] * zbase[1]
                dss.Transformers.R(100 * rw2_eq / zbase[1])
                mdl.info(f"{rw2=}") if debug else None
                mdl.info(f"{rw2_eq=}") if debug else None
                dss.run_command("calcv")

                # Changing the windings
                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(1)
                dss.Properties.Value("bus", f"int_{bus2}")
                dss.Transformers.kV(vbase[1])
                dss.Transformers.R(0)
                dss.Transformers.IsDelta(True if conn2 != "Y" else False)

                rw2_r1 = rw2_eq
                rw2_r0 = rw2_eq
                rw2_x0 = 1e-6
                rw2_x1 = 1e-6

                prim_prop = {}
                prim_prop["bus1"] = f"int_{bus2}"
                prim_prop["bus2"] = f"{bus2}"
                prim_prop["phases"] = 3
                prim_prop["R1"] = rw2_r1
                prim_prop["R0"] = rw2_r0
                prim_prop["X1"] = rw2_x1
                prim_prop["X0"] = rw2_x0
                prim_prop["C1"] = 0
                prim_prop["C0"] = 0
                params = [f'{param}={prim_prop.get(param)}' for param in prim_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_pri " + " ".join(params)
                mdl.info(cmd_string) if debug else None
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(2)
                dss.Properties.Value("bus", f"int_{bus1}")
                dss.Transformers.kV(vbase[0])
                dss.Transformers.R(0)
                #dss.Transformers.IsDelta(True if conn1 != "Y" else False)
                dss.Transformers.IsDelta(False)

                rw1_r1 = -1*rw1_eq
                rw1_r0 = 2*rw1_eq
                rw1_x1 = 1e-6
                rw1_x0 = rw1_eq
                dss.Properties.Value("ppm_antifloat", "0.0")

                sec_prop = {}
                sec_prop["bus1"] = f"int_{bus1}"
                sec_prop["bus2"] = f"{bus1}"
                sec_prop["phases"] = 3
                sec_prop["R1"] = rw1_r1
                sec_prop["R0"] = rw1_r0
                sec_prop["X1"] = rw1_x1
                sec_prop["X0"] = rw1_x0
                sec_prop["C1"] = 0
                sec_prop["C0"] = 0
                params = [f'{param}={sec_prop.get(param)}' for param in sec_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_sec " + " ".join(params)
                mdl.info(cmd_string) if debug else None
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                dss.Transformers.Name(dss_trf_name)
                noloadloss = 1e-2 * float(dss.Properties.Value("%noloadloss"))
                imag = 1e-2 * float(dss.Properties.Value("%imag"))
                #mdl.info("transformer connections")
                #mdl.info(dss.CktElement.BusNames())

                # dss.Properties.Value("%noloadloss", f"{100*noloadloss}")
                # dss.Properties.Value("%imag", f"{100*imag}")

                if noloadloss != 0 or imag != 0:
                    try:
                        # rloss = 1e3*vbase[1]*vbase[1]/(noloadloss*pbase[1])
                        rloss = (1 / noloadloss) * zbase[0]
                    except:
                        rloss = 1e15
                    try:
                        xmag = (1 / imag) * zbase[0]
                        rmag = scale_l * xmag  # (1/ts)*(xmag/(2*np.pi*freq))
                    except:
                        rmag = 1e15

                    rcore = rloss * rmag / (rloss + rmag)

                    # Tentative: Apply a compensation of the OPENDSS Circuit (core is on the terminal side)
                    r1 = rw1_eq
                    r2 = rw2_eq * trf_ratio ** 2
                    core_middle = r1 + r2 * rcore / (r2 + rcore)
                    core_end = (r1 + r2) * rcore / (r1 + r2 + rcore)
                    loss_mult = core_end / core_middle

                    rw1_new = rw1_eq * rcore / (rw1_eq + rcore)
                    #dss.Transformers.Name(dss_trf_name)
                    #dss.Transformers.Wdg(2)
                    #dss.Transformers.R(100 * rw1_new / zbase[0])
                    # 25 is a alleatory factor :)
                    #dss.Properties.Value("%noloadloss", f"{5 * (zbase[0] / rcore)}")
                    #dss.Properties.Value("%imag", f"0")
                    # dss.Transformers.Name(dss_trf_name)
                    # dss.Transformers.Wdg(1)
                    # dss.Transformers.R(100 * rw2_new / zbase[1])

                    # DSS
                    # rloss_new = 1e3 * vbase[1] * vbase[1] / (noloadloss * pbase[1])
                    # ploss_old = noloadloss * pbase[1] / 2

                    # ploss_new = ploss_old / 1e3
                    # dss.Properties.Value("%noloadloss", f"{100*ploss_new}")
                    # dss.Transformers.Wdg(2)
                    # dss.Transformers.R(100 * req_22)
                    # mdl.info(dss.Transformers.R())

                    # core_prop = {}
                    # core_prop["bus1"] = f"{bus1}"
                    # core_prop["phases"] = 3
                    # core_prop["R"] = req
                    # core_prop["X"] = 1e-9
                    # params = [f'{param}={core_prop.get(param)}' for param in core_prop]
                    # cmd_string = "new" + f" REACTOR.{dss_trf_name}_EQCORE" + " ".join(params)
                    # dss.run_command(cmd_string)
                    # dss.Transformers.Name(dss_trf_name)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = 0"
                    # dss.run_command(cmd_string)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = 0"
                    # dss.run_command(cmd_string)

                    # noloadloss_eq = 100*(1e3*vbase[1]*vbase[1]/req)/pbase[1]
                    # mdl.info(f"{noloadloss_eq=}")
                    # dss.run_command("calcv")
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = {noloadloss_eq}"
                    # dss.run_command(cmd_string)
                    # cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = {1e-4}"
                    # dss.run_command(cmd_string)

                    # dss.Properties.Value("%noloadloss", str(noloadloss_eq))
                    # mdl.info(cmd_string)
                    # dss.run_command(cmd_string)
                    # mdl.info(dss.Transformers.Name())
                    # dss.Properties.Value("%imag", "1e-5")
                    # mdl.info(cmd_string)
                    # dss.run_command(cmd_string)
                    # mdl.info(dss.Transformers.Name())
                    dss.run_command("calcv")

                # ppm_antifloat
                # dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
                # dss.Properties.Value("ppm_antifloat", "0.01")
                # dss.run_command("calcv")

        elif method == 6:
            # Jogando toda a impedância para R. E calculando um valor equivalente de impedância se o núcleo for
            # representado. Não funciona dependendo da impedância que estiver conectada ao secundário do trafo!!!
            for trf_handle in get_all_dss_elements(mdl, comp_type="Three-Phase Transformer"):

                dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
                if dss_trf_name in ['TREAL3', 'TREAL4', 'TDEBUG3', 'TDEBUG4']:
                    return dss
                dss.run_command("calcv")
                dss.Transformers.Name(dss_trf_name)
                bus1, bus2 = [bus_name for bus_name in dss.CktElement.BusNames()]
                freq = float(dss.Properties.Value("basefreq"))
                scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
                # Assuming two windigs for now
                vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
                pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
                trf_ratio = vbase[0] / vbase[1]
                #mdl.info(f"{trf_ratio=}")
                conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
                zbase = [1e3 * volt * volt / pot for volt, pot in zip(vbase, pbase)]
                if conn1 != "Y":
                    zbase[0] = zbase[0]*1
                if conn2 != "Y":
                    zbase[1] = zbase[1]*1
                xarray = [1e-2 * xval for xval in mdl.get_property_value(mdl.prop(trf_handle, "XArray"))]
                # Windings
                dss.Transformers.Xhl(1e-3)
                #dss.Properties.Value("ppm_antifloat", "0.01")
                dss.Properties.Value("ppm_antifloat", "0.1")

                dss.Transformers.Wdg(1)
                rw1 = 1e-2 * dss.Transformers.R() * zbase[0]
                rw1_eq = rw1 + scale_l * xarray[0] * zbase[0]
                dss.run_command("calcv")
                mdl.info(f"{rw1=}") if debug else None
                mdl.info(f"{rw1_eq=}") if debug else None
                dss.Transformers.R(100 * rw1_eq / zbase[0])

                dss.Transformers.Wdg(2)
                rw2 = 1e-2 * dss.Transformers.R() * zbase[1]
                rw2_eq = rw2 + scale_l * xarray[1] * zbase[1]
                dss.Transformers.R(100 * rw2_eq / zbase[1])
                mdl.info(f"{rw2=}") if debug else None
                mdl.info(f"{rw2_eq=}") if debug else None
                dss.run_command("calcv")

                # Changing the windings
                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(1)
                rtotal = rw1_eq + rw2_eq*trf_ratio**2
                mdl.info(f"{rtotal=}")
                dss.Transformers.R(100 * rtotal/zbase[0])

                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(2)
                dss.Transformers.R(0)

                dss.Transformers.Name(dss_trf_name)
                noloadloss = 1e-2 * float(dss.Properties.Value("%noloadloss"))
                imag = 1e-2 * float(dss.Properties.Value("%imag"))

                if noloadloss != 0 or imag != 0:
                    try:
                        # rloss = 1e3*vbase[1]*vbase[1]/(noloadloss*pbase[1])
                        rloss = (1 / noloadloss) * zbase[0]
                    except:
                        rloss = 1e15
                    try:
                        xmag = (1 / imag) * zbase[0]
                        rmag = scale_l * xmag
                    except:
                        rmag = 1e15

                    rcore = rloss * rmag / (rloss + rmag)

                    # Tentative: Apply a compensation of the OPENDSS Circuit (core is on the terminal side)
                    r_half = rtotal/2
                    dss.Transformers.Name(dss_trf_name)
                    dss.CktElement.Open(2, 0)
                    dss.run_command("calcv")
                    dss.run_command("Solve Mode=FaultStudy")
                    mdl.info(f"{bus2=}")
                    dss.Circuit.SetActiveBus(bus2)
                    mdl.info(f"{dss.Bus.Name()}")
                    dss.Bus.ZscRefresh()
                    zsc1 = [float(z) for z in dss.Bus.Zsc1()]
                    mdl.info(f"{zsc1=}")
                    if zsc1[1] >= 0:
                        rsc = (zsc1[0] + scale_l*zsc1[1])*trf_ratio**2
                    else:
                        rsc = (zsc1[0] + scale_x*zsc1[1])*trf_ratio**2

                    r_comp = r_half + (r_half+rsc)*rcore/((r_half+rsc)+rcore)
                    mdl.info(f"{rtotal=}")
                    mdl.info(f"{r_comp=}")
                    dss.Transformers.Name(dss_trf_name)
                    dss.CktElement.Close(2, 0)
                    dss.run_command("Solve Mode=Snapshot")

                    dss.Transformers.Name(dss_trf_name)
                    dss.Transformers.Wdg(1)
                    dss.Transformers.R(100 * r_comp / zbase[0])

                    dss.Properties.Value("%noloadloss", "0")
                    dss.Properties.Value("%imag", "0")
                    dss.run_command("calcv")

        elif method == 7:
            # Jogando toda a impedância para R. E Apenas invertendo os terminais!!!
            for trf_handle in get_all_dss_elements(mdl, comp_type="Three-Phase Transformer"):

                dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
                dss.run_command("calcv")
                dss.Transformers.Name(dss_trf_name)
                bus1, bus2 = [bus_name for bus_name in dss.CktElement.BusNames()]
                freq = float(dss.Properties.Value("basefreq"))
                scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
                # Assuming two windigs for now
                vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
                pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
                trf_ratio = vbase[0] / vbase[1]
                #mdl.info(f"{trf_ratio=}")
                conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
                zbase = [1e3 * volt * volt / pot for volt, pot in zip(vbase, pbase)]
                if conn1 != "Y":
                    zbase[0] = zbase[0]*1
                if conn2 != "Y":
                    zbase[1] = zbase[1]*1
                xarray = [1e-2 * xval for xval in mdl.get_property_value(mdl.prop(trf_handle, "XArray"))]
                # Windings
                dss.Transformers.Xhl(1e-3)
                #dss.Properties.Value("ppm_antifloat", "0.01")
                dss.Properties.Value("ppm_antifloat", "0.005")

                dss.Transformers.Wdg(1)
                rw1 = 1e-2 * dss.Transformers.R() * zbase[0]
                rw1_eq = rw1 + scale_l * xarray[0] * zbase[0]
                dss.run_command("calcv")
                mdl.info(f"{rw1=}") if debug else None
                mdl.info(f"{rw1_eq=}") if debug else None
                dss.Transformers.R(100 * rw1_eq / zbase[0])

                dss.Transformers.Wdg(2)
                rw2 = 1e-2 * dss.Transformers.R() * zbase[1]
                rw2_eq = rw2 + scale_l * xarray[1] * zbase[1]
                dss.Transformers.R(100 * rw2_eq / zbase[1])
                mdl.info(f"{rw2=}") if debug else None
                mdl.info(f"{rw2_eq=}") if debug else None
                dss.run_command("calcv")

                # Changing the windings
                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(1)
                dss.Properties.Value("bus", f"{bus2}")
                dss.Transformers.kV(vbase[1])
                dss.Transformers.R(100 * rw2_eq/zbase[1])
                dss.Transformers.IsDelta(True if conn2 != "Y" else False)

                dss.Transformers.Name(dss_trf_name)
                dss.Transformers.Wdg(2)
                dss.Properties.Value("bus", f"{bus1}")
                dss.Transformers.kV(vbase[0])
                dss.Transformers.R(100 * rw1_eq/zbase[0])
                dss.Transformers.IsDelta(True if conn1 != "Y" else False)

        elif method == 8:
            # Jogando toda a impedância para R. E Apenas invertendo os terminais!!!
            for trf_handle in get_all_dss_elements(mdl, comp_type="Three-Phase Transformer"):

                dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
                dss.run_command("calcv")
                dss.Transformers.Name(dss_trf_name)
                bus1, bus2 = [bus_name for bus_name in dss.CktElement.BusNames()]
                freq = float(dss.Properties.Value("basefreq"))
                scale_l = (1 / ts) / (2 * np.pi * freq)  # Use as "scale_l*X"
                # Assuming two windigs for now
                vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
                pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
                trf_ratio = vbase[0] / vbase[1]
                #mdl.info(f"{trf_ratio=}")
                conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
                zbase = [1e3 * volt * volt / pot for volt, pot in zip(vbase, pbase)]
                if conn1 != "Y":
                    zbase[0] = zbase[0]*3
                if conn2 != "Y":
                    zbase[1] = zbase[1]*3
                mdl.info(f"{zbase=}")
                xarray = [1e-2 * xval for xval in mdl.get_property_value(mdl.prop(trf_handle, "XArray"))]
                # Windings
                dss.Transformers.Xhl(1e-3)
                #dss.Properties.Value("ppm_antifloat", "0.01")
                dss.Properties.Value("ppm_antifloat", "0.005")

                dss.Transformers.Wdg(1)
                rw1 = 1e-2 * dss.Transformers.R() * zbase[0]
                rw1_eq = rw1 + scale_l * xarray[0] * zbase[0]
                dss.run_command("calcv")
                mdl.info(f"{rw1=}") if debug else None
                mdl.info(f"{rw1_eq=}") if debug else None
                dss.Transformers.R(100 * rw1_eq / zbase[0])

                dss.Transformers.Wdg(2)
                rw2 = 1e-2 * dss.Transformers.R() * zbase[1]
                rw2_eq = rw2 + scale_l * xarray[1] * zbase[1]
                dss.Transformers.R(100 * rw2_eq / zbase[1])
                mdl.info(f"{rw2=}") if debug else None
                mdl.info(f"{rw2_eq=}") if debug else None
                dss.run_command("calcv")

                noloadloss = 1e-2 * float(dss.Properties.Value("%noloadloss"))
                imag = 1e-2 * float(dss.Properties.Value("%imag"))

                # Compensation Stage
                dss.Transformers.Name(dss_trf_name)
                mdl.info(f"{dss.CktElement.Name()}")
                dss.CktElement.Enabled(False)

                bus1 = bus1.split('.')[0]
                bus2 = bus2.split('.')[0]
                int_bus1 = f"int{bus1}"
                int_bus2 = f"int{bus2}"
                trf_names = ["t1", "t2", "t3"]
                if conn1 != "Y":
                    pri_nodes = ["1.2", "2.3", "3.1"]
                    pri_kv = vbase[0]
                else:
                    pri_nodes = ["1.0", "2.0", "3.0"]
                    pri_kv = vbase[0]/np.sqrt(3)
                if conn2 != "Y":
                    sec_nodes = ["1.2", "2.3", "3.1"]
                    sec_kv = vbase[1]
                else:
                    sec_nodes = ["1.0", "2.0", "3.0"]
                    sec_kv = vbase[1]/np.sqrt(3)

                pri_rmatrix = f"({rw1_eq} | 0 1e-6)"
                sec_rmatrix = f"({rw2_eq} | 0 1e-6)"
                xmatrix = f"(1e-6 | 0 1e-6)"
                cmatrix = f"(0 | 0 0)"

                core_loss = 0
                if noloadloss != 0 or imag != 0:
                    try:
                        rloss = (1 / noloadloss) * zbase[1]
                    except:
                        rloss = 1e15
                    try:
                        xmag = (1 / imag) * zbase[1]
                        rmag = scale_l * xmag
                    except:
                        rmag = 1e15

                    rcore = rloss * rmag / (rloss + rmag)
                    core_loss = 100*(zbase[1]/rcore)
                    mdl.info(f"{core_loss=}")

                for idx in range(3):
                    trafo_prop = {}
                    trafo_prop["Buses"] = f"[{int_bus2}_{trf_names[idx]}.1.2, {int_bus1}_{trf_names[idx]}.1.2]"
                    trafo_prop["KVs"] = f"[{sec_kv}, {pri_kv}]"
                    trafo_prop["KVAs"] = f"[{pbase[0]/3}, {pbase[1]/3}]"
                    trafo_prop["XHL"] = "1e-6"
                    trafo_prop["%Rs"] = "[0, 0]"
                    trafo_prop["%noloadloss"] = core_loss
                    trafo_prop["%imag"] = "0"
                    trafo_prop["phases"] = "1"
                    trafo_prop["ppm_antifloat"] = "0.0"
                    params = [f'{param}={trafo_prop.get(param)}' for param in trafo_prop]
                    cmd_string = "new" + f" TRANSFORMER.{dss_trf_name}_{trf_names[idx]} " + " ".join(params)
                    mdl.info(cmd_string)
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")

                    line_pri_prop = {}
                    line_pri_prop["bus1"] = f"{int_bus1}_{trf_names[idx]}.1.2"
                    line_pri_prop["bus2"] = f"{bus1}.{pri_nodes[idx]}"
                    line_pri_prop["phases"] = 2
                    line_pri_prop["rmatrix"] = pri_rmatrix
                    line_pri_prop["xmatrix"] = xmatrix
                    line_pri_prop["cmatrix"] = cmatrix
                    params = [f'{param}={line_pri_prop.get(param)}' for param in line_pri_prop]
                    cmd_string = "new" + f" LINE.{dss_trf_name}_{trf_names[idx]}pri " + " ".join(params)
                    mdl.info(cmd_string)
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")

                    line_sec_prop = {}
                    line_sec_prop["bus1"] = f"{int_bus2}_{trf_names[idx]}.1.2"
                    line_sec_prop["bus2"] = f"{bus2}.{sec_nodes[idx]}"
                    line_sec_prop["phases"] = 2
                    line_sec_prop["rmatrix"] = sec_rmatrix
                    line_sec_prop["xmatrix"] = xmatrix
                    line_sec_prop["cmatrix"] = cmatrix
                    params = [f'{param}={line_sec_prop.get(param)}' for param in line_sec_prop]
                    cmd_string = "new" + f" LINE.{dss_trf_name}_{trf_names[idx]}sec " + " ".join(params)
                    mdl.info(cmd_string)
                    dss.run_command(cmd_string)
                    dss.run_command("calcv")


                """
                trafo1_prop = {}
                trafo1_prop["Buses"] = "[ib2_t1.1.2, ib1_t1.1.2]"
                trafo1_prop["KVs"] = "[1, 1.73205]"
                trafo1_prop["KVAs"] = "[333.333, 333.333]"
                trafo1_prop["XHL"] = "1e-6"
                trafo1_prop["%Rs"] = "[0, 0]"
                trafo1_prop["%noloadloss"] = load_loss
                trafo1_prop["%imag"] = "0"
                trafo1_prop["phases"] = "1"
                trafo1_prop["ppm_antifloat"] = "0.0"
                params = [f'{param}={trafo1_prop.get(param)}' for param in trafo1_prop]
                cmd_string = "new" + f" TRANSFORMER.{dss_trf_name}_t1 " + " ".join(params)
                mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                line1_pri_prop = {}
                line1_pri_prop["bus1"] = f"ib1_t1.1.2"
                line1_pri_prop["bus2"] = f"b1.1.2"
                line1_pri_prop["phases"] = 2
                line1_pri_prop["rmatrix"] = f"({rw1_r1} | 0 1e-6)"
                line1_pri_prop["xmatrix"] = f"({rw1_x1} | 0 {rw1_x1})"
                line1_pri_prop["cmatrix"] = f"(0 | 0 0)"
                params = [f'{param}={line1_pri_prop.get(param)}' for param in line1_pri_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_l1pri " + " ".join(params)
                mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                line1_sec_prop = {}
                line1_sec_prop["bus1"] = f"ib2_t1.1.2"
                line1_sec_prop["bus2"] = f"b2.1.0"
                line1_sec_prop["phases"] = 2
                line1_sec_prop["rmatrix"] = f"({rw2_r1} | 0 1e-6)"
                line1_sec_prop["xmatrix"] = f"({rw2_x1} | 0 {rw2_x1})"
                line1_sec_prop["cmatrix"] = f"(0 | 0 0)"
                params = [f'{param}={line1_sec_prop.get(param)}' for param in line1_sec_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_l1sec " + " ".join(params)
                mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                trafo2_prop = {}
                trafo2_prop["Buses"] = "[ib2_t2.1.2, ib1_t2.1.2]"
                trafo2_prop["KVs"] = "[1, 1.73205]"
                trafo2_prop["KVAs"] = "[333.333, 333.333]"
                trafo2_prop["XHL"] = "1e-6"
                trafo2_prop["%Rs"] = "[0, 0]"
                trafo2_prop["phases"] = "1"
                trafo2_prop["%noloadloss"] = load_loss
                trafo2_prop["%imag"] = "0"
                trafo2_prop["ppm_antifloat"] = "0.0"
                params = [f'{param}={trafo2_prop.get(param)}' for param in trafo2_prop]
                cmd_string = "new" + f" TRANSFORMER.{dss_trf_name}_t2 " + " ".join(params)
                mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                line2_pri_prop = {}
                line2_pri_prop["bus1"] = f"ib1_t2.1.2"
                line2_pri_prop["bus2"] = f"b1.2.3"
                line2_pri_prop["phases"] = 2
                line2_pri_prop["rmatrix"] = f"({rw1_r1} | 0 1e-6)"
                line2_pri_prop["xmatrix"] = f"({rw1_x1} | 0 {rw1_x1})"
                line2_pri_prop["cmatrix"] = f"(0 | 0 0)"
                params = [f'{param}={line2_pri_prop.get(param)}' for param in line2_pri_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_l2pri " + " ".join(params)
                mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                line2_sec_prop = {}
                line2_sec_prop["bus1"] = f"ib2_t2.1.2"
                line2_sec_prop["bus2"] = f"b2.2.0"
                line2_sec_prop["phases"] = 2
                line2_sec_prop["rmatrix"] = f"({rw2_r1} | 0 1e-6)"
                line2_sec_prop["xmatrix"] = f"({rw2_x1} | 0 {rw2_x1})"
                line2_sec_prop["cmatrix"] = f"(0 | 0 0)"
                params = [f'{param}={line2_sec_prop.get(param)}' for param in line2_sec_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_l2sec " + " ".join(params)
                mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                trafo3_prop = {}
                trafo3_prop["Buses"] = "[ib2_t3.1.2, ib1_t3.1.2]"
                trafo3_prop["KVs"] = "[1, 1.73205]"
                trafo3_prop["KVAs"] = "[333.333, 333.333]"
                trafo3_prop["XHL"] = "1e-6"
                trafo3_prop["%Rs"] = "[0, 0]"
                trafo3_prop["phases"] = "1"
                trafo3_prop["%noloadloss"] = load_loss
                trafo3_prop["%imag"] = "0"
                trafo3_prop["ppm_antifloat"] = "0.0"
                params = [f'{param}={trafo3_prop.get(param)}' for param in trafo3_prop]
                cmd_string = "new" + f" TRANSFORMER.{dss_trf_name}_t3 " + " ".join(params)
                mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

                line3_pri_prop = {}
                line3_pri_prop["bus1"] = f"ib1_t3.1.2"
                line3_pri_prop["bus2"] = f"b1.3.1"
                line3_pri_prop["phases"] = 2
                line3_pri_prop["rmatrix"] = f"({rw1_r1} | 0 1e-6)"
                line3_pri_prop["xmatrix"] = f"({rw1_x1} | 0 {rw1_x1})"
                line3_pri_prop["cmatrix"] = f"(0 | 0 0)"
                params = [f'{param}={line3_pri_prop.get(param)}' for param in line3_pri_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_l3pri " + " ".join(params)
                dss.run_command(cmd_string)
                mdl.info(cmd_string)
                dss.run_command("calcv")

                line3_sec_prop = {}
                line3_sec_prop["bus1"] = f"ib2_t3.1.2"
                line3_sec_prop["bus2"] = f"b2.3.0"
                line3_sec_prop["phases"] = 2
                line3_sec_prop["rmatrix"] = f"({rw2_r1} | 0 1e-6)"
                line3_sec_prop["xmatrix"] = f"({rw2_x1} | 0 {rw2_x1})"
                line3_sec_prop["cmatrix"] = f"(0 | 0 0)"
                params = [f'{param}={line3_sec_prop.get(param)}' for param in line3_sec_prop]
                cmd_string = "new" + f" LINE.{dss_trf_name}_l3sec " + " ".join(params)
                mdl.info(cmd_string)
                mdl.info(dss.run_command(cmd_string))

                dss.run_command("calcv")
                dss.run_command("Solve")
                mdl.info(dss.run_command("Show Voltages"))
                """


    elif element_type == "Manual Switch":
        for swt_handle in get_all_dss_elements(mdl, comp_type="Manual Switch"):
            dss_swt_name = mdl.get_fqn(swt_handle).replace(".", "_").upper()
            dss.Circuit.SetActiveElement(f"LINE.{dss_swt_name}")
            dss.Lines.C1(0)
            dss.Lines.C0(0)
            dss.Lines.X0(1e-6)
            dss.Lines.X1(1e-6)
            dss.Lines.R0(1e-6)
            dss.Lines.R1(1e-6)
            dss.run_command("calcv")

    return dss


def sc_notation(val, num_decimals=2, exponent_pad=2):
    exponent_template = "{:0>%d}" % exponent_pad
    mantissa_template = "{:.%df}" % num_decimals

    order_of_magnitude = floor(log10(abs(val)))
    nearest_lower_third = 3 * (order_of_magnitude // 3)
    adjusted_mantissa = val * 10 ** (-nearest_lower_third)
    adjusted_mantissa_string = mantissa_template.format(adjusted_mantissa)
    adjusted_exponent_string = "+-"[nearest_lower_third < 0] + exponent_template.format(abs(nearest_lower_third))
    if int(adjusted_exponent_string) == 3:
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

""" Code reserved for future purposes (get_zsc_impedances)
        r1_sc = []
        x1_sc = []
        r1 = []
        rsc_matrix = rsc_array.reshape(n_phases, n_phases)
        xsc_matrix = xsc_array.reshape(n_phases, n_phases)
        mdl.info(f"{coupling_line}")
        mdl.info("Current Side")
        mdl.info(f"{rsc_matrix=}")
        mdl.info(f"{xsc_matrix=}")
        zsc1 = [float(z) for z in dss.Bus.Zsc1()]
        zsc0 = [float(z) for z in dss.Bus.Zsc0()]
        mdl.info(f"{zsc1=}")
        mdl.info(f"{zsc0=}")
        # Current sources ITM uses self impedance
        for idx in range(n_phases):
            r1_sc.append(rsc_matrix[idx, idx])
            x1_sc.append(xsc_matrix[idx, idx])
        # Resistance seen by the THCC
        for idx in range(n_phases):
            if x1_sc[idx] >= 0:
                r1x = (1 / ts) * x1_sc[idx] / (2 * np.pi * freq)
            else:
                r1x = (ts) / (x1_sc[idx] * 2 * np.pi * freq)
            r_eq = r1_sc[idx] + r1x
            r1.append(r_eq)

        r2_sc = []
        x2_sc = []
        r2 = []
        rsc_array = np.array(zsc_matrix[0::2])
        xsc_array = np.array(zsc_matrix[1::2])
        rsc_matrix = rsc_array.reshape(n_phases, n_phases)
        xsc_matrix = xsc_array.reshape(n_phases, n_phases)
        mdl.info("Voltage Side")
        mdl.info(f"{rsc_matrix=}")
        mdl.info(f"{xsc_matrix=}")
        zsc1 = [float(z) for z in dss.Bus.Zsc1()]
        zsc0 = [float(z) for z in dss.Bus.Zsc0()]
        mdl.info(f"{zsc1=}")
        mdl.info(f"{zsc0=}")
        thil_sc2 = np.zeros(len(rsc_array))
        for idx in range(len(rsc_array)):
            r_aux = rsc_array[idx]
            x_aux = xsc_array[idx]
            if xsc_array[idx] >= 0:
                thil_sc2[idx] = r_aux + scale_l * x_aux
            else:
                thil_sc2[idx] = r_aux + scale_c / x_aux
        thil_sc2_matrix = thil_sc2.reshape(n_phases, n_phases)
        r2_thil = []
        for idx in range(n_phases):
            # resistance
            k = thil_sc2_matrix[idx, idx]
            l = np.array([thil_sc2_matrix[idx, yvec] for yvec in range(n_phases) if yvec != idx]).reshape(1, n_phases-1)
            lt = np.array([thil_sc2_matrix[xvec, idx] for xvec in range(n_phases) if xvec != idx]).reshape(n_phases-1, 1)
            m = np.array([thil_sc2_matrix[xvec, yvec]
                          for xvec in range(n_phases) if xvec != idx
                          for yvec in range(n_phases) if yvec != idx]).reshape(n_phases-1, n_phases-1)
            try:
                r2_thil.append(k - np.dot(np.dot(l, np.linalg.inv(m)), lt)[0, 0])
            except:
                r2_thil.append(0)
        mdl.info(f"{r2_thil=}")

        # Voltage sources ITM uses kron reduction
        for idx in range(n_phases):
            # resistance
            k = rsc_matrix[idx, idx]
            l = np.array([rsc_matrix[idx, yvec] for yvec in range(n_phases) if yvec != idx]).reshape(1, n_phases-1)
            lt = np.array([rsc_matrix[xvec, idx] for xvec in range(n_phases) if xvec != idx]).reshape(n_phases-1, 1)
            m = np.array([rsc_matrix[xvec, yvec]
                          for xvec in range(n_phases) if xvec != idx
                          for yvec in range(n_phases) if yvec != idx]).reshape(n_phases-1, n_phases-1)
            try:
                r2_sc.append(k - np.dot(np.dot(l, np.linalg.inv(m)), lt)[0, 0])
            except:
                r2_sc.append(0)
            # reactance
            k = xsc_matrix[idx, idx]
            l = np.array([xsc_matrix[idx, yvec] for yvec in range(n_phases) if yvec != idx]).reshape(1, n_phases-1)
            lt = np.array([xsc_matrix[xvec, idx] for xvec in range(n_phases) if xvec != idx]).reshape(n_phases-1, 1)
            m = np.array([xsc_matrix[xvec, yvec]
                          for xvec in range(n_phases) if xvec != idx
                          for yvec in range(n_phases) if yvec != idx]).reshape(n_phases-1, n_phases-1)
            try:
                x2_sc.append(k - np.dot(np.dot(l, np.linalg.inv(m)), lt)[0, 0])
            except:
                x2_sc.append(0)
        #mdl.info(f"{r2_sc=}")
        #mdl.info(f"{x2_sc=}")
        # Resistance seen by the THCC
        for idx in range(n_phases):
            if x2_sc[idx] >= 0:
                r2x = (1 / ts) * x2_sc[idx] / (2 * np.pi * freq)
            else:
                r2x = (ts) / (x2_sc[idx] * 2 * np.pi * freq)
            mdl.info(f"{r2_sc[idx]=}")
            mdl.info(f"{r2x=}")
            r_eq = r2_sc[idx] + r2x
            r2.append(r_eq)

        if zsc1[1] >= 0:
            r2x_t = (1 / ts) * zsc1[1] / (2 * np.pi * freq)
        else:
            r2x_t = ts / (zsc1[1] * 2 * np.pi * freq)
        r2_pos = zsc1[0] + r2x_t

        zsc0 = [float(z) for z in dss.Bus.Zsc0()]
        mdl.info(f"{zsc0=}")
        if zsc0[1] >= 0:
            r2x_t = (1 / ts) * zsc0[1] / (2 * np.pi * freq)
        else:
            r2x_t = ts / (zsc0[1] * 2 * np.pi * freq)
        r2_zero = zsc0[0] + r2x_t
        r2s = (2 * r2_pos + r2_zero) / 3
        r2m = (r2_zero - r2_pos) / 3
        r2_t= r2s - 2 * (r2m * r2m) / (r2s + r2m)
        mdl.info(f"{r2_t=}")

"""

"""
        
        # Voltage sources ITM uses kron reduction
        r2 = []
        # Check if it is balanced (if not, I'll use the kron reduction)
        kron_cond = []
        zs = thil_sc_matrix[0, 0]
        zm = thil_sc_matrix[0, 1]
        for idx in range(n_phases):
            kron_cond.append(thil_sc_matrix[idx, idx] != zs)
            kron_cond.append(any([thil_sc_matrix[idx, yvec] != zm for yvec in range(n_phases) if yvec != idx]))
            kron_cond.append(any([thil_sc_matrix[xvec, idx] != zm for xvec in range(n_phases) if xvec != idx]))

        use_kron = any(kron_cond)
        use_kron = True
        if use_kron:
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
        else:
            zsc1 = [float(z) for z in dss.Bus.Zsc1()]
            if zsc1[1] >= 0:
                r2_pos = zsc1[0] + scale_l * zsc1[1]
            else:
                r2_pos = zsc1[0] + scale_c / zsc1[1]
            zsc0 = [float(z) for z in dss.Bus.Zsc0()]
            if zsc0[1] >= 0:
                r2_zero = zsc0[0] + scale_l * zsc0[1]
            else:
                r2_zero = zsc0[0] + scale_c / zsc0[1]
            r2s = (2 * r2_pos + r2_zero) / 3
            r2m = (r2_zero - r2_pos) / 3
            r2 = r2s - 2 * (r2m * r2m) / (r2s + r2m)
            r2 = [r2]*n_phases

"""

"""
    if mode == "sequence":

        dss.Circuit.SetActiveElement(coupling_line)
        bus = [bus_name.split(".")[0] for bus_name in dss.CktElement.BusNames()]
        dss.CktElement.Open(0, 0)
        dss.run_command("Solve Mode=FaultStudy")
        # dss.run_command("calcv")

        # Thevenin Impedances
        # Bus1
        # Current sources ITM uses self impedance
        bus1 = bus[0]
        dss.Circuit.SetActiveBus(bus1)
        zsc1 = [float(z) for z in dss.Bus.Zsc1()]
        mdl.info("Current Source Side")
        mdl.info(f"{zsc1=}")
        if zsc1[1] >= 0:
            r1x = (1 / ts) * zsc1[1] / (2 * np.pi * freq)
        else:
            r1x = (ts) / (zsc1[1] * 2 * np.pi * freq)
        r1_pos = zsc1[0] + r1x

        zsc0 = [float(z) for z in dss.Bus.Zsc0()]
        mdl.info(f"{zsc0=}")
        if zsc0[1] >= 0:
            r1x = (1 / ts) * zsc0[1] / (2 * np.pi * freq)
        else:
            r1x = ts / (zsc0[1] * 2 * np.pi * freq)
        r1_zero = zsc0[0] + r1x
        r1 = (2 * r1_pos + r1_zero) / 3
        r1 = [r1]*3 # TODO: Assuming phases = 3

        # Bus2
        # Voltage sources ITM uses kron reduction
        bus2 = bus[1]
        dss.Circuit.SetActiveBus(bus2)
        zsc1 = [float(z) for z in dss.Bus.Zsc1()]
        mdl.info("Voltage Source Side")
        mdl.info(f"{zsc1=}")
        if zsc1[1] >= 0:
            r2x = (1 / ts) * zsc1[1] / (2 * np.pi * freq)
        else:
            r2x = ts / (zsc1[1] * 2 * np.pi * freq)
        r2_pos = zsc1[0] + r2x

        zsc0 = [float(z) for z in dss.Bus.Zsc0()]
        mdl.info(f"{zsc0=}")
        if zsc0[1] >= 0:
            r2x = (1 / ts) * zsc0[1] / (2 * np.pi * freq)
        else:
            r2x = ts / (zsc0[1] * 2 * np.pi * freq)
        r2_zero = zsc0[0] + r2x
        r2s = (2 * r2_pos + r2_zero) / 3
        r2m = (r2_zero - r2_pos) / 3
        r2 = r2s - 2 * (r2m * r2m) / (r2s + r2m)
        r2 = [r2]*3  # TODO: Assuming phases = 3

        dss.Circuit.SetActiveElement(coupling_line)
        # dss_ckt_element.Close(0, 0)
        dss.run_command("Solve Mode=Snap")
"""
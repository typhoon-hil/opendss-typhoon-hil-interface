import os, pathlib
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QFileDialog, QWidget
import numpy as np
import re
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

    # Interface vars
    # dss_circuit = dss.Circuit
    # dss_ckt_element = dss.CktElement
    # dss_bus = dss.Bus
    # dss_lines = dss.Lines
    dss.run_command(f'Compile "{dss_file}"')
    ts = 10e-6  # TODO use get_model_property and find a way to estimate it

    tse_elements = []
    dss_elements = []
    for coupling_handle in get_all_dss_elements(mdl, comp_type="Coupling"):
        tse_elements.append(coupling_handle)
        dss_elements.append(f"LINE.{mdl.get_name(coupling_handle)}")

    # Constant Power Load Compensation (DSS uses Constant Impedance for loads. We need to change the loads impedances)
    dss = dss_to_thcc_compensation(mdl, dss, "Coupling")
    dss = dss_to_thcc_compensation(mdl, dss, "Load")
    dss = dss_to_thcc_compensation(mdl, dss, "Line")
    dss = dss_to_thcc_compensation(mdl, dss, "Vsource")
    dss = dss_to_thcc_compensation(mdl, dss, "Three-Phase Transformer")
    dss = dss_to_thcc_compensation(mdl, dss, "Manual Switch")


    # mdl.info(dss.Circuit.AllElementNames())

    if dss_elements:
        mdl.info("OpenDSS Coupling Assistance started...")
        for idx_el, element in enumerate(dss_elements):

            mdl.info(f"----- {mdl.get_name(tse_elements[idx_el])} Element -----")
            r1, r2, bus1, bus2 = get_zsc_impedances(mdl, mask_handle, dss, element, "matrix")

            mode = mdl.get_property_value(mdl.prop(tse_elements[idx_el], "auto_mode"))
            if mode == "Manual":
                mdl.info("Operational Mode: Manual")
                # Snubbers
                current_side_snubber = True
                voltage_side_snubber = True
                itm_csnb_type = mdl.get_property_value(mdl.prop(tse_elements[idx_el], "itm_csnb_type"))
                itm_vsnb_type = mdl.get_property_value(mdl.prop(tse_elements[idx_el], "itm_vsnb_type"))
                if itm_csnb_type == "none":
                    r1_snb = 1e12
                    current_side_snubber = False
                elif itm_csnb_type == "R1":
                    r1_snb = float(mdl.get_property_value(mdl.prop(tse_elements[idx_el], "itm_csnb_r")))
                elif itm_csnb_type == "R1-C1":
                    r1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_elements[idx_el], "itm_csnb_r")))
                    c1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_elements[idx_el], "itm_csnb_c")))
                    r1_snb = r1_cc_snb + ts/c1_cc_snb

                if itm_vsnb_type == "none":
                    r2_snb = 0
                    voltage_side_snubber = False
                elif itm_vsnb_type == "R2":
                    r2_snb = float(mdl.get_property_value(mdl.prop(tse_elements[idx_el], "itm_vsnb_r")))
                elif itm_vsnb_type == "R2||L1":
                    r2_cc_snb = float(mdl.get_property_value(mdl.prop(tse_elements[idx_el], "itm_vsnb_r")))
                    l1_cc_snb = float(mdl.get_property_value(mdl.prop(tse_elements[idx_el], "itm_vsnb_l")))
                    l1_cc_snb_r = (1/ts)*l1_cc_snb
                    r2_snb = r2_cc_snb*l1_cc_snb_r/(r2_cc_snb+l1_cc_snb_r)

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
                        topological_conflict_msg.append(f"  - There are topological conflicts between {mdl.get_name(tse_elements[idx_el])} and {aux_element}."
                                                        f" Please, considers to use a snubber at the current source side of {mdl.get_name(tse_elements[idx_el])}")

                for pce in pce_connected:
                    if pce.split(".")[0] in ["VSOURCE"] and not current_side_snubber:
                        topological_conflict = True
                        topological_status_msg = "Yes"
                        aux_element = pce.split(".")[1]
                        topological_conflict_msg.append(f"  - There are topological conflicts between {mdl.get_name(tse_elements[idx_el])} and {aux_element}."
                                                        f" Please, considers to use a snubber at the current source side of {mdl.get_name(tse_elements[idx_el])}")

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
                            topological_conflict_msg.append(f"  - There are topological conflicts between {mdl.get_name(tse_elements[idx_el])} and {aux_element}."
                                                            f" Please, considers to use a snubber at the voltage source side of {mdl.get_name(tse_elements[idx_el])}")
                    if pde.split(".")[0] in ["CAPACITOR"] and not voltage_side_snubber:
                        topological_conflict = True
                        topological_status_msg = "Yes"
                        aux_element = pde.split(".")[1]
                        topological_conflict_msg.append(f"  - There are topological conflicts between {mdl.get_name(tse_elements[idx_el])} and {aux_element}."
                                                        f" Please, considers to use a snubber at the voltage source side of {mdl.get_name(tse_elements[idx_el])}")

                mdl.info(f"Topological Conflicts: {topological_status_msg}")

                if topological_conflict:
                    for msg in topological_conflict_msg:
                        mdl.info(msg)
                        # mdl.warning(msg, kind=f"Coupling Element: {mdl.get_name(coupling_handle)}", context=mask_handle)

                # Stability Check
                #r1_snb = 1e9
                #r2_snb = 0
                r1_fixed = [rdss*r1_snb/(rdss + r1_snb) for rdss in r1]
                r2_fixed = [rdss + r2_snb for rdss in r2]

                for ph in range(len(r1_fixed)):
                    mdl.info(f"{[r1_fixed[ph], r2_fixed[ph]]}")
                    if r1_fixed[ph] >= r2_fixed[ph]:
                        mdl.info(f"Stability Info: {mdl.get_name(tse_elements[idx_el])}.{ph} is unstable.")
                        # msg = f"Coupling element {mdl.get_name(coupling_handle)} is unstable."
                        # mdl.warning(msg, kind='General warning', context=coupling_handle)
                    else:
                        # msg = f"Coupling element {mdl.get_name(coupling_handle)} is stable."
                        # mdl.info(msg, context=coupling_handle)
                        mdl.info(f"Stability Info: {mdl.get_name(tse_elements[idx_el])}.{ph} is stable.")

                #mdl.info(f"{r1_fixed=}")
                #mdl.info(f"{r2_fixed=}")

            elif mode == "Automatic":
                mdl.info("Operational Mode: Automatic")

                mdl.info(f"Element Actions:")
                # Stability Check
                flip_status = mdl.get_property_value(mdl.prop(tse_elements[idx_el], "flip_status"))
                if flip_status:
                    r1, r2 = r2, r1
                    bus1, bus2 = bus2, bus1
                if r1 >= r2:
                    mdl.info(f"  - Horizontal Flip")
                    mdl.set_property_value(mdl.prop(tse_elements[idx_el], "flip_status"), not flip_status)

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
                    mdl.info(tse_elements[idx_el])
                    mdl.set_property_value(mdl.prop(tse_elements[idx_el], "itm_csnb_type"), "R1")
                    mdl.set_property_value(mdl.prop(tse_elements[idx_el], "itm_csnb_r_auto"), "1e6")
                    mdl.info(f"  - Added Snubber in Current Source Side: R1 = 1e6 Ω")

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
                    mdl.info(tse_elements[idx_el])
                    mdl.set_property_value(mdl.prop(tse_elements[idx_el], "itm_vsnb_type"), "R2")
                    mdl.set_property_value(mdl.prop(tse_elements[idx_el], "itm_vsnb_r_auto"), "1e-3")
                    mdl.info(f"  - Added Snubber in Voltage Source Side: R2 = 1e-3 Ω")

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


def get_zsc_impedances(mdl, mask_handle, dss, coupling_line, mode):

    freq = float(mdl.get_property_value(mdl.prop(mask_handle, "basefrequency")))
    # dss_circuit = dss.Circuit
    # dss_ckt_element = dss.CktElement
    # dss_bus = dss.Bus
    # dss_lines = dss.Lines
    ts = 10e-6  # TODO use get_model_property and find a way to estimate it

    #mdl.info(f"{coupling_line=}")
    #mdl.info(dss.Circuit.AllElementNames())


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

    elif mode == "matrix":

        dss.run_command("Solve Mode=FaultStudy")
        dss.run_command("calcv")
        dss.Circuit.SetActiveElement(coupling_line)
        bus = [bus_name.split(".")[0] for bus_name in dss.CktElement.BusNames()]
        bus1 = bus[0]
        bus2 = bus[1]
        # dss_ckt_element.Open(0, 0)

        # I should to remove the reactors created during the compensation stage
        dss.run_command("calcv")
        dss.Circuit.SetActiveBus(bus1)
        bus1_snb_list = []
        bus2_snb_list = []
        pce_pde = dss.Bus.AllPCEatBus() + dss.Bus.AllPDEatBus()
        #mdl.info(f"Connected to {bus1}")
        #mdl.info(f"{pce_pde}")
        for connected_element in pce_pde:
            #mdl.info(f"1{connected_element=}")
            reactor_match = re.match(r"^REACTOR.(.+)_([VC])(?:SIDE_snb\d$)", connected_element, re.IGNORECASE)
            #mdl.info(f"1{reactor_match=}")
            if reactor_match:
                if reactor_match.group(1).lower() == coupling_line.split(".")[-1].lower():
                    bus1_snb_list.append(connected_element)

        dss.run_command("calcv")
        dss.Circuit.SetActiveBus(bus2)
        pce_pde = dss.Bus.AllPCEatBus() + dss.Bus.AllPDEatBus()
        for connected_element in pce_pde:
            #mdl.info(f"2{connected_element=}")
            reactor_match = re.match(r"^REACTOR.(.+)_([VC])(?:SIDE_snb\d$)", connected_element, re.IGNORECASE)
            #mdl.info(f"2{reactor_match=}")
            if reactor_match:
                if reactor_match.group(1).lower() == coupling_line.split(".")[-1].lower():
                    bus2_snb_list.append(connected_element)

        #mdl.info(f"{bus1=}")
        [dss.run_command(f"{pde}.enabled=no") for pde in bus1_snb_list]
        #[mdl.info(f"{pde}.enabled=no") for pde in bus1_snb_list]

        #mdl.info(f"{bus2=}")
        [dss.run_command(f"{pde}.enabled=no") for pde in bus2_snb_list]
        #[mdl.info(f"{pde}.enabled=no") for pde in bus2_snb_list]

        dss.run_command("Solve Mode=FaultStudy")
        # Thevenin Impedances
        # Bus1
        # Current sources ITM uses self impedance
        dss.run_command("calcv")
        dss.Circuit.SetActiveBus(bus1)
        dss.Bus.ZscRefresh()
        zsc_matrix = dss.Bus.ZscMatrix()
        n_phases = int(np.sqrt(len(zsc_matrix)/2))
        r1_sc = []
        x1_sc = []
        r1 = []
        rsc_array = np.array(zsc_matrix[0::2])
        xsc_array = np.array(zsc_matrix[1::2])
        rsc_matrix = rsc_array.reshape(n_phases, n_phases)
        xsc_matrix = xsc_array.reshape(n_phases, n_phases)
        mdl.info(f"{coupling_line}")
        mdl.info("Current Side")
        mdl.info(f"{rsc_matrix=}")
        mdl.info(f"{xsc_matrix=}")
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

        # Bus2
        dss.run_command("calcv")
        dss.Circuit.SetActiveBus(bus2)
        dss.Bus.ZscRefresh()
        zsc_matrix = dss.Bus.ZscMatrix()
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
            r_eq = r2_sc[idx] + r2x
            r2.append(r_eq)

        # I should to add the reactors created during the compensation stage
        [dss.run_command(f"{pde}.enabled=yes") for pde in bus1_snb_list]
        [dss.run_command(f"{pde}.enabled=yes") for pde in bus2_snb_list]
        #[mdl.info(f"{pde}.enabled=yes") for pde in bus1_snb_list]
        #[mdl.info(f"{pde}.enabled=yes") for pde in bus2_snb_list]

        dss.run_command("calcv")
        dss.run_command("Solve Mode=Snap")

    return r1, r2, bus1, bus2


def dss_to_thcc_compensation(mdl, dss, element_type):

    ts = 10e-6
    if element_type == "Load":
        for load_handle in get_all_dss_elements(mdl, comp_type="Load"):
            # Getting THCC properties
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
            bus = dss.CktElement.BusNames()[0].split(".")[0]
            nodes = dss.CktElement.BusNames()[0].split(".")[1:]
            # dss.CktElement.Enabled = 0
            dss.run_command(f"Load.{dss_load_name}.enabled=no")
            #mdl.info(f"Load.{dss_load_name}.enabled=no")
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
            freq = float(dss.Properties.Value("frequency"))
            r1, x1 = [float(prop_value) for prop_value in ast.literal_eval(dss.Properties.Value("Z1"))]
            r0, x0 = [float(prop_value) for prop_value in ast.literal_eval(dss.Properties.Value("Z0"))]

            #mdl.info(f"{r1=}")
            #mdl.info(f"{x1=}")
            #mdl.info(f"{r0=}")
            #mdl.info(f"{x0=}")

            r1_new = r1 + (1/ts)*(x1/(2*np.pi*freq))
            x1_new = 1e-6
            r0_new = r0 + (1/ts)*(x0/(2*np.pi*freq))
            x0_new = 1e-6
            cmd_string = f"VSOURCE.{dss_vsource_name}.Z1 = [{r1_new}, {x1_new}]"
            #mdl.info(cmd_string)
            dss.run_command(cmd_string)
            dss.run_command("calcv")
            cmd_string = f"VSOURCE.{dss_vsource_name}.Z0 = [{r0_new}, {x0_new}]"
            #mdl.info(cmd_string)
            dss.run_command(cmd_string)
            dss.run_command("calcv")

            r1_new, x1_new = [float(prop_value) for prop_value in ast.literal_eval(dss.Properties.Value("Z1"))]
            r0_new, x0_new = [float(prop_value) for prop_value in ast.literal_eval(dss.Properties.Value("Z0"))]
            #mdl.info(f"{r1_new=}")
            #mdl.info(f"{x1_new=}")
            #mdl.info(f"{r0_new=}")
            #mdl.info(f"{x0_new=}")

    elif element_type == "Three-Phase Transformer":
        for trf_handle in get_all_dss_elements(mdl, comp_type="Three-Phase Transformer"):
            dss_trf_name = mdl.get_fqn(trf_handle).replace(".", "_").upper()
            dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
            freq = float(dss.Properties.Value("basefreq"))
            # Assuming two windigs for now
            vbase = mdl.get_property_value(mdl.prop(trf_handle, "KVs"))
            pbase = mdl.get_property_value(mdl.prop(trf_handle, "KVAs"))
            prim_conn = not mdl.get_property_value(mdl.prop(trf_handle, "prim_conn")) == "Y"
            sec_conn = not mdl.get_property_value(mdl.prop(trf_handle, "sec1_conn")) == "Y"
            # conn1, conn2 = [mdl.get_property_value(mdl.prop(trf_handle, prop)) for prop in ["prim_conn", "sec1_conn"]]
            zbase = [1e3*volt*volt/pot for volt, pot in zip(vbase, pbase)]
            xarray = mdl.get_property_value(mdl.prop(trf_handle, "XArray"))
            larray = [(1e-2*x/zb)/(2*np.pi*freq) for x,zb in zip(xarray, zbase)]
            # Windings
            dss.Transformers.Wdg(1)
            rw1 = dss.Transformers.R()
            rw1_eq = rw1 + (1/ts)*larray[0]
            dss.Transformers.R(rw1_eq)
            dss.Transformers.IsDelta(prim_conn)
            mdl.info(dss.Transformers.IsDelta())
            dss.Transformers.Wdg(2)
            rw2 = dss.Transformers.R()
            rw2_eq = rw2 + (1 / ts) * larray[1]
            dss.Transformers.R(rw2_eq)
            dss.Transformers.Xhl(1e-3)
            dss.Transformers.IsDelta(sec_conn)


            dss.run_command("calcv")

            # Core
            dss.Circuit.SetActiveElement(f"TRANSFORMER.{dss_trf_name}")
            #dss.Transformers.Xhl(xarray[0] + xarray[1])
            #dss.Properties.Value("ppm_antifloat", "0")
            noloadloss = float(dss.Properties.Value("%noloadloss"))/100
            imag = float(dss.Properties.Value("%imag"))/100
            #mdl.info(f"{noloadloss=}")
            #mdl.info(f"{imag=}")

            if noloadloss != 0 or imag != 0:
                try:
                    rloss = (1/noloadloss)*zbase[0]
                except:
                    rloss = 1e12
                try:
                    xmag = (1/imag)*zbase[0]
                    rmag = (1/ts)*(xmag/(2*np.pi*freq))
                except:
                    rmag = 1e12

                req = rloss*rmag/(rloss+rmag)
                noloadloss_eq = 100*1/(req/zbase[0])
                cmd_string = f"TRANSFORMER.{dss_trf_name}.%noloadloss = {noloadloss_eq}"
                #mdl.info(cmd_string)
                dss.run_command(cmd_string)
                cmd_string = f"TRANSFORMER.{dss_trf_name}.%imag = {1e-4}"
                #mdl.info(cmd_string)
                dss.run_command(cmd_string)
                dss.run_command("calcv")

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


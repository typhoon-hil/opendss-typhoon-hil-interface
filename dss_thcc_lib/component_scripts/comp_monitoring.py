import typhoon.api.hil as hil
import string, os, sys, pathlib
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QFileDialog, QWidget, QApplication, QVBoxLayout, QLabel
import csv
import pandas as pd
import matplotlib.pyplot as plt
import json
import subprocess
import re
# import numpy as np



class Ui_objects(object):
    def setupUi(self, objects):
        objects.setObjectName("objects")
        objects.resize(565, 300)
        objects.setMinimumSize(QtCore.QSize(565, 300))
        objects.setMaximumSize(QtCore.QSize(565, 300))
        self.tabWidget = QtWidgets.QTabWidget(objects)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 545, 250))
        self.tabWidget.setObjectName("tabWidget")
        self.tab_monitor = QtWidgets.QWidget()
        self.tab_monitor.setObjectName("tab_monitor")
        self.label_comps = QtWidgets.QLabel(self.tab_monitor)
        self.label_comps.setGeometry(QtCore.QRect(10, 5, 61, 16))
        self.label_comps.setObjectName("label_comps")
        self.label_parameters = QtWidgets.QLabel(self.tab_monitor)
        self.label_parameters.setGeometry(QtCore.QRect(140, 5, 81, 16))
        self.label_parameters.setObjectName("label_parameters")
        self.label_plots = QtWidgets.QLabel(self.tab_monitor)
        self.label_plots.setGeometry(QtCore.QRect(335, 5, 81, 16))
        self.label_plots.setObjectName("label_plots")
        self.label_sa_open = QtWidgets.QLabel(self.tab_monitor)
        self.label_sa_open.setGeometry(QtCore.QRect(270, 161, 81, 16))
        self.label_sa_open.setObjectName("label_sa_open")
        self.list_comps = QtWidgets.QListWidget(self.tab_monitor)
        self.list_comps.setGeometry(QtCore.QRect(10, 25, 121, 100))
        self.list_comps.setObjectName("list_comps")
        self.list_dss_signal = QtWidgets.QListWidget(self.tab_monitor)
        self.list_dss_signal.setGeometry(QtCore.QRect(135, 25, 161, 100))
        self.list_dss_signal.setObjectName("list_dss_signal")
        self.list_dss_plot = QtWidgets.QListWidget(self.tab_monitor)
        self.list_dss_plot.setGeometry(QtCore.QRect(330, 25, 200, 100))
        self.list_dss_plot.setObjectName("list_dss_plot")
        self.button_add_plot = QtWidgets.QPushButton(self.tab_monitor)
        self.button_add_plot.setGeometry(QtCore.QRect(300, 45, 25, 23))
        self.button_add_plot.setObjectName("button_add_plot")
        self.button_del_plot = QtWidgets.QPushButton(self.tab_monitor)
        self.button_del_plot.setGeometry(QtCore.QRect(300, 75, 25, 23))
        self.button_del_plot.setObjectName("button_del_plot")
        self.button_clear_plot = QtWidgets.QPushButton(self.tab_monitor)
        self.button_clear_plot.setGeometry(QtCore.QRect(330, 133, 55, 23))
        self.button_clear_plot.setObjectName("button_clear_plot")
        self.button_do_plot = QtWidgets.QPushButton(self.tab_monitor)
        self.button_do_plot.setGeometry(QtCore.QRect(390, 133, 55, 23))
        self.button_do_plot.setObjectName("button_do_plot")
        self.button_do_plot1 = QtWidgets.QPushButton(self.tab_monitor)
        self.button_do_plot1.setGeometry(QtCore.QRect(450, 133, 80, 23))
        self.button_do_plot1.setObjectName("button_do_plot1")
        self.button_sa_plot = QtWidgets.QPushButton(self.tab_monitor)
        self.button_sa_plot.setGeometry(QtCore.QRect(330, 161, 150, 23))
        self.button_sa_plot.setObjectName("button_sa_plot")
        self.button_sa_plot1 = QtWidgets.QPushButton(self.tab_monitor)
        self.button_sa_plot1.setGeometry(QtCore.QRect(330, 189, 150, 23))
        self.button_sa_plot1.setObjectName("button_sa_plot1")
        self.button_open_output = QtWidgets.QPushButton(self.tab_monitor)
        self.button_open_output.setGeometry(QtCore.QRect(10, 133, 121, 23))
        self.button_open_output.setObjectName("button_open_output")
        self.button_export_all = QtWidgets.QPushButton(self.tab_monitor)
        self.button_export_all.setGeometry(QtCore.QRect(10, 161, 121, 23))
        self.button_export_all.setObjectName("button_export_all")
        self.tabWidget.addTab(self.tab_monitor, "")
        self.button_ok = QtWidgets.QPushButton(objects)
        self.button_ok.setGeometry(QtCore.QRect(190, 270, 75, 23))
        self.button_ok.setObjectName("button_ok")
        self.button_cancel = QtWidgets.QPushButton(objects)
        self.button_cancel.setGeometry(QtCore.QRect(310, 270, 75, 23))
        self.button_cancel.setObjectName("button_cancel")

        self.retranslateUi(objects)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(objects)

    def retranslateUi(self, objects):
        _translate = QtCore.QCoreApplication.translate
        objects.setWindowTitle(_translate("objects", "Monitoring"))
        self.label_comps.setText(_translate("objects", "Components"))
        self.label_parameters.setText(_translate("objects", "Available Signals"))
        self.label_plots.setText(_translate("objects", "Plot List"))
        self.label_sa_open.setText(_translate("objects", "Open in: "))
        self.button_add_plot.setText(_translate("objects", ">>"))
        self.button_del_plot.setText(_translate("objects", "x"))
        self.button_clear_plot.setText(_translate("objects", "Clear"))
        self.button_do_plot.setText(_translate("objects", "Plot"))
        self.button_do_plot1.setText(_translate("objects", "Plot Selected"))
        self.button_sa_plot1.setText(_translate("objects", "Signal Analyzer (Selected)"))
        self.button_sa_plot.setText(_translate("objects", "Signal Analyzer (All)"))
        self.button_open_output.setText(_translate("objects", "Open Output Folder"))
        self.button_export_all.setText(_translate("objects", "Export all to *.CSV"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_monitor), _translate("objects", "Time Series Monitor"))
        self.button_ok.setText(_translate("objects", "Ok"))
        self.button_cancel.setText(_translate("objects", "Cancel"))

    def edited(self):
        self.linecode_pars = {
            "symmetrical":
                {"r1": self.edit_r1,
                 "r0": self.edit_r0,
                 "x1": self.edit_x1,
                 "x0": self.edit_x0,
                 "c1": self.edit_c1,
                 "c0": self.edit_c0},
            "matrix":
                {"rmatrix": self.edit_rmatrix,
                 "xmatrix": self.edit_xmatrix,
                 "cmatrix": self.edit_cmatrix,
                }
        }

        self.double_validator = QtGui.QDoubleValidator()
        self.edit_r0.setValidator(self.double_validator)
        self.edit_c0.setValidator(self.double_validator)
        self.edit_c1.setValidator(self.double_validator)
        self.edit_r1.setValidator(self.double_validator)
        self.edit_x0.setValidator(self.double_validator)
        self.edit_x1.setValidator(self.double_validator)

        self.button_linecode_save.setDisabled(True)


def dss_components(dssfile):
    dss_component_list = []
    if dssfile:
        f = open(dssfile, 'r')
        lines = f.readlines()
    else:
        lines = []

    for line in lines:
        if 'new "MONITOR.' in line:
            dss_comp_name = re.search(r'new \"monitor\.([A-z ]+)\"', string=line, flags=re.IGNORECASE).group(1)
            # line_elem = line.split()
            # new_line_elem = []
            # for wrd in line_elem:
            #
            #     spaced_name = ""
            #     if wrd[:9] == '"MONITOR.' and not wrd[-1] == '"':
            #         spaced_name += wrd
            #     elif not wrd[:9] == '"MONITOR.' and wrd[-1] == '"':
            #         spaced_name += wrd
            #         new_line_elem.append(spaced_name)
            #         break
            #     else:
            #         new_line_elem.append(wrd)
            # line_elem = new_line_elem
            # for wrd in line_elem:
            #     if 'MONITOR' in wrd:
            #         monitor_name = wrd.split('MONITOR.')
            #         dss_comp_name_temp = monitor_name[1].split("_")
            #         dss_comp_name = dss_comp_name_temp[0]
            if not dss_comp_name.split("_")[0] in dss_component_list:
                dss_component_list.append(dss_comp_name.split("_")[0])
    return dss_component_list


class Mon_obj(QtWidgets.QDialog, Ui_objects):

    def __init__(self, obj_dicts={}):
        super().__init__()
        self.setupUi(self)

        self.obj_dicts = obj_dicts
        self.dssfile = ""
        self.process = QtCore.QProcess(self)
        self.plotprocess = QtCore.QProcess(self)

        self.linecodes_dict = {}
        self.comp_dict = {}
        self.dss_mon_dict = {}
        self.signal_list_dict = {}
        self.plot_list_dict = {}
        self.comp_handle = ""
        self.mdl_ref = ""
        self.core_model = ""
        self.dss_folder = ""
        self.dss_output_path = ""
        self.dss_model_name = ""
        self.wiredata_dict = {}
        self.linespacing_dict = {}
        self.linegeometry_dict = {}
        self.dss_comps = []
        self.w = None
        self.cfg_file_vi = None
        self.cfg_file_pq = None

        self.current_plot_cfg_pq = {}
        self.current_plot_cfg_vi = {}

        # Auxiliary vars
        self.old_listitem_name = ""
        self.valid_characters = list(string.ascii_lowercase + string.ascii_uppercase + string.digits + "_<>:-")


        # Monitors
        self.list_comps.itemClicked.connect(self.update_signal_list)

        self.list_dss_signal.itemDoubleClicked.connect(self.add_signal_plot_dclck)
        self.list_dss_plot.itemDoubleClicked.connect(self.del_signal_plot_dclick)

        self.button_add_plot.clicked.connect(self.add_signal_plot)
        self.button_del_plot.clicked.connect(self.del_signal_plot)
        self.button_clear_plot.clicked.connect(self.clear_signal_plot)
        self.button_do_plot.clicked.connect(self.do_signal_plot)
        self.button_do_plot1.clicked.connect(self.do_signal_plot_one)
        self.button_sa_plot1.clicked.connect(self.output_sa)
        self.button_sa_plot.clicked.connect(self.output_sa_all)
        self.button_open_output.clicked.connect(self.open_output_folder)
        self.button_export_all.clicked.connect(self.export_all_csv)

        self.button_ok.clicked.connect(self.return_updated_dict)
        self.button_cancel.clicked.connect(self.reject)



        # Initialize dictionaries
        self.get_object_dicts()

    def get_obj_defaults(self, obj_type):

        if obj_type == "linecode":
            linecode_def = {
                "mode": "symmetrical",
                "r1": "0.01273",
                "r0": "0.3864",
                "x1": "0.9337e-3",
                "x0": "4.1264e-3",
                "c1": "12.74e-9",
                "c0": "7.751e-9",
            }

            return linecode_def

    def get_object_dicts(self):

        linecode_def = {"Default": self.get_obj_defaults("linecode")}

        if self.obj_dicts:
            if self.obj_dicts.get("linecodes"):
                self.linecodes_dict.update(self.obj_dicts.get("linecodes"))
            else:
                self.linecodes_dict.update(linecode_def)
        else:
            self.linecodes_dict.update(linecode_def)

    def dss_update_monitor_list(self):

        self.dss_mon_dict.clear()

        prop_dict = {"name": [], "mode": [], "terminal": []}
        if self.dssfile:
            f = open(self.dssfile, 'r')
            lines = f.readlines()
        else:
            lines = []

        for line in lines:
            if 'new "MONITOR.' in line:
                line_elem = line.split()

                monitor_name = re.search(r'new \"monitor\.([A-z 0-9\-]+)\"', string=line, flags=re.IGNORECASE).group(1)
                chopped_name_len = len(monitor_name.split("_"))
                true_name = monitor_name.split(str(
                    "_" + monitor_name.split("_")[chopped_name_len - 2] + "_" + monitor_name.split("_")[
                        chopped_name_len - 1]))[0]
                dss_comp_name = true_name

                for wrd in line_elem:
                    if "element" in wrd:
                        element = wrd.split("=")[1]
                    if "mode" in wrd:
                        mode = wrd.split("=")[1]
                    if "terminal" in wrd:
                        terminal = wrd.split("=")[1]
                    # if "MONITOR" in wrd:
                    #     monitor_name = wrd.split("MONITOR.")
                    #     dss_comp_name_temp = monitor_name[1].split("_")
                    #     dss_comp_name = dss_comp_name_temp[0]
                    #     dss_comp_name =
                if not dss_comp_name in self.dss_mon_dict.keys():
                    self.dss_mon_dict[str(dss_comp_name)] = {"name": [element], "mode": [mode], "terminal": [terminal], "monitor name": [monitor_name]}
                else:
                    (self.dss_mon_dict[str(dss_comp_name)])["name"].append(element)
                    (self.dss_mon_dict[str(dss_comp_name)])["mode"].append(mode)
                    (self.dss_mon_dict[str(dss_comp_name)])["terminal"].append(terminal)
                    (self.dss_mon_dict[str(dss_comp_name)])["monitor name"].append(monitor_name)

    def dss_components(self):
        self.dss_comps = []

        if self.dssfile:
            f = open(self.dssfile, 'r')
            lines = f.readlines()
        else:
            lines = []


        for line in lines:

            if 'new "MONITOR.' in line:
                dss_comp_name = re.search(r'new \"monitor\.([A-z 0-9\-]+)\"', string=line, flags=re.IGNORECASE).group(1)

                # line_elem = line.split()
                # new_line_elem = []
                # for wrd in line_elem:
                #
                #     spaced_name = ""
                #     if wrd[:9] == '"MONITOR.' and not wrd[-1] == '"':
                #         spaced_name += wrd
                #     elif not wrd[:9] == '"MONITOR.' and wrd[-1] == '"':
                #         spaced_name += wrd
                #         new_line_elem.append(spaced_name)
                #         break
                #     else:
                #         new_line_elem.append(wrd)
                # line_elem = new_line_elem
                # for wrd in line_elem:
                #     if 'MONITOR' in wrd:
                #         monitor_name = wrd.split('MONITOR.')
                #         dss_comp_name_temp = monitor_name[1].split("_")
                #         dss_comp_name = dss_comp_name_temp[0]
                # if not dss_comp_name in dss_component_list:
                #     dss_component_list.append(dss_comp_name)
                # for wrd in line_elem:
                #     if "MONITOR" in wrd:
                #         monitor_name = wrd.split("MONITOR.")
                #         dss_comp_name_temp = monitor_name[1].split("_")
                #         dss_comp_name = dss_comp_name_temp[0]

                chopped_name_len = len(dss_comp_name.split("_"))
                true_name = dss_comp_name.split(str("_" + dss_comp_name.split("_")[chopped_name_len-2] + "_" + dss_comp_name.split("_")[chopped_name_len-1]))[0]

                if not true_name in self.dss_comps:
                    self.dss_comps.append(true_name)

    def update_comp_handle(self, handle):

        self.comp_handle = handle

    def update_core_model(self, mdl, instance):

        self.core_model = mdl.core_model
        self.mdl_ref = mdl
        self.saved_instance = instance  # Avoid window closing instantly


    def update_dss_path(self, path, filename):

        self.dss_folder = path
        self.dss_output_path = self.dss_folder.joinpath('output')
        if not os.path.exists(self.dss_output_path):
            os.mkdir(self.dss_output_path)
        self.dss_model_name = filename
        self.cfg_file_vi = self.dss_output_path.joinpath('plot_vi' + '.json')
        self.cfg_file_pq = self.dss_output_path.joinpath('plot_pq' + '.json')

        self.current_plot_cfg_pq = {"signals": {" P1 (kW)": {"viewports": [1]},
                                                " P2 (kW)": {"viewports": [1]},
                                                " P3 (kW)": {"viewports": [1]},
                                                " Q1 (kvar)": {"viewports": [2]},
                                                " Q2 (kvar)": {"viewports": [2]},
                                                " Q3 (kvar)": {"viewports": [2]}},
                                    "viewports": {
                                        "1": {"x_label": "time (h)"},
                                        "2": {"x_label": "time (h)"},
                                        "3": {"x_label": "time (h)"},
                                        "4": {"x_label": "time (h)"}
         }
         }

        self.current_plot_cfg_vi = {"signals": {" V1": {"viewports": [1]},
                                                " V2": {"viewports": [1]},
                                                " V3": {"viewports": [1]},
                                                " I1": {"viewports": [2]},
                                                " I2": {"viewports": [2]},
                                                " I3": {"viewports": [2]},
                                                " VAngle1": {"viewports": [3]},
                                                " VAngle2": {"viewports": [3]},
                                                " VAngle3": {"viewports": [3]},
                                                " IAngle1": {"viewports": [4]},
                                                " IAngle2": {"viewports": [4]},
                                                " IAngle3": {"viewports": [4]}
                                                },
                                    "viewports": {
                                        "1": {"x_label": "time (h)"},
                                        "2": {"x_label": "time (h)"},
                                        "3": {"x_label": "time (h)"},
                                        "4": {"x_label": "time (h)"}
                                    }
                                    }

        with open(self.cfg_file_pq, 'w') as f1:
            json.dump(self.current_plot_cfg_pq, f1, indent=4)
        with open(self.cfg_file_vi, 'w') as f2:
            json.dump(self.current_plot_cfg_vi, f2, indent=4)
        # print(self.current_plot_cfg)

    def update_comps_list(self, dss_path):

        self.dssfile = dss_path
        self.list_comps.clear()
        self.dss_components()
        self.dss_update_monitor_list()
        all_comps = self.dss_comps

        if all_comps:
            all_comps.sort()

            self.list_comps.addItems(all_comps)

    def update_signal_list(self, list_item):
        self.list_dss_signal.clear()
        self.signal_list_dict.clear()
        item_signal_list = []
        item_props = self.dss_mon_dict.get(str(list_item.text()))
        item_names = item_props["name"]
        item_modes = item_props["mode"]
        item_terminals = item_props["terminal"]
        item_mon_names = item_props["monitor name"]
        for idx in range(len(item_names)):
            if item_modes[idx] == "0":
                item_signal_list.append("Voltage/Current " + "(terminal " + str(item_terminals[idx]) + ")")
                self.signal_list_dict[str("Voltage/Current " + "(terminal " + str(item_terminals[idx]) + ")")] = str(item_mon_names[idx])
            elif item_modes[idx] == "1":
                item_signal_list.append("Power " + "(terminal " + str(item_terminals[idx]) + ")")
                self.signal_list_dict[str("Power " + "(terminal " + str(item_terminals[idx]) + ")")] = str(item_mon_names[idx])
            else:
                item_signal_list.append("invalid signal")
        self.list_dss_signal.addItems(item_signal_list)

    def add_signal_plot_dclck(self, list_item):
        current_item1 = self.list_comps.currentItem()
        current_item2 = self.list_dss_signal.currentItem()
        if current_item1 and current_item2:
            plot_name = str(current_item1.text()) + " " + str(current_item2.text())
            if not plot_name in self.plot_list_dict.keys():
                self.plot_list_dict[plot_name] = self.signal_list_dict[str(current_item2.text())]
                self.list_dss_plot.addItem(plot_name)
                command_line = f'export monitors "{str(self.signal_list_dict[str(current_item2.text())])}"'
                self.mdl_ref.core_model = self.core_model
                run_command(self.mdl_ref, command_line)
                self.hour_to_time(plot_name)

    def add_signal_plot(self):
        current_item1 = self.list_comps.currentItem()
        current_item2 = self.list_dss_signal.currentItem()
        if current_item1 and current_item2:
            plot_name = str(current_item1.text()) + " " + str(current_item2.text())
            if not plot_name in self.plot_list_dict.keys():
                self.plot_list_dict[plot_name] = self.signal_list_dict[str(current_item2.text())]
                self.list_dss_plot.addItem(plot_name)
                command_line = f'export monitors "{str(self.signal_list_dict[str(current_item2.text())])}"'
                self.mdl_ref.core_model = self.core_model
                run_command(self.mdl_ref, command_line)
                self.hour_to_time(plot_name)

    def export_all_csv(self):
        item_count = self.list_comps.count()
        for row in range(item_count):
            item = self.list_comps.item(row)
            component = self.dss_mon_dict.get(str(item.text()))
            item_names = component["name"]
            item_modes = component["mode"]
            item_terminals = component["terminal"]
            item_mon_names = component["monitor name"]
            for idx in range(len(item_names)):
                item_mon_names[idx]
                command_line = "export monitors " + str(item_mon_names[idx])
                self.mdl_ref.core_model = self.core_model
                run_command(self.mdl_ref, command_line)
                self.hour_to_time_all(str(item_mon_names[idx]))

    def hour_to_time_all(self, plot_name):
        csv_name = str(self.dss_model_name) + "_Mon_" + plot_name
        csv_file_path = self.dss_output_path.joinpath(csv_name + '.csv')
        csvread = pd.read_csv(csv_file_path)
        csvread.rename(columns={'hour': 'Time'}, inplace=True)
        csvread.to_csv(csv_file_path)

    def hour_to_time(self, plot_name):
        csv_name = str(self.dss_model_name) + "_Mon_" + str(self.plot_list_dict[str(plot_name)])
        csv_file_path = self.dss_output_path.joinpath(csv_name + '.csv')
        csvread = pd.read_csv(csv_file_path)
        csvread.rename(columns={'hour': 'Time'}, inplace=True)
        csvread.to_csv(csv_file_path)

    def del_signal_plot_dclick(self, list_item):
        current_item = self.list_dss_plot.currentItem()
        row = self.list_dss_plot.currentRow()
        if current_item:
            plot_name = str(current_item.text())
            if plot_name in self.plot_list_dict.keys():
                self.plot_list_dict.pop(plot_name)
                self.list_dss_plot.takeItem(row)

    def del_signal_plot(self):
        current_item = self.list_dss_plot.currentItem()
        row = self.list_dss_plot.currentRow()
        if current_item:
            plot_name = str(current_item.text())
            if plot_name in self.plot_list_dict.keys():
                self.plot_list_dict.pop(plot_name)
                self.list_dss_plot.takeItem(row)

    def clear_signal_plot(self):
        self.list_dss_plot.clear()
        self.plot_list_dict.clear()

    def open_output_folder(self):

        subprocess.Popen(['explorer.exe', str(self.dss_output_path)])

    def output_sa(self):
        current_item = self.list_dss_plot.currentItem()
        self.output_sa_one(current_item)
            # self.plotprocess.startDetached(f'cmd /c pushd "{thcc_folder[:2]}" & typhoon_hil sa --data_file="{os.getcwd()}\\{filename}.csv" --config_file="{cfg_file}" ')
            # subprocess.Popen(['typhoon_hil -sa', str(csv_file_path)])

    def output_sa_all(self):
        item_count = self.list_dss_plot.count()

        for row in range(item_count):
            item = self.list_dss_plot.item(row)
            self.output_sa_one(item)

    def output_sa_one(self, current_item):
        if current_item:
            csv_name = str(self.dss_model_name) + "_Mon_" + str(self.plot_list_dict[str(current_item.text())])
            csv_file_path = self.dss_output_path.joinpath(csv_name + '.csv')
            cfg_select = None
            thcc_folder = os.environ["TYPHOONPATH"]
            if "power" in csv_name:
                cfg_select = self.cfg_file_pq
            elif "voltage" in csv_name:
                cfg_select = self.cfg_file_vi
            self.plotprocess.startDetached(f'cmd /c pushd "{thcc_folder[:2]}" & typhoon_hil sa --data_file="{csv_file_path}" --config_file="{cfg_select}"')


    def do_signal_plot(self):
        item_count = self.list_dss_plot.count()

        for row in range(item_count):
            item = self.list_dss_plot.item(row)
            self.do_signal_plotter_one(item)

    def do_signal_plot_one(self):
        current_item = self.list_dss_plot.currentItem()
        self.do_signal_plotter_one(current_item)

    def do_signal_plotter_one(self, current_item):
        # current_item = self.list_dss_plot.currentItem()
        item_chunks = current_item.text().split(" ")

        mode = "0"
        if current_item:
            csv_name = str(self.dss_model_name) + "_Mon_" + str(self.plot_list_dict[str(current_item.text())])
            if "VOLTAGE" in csv_name:
                mode = "0"
            elif "POWER" in csv_name:
                mode = "1"
            else:
                print("invalid")
            csv_file_path = self.dss_output_path.joinpath(csv_name + '.csv')
            csvread = pd.read_csv(csv_file_path)

            #matplotlibLayoutWidget = MatplotlibWidget(None, width=5, height=6, dpi=80)
            #matplotlibLayoutWidget.setWindowTitle("graph_title")
            #matplotlibLayoutWidget.setWindowModality(QtCore.Qt.ApplicationModal)

            #matplotlibwidget = matplotlibLayoutWidget.return_Figure_Canvas()
            #matplotlibwidget.generic_draw([0, 1, 2], [33, 45, 22], title="graph_title", x_label="x_label", y_label="y_label")
            #matplotlibLayoutWidget.exec_()

            time_header = str(list(csvread)[0])

            if mode == "0":
                p1ylabel = "Vrms (V)"
                p1label = ["V1", "V2", "V3"]
                p2label = ["I1", "I2", "I3"]
                p2ylabel = "Irms (A)"
                p1keys = [" V1", " V2", " V3"]
                p2keys = [" I1", " I2", " I3"]
                subplotsize = 220
                fig = plt.figure(figsize=(12, 6))
                p1title = item_chunks[0] + " Phase to Neutral Voltage " + item_chunks[(len(item_chunks)-2)] + " " + item_chunks[(len(item_chunks)-1)]
                p2title = item_chunks[0] + " Phase Current " + item_chunks[(len(item_chunks)-2)] + " " + item_chunks[(len(item_chunks)-1)]
                p3title = item_chunks[0] + " Phase Voltage Angle " + item_chunks[(len(item_chunks)-2)] + " " + item_chunks[(len(item_chunks)-1)]
                p4title = item_chunks[0] + " Phase Current Angle " + item_chunks[(len(item_chunks)-2)] + " " + item_chunks[(len(item_chunks)-1)]
            elif mode == "1":
                p1ylabel = "Active power (kW)"
                p2ylabel = "Reactive power (kVAR)"
                p1label = ["P1", "P2", "P3"]
                p2label = ["Q1", "Q2", "Q3"]
                p1keys = [" P1 (kW)", " P2 (kW)", " P3 (kW)"]
                p2keys = [" Q1 (kvar)", " Q2 (kvar)", " Q3 (kvar)"]
                subplotsize = 120
                fig = plt.figure(figsize=(12, 3.8))
                p1title = item_chunks[0] + " Phase Active Power " + item_chunks[(len(item_chunks)-2)] + " " + item_chunks[(len(item_chunks)-1)]
                p2title = item_chunks[0] + " Phase Reactive Power " + item_chunks[(len(item_chunks)-2)] + " " + item_chunks[(len(item_chunks)-1)]
                p3title = item_chunks[0] + " Phase Voltage Angle " + item_chunks[(len(item_chunks)-2)] + " " + item_chunks[(len(item_chunks)-1)]
                p4title = item_chunks[0] + " Phase Current Angle " + item_chunks[(len(item_chunks)-2)] + " " + item_chunks[(len(item_chunks)-1)]
            else:
                p1ylabel = "Vrms (V)"
                p2ylabel = "Irms (A)"
                p1label = ["V1", "V2", "V3"]
                p2label = ["I1", "I2", "I3"]
                p1keys = [" V1", " V2", " V3"]
                p2keys = [" I1", " I2", " I3"]
                subplotsize = 220
                fig = plt.figure(figsize=(12, 6))
                p1title = item_chunks[0] + " Phase to Neutral Voltage " + item_chunks[(len(item_chunks) - 2)] + " " + item_chunks[(len(item_chunks) - 1)]
                p2title = item_chunks[0] + " Phase Current " + item_chunks[(len(item_chunks) - 2)] + " " + item_chunks[(len(item_chunks) - 1)]
                p3title = item_chunks[0] + " Phase Voltage Angle " + item_chunks[(len(item_chunks) - 2)] + " " + item_chunks[(len(item_chunks) - 1)]
                p4title = item_chunks[0] + " Phase Current Angle " + item_chunks[(len(item_chunks) - 2)] + " " + item_chunks[(len(item_chunks) - 1)]

            p1 = plt.subplot(subplotsize+1)
            # plt.ion()
            plt.plot(csvread[time_header], csvread[p1keys[0]], label=p1label[0], color='blue', marker='o')
            if p1keys[1] in csvread.columns:
                plt.plot(csvread[time_header], csvread[p1keys[1]], label=p1label[1], color='green', marker='o')
            if p1keys[2] in csvread.columns:
                plt.plot(csvread[time_header], csvread[p1keys[2]], label=p1label[2], color='red', marker='o')
            if mode == "1":
                plt.xlabel('time (h)')
            plt.ylabel(p1ylabel)
            plt.ticklabel_format(useOffset=False)
            plt.title(p1title)
            plt.grid(which='both', axis='both', linestyle='-', linewidth=1)
            plt.legend(loc='best', ncol=1)

            if mode == "0":
                p3 = plt.subplot(subplotsize+3)
                # plt.ion()
                plt.plot(csvread[time_header], csvread[" VAngle1"], label="V1 Angle", color='blue', marker='o')
                if " VAngle2" in csvread.columns:
                    plt.plot(csvread[time_header], csvread[" VAngle2"], label="V2 Angle", color='green', marker='o')
                if " VAngle3" in csvread.columns:
                    plt.plot(csvread[time_header], csvread[" VAngle3"], label="V3 Angle", color='red', marker='o')
                #plt.plot(csvread["hour"], csvread[" VAngle2"], color='tab:green', marker='o')
                #plt.plot(csvread["hour"], csvread[" VAngle2"], color='green')
                #plt.plot(csvread["hour"], csvread[" VAngle3"], color='tab:red', marker='o')
                #plt.plot(csvread["hour"], csvread[" VAngle3"], color='red')
                plt.xlabel('time (h)')
                plt.ylabel('Degrees')
                plt.ticklabel_format(useOffset=False)
                plt.title(p3title)
                plt.grid(which='both', axis='both', linestyle='-', linewidth=1)
                plt.legend(loc='best', ncol=1)

            p2 = plt.subplot(subplotsize+2)
            # plt.ion()
            plt.plot(csvread[time_header], csvread[p2keys[0]], label=p2label[0], color='blue', marker='o')
            if p2keys[1] in csvread.columns:
                plt.plot(csvread[time_header], csvread[p2keys[1]], label=p2label[1], color='green', marker='o')
            if p2keys[2] in csvread.columns:
                plt.plot(csvread[time_header], csvread[p2keys[2]], label=p2label[2], color='red', marker='o')
            if mode == "1":
                plt.xlabel('time (h)')
            plt.ylabel(p2ylabel)
            plt.ticklabel_format(useOffset=False)
            plt.title(p2title)
            plt.grid(which='both', axis='both', linestyle='-', linewidth=1)
            plt.legend(loc='best', ncol=1)

            if mode == "0":
                p4 = plt.subplot(subplotsize+4)
                # plt.ion()
                plt.plot(csvread[time_header], csvread[" IAngle1"], label="I1 Angle", color='blue', marker='o')
                if " IAngle2" in csvread.columns:
                    plt.plot(csvread[time_header], csvread[" IAngle2"], label="I2 Angle", color='green', marker='o')
                if " IAngle3" in csvread.columns:
                    plt.plot(csvread[time_header], csvread[" IAngle3"], label="I3 Angle", color='red', marker='o')
                # plt.plot(csvread["hour"], csvread[" VAngle2"], color='tab:green', marker='o')
                # plt.plot(csvread["hour"], csvread[" VAngle2"], color='green')
                # plt.plot(csvread["hour"], csvread[" VAngle3"], color='tab:red', marker='o')
                # plt.plot(csvread["hour"], csvread[" VAngle3"], color='red')
                plt.xlabel('time (h)')
                plt.ylabel('Degrees')
                plt.ticklabel_format(useOffset=False)
                plt.title(p4title)
                plt.grid(which='both', axis='both', linestyle='-', linewidth=1)
                plt.legend(loc='best', ncol=1)

            plt.show()

    def return_updated_dict(self):
        self.accept()


# Append commands dialog
class Mon_panels(object):
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


class AppendDialog(QDialog, Mon_panels):

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


# Reminder: this is not a published API call
# import typhoon.util.path as up
#
# py3_port_path = up.get_base_python_portable_path()
# sys.path.append(os.path.join(py3_port_path, "lib", "site-packages"))
#
# SW_VERS = hil.get_sw_version()
# appdata_path = os.getenv('APPDATA')
# dss_direct_path = fr"{appdata_path}\typhoon\{SW_VERS}\python_portables\python3_portable\Lib\site-packages"
# if not dss_direct_path in sys.path:
#     sys.path.append(dss_direct_path)


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

    import tse_to_opendss
    from tse_to_opendss.tse2tpt_base_converter import tse2tpt

    if tse2tpt.convert(json_file_path, tse_to_opendss, sim_parameters):
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


def run_command(mdl, comm):
    import opendssdirect as dss
    from pathlib import Path

    #command_prop = mdl.prop(mask_handle, "command")
    #command = mdl.get_property_disp_value(command_prop)
    #command = "export monitors load1_power1"
    command = comm

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

    mdlfile = mdl.get_model_file_path()
    mdlfile_name = pathlib.Path(mdlfile).stem

    if mode == "snap":
        rep_successful = repf.generate_report(mdlfile_name)
    elif mode == "fault":
        rep_successful = repf.generate_faultstudy_report(mdlfile_name)
    if not rep_successful[0]:
        mdl.info(rep_successful[1])

def define_icon(mdl, mask_handle):
    mdl.set_component_icon_image(mask_handle, "images/monitoring.svg")



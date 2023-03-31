from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable, KeepTogether
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, PageBreak, Spacer
from reportlab.lib.pagesizes import A4

import opendssdirect as dss
from .report_functions import *

ALL_OBJ_TYPES = ["BUS", "VSOURCE", "GENERATOR", "LINE", "LOAD", "TRANSFORMER"]

def dss_data_build(dss_data_dict):

    for obj_type in ALL_OBJ_TYPES:
        # Bus must be first because of the elements list

        dss_data_dict[obj_type] = {}

        # Go to first
        if not obj_type == "BUS":
            dss.Circuit.SetActiveClass(obj_type)
            dss.ActiveClass.First()

        if not dss.ActiveClass.First() == 0 and not obj_type == "BUS":
            for idx in range(dss.ActiveClass.Count()):
                if dss.CktElement.Enabled():
                    obj_data = {"buses": [],
                                "voltages": [],
                                "currents": [],
                                "phases": [],
                                "basekV": [],
                                "basekVA": [],
                                "PF": [],
                                "powers": [],
                                "losses": [],
                                "phases": []
                                }

                    # Get the name
                    fullname = dss.CktElement.Name().upper()
                    obj_name = fullname.split(obj_type + ".")[1]

                    # Set corresponding object
                    if obj_type == "LOAD":
                        dss.Loads.Idx(idx + 1)
                    elif obj_type == "LINE":
                        dss.Lines.Idx(idx + 1)
                    elif obj_type == "VSOURCE":
                        dss.Vsources.Idx(idx + 1)
                    elif obj_type == "ISOURCE":
                        dss.Isource.Idx(idx + 1)
                    elif obj_type == "TRANSFORMER":
                        dss.Transformers.Idx(idx + 1)
                    elif obj_type == "GENERATOR":
                        dss.Generators.Idx(idx + 1)

                    # Get the connected buses names
                    obj_data["buses"] = [busname.upper().split(".")[0] for busname in dss.CktElement.BusNames()]
                    for bus in obj_data["buses"]:
                        if obj_name not in dss_data_dict.get("BUS").get(bus).get("elements"):
                            dss_data_dict.get("BUS").get(bus).get("elements").append(f"{obj_type}.{obj_name}")
                            dss_data_dict.get("BUS").get(bus).get("elements").sort()

                    # Voltage data (first phase only)
                    vdata = dss.CktElement.VoltagesMagAng()
                    obj_data["voltages"] = vdata

                    # BasekV
                    if obj_type == "VSOURCE":
                        obj_data["basekV"] = dss.Vsources.BasekV()
                    if obj_type == "GENERATOR":
                        obj_data["basekV"] = dss.Generators.kV()

                    # BasekVA
                    if obj_type == "LOAD":
                        obj_data["basekVA"] = dss.Loads.kVABase()

                    # PF
                    if obj_type == "LOAD":
                        obj_data["PF"] = dss.Loads.PF()

                    # Current data
                    idata = dss.CktElement.CurrentsMagAng()
                    obj_data["currents"] = idata

                    # Power data
                    sdata = dss.CktElement.Powers()
                    obj_data["powers"] = sdata

                    # Losses
                    obj_data["losses"] = dss.CktElement.Losses()

                    # Phases
                    obj_data["phases"] = dss.CktElement.NumPhases()

                    if obj_type == "VSOURCE":
                        dss_data_dict.get("BUS").get(bus).get("vsources").append(f"{obj_type}.{obj_name}")
                        dss_data_dict.get("BUS").get(bus).get("vsources").sort()
                    elif obj_type == "ISOURCE":
                        dss_data_dict.get("BUS").get(bus).get("isources").append(f"{obj_type}.{obj_name}")
                        dss_data_dict.get("BUS").get(bus).get("isources").sort()

                    dss_data_dict[obj_type].update({obj_name: obj_data})

                dss.ActiveClass.Next()

        elif obj_type == "BUS":
            # Get the names
            busnames = sorted(dss.Circuit.AllBusNames())
            for busname in [bn.upper() for bn in busnames]:
                obj_data = {"voltages": [],
                            "line_voltages": [],
                            "basekV": [],
                            "powers": [],
                            "phases": [],
                            "elements": [],
                            "loads": [],
                            "vsources": [],
                            "isources": []
                            }

                dss.Circuit.SetActiveBus(busname)
                obj_data["basekV"] = dss.Bus.kVBase()
                obj_data["voltages"] = dss.Bus.VMagAngle()
                obj_data["line_voltages"] = dss.Bus.VLL()
                obj_data["phases"] = dss.Bus.NumNodes()
                obj_data["loads"] = [load.upper() for load in dss.Bus.LoadList()]
                obj_data["elements"].sort()

                dss_data_dict[obj_type].update({busname: obj_data})

def generate_report(mdlfile):
    import os
    filename = pathlib.Path(mdlfile).stem

    pg_w, pg_h = A4
    margin = 5
    tw = pg_w - 100  # Width of the tables
    story = []
    dss_data_dict = {}

    sections_dict = {
        "Summary": {
            "col1_names": [["Circuit name", "Total buses", "Total elements"]],
            "col1_widths": [tw * p / 100 for p in [20, 20, 20]],
            "col2_names": [["Total load P (kW)", "Total load Q (kVAr)", "Total delivered P (kW)", "Total delivered Q (kVAR)"]],
            "col2_widths": [tw * p / 100 for p in [20, 20, 20, 20]],
            "col3_names": [["Total P losses (kW)", "Losses (%)", "Total demanded Q (kVAr)"]],
            "col3_widths": [tw * p / 100 for p in [20, 20, 20]]
        },
        "VSOURCES": {
            "col_names": [["Name", "Bus", "Node", "Phase V (kV)", "Base kV", "V pu", "V drop", "kW", "kVAr"]],
            "col_widths": [tw * p / 100 for p in [22, 14, 6, 15, 7, 7, 9, 7, 7]]
        },
        "BUSES": {
            "col_names": [["Name", "Node", "Phase V (kV)", "Base kV", "V pu", "Sources", "Loads", "Connected elements"]],
            "col_widths": [tw * p / 100 for p in [22, 6, 12, 7, 5, 14, 14, 34]],
            "col_names_2": [["", "", "", "", "", "kW", "kVAr", "kW", "kVAr", ""]],
            "col_widths_2": [tw * p / 100 for p in [22, 6, 12, 7, 5, 7, 7, 7, 7, 34]]
        },
        "LINES": {
            "col_names": [["Name", "Bus", "Node", "Phase V (kV)", "Current (A)", "Rating (A)",
                           "kW", "kVAr", "kW Loss", "kVA Loss", "V drop"]],
            "col_widths": [tw * p / 100 for p in [22, 14, 6, 15, 12, 8, 7, 7, 8, 8, 8]]
        },
        "LOADS": {
            "col_names": [["Name", "Bus", "Node", "Phase V (kV)", "kW", "kVAr", "kVA", "PF", "kVABase", "pu kVA"]],
            "col_widths": [tw * p / 100 for p in [22, 14, 6, 15, 7, 7, 7, 7, 9, 7]]
        },
        "GENERATORS": {
            "col_names": [["Name", "Bus", "Voltage (kV)", "pu Volts", "V drop (%)", "P (kW)", "S (kVA)", "PF"]],
            "col_widths": [tw * p / 100 for p in [22, 14, 15, 8, 15, 14, 15, 10]]
        },
        "TRANSFORMERS": {
            "col_names": [["Name", "Wdg / Bus", "Node", "Phase V (kV)",
                           "kVA base", "kW", "kVAr", "kVA", "PF", "pu kVA", "kW Loss", "kVA Loss"]],
            "col_widths": [tw * p / 100 for p in [22, 14, 6, 15, 8, 8, 8, 8, 5, 7, 8, 8]]
        }}

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            """add page info to each page (page x of y)"""
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.footer()
                self.header()
                self.draw_page_number(num_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_page_number(self, page_count):
            self.setFont("Helvetica", 8)
            self.setFillColorRGB(255, 255, 255)
            self.drawRightString(pg_w - 30, 8, f"Page {self._pageNumber} of {page_count}")

        def footer(self):
            # Bottom lines
            self.setLineWidth(20)
            self.setStrokeColorRGB(255, 0, 0)
            #self.line(margin + 100 - 20, 10, pg_w - 210, 10)
            self.line(pg_w - 100, 10, pg_w, 10)
            text_obj = self.beginText()
            text_obj.setTextOrigin(margin + 100, 12)
            text_obj.setFont("Helvetica", 8)
            # text_obj.setFillColorRGB(255, 255, 255)
            text_obj.textLine('https://www.typhoon-hil.com           https://www.epri.com/pages/sa/opendss')
            self.drawText(text_obj)
            self.drawImage(os.path.join(image_path, "elephant.png"), 60, 2, 0.05 * 843,
                           0.05 * 478)
            self.drawImage(os.path.join(image_path, "opendss.jpg"), pg_w - 210, 0, 0.1 * 400, 0.1 * 291)

        def header(self):
            # Top line
            self.setLineWidth(30)
            self.setStrokeColorRGB(255, 0, 0)
            self.line(0, pg_h-20, pg_w - 100, pg_h-20)
            # Text 1
            text_obj = self.beginText()
            text_obj.setTextOrigin(pg_w - 85, pg_h - 17)
            text_obj.setFont("Helvetica-Bold", 10)
            text_obj.textLine("Typhoon HIL")
            text_obj.textLine("OpenDSS")
            text_obj.setFillColorRGB(255, 255, 255)
            self.drawText(text_obj)
            # Text 2
            text_obj = self.beginText()
            text_obj.setFillColorRGB(255, 255, 255)
            text_obj.setTextOrigin(margin + 20, pg_h - 25)
            text_obj.setFont("Helvetica-Bold", 11)
            text_obj.textLine("LOAD FLOW SIMULATION REPORT")
            self.drawText(text_obj)


    class SectionHeader(Flowable):

        def __init__(self, title, size=20):
            self.title = title
            self.size = size

        def wrap(self, *args):
            return (0, 40)

        def draw(self):
            c = self.canv
            c.setFont("Helvetica-Bold", 11)
            c.drawString(30, 5, self.title.upper())
            # Bottom line
            c.setLineWidth(3)
            c.line(0, -2, 45 + len(self.title)*7.2, -2)


    class ColumnTitleUnderlines(Flowable):

        def __init__(self, cols_widths, column_names):
            self.cols_widths = cols_widths
            self.column_names = column_names
            self.spaceAfter = 0

        def wrap(self, *args):
            return (0, 0)

        def draw(self):
            c = self.canv
            start = -2.5
            c.setLineWidth(1)
            for idx, col_name in enumerate(self.column_names):
                width = self.cols_widths[idx]
                if col_name:
                    c.line(start + 3, 3, start + width - 3, 3)
                start = start + width

    def column_names(col_names, col_widths):
        LIST_STYLE = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
        ])
        t = Table(col_names, colWidths=col_widths,
                  style=LIST_STYLE, hAlign="LEFT", rowHeights=[15])
        return t

    def data_table(data, col_widths, object_type):

        # Bold totals
        list_sum = []
        for row, row_list in enumerate(data):
            if "Total:" in row_list:
                list_sum.append(row)

        bolds = []
        for row in list_sum:
            if object_type == "BUS":
                bolds.append(('FONTNAME', (0, row), (-2, row), 'Helvetica-Bold'))
            else:
                bolds.append(('FONTNAME', (0, row), (-1, row), 'Helvetica-Bold'))

        # Colored over ratings
        colored = []
        if object_type == "LINE":
            for row, row_list in enumerate(data):
                if row_list and "Total:" not in row_list:
                    try:
                        rating = float(row_list[5]) if row_list[5] else 0
                        if rating:
                            ratio = float(row_list[4].split("∠")[0])/rating
                            if ratio > 1.10:
                                colored.append(('TEXTCOLOR', (4, row), (4, row), (1, 0, 0)))
                            elif ratio > 1:
                                colored.append(('TEXTCOLOR', (4, row), (4, row), (1, 0.5, 0)))
                    except IndexError:
                        pass
        elif object_type == "LOAD":
            for row, row_list in enumerate(data):
                if row_list and "Total:" in row_list:
                    try:
                        pu = float(row_list[9]) if row_list[9] else 0
                        if pu:
                            if pu > 1.10:
                                colored.append(('TEXTCOLOR', (9, row), (9, row), (1, 0, 0)))
                            elif pu > 1:
                                colored.append(('TEXTCOLOR', (9, row), (9, row), (1, 0.5, 0)))
                    except IndexError:
                        pass
        elif object_type == "TRANSFORMER":
            for row, row_list in enumerate(data):
                if row_list and "Total:" in row_list:
                    try:
                        pu = float(row_list[9]) if row_list[9] else 0
                        if pu:
                            if pu > 1.10:
                                colored.append(('TEXTCOLOR', (9, row), (9, row), (1, 0, 0)))
                            elif pu > 1:
                                colored.append(('TEXTCOLOR', (9, row), (9, row), (1, 0.5, 0)))
                    except IndexError:
                        pass

        LIST_STYLE = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('LEADING', (0, 0), (-1, -1), 10)
        ] + bolds + colored)

        t = Table(data, colWidths=col_widths, style=LIST_STYLE, hAlign="LEFT", rowHeights=15)
        return t

    def limit_name_chars(org_name, chars=20):
        # Limit to 30 characters
        new_name = org_name[:int(chars / 3)] + "…" + org_name[-int(2 * chars / 3):]
        if len(org_name) > chars:
            return new_name
        else:
            return org_name

    def add_section(object_type):

        # Summary
        def proc_summary():
            proc_line = []
            cktname = dss.Circuit.Name() if len(dss.Circuit.Name()) < 30 else dss.Circuit.Name()[:27] + "..."
            proc_line.append(cktname)
            proc_line.append(dss.Circuit.NumBuses())
            proc_line.append(dss.Circuit.NumCktElements())
            # Calculate total Load power
            l_kW = 0
            l_kVAr = 0
            dss.Loads.First()
            l_kW += dss.CktElement.Losses()[0]
            l_kVAr += dss.CktElement.Losses()[1]
            while not dss.Loads.Next() == 0:
                l_kW += dss.CktElement.Losses()[0]
                l_kVAr += dss.CktElement.Losses()[1]
            proc_line.append(round_mod(l_kW / 1000, 2))
            proc_line.append(round_mod(l_kVAr / 1000, 2))
            # Total delivered power
            proc_line.extend([-round_mod(n, 2) for n in dss.Circuit.TotalPower()])
            # Losses
            proc_line.append(round_mod(dss.Circuit.Losses()[0]/1000, 2))
            # Losses %
            try:
                proc_line.append(round_mod(dss.Circuit.Losses()[0]/l_kW*100, 1))
            except ZeroDivisionError:
                l_kW = VIRTUAL_ZERO
                proc_line.append(round_mod(dss.Circuit.Losses()[0] / l_kW * 100, 1))
            proc_line.append(round_mod(dss.Circuit.Losses()[1]/1000, 2))

            return proc_line

        # Buses
        def proc_line_bus(data, obj_name):
            # Node voltages
            proc_lines = []

            elements_to_be_added = data.get("elements")
            elements_to_be_added = sorted(set(elements_to_be_added), key=len)
            max_len = 45

            total_kw_src, total_kvar_src, total_kw_load, total_kvar_load = (0, 0, 0, 0)

            for phase in range(data.get("phases")):
                proc_line = []
                basekV = data.get('basekV')
                if phase == 0:
                    # Name
                    proc_line.append(limit_name_chars(obj_name))
                else:
                    proc_line.append("")
                # Node
                proc_line.append(phase + 1)

                v = f"{round_mod(data.get('voltages')[2*phase] / 1000, 3)} ∠" \
                    f"{round_mod(data.get('voltages')[2 * phase + 1], 1)}°"
                proc_line.append(v)
                # BasekV
                if phase == 0:
                    proc_line.append(f"{round_mod(basekV, 3)}")
                else:
                    proc_line.append("")
                v_pu = f"{round_mod(data.get('voltages')[2*phase] / 1000 / basekV, 3)}"
                proc_line.append(v_pu)

                vsources = [src.split("VSOURCE.")[1] for src in data.get('vsources')]
                isources = [src.split("ISOURCE.")[1] for src in data.get('isources')]
                loads = [load.split("LOAD.")[1] for load in data.get('loads')]
                kw_src, kvar_src, kw_load, kvar_load = get_bus_power_loads_and_sources(dss_data_dict, phase,
                                                                                       loads, vsources, isources)
                total_kw_src += kw_src
                total_kvar_src += kvar_src
                total_kw_load += kw_load
                total_kvar_load += kvar_load

                # Generation and Loading
                proc_line.extend([f"{kw_src}", f"{kvar_src}", f"{kw_load}", f"{kvar_load}"])

                proc_lines.append(proc_line)

            # Append total powers and Vline
            total_line = []
            str_kw_src = f"{round_mod(total_kw_src, 2)}"
            str_var_src = f"{round_mod(total_kvar_src, 2)}"
            str_kw_load = f"{round_mod(total_kw_load, 2)}"
            str_kvar_load = f"{round_mod(total_kvar_load, 2)}"
            if int(data.get("phases")) > 1 and data.get("line_voltages"):
                v_line = cart2pol(float(data.get("line_voltages")[0]), float(data.get("line_voltages")[1]))
                total_line.extend(["", "V12:", f"{round_mod(v_line[0]/1000, 3)} ∠{round_mod(v_line[1], 1)}°", "",
                                   "Total:", str_kw_src, str_var_src, str_kw_load, str_kvar_load])
            else:
                total_line.extend(["", "", "", "", "Total:", str_kw_src, str_var_src, str_kw_load, str_kvar_load])
            proc_lines.append(total_line)

            # Element list
            elements_strings = []
            while elements_to_be_added:
                elems_str = f"{limit_name_chars(elements_to_be_added[0], 34)}"
                del elements_to_be_added[0]
                for el in elements_to_be_added[:]:
                    new_str = f"{elems_str} | {el}"
                    if len(new_str) < max_len:
                        elems_str = new_str
                        elements_to_be_added.remove(el)
                elements_strings.append(elems_str)

            for idx, es in enumerate(elements_strings):
                if len(proc_lines) > idx:
                    proc_lines[idx].append(es)
                else:
                    proc_lines.append(["", "", "", "", "", "", "", "", "", es])

            proc_lines.append([""])
            return proc_lines

        # Voltage source
        def proc_line_vsource(data, obj_name):
            proc_lines = []

            total_kw, total_kvar = (0, 0)

            for phase in range(data.get("phases")):
                proc_line = []

                # Name
                if phase == 0:
                    proc_line.append(limit_name_chars(obj_name))
                else:
                    proc_line.append("")

                # Connected buses
                connected_buses = list(set(data.get("buses")))
                num_buses = len(connected_buses)
                if phase < num_buses:
                    proc_line.append([limit_name_chars(bname, 14) for bname in connected_buses][phase])
                else:
                    proc_line.append("")

                # Node
                proc_line.append(phase + 1)

                # Voltages
                v1 = f"{round_mod(data.get('voltages')[2 * phase] / 1000, 3)} " \
                     f"∠{round_mod(data.get('voltages')[2 * phase + 1], 1)}°"
                proc_line.extend([v1])

                # Base kV
                basekv = data.get('basekV') / np.sqrt(3)
                proc_line.append(round_mod(basekv, 3))

                # Voltage drop
                pu_volts = data.get('voltages')[2 * phase] / 1000 / basekv
                vdrop = round_mod((1 - pu_volts) * 100, 2)
                pu_volts = round_mod(pu_volts, 3)
                proc_line.extend([pu_volts, f"{vdrop} %"])

                # Powers
                kw = data.get('powers')[2 * phase]
                kvar = data.get('powers')[2 * phase + 1]
                total_kw += kw
                total_kvar += kvar
                proc_line.extend([f"{round_mod(kw, 2)}", f"{round_mod(kvar, 2)}"])
                proc_lines.append(proc_line)

            # Append total powers and Vline
            str_kw = f"{round_mod(total_kw, 2)}"
            str_kvar = f"{round_mod(total_kvar, 2)}"
            if int(data.get("phases")) > 1:
                v1_mag, v1_phase = (data.get("voltages")[0], data.get("voltages")[1])
                v2_mag, v2_phase = (data.get("voltages")[2], data.get("voltages")[3])
                v_line_mag, v_line_ang = calculate_line_voltage(v1_mag, v1_phase, v2_mag, v2_phase)
                proc_lines.append(["", "", "V12:", f"{round_mod(v_line_mag / 1000, 3)} ∠{round_mod(v_line_ang, 1)}°",
                                   "", "", "Total:", str_kw, str_kvar])
            else:
                proc_lines.append(
                    ["", "", "", "", "", "", "Total:", str_kw, str_kvar])

            proc_lines.append([""])
            return proc_lines

        # Generator
        def proc_line_generator(data, obj_name):
            proc_lines = []

            for phase in range(data.get("phases")):
                proc_line = []

                # Name
                if phase == 0:
                    proc_line.append(limit_name_chars(obj_name))
                else:
                    proc_line.append("")

                # Connected buses
                connected_buses = list(set(data.get("buses")))
                num_buses = len(connected_buses)
                if phase < num_buses:
                    proc_line.append([limit_name_chars(bname, 14) for bname in connected_buses][phase])
                else:
                    proc_line.append("")

                # Voltages
                v1 = f"{round_mod(data.get('voltages')[2 * phase] / 1000, 3)} " \
                     f"∠{round_mod(data.get('voltages')[2 * phase + 1], 1)}°"
                proc_line.extend([v1])

                # Base kV
                basekv = data.get('basekV') / np.sqrt(3)
                proc_line.append(round_mod(basekv, 3))

                # Voltage drop
                pu_volts = data.get('voltages')[2 * phase] / 1000 / basekv
                vdrop = round_mod((1 - pu_volts) * 100, 2)
                pu_volts = round_mod(pu_volts, 3)
                proc_line.extend([pu_volts, vdrop])

                # Powers
                kw = data.get('powers')[2 * phase]
                kvar = data.get('powers')[2 * phase + 1]
                proc_line.extend([f"{round_mod(kw, 2)}", f"{round_mod(kvar, 2)}"])
                proc_lines.append(proc_line)

                proc_line.extend([pu_volts, vdrop, round_mod(kw, 2), round_mod(kvar, 2)])
                proc_lines.append(proc_line)

            proc_lines.append([""])
            return proc_lines

        # Transmission Line
        def proc_line_tl(data, obj_name):

            proc_lines = []

            appended_name = False
            num_phases = data.get("phases")
            for bus_idx, bus in enumerate(data.get("buses")):

                total_kw, total_kvar = (0, 0)

                for phase in range(num_phases):
                    proc_line = []

                    # Name
                    if not appended_name:
                        proc_line.append(limit_name_chars(obj_name))
                        appended_name = True
                    else:
                        proc_line.append("")

                    # Connected bus
                    if phase == 0:
                        proc_line.append(limit_name_chars(bus, 14))
                    else:
                        proc_line.append("")

                    # Node
                    proc_line.append(phase + 1)

                    # Voltages
                    v = f"{round_mod(data.get('voltages')[2 * phase + bus_idx * num_phases * 2] / 1000, 3)} " \
                         f"∠{round_mod(data.get('voltages')[2 * phase + 1 + bus_idx * num_phases * 2], 1)}°"
                    proc_line.append(v)

                    # Currents
                    i = f"{round_mod(data.get('currents')[2 * phase + bus_idx * num_phases * 2], 3)} " \
                        f"∠{round_mod(data.get('currents')[2 * phase + 1 + bus_idx * num_phases * 2], 1)}°"
                    proc_line.append(i)
                    proc_line.append("")

                    # Powers
                    kw = data.get('powers')[2 * phase + bus_idx * num_phases * 2]
                    kvar = data.get('powers')[2 * phase + 1 + bus_idx * num_phases * 2]
                    proc_line.extend([f"{round_mod(kw, 2)}", f"{round_mod(kvar, 2)}"])
                    proc_lines.append(proc_line)
                    total_kw += kw
                    total_kvar += kvar

                    # Losses
                    if bus_idx == 0 and phase == 0:
                        kw_loss = abs(data.get('losses')[0] / 1000)
                        kvar_loss = abs(data.get('losses')[1] / 1000)
                        proc_line.extend([f"{round_mod(kw_loss, 3)}", f"{round_mod(kvar_loss, 3)}"])
                    else:
                        proc_line.extend(["", ""])

                    # Voltage drop
                    if bus_idx == 0:
                        v1 = data.get('voltages')[2 * phase]
                        v2 = data.get('voltages')[2 * phase + num_phases * 2]
                        vdrop = abs(round_mod((v1 - v2) / v1 * 100, 1))
                        proc_line.append(f"{vdrop} %")

                if num_phases > 1:
                    v1_mag, v1_phase = (data.get("voltages")[bus_idx * num_phases * 2],
                                        data.get("voltages")[bus_idx * num_phases * 2 + 1])
                    v2_mag, v2_phase = (data.get("voltages")[bus_idx * num_phases * 2 + 2],
                                        data.get("voltages")[bus_idx * num_phases * 2 + 3])
                    v_line_mag, v_line_ang = calculate_line_voltage(v1_mag, v1_phase, v2_mag, v2_phase)
                    proc_lines.append(
                        ["", "", "V12:", f"{round_mod(v_line_mag / 1000, 3)} ∠{round_mod(v_line_ang, 2)}°", "",
                         "Total:", f"{round_mod(total_kw, 3)}", f"{round_mod(total_kvar, 3)}", "", ""])
                else:
                    proc_lines.append(["", "", "", "", "", "Total:",
                                       f"{round_mod(total_kw, 3)}", f"{round_mod(total_kvar, 3)}", "", ""])
                if bus_idx == 0:
                    proc_lines.append(["", "", "----------------", "","" "", "", "", ""])
            proc_lines.append([])
            return proc_lines

        # Load
        def proc_line_load(data, obj_name):
            proc_lines = []

            total_kw, total_kvar = (0, 0)

            for phase in range(data.get("phases")):
                proc_line = []

                # Name
                if phase == 0:
                    proc_line.append(limit_name_chars(obj_name))
                else:
                    proc_line.append("")

                # Connected buses
                connected_buses = list(set(data.get("buses")))
                num_buses = len(connected_buses)
                if phase < num_buses:
                    proc_line.append([limit_name_chars(bname, 14) for bname in connected_buses][phase])
                else:
                    proc_line.append("")

                # Node
                proc_line.append(phase + 1)

                # Voltages
                v = f"{round_mod(data.get('voltages')[2 * phase] / 1000, 3)} " \
                    f"∠{round_mod(data.get('voltages')[2 * phase + 1], 1)}°"
                proc_line.append(v)

                # Powers
                kw = data.get('powers')[2 * phase]
                kvar = data.get('powers')[2 * phase + 1]
                proc_line.extend([f"{round_mod(kw, 2)}", f"{round_mod(kvar, 2)}"])

                # kVA
                kva = (kvar ** 2 + kw ** 2) ** 0.5
                proc_line.append(f"{round_mod(kva, 2)}")

                # Power Factor
                if kva:
                    pf = float(kw / kva)
                    proc_line.append(f"{round_mod(pf, 2)}")
                else:
                    proc_line.append("0")

                total_kw += kw
                total_kvar += kvar

                proc_lines.append(proc_line)

            last_line = []
            # kVA
            total_kva = (total_kvar ** 2 + total_kw ** 2) ** 0.5

            # Power Factor
            pf = float(total_kw / total_kva)
            last_line.extend(["", "", "", "Total:", f"{round_mod(total_kw, 3)}",
                              f"{round_mod(total_kvar, 3)}",
                              f"{round_mod(total_kva, 2)}", f"{round_mod(pf, 2)}"])

            if data.get('basekVA'):
                # kVABase
                kva_base = float(data.get('basekVA'))
                kva_base_str = f"{round_mod(kva_base, 3)}"

                # kVA pu
                kva_pu = total_kva/kva_base

                last_line.extend([kva_base_str, f"{round_mod(kva_pu, 2)}"])

            proc_lines.append(last_line)
            proc_lines.append([])
            return proc_lines

        # Transformer
        def proc_line_transformer(data, obj_name):
            proc_lines = []

            appended_name = False
            num_phases = data.get("phases")
            for bus_idx, bus in enumerate(data.get("buses")):

                total_kw, total_kvar = (0, 0)

                for phase in range(num_phases + 1):
                    proc_line = []

                    # Name
                    if not appended_name:
                        proc_line.append(limit_name_chars(obj_name))
                        appended_name = True
                    else:
                        proc_line.append("")

                    # Activate winding by index
                    dss.Transformers.Wdg(bus_idx)

                    # Connected bus
                    if phase == 0:
                        proc_line.append(f"{bus_idx + 1} / {limit_name_chars(bus, 11)}")
                    else:
                        proc_line.append("")

                    # Node
                    if phase == num_phases:
                        proc_line.append("N")
                    else:
                        proc_line.append(phase + 1)

                    # Voltages
                    v = f"{round_mod(data.get('voltages')[2 * phase + bus_idx * (num_phases + 1) * 2] / 1000, 3)} " \
                        f"∠{round_mod(data.get('voltages')[2 * phase + 1 + bus_idx * (num_phases + 1) * 2], 1)}°"
                    proc_line.append(v)

                    # kVA rating
                    kva_base = dss.Transformers.kVA()
                    if phase == 0:
                        proc_line.append(f"{round_mod(kva_base, 3)}")
                    else:
                        proc_line.append("")

                    # Powers
                    kw = data.get('powers')[2 * phase + bus_idx * (num_phases + 1) * 2]
                    kvar = data.get('powers')[2 * phase + 1 + bus_idx * (num_phases + 1) * 2]
                    kva = (kw ** 2 + kvar ** 2) ** 0.5
                    pf = abs(kw / kva) if not kva == 0 else 0
                    proc_line.extend([f"{round_mod(kw, 2)}", f"{round_mod(kvar, 2)}", f"{round_mod(kva, 2)}", f"{round_mod(pf, 2)}"])
                    proc_lines.append(proc_line)
                    total_kw += kw
                    total_kvar += kvar

                    # pu skip
                    proc_line.append("")

                    # Losses
                    if bus_idx == 0 and phase == 0:
                        kw_loss = abs(data.get('losses')[0] / 1000)
                        kvar_loss = abs(data.get('losses')[1] / 1000)
                        proc_line.extend([f"{round_mod(kw_loss, 3)}", f"{round_mod(kvar_loss, 3)}"])
                    else:
                        proc_line.extend(["", ""])

                # kVA ratings
                total_kva = (total_kvar ** 2 + total_kw ** 2) ** 0.5
                total_pf = total_kw / total_kva if total_kva > 0 else 0
                pu_kva = total_kva / kva_base if kva_base > 0 else 0

                total_kva_str = f"{round_mod(total_kva, 3)}"
                total_pf_str = f"{abs(round_mod(total_pf, 2))}"
                pu_kva_str = f"{round_mod(pu_kva, 2)}"

                if num_phases > 1:

                    v1_mag, v1_phase = (data.get("voltages")[bus_idx * (num_phases + 1) * 2],
                                        data.get("voltages")[bus_idx * (num_phases + 1) * 2 + 1])
                    v2_mag, v2_phase = (data.get("voltages")[bus_idx * (num_phases + 1) * 2 + 2],
                                        data.get("voltages")[bus_idx * (num_phases + 1) * 2 + 3])
                    v_line_mag, v_line_ang = calculate_line_voltage(v1_mag, v1_phase, v2_mag, v2_phase)
                    proc_lines.append(
                        ["", "", "V12:",
                         f"{round_mod(v_line_mag / 1000, 3)} ∠{round_mod(v_line_ang, 1)}°",
                         "Total:", f"{round_mod(total_kw, 3)}", f"{round_mod(total_kvar, 3)}",
                         total_kva_str, total_pf_str, pu_kva_str])
                else:
                    proc_lines.append(["", "", "", "", "", "Total:",
                                       f"{round_mod(total_kw, 3)}", f"{round_mod(total_kvar, 3)}",
                                       total_kva_str, total_pf_str, pu_kva_str])

                # Winding separator
                if not bus_idx == len(data.get("buses")) - 1:
                    proc_lines.append(["", "", "----------------", "", "", "", "", "", "", ""])

            return proc_lines

        # A function for each object type
        func_dict = {"LINE": proc_line_tl, "LOAD": proc_line_load, "VSOURCE": proc_line_vsource,
                     "TRANSFORMER": proc_line_transformer, "GENERATOR": proc_line_generator, "BUS": proc_line_bus}

        if object_type == "Summary":
            section_name = object_type
            spacer = Spacer(0, 20)
            col1_names = sections_dict.get(section_name).get("col1_names")
            col2_names = sections_dict.get(section_name).get("col2_names")
            col3_names = sections_dict.get(section_name).get("col3_names")
            col1_widths = sections_dict.get(section_name).get("col1_widths")
            col2_widths = sections_dict.get(section_name).get("col2_widths")
            col3_widths = sections_dict.get(section_name).get("col3_widths")
            # Header
            header = SectionHeader(section_name)
            story.append(header)
            story.append(spacer)
            # First piece of data
            cols_flow = column_names(col1_names, col1_widths)
            story.append(cols_flow)
            processed_data = [proc_summary()[:3]]
            data_flow = data_table(processed_data, col1_widths, object_type)
            story.append(data_flow)
            story.append(spacer)
            # Second piece of data
            cols_flow = column_names(col2_names, col2_widths)
            story.append(cols_flow)
            processed_data = [proc_summary()[3:7]]
            data_flow = data_table(processed_data, col2_widths, object_type)
            story.append(data_flow)
            story.append(spacer)
            # Third piece of data
            cols_flow = column_names(col3_names, col3_widths)
            story.append(cols_flow)
            processed_data = [proc_summary()[7:]]
            data_flow = data_table(processed_data, col3_widths, object_type)

            story.append(data_flow)
            story.append(PageBreak())
        else:
            # Header
            def create_header(after=False):
                # Object section
                section_name = object_type + "S" if not object_type[-1] in ["S", "H"] else object_type + "ES"
                col_names = sections_dict.get(section_name).get("col_names")
                col_widths = sections_dict.get(section_name).get("col_widths")
                cols_underlines = ColumnTitleUnderlines(col_widths, col_names[0])
                if not after:
                    header = SectionHeader(section_name)
                    spacer = Spacer(0, 20)
                cols_flow = column_names(col_names, col_widths)
                if object_type in ["BUS"]:
                    col_names_2 = sections_dict.get(section_name).get("col_names_2")
                    col_widths_2 = sections_dict.get(section_name).get("col_widths_2")
                    cols_flow_2 = column_names(col_names_2, col_widths_2)
                    cols_underlines_2 = ColumnTitleUnderlines(col_widths_2, col_names_2[0])
                    col_widths = col_widths_2
                    if not after:
                        kt = [header, spacer, cols_flow, cols_underlines, cols_flow_2, cols_underlines_2]
                    else:
                        kt = [cols_flow, cols_underlines, cols_flow_2, cols_underlines_2]
                else:
                    if not after:
                        kt = [header, spacer, cols_flow, cols_underlines]
                    else:
                        kt = [cols_flow, cols_underlines]
                return col_widths, kt
            col_widths, kt = create_header()
            story.append(KeepTogether(kt))

            row_count = 0
            iter_count = 0
            iter_max = len(dss_data_dict.get(object_type))
            if dss_data_dict.get(object_type):
                for obj_name, data_dict in dss_data_dict.get(object_type).items():
                    processed_data = func_dict[object_type](data_dict, obj_name)
                    data_flow = data_table(processed_data, col_widths, object_type)
                    row_count += len(processed_data)
                    if row_count > 43 and iter_count < iter_max:
                        _, kt = create_header(after=True)
                        row_count = 0
                        kt.append(data_flow)
                        flow_chunk = KeepTogether(kt)
                    else:
                        flow_chunk = KeepTogether(data_flow)
                    story.append(flow_chunk)
                    iter_count += 1

                story.append(PageBreak())

    # Build the circuit data
    dss_data_build(dss_data_dict)

    # Add the sections
    add_section("Summary")
    add_section("BUS")
    if not dss.Vsources.First() == 0:
        add_section("VSOURCE")
    if not dss.Generators.First() == 0:
        add_section("GENERATOR")
    if not dss.Lines.First() == 0:
        add_section("LINE")
    if not dss.Loads.First() == 0:
        add_section("LOAD")
    if not dss.Transformers.First() == 0:
        add_section("TRANSFORMER")


    try:
        import subprocess

        target_files_folder = pathlib.Path(mdlfile).parent.joinpath(f"{filename} Target files")

        if not os.path.isdir(f'{target_files_folder}/dss/reports'):
            os.makedirs(f'{target_files_folder}/dss/reports')

        file_output_path = f'{target_files_folder}/dss/reports/{filename}_powerflow_report.pdf'
        doc = SimpleDocTemplate(file_output_path,
                                rightMargin=margin, leftMargin=margin, topMargin=40, bottomMargin=50)
        doc.build(story, canvasmaker=NumberedCanvas)
        subprocess.Popen(file_output_path, shell=True)

        return [True, ""]
    except PermissionError:
        # Report file is already open
        return [False, "Could not write the report to disk. Please close any previous reports."]
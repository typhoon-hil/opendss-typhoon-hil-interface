import subprocess
import math
import opendssdirect as dss


def dss_data_build(data_source_object_type):
    obj_data = {"names": [],
                "buses": [],
                "voltages": [],
                "basekVs": [],
                "powers": [],
                "phases": []
                }

    # Go to first
    if not data_source_object_type == "Bus":
        dss.Circuit.SetActiveClass(data_source_object_type)

    if not dss.ActiveClass.First() == 0 and not data_source_object_type == "Bus":
        for _ in range(dss.ActiveClass.Count()):
            if dss.CktElement.Enabled():
                 # Get the name
                obj_data["names"].append(dss.CktElement.Name().split(data_source_object_type + ".")[1])

                # Get the connected buses names
                obj_data["buses"].append([bname.split(".")[0] for bname in dss.CktElement.BusNames()])
                num_buses = len(dss.CktElement.BusNames())

                # Voltage data (first phase only)
                vdata = dss.CktElement.VoltagesMagAng()
                num_terminals_per_bus = int(len(vdata) / num_buses)

                v_list = []
                for idx in range(num_buses):
                    if dss.CktElement.NumPhases() == 3:
                        vmag = vdata[idx * num_terminals_per_bus] * 3 ** (0.5)
                        vangle = vdata[idx * num_terminals_per_bus + 1] + 30
                    else:
                        vmag = vdata[idx * num_terminals_per_bus]
                        vangle = vdata[idx * num_terminals_per_bus + 1]
                    v_list.extend([vmag, vangle])
                obj_data["voltages"].append(v_list)

                if data_source_object_type == "Vsource":
                    obj_data["basekVs"].append(dss.Vsources.BasekV())
                if data_source_object_type == "Generator":
                    obj_data["basekVs"].append(dss.Generators.kV())

                # Power data
                sdata = dss.CktElement.Powers()
                s_list = []
                for idx in range(num_buses):
                    p = sum(sdata[idx * num_terminals_per_bus:(1 + idx) * num_terminals_per_bus:2])
                    q = sum(sdata[(idx * num_terminals_per_bus + 1):((1 + idx) * num_terminals_per_bus + 1):2])
                    s_list.extend([p, q])
                obj_data["powers"].append(s_list)

            dss.ActiveClass.Next()

        return obj_data
    elif data_source_object_type == "Bus":
         # Get the names
        obj_data["names"].extend(dss.Circuit.AllBusNames())
        for busname in obj_data["names"]:
            dss.Circuit.SetActiveBus(busname)
            obj_data["basekVs"].append(dss.Bus.kVBase())
            obj_data["voltages"].append(dss.Bus.VMagAngle())
            obj_data["phases"].append(dss.Bus.NumNodes())

        return obj_data
    else:
        return None


def generate_report(filename):
    import os

    from reportlab.pdfgen import canvas
    from reportlab.platypus.flowables import Flowable, KeepTogether
    from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, PageBreak
    from reportlab.lib.pagesizes import A4

    pg_w, pg_h = A4
    margin = 15
    tw = pg_w - 100  # Width of the tables
    story = []

    sections_dict = {
        "Summary": {
            "col1_names": [["Circuit name", "Total buses", "Total elements"]],
            "col1_widths": [tw * p / 100 for p in [20, 20, 20]],
            "col2_names": [["Total load P (kW)", "Total load Q (kVAr)", "Total delivered P (kW)", "Total delivered Q (kVAR)"]],
            "col2_widths": [tw * p / 100 for p in [20, 20, 20, 20]],
            "col3_names": [["Total P losses (kW)", "Losses (%)", "Total demanded Q (kVAr)"]],
            "col3_widths": [tw * p / 100 for p in [20, 20]]
        },
        "Vsources": {
            "col_names": [["Name", "Bus", "Voltage (kV)", "pu Volts", "V drop (%)"]],
            "col_widths": [tw * p / 100 for p in [12, 14, 15, 8, 15]]
        },
        "Buses": {
            "col_names": [["Name", "Node", "Base voltage (kV)", "Voltage (kV)", "pu Volts"]],
            "col_widths": [tw * p / 100 for p in [12, 8, 18, 18, 18]]
        },
        "Lines": {
            "col_names": [["Name", "Bus", "Voltage (kV)",
                           "Losses (kW)", "S (kVA)", "PF"]],
            "col_widths": [tw * p / 100 for p in [12, 14, 15, 10, 15, 10, 5]]
        },
        "Loads": {
            "col_names": [["Name", "Bus", "Voltage (kV)",
                           "P (kW)", "S (kVA)", "PF"]],
            "col_widths": [tw * p / 100 for p in [12, 14, 15, 14, 15, 10]]
        },
        "Generators": {
            "col_names": [["Name", "Bus", "Voltage (kV)", "pu Volts", "V drop (%)", "P (kW)", "S (kVA)", "PF"]],
            "col_widths": [tw * p / 100 for p in [12, 14, 15, 8, 15, 14, 15, 10]]
        },
        "Transformers": {
            "col_names": [["Name", "Bus", "Voltage (kV)",
                           "Losses (kW)", "S (kVA)", "PF"]],
            "col_widths": [tw * p / 100 for p in [12, 14, 18, 8, 15, 10, 15, 10, 5]]
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
            # self.line(50, 20, pg_w / 2 - 50, 20)
            # self.line(pg_w / 2 + 50, 20, pg_w - 50, 20)
            # Square
            # self.setLineWidth(30)
            # self.setStrokeColorRGB(255, 0, 0)
            # self.line(pg_w - 80, 20, pg_w - 20, 20)
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
            image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
            self.drawImage(os.path.join(image_path, "elephant.png"), 60, 2, 0.05 * 843,
                           0.05 * 478)
            self.drawImage(os.path.join(image_path, "opendss.jpg"), pg_w - 210, 0, 0.1 * 400, 0.1 * 291)

        def header(self):
            # Top line
            self.setLineWidth(30)
            self.setStrokeColorRGB(255, 0, 0)
            self.line(0, pg_h-20, pg_w - 100, pg_h-20)
            # Text 1
            # text_obj = self.beginText()
            # text_obj.setTextOrigin(pg_w - 100, pg_h - 25)
            # text_obj.setFont("Helvetica-Bold", 10)
            # text_obj.textLine("Typhoon HIL")
            # text_obj.textLine("OpenDSS")
            # text_obj.setFillColorRGB(255, 255, 255)
            # self.drawText(text_obj)
            # Text 2
            text_obj = self.beginText()
            text_obj.setFillColorRGB(255, 255, 255)
            text_obj.setTextOrigin(margin + 20, pg_h - 25)
            text_obj.setFont("Helvetica-Bold", 12)
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
            # Upper line
            #c.setLineWidth(2)
            #c.line(margin, 0, pg_w - 40 - margin, 0)
            # Title
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, 5, self.title.upper())
            # Bottom line
            c.setLineWidth(3)
            c.line(0, 0, 45 + len(self.title)*7.2, 0)

    def column_names(col_names, col_widths):
        LIST_STYLE = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 40),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8)
        ])
        t = Table(col_names, colWidths=col_widths,
                  style=LIST_STYLE, hAlign="LEFT", rowHeights=[25])
        return t

    def data_table(data, col_widths):
        LIST_STYLE = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 40),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8)
        ])
        t = Table(data, colWidths=col_widths, style=LIST_STYLE, hAlign="LEFT")
        return t

    def limit_name_chars(org_name):
        # Limit to 12 characters
        new_name = org_name[:6] + "…" + org_name[-6:]
        if len(org_name) > 12:
            return new_name
        else:
            return org_name

    def add_section(object_type):

        virtual_zero = 10**(-9)

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
            proc_line.append(round(l_kW / 1000, 2))
            proc_line.append(round(l_kVAr / 1000, 2))
            # Total delivered power
            proc_line.extend([-round(n, 2) for n in dss.Circuit.TotalPower()])
            # Losses
            proc_line.append(round(dss.Circuit.Losses()[0]/1000, 2))
            # Losses %
            try:
                proc_line.append(round(dss.Circuit.Losses()[0]/l_kW*100, 1))
            except ZeroDivisionError:
                l_kW = virtual_zero
                proc_line.append(round(dss.Circuit.Losses()[0] / l_kW * 100, 1))
            proc_line.append(round(dss.Circuit.Losses()[1]/1000, 2))

            return proc_line

        # Buses
        def proc_line_bus(data, idx):
            proc_line = []

            # Node voltages
            v_lines = []
            for phase in range(data.get("phases")[idx]):
                v_line = []
                basekV = data.get('basekVs')[idx]
                if phase == 0:
                    # Name
                    v_line.append(limit_name_chars(data.get("names")[idx]))
                else:
                    v_line.append("")
                # Node
                v_line.append(phase + 1)
                # BasekV
                if phase == 0:
                    v_line.append(f"{round(basekV, 2)}")
                else:
                    v_line.append("")
                v = f"{round(data.get('voltages')[idx][2*phase] / 1000, 2)} ∠ {round(data.get('voltages')[idx][2*phase + 1], 1)}°"
                v_line.append(v)
                v_pu = f"{round(data.get('voltages')[idx][2*phase] / 1000 / basekV, 3)}"
                v_line.append(v_pu)
                v_lines.append(v_line)

            return v_lines

        # Voltage source
        def proc_line_vsource(data, idx):
            proc_line = []
            # Name
            proc_line.append(limit_name_chars(data.get("names")[idx]))
            # Connected buses and voltages
            proc_line.append([limit_name_chars(bname) for bname in data.get("buses")[idx]][0])
            v1 = f"{round(data.get('voltages')[idx][0] / 1000, 2)} ∠ {round(data.get('voltages')[idx][1], 1)}°"
            proc_line.extend([v1])
            # Voltage drop
            pu_volts = data.get('voltages')[idx][0] / 1000 / data.get('basekVs')[idx]
            vdrop = round((1 - pu_volts) * 100, 2)
            pu_volts = round(pu_volts, 3)

            proc_line.extend([pu_volts, vdrop])
            return [proc_line]

        # Generator
        def proc_line_generator(data, idx):
            proc_line = []
            # Name
            proc_line.append(limit_name_chars(data.get("names")[idx]))
            # Connected buses and voltages
            proc_line.extend([limit_name_chars(bname) for bname in data.get("buses")[idx]])
            v1 = f"{round(data.get('voltages')[idx][0] / 1000, 2)} ∠ {round(data.get('voltages')[idx][1], 1)}°"
            proc_line.extend([v1])
            # Voltage drop
            pu_volts = data.get('voltages')[idx][0] / 1000 / data.get('basekVs')[idx]
            vdrop = round((1 - pu_volts) * 100, 2)
            pu_volts = round(pu_volts, 3)

            # Power and losses
            kW_losses = math.fabs(data.get("powers")[idx][0])
            kVA_processed = math.sqrt(data.get("powers")[idx][0] ** 2 + data.get("powers")[idx][1] ** 2)
            pf = kW_losses / kVA_processed

            proc_line.extend([pu_volts, vdrop, round(kW_losses, 2), round(kVA_processed, 2), round(pf, 2)])

            return [proc_line]

        # Transmission Line
        def proc_line_tl(data, idx):
            line1 = []
            line2 = [""]
            # Name
            line1.append(limit_name_chars(data.get("names")[idx]))
            # Connected buses and voltages
            line1.append([limit_name_chars(bname) for bname in data.get("buses")[idx]][0])
            v1 = f"{round(data.get('voltages')[idx][0] / 1000, 2)} ∠ {round(data.get('voltages')[idx][1], 1)}°"
            line1.extend([v1])
            line2.append([limit_name_chars(bname) for bname in data.get("buses")[idx]][1])
            v2 = f"{round(data.get('voltages')[idx][2] / 1000, 2)} ∠ {round(data.get('voltages')[idx][3], 1)}°"
            line2.extend([v2])
            # Power and losses
            kW_losses = math.fabs(math.fabs(data.get("powers")[idx][0]) - math.fabs(data.get("powers")[idx][2]))
            kVA_1 = math.sqrt(data.get("powers")[idx][0] ** 2 + data.get("powers")[idx][1] ** 2)
            kVA_2 = math.sqrt(data.get("powers")[idx][2] ** 2 + data.get("powers")[idx][3] ** 2)
            kVA_processed = math.fabs(math.fabs(kVA_1) - math.fabs(kVA_2))
            try:
                pf = kW_losses / kVA_processed
            except ZeroDivisionError:
                pf = 0
            line1.extend([round(kW_losses, 1), round(kVA_processed, 1), round(pf, 2)])
            return [line1, line2]

        # Load
        def proc_line_load(data, idx):
            proc_line = []
            # Name
            proc_line.append(limit_name_chars(data.get("names")[idx]))
            # Connected buses and voltages
            proc_line.extend([limit_name_chars(bname) for bname in data.get("buses")[idx]])
            v = f"{round(data.get('voltages')[idx][0] / 1000, 2)} ∠ {round(data.get('voltages')[idx][1], 1)}°"
            proc_line.extend([v])
            # Power and losses
            kW_losses = math.fabs(data.get("powers")[idx][0])
            kVA_processed = math.sqrt(data.get("powers")[idx][0] ** 2 + data.get("powers")[idx][1] ** 2)
            try:
                pf = kW_losses / kVA_processed
            except ZeroDivisionError:
                pf = 0
            proc_line.extend([round(kW_losses, 1), round(kVA_processed, 1), round(pf, 2)])
            return [proc_line]

        # Transformer
        def proc_line_transformer(data, idx):
            lines = []
            # One line for each bus
            connected_buses = data.get("buses")[idx]
            stepping = len(connected_buses)
            for b in connected_buses:
                line = []
                b_idx = connected_buses.index(b)
                if b_idx == 0:  # First line
                    # Name
                    line.append(limit_name_chars(data.get("names")[idx]))
                else:
                    line.append("")
                # Connected buses and voltages
                line.append(limit_name_chars(b))

                v = f"{round(data.get('voltages')[idx][2*b_idx] / 1000, 2)} ∠ " \
                    f"{round(data.get('voltages')[idx][2*b_idx+1], 1)}°"
                line.extend([v])
                if b_idx == 0:  # First line
                    # Power and losses
                    kW_losses = math.fabs(math.fabs(data.get("powers")[idx][0]) - math.fabs(data.get("powers")[idx][2]))
                    kVA_1 = math.sqrt(data.get("powers")[idx][b_idx+1] ** 2 + data.get("powers")[idx][b_idx+1] ** 2)
                    kVA_2 = math.sqrt(data.get("powers")[idx][b_idx+2] ** 2 + data.get("powers")[idx][b_idx+3] ** 2)
                    kVA_processed = math.fabs(math.fabs(kVA_1) - math.fabs(kVA_2))
                    try:
                        pf = kW_losses / kVA_processed
                    except ZeroDivisionError:
                        pf = 0
                    line.extend([round(kW_losses, 1), round(kVA_processed, 1), round(pf, 2)])
                lines.append(line)
            return lines

        # A function for each object type
        func_dict = {"Line": proc_line_tl, "Load": proc_line_load, "Vsource": proc_line_vsource,
                     "Transformer": proc_line_transformer, "Generator": proc_line_generator, "Bus": proc_line_bus}

        if object_type == "Summary":
            section_name = object_type
            col1_names = sections_dict.get(section_name).get("col1_names")
            col2_names = sections_dict.get(section_name).get("col2_names")
            col3_names = sections_dict.get(section_name).get("col3_names")
            col1_widths = sections_dict.get(section_name).get("col1_widths")
            col2_widths = sections_dict.get(section_name).get("col2_widths")
            col3_widths = sections_dict.get(section_name).get("col3_widths")
            # Header
            header = SectionHeader(section_name)
            story.append(header)
            # First piece of data
            cols_flow = column_names(col1_names, col1_widths)
            story.append(cols_flow)
            processed_data = [proc_summary()[:3]]
            data_flow = data_table(processed_data, col1_widths)
            story.append(data_flow)
            # Second piece of data
            cols_flow = column_names(col2_names, col2_widths)
            story.append(cols_flow)
            processed_data = [proc_summary()[3:7]]
            data_flow = data_table(processed_data, col2_widths)
            story.append(data_flow)
            # Third piece of data
            cols_flow = column_names(col3_names, col3_widths)
            story.append(cols_flow)
            processed_data = [proc_summary()[7:]]
            data_flow = data_table(processed_data, col3_widths)

            story.append(data_flow)
            story.append(PageBreak())
        else:
            # Object section
            section_name = object_type + "s" if not object_type[-1] == "s" else object_type + "es"
            col_names = sections_dict.get(section_name).get("col_names")
            col_widths = sections_dict.get(section_name).get("col_widths")
            # Header
            header = SectionHeader(section_name)
            cols_flow = column_names(col_names, col_widths)
            kt = KeepTogether([header, cols_flow])
            story.append(kt)

            data = dss_data_build(object_type)

            if data:
                processed_data = []
                for idx in range(len(data.get("names"))):
                    processed_data.extend(func_dict[object_type](data, idx))

                data_flow = data_table(processed_data, col_widths)
                story.append(data_flow)
                story.append(PageBreak())

    # Add the sections
    add_section("Summary")
    add_section("Bus")
    if not dss.Vsources.First() == 0:
        add_section("Vsource")
    if not dss.Generators.First() == 0:
        add_section("Generator")
    if not dss.Lines.First() == 0:
        add_section("Line")
    if not dss.Loads.First() == 0:
        add_section("Load")
    if not dss.Transformers.First() == 0:
        add_section("Transformer")


    try:
        if not os.path.isdir('reports'):
            os.makedirs('reports')

        doc = SimpleDocTemplate(f'reports/{filename}_powerflow_report.pdf', rightMargin=margin, leftMargin=margin, topMargin=40,
                                bottomMargin=50)
        doc.build(story, canvasmaker=NumberedCanvas)
        subprocess.Popen(f'{filename}_powerflow_report.pdf', cwd='reports', shell=True)

        return [True, ""]
    except PermissionError:
        # Report file is already open
        return [False, "Could not write the report to disk. Please close any previous reports."]


# FAULTSTUDY

def dss_faultstudy_data_build():
    obj_data = {"names": [],
                "iscs": [],
                }

    obj_data["names"].extend(dss.Circuit.AllBusNames())
    for busname in obj_data["names"]:
        dss.Circuit.SetActiveBus(busname)
        obj_data["iscs"].append(dss.Bus.Isc())
    return obj_data

def generate_faultstudy_report(filename):
    import os

    from reportlab.pdfgen import canvas
    from reportlab.platypus.flowables import Flowable, KeepTogether
    from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, PageBreak
    from reportlab.lib.pagesizes import A4

    pg_w, pg_h = A4
    margin = 15
    tw = pg_w - 100  # Width of the tables
    story = []

    sections_dict = {
        "Summary": {
            "col1_names": [["Circuit name", "Total buses", "Total elements"]],
            "col1_widths": [tw * p / 100 for p in [20, 20, 20]],
        },
        "Short-circuit currents": {
            "col_names": [["Bus name", "Phase A (kA)", "Phase B (kA)", "Phase C (kA)"]],
            "col_widths": [tw * p / 100 for p in [15, 15, 15]]
        },
        "node_to_ground": {
            "col_names": [["Node", "Current (A)", "Node 1 voltage (pu)", "Node 2 voltage (pu)", "Node 3 voltage (pu)"]],
            "col_widths": [tw * p / 100 for p in [12, 14, 15, 8]]
        },
        "adjacent": {
            "col_names": [["Node 1", "Node 2", "Current (A)", "Node 1 voltage (pu)", "Node 2 voltage (pu)", "Node 3 voltage (pu)"]],
            "col_widths": [tw * p / 100 for p in [12, 14, 15, 8, 15]]
        },
    }

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
            image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
            self.drawImage(os.path.join(image_path, "elephant.png"), 60, 2, 0.05 * 843,
                           0.05 * 478)
            self.drawImage(os.path.join(image_path, "opendss.jpg"), pg_w - 210, 0, 0.1 * 400, 0.1 * 291)

        def header(self):
            # Top line
            self.setLineWidth(30)
            self.setStrokeColorRGB(255, 0, 0)
            self.line(0, pg_h-20, pg_w - 100, pg_h-20)
            # Text 2
            text_obj = self.beginText()
            text_obj.setFillColorRGB(255, 255, 255)
            text_obj.setTextOrigin(margin + 20, pg_h - 25)
            text_obj.setFont("Helvetica-Bold", 12)
            text_obj.textLine("FAULT STUDY SIMULATION REPORT")
            self.drawText(text_obj)


    class SectionHeader(Flowable):

        def __init__(self, title, size=20):
            self.title = title
            self.size = size

        def wrap(self, *args):
            return (0, 40)

        def draw(self):
            c = self.canv
            # Upper line
            #c.setLineWidth(2)
            #c.line(margin, 0, pg_w - 40 - margin, 0)
            # Title
            c.setFont("Helvetica-Bold", 10)
            c.drawString(35, 5, self.title.upper())
            # Bottom line
            c.setLineWidth(3)
            c.line(0, 0, 45 + len(self.title)*7.2, 0)

    def column_names(col_names, col_widths):
        LIST_STYLE = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 40),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8)
        ])
        t = Table(col_names, colWidths=col_widths,
                  style=LIST_STYLE, hAlign="LEFT", rowHeights=[25])
        return t

    def data_table(data, col_widths):
        LIST_STYLE = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 40),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8)
        ])
        t = Table(data, colWidths=col_widths, style=LIST_STYLE, hAlign="LEFT")
        return t

    def limit_name_chars(org_name):
        # Limit to 12 characters
        new_name = org_name[:6] + "…" + org_name[-6:]
        if len(org_name) > 12:
            return new_name.upper()
        else:
            return org_name.upper()

    def add_section(object_type):

        virtual_zero = 10**(-9)

        # Summary
        def proc_summary():
            proc_line = []
            cktname = dss.Circuit.Name() if len(dss.Circuit.Name()) < 30 else dss.Circuit.Name()[:27] + "..."
            proc_line.append(cktname)
            proc_line.append(dss.Circuit.NumBuses())
            proc_line.append(dss.Circuit.NumCktElements())

            return proc_line

        def all_nodes(data, idx):
            proc_line = []
            # Name
            proc_line.append(limit_name_chars(data.get("names")[idx]))
            isc_list = data.get("iscs")[idx]
            for isc_idx in range(len(isc_list)//2):
                mod_isc = math.sqrt(isc_list[2*isc_idx]**2 + isc_list[2*isc_idx + 1]**2)
                proc_line.append(str(round(mod_isc/1000, 3)))
            return proc_line


        def node_to_ground(data, idx):
            pass

        def adjacent(data, idx):
            pass

         # A function for each object type
        func_dict = {"Short-circuit currents": all_nodes, "node_to_ground": node_to_ground, "adjacent": adjacent}

        if object_type == "Summary":
            section_name = object_type
            col1_names = sections_dict.get(section_name).get("col1_names")
            col1_widths = sections_dict.get(section_name).get("col1_widths")
            # Header
            header = SectionHeader(section_name)
            story.append(header)
            # First piece of data
            cols_flow = column_names(col1_names, col1_widths)
            story.append(cols_flow)
            processed_data = [proc_summary()[:3]]
            data_flow = data_table(processed_data, col1_widths)
            story.append(data_flow)

            #story.append(PageBreak())
        elif not object_type == "Bus":
            # # Object section
            section_name = object_type
            col_names = sections_dict.get(section_name).get("col_names")
            col_widths = sections_dict.get(section_name).get("col_widths")
            # # Header
            header = SectionHeader(section_name)
            cols_flow = column_names(col_names, col_widths)
            kt = KeepTogether([header, cols_flow])
            story.append(kt)

            data = dss_faultstudy_data_build()

            if data:
                processed_data = []
                for idx in range(len(data.get("names"))):
                    processed_data.append(func_dict[object_type](data, idx))

                data_flow = data_table(processed_data, col_widths)
                story.append(data_flow)
                story.append(PageBreak())

    # Add the sections
    add_section("Summary")
    add_section("Short-circuit currents")

    try:
        if not os.path.isdir('reports'):
            os.makedirs('reports')

        doc = SimpleDocTemplate(f"reports/{filename}_faultstudy_report.pdf", rightMargin=margin, leftMargin=margin, topMargin=40, bottomMargin=50)
        doc.build(story, canvasmaker=NumberedCanvas)
        subprocess.Popen(f"{filename}_faultstudy_report.pdf", cwd='reports', shell=True)

        return [True, ""]
    except PermissionError:
        # Report file is already open
        return [False, "Could not write the report to disk. Please close any previous reports."]

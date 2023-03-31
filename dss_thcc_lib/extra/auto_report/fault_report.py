import math

from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable, KeepTogether
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, PageBreak, Spacer
from reportlab.lib.pagesizes import A4

import opendssdirect as dss
from .report_functions import *


def dss_data_build(dss_data_dict):

    for obj_type in ALL_OBJ_TYPES:

        dss_data_dict[obj_type] = {}

        obj_data = {"names": [],
                    "iscs": [],
                    }

        obj_data["names"].extend(dss.Circuit.AllBusNames())
        for busname in sorted(obj_data["names"]):
            dss.Circuit.SetActiveBus(busname)
            obj_data["iscs"].append(dss.Bus.Isc())

        dss_data_dict[obj_type].update({busname: obj_data})


def generate_report(mdlfile):
    import os
    filename = pathlib.Path(mdlfile).stem

    pg_w, pg_h = A4
    margin = 15
    tw = pg_w - 100  # Width of the tables
    story = []
    dss_data_dict = {}

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
            "col_names": [["Node 1", "Node 2", "Current (A)", "Node 1 voltage (pu)", "Node 2 voltage (pu)",
                           "Node 3 voltage (pu)"]],
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
            text_obj.setFont("Helvetica-Bold", 10)
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
            c.setFont("Helvetica-Bold", 11)
            c.drawString(30, 5, self.title.upper())
            # Bottom line
            c.setLineWidth(3)
            c.line(0, -2, 45 + len(self.title) * 7.2, -2)

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
                            ratio = float(row_list[4].split("∠")[0]) / rating
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
                proc_line.append(str(round_mod(mod_isc/1000, 3)))
            return proc_line


        def node_to_ground(data, idx):
            pass

        def adjacent(data, idx):
            pass

         # A function for each object type
        func_dict = {"Short-circuit currents": all_nodes, "node_to_ground": node_to_ground, "adjacent": adjacent}

        if object_type == "Summary":
            section_name = object_type
            spacer = Spacer(0, 20)
            col1_names = sections_dict.get(section_name).get("col1_names")
            col1_widths = sections_dict.get(section_name).get("col1_widths")
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

            story.append(PageBreak())

        else:
            # Header
            def create_header(after=False):
                # Object section
                section_name = object_type
                col_names = sections_dict.get(section_name).get("col_names")
                col_widths = sections_dict.get(section_name).get("col_widths")
                cols_underlines = ColumnTitleUnderlines(col_widths, col_names[0])
                if not after:
                    header = SectionHeader(section_name)
                    spacer = Spacer(0, 20)
                cols_flow = column_names(col_names, col_widths)
                if not after:
                    kt = [header, spacer, cols_flow, cols_underlines]
                else:
                    kt = [cols_flow, cols_underlines]
                return col_widths, kt

            col_widths, kt = create_header()
            story.append(KeepTogether(kt))

            row_count = 0
            iter_count = 0
            if dss_data_dict.get(object_type):
                iter_max = len(dss_data_dict.get(object_type))
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

    # Add the sections
    add_section("Summary")
    add_section("Short-circuit currents")

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
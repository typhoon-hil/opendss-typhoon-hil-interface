import json
import os
import time
import pathlib
import numpy as np
import ast

def return_bus_connections(elem_name, nodes, buses_dict, num_buses, phases, neutral=False):
    """ Returns a list of strings that define how the element is connected to buses.
    Will return for a 2-phase element connected to 3 AB-type buses and one AC,
    with the 1 and 2 wires swapped on busname3:
    [busAB1.1.2, busAB2.1.2, busAB3.2.1, busAC4.1.3]"""

    # List of characters according to the number of Phases: 1-A, 2-B, 3-C, 4-D, etc.
    # The component terminals in TSE must follow the same naming scheme
    phase_letters = [chr(65 + n) for n in range(phases)]
    buses = []
    buses_idx_order = []

    # Create a variable-sized list (depends on the number of phases) that contains
    # lists of nodes per bus group - e.g. [[n_A1,n_B1],[n_A2,n_B2],[n_A3,n_B3]]
    if neutral:  # Neutral should be true only if it is going to be connected to a bus (floating neutral = False)
        nodes_lists = [[nodes.get(str(phase_letters[ph]) + str(b + 1)) for ph in range(phases-1)] for b in
                       range(num_buses)]
        for busgroup in nodes_lists:
            busgroup.append(nodes.get("N"))
    else:
        nodes_lists = [[nodes.get(str(phase_letters[ph]) + str(b + 1)) for ph in range(phases)] for b in range(num_buses)]

    for bus, bus_nodedict in buses_dict.items():
        # bus_nodedict is the dictionary of the current bus' nodes
        for idx in range(num_buses):
            for bn in bus_nodedict.values():
                # Check every node of this bus for a connection with the element
                if bn in nodes_lists[idx]:
                    # If the element's bus group is connected to bus
                    try:
                        bus_terminals = list(bus_nodedict.keys())
                        bus_letters = list(set(terminal[0] for terminal in bus_terminals))  # [A, B, C], [A, C], etc.

                        node_numbers = []
                        for node in nodes_lists[idx]:
                            if not node in bus_nodedict.values():
                                # There are problems with the connection
                                raise ValueError

                            for phase in range(len(bus_letters)):
                                letter = bus_letters[phase]
                                if node == bus_nodedict.get(letter + "1") or node == bus_nodedict.get(letter + "2"):
                                    # In the current implementation, all buses are actually 3-phase
                                    node_numbers.append({"A": "1", "B": "2", "C": "3"}.get(letter))
                                    break
                                elif node == bus_nodedict.get("0"):
                                    node_numbers.append("0")
                                    break

                        if not len(node_numbers) == len(nodes_lists[idx]):
                            raise Exception(
                                f"Please check the connection between {elem_name} and {bus} for short circuits.")

                        buses.append(f'{str(bus)}.' + f'{".".join(node_numbers)}')
                        buses_idx_order.append(idx)
                        break

                    except ValueError:
                        raise Exception(
                            f"Not every Group {idx + 1} terminal of the {elem_name} element are connected to the same Bus.")

    zipped_for_reordering = zip(buses_idx_order, buses)
    buses = [b for _, b in sorted(zipped_for_reordering, key=lambda pair: pair[0])]

    if not len(buses) == len(nodes_lists):
        raise Exception(
            f"Make sure all {elem_name} terminals are connected to a bus.")
    return buses


class Element:
    ''' Element is the main class. Circuit elements inherit from this class and
    must have string-type method arguments. '''

    def __init__(self, name):
        self.name = name
        self.value = self.params = self.model = ""

    def identifier(self):
        # Part of the syntax line construction of most elements.
        return self.type + "." + self.name  # OpenDSS Example: Vsource.Grid1

    @staticmethod
    def pick_correct_subclass(elem_type, elem_data):
        # Instantiates the appropriate class depending on elem_type.
        if elem_type == "BUS":
            return Bus(elem_type, elem_data.get("name"), elem_data.get("nodes"))
        if elem_type == "VSOURCE":
            return Vsource(elem_type, **elem_data)
        elif elem_type == "ISOURCE":
            return Isource(elem_type, **elem_data)
        elif elem_type == "FAULT":
            return Fault(elem_type, **elem_data)
        elif elem_type == "CAPACITOR":
            return Capacitor(elem_type, **elem_data)
        elif elem_type == "LINE":
            return Line(elem_type, **elem_data)
        elif elem_type == "SWLINE":
            return Switch(elem_type, **elem_data)
        elif elem_type == "CSWLINE":
            return Switch(elem_type, **elem_data)
        elif elem_type == "TRANSFORMER1P":
            return SinglePhaseTransformer(elem_type, **elem_data)
        elif elem_type == "TRANSFORMER3P":
            return ThreePhaseTransformer(elem_type, **elem_data)
        elif elem_type == "GICTRANSFORMER":
            return GICTransformer(elem_type, **elem_data)
        elif elem_type == "GICLINE":
            return GICLine(elem_type, **elem_data)
        elif elem_type == "LOAD":
            return Load(elem_type, **elem_data)
        elif elem_type == "GENERATOR":
            return Generator(elem_type, **elem_data)
        elif elem_type == "INDMACH012":
            return InductionMachine012(elem_type, **elem_data)
        elif elem_type == "STORAGE":
            return Storage(elem_type, **elem_data)
        elif elem_type == "CAPCONTROL":
            return CapControl(elem_type, **elem_data)
        elif elem_type == "REGCONTROL":
            return RegControl(elem_type, **elem_data)
        elif elem_type == "ENERGYMETER":
            return EnergyMeter(elem_type, **elem_data)
        elif elem_type == "MONITOR":
            return Monitor(elem_type, **elem_data)
        elif elem_type == "LOADSHAPE":
            return LoadShape(elem_type, **elem_data)


################################################################################

# Buses
class Bus(Element):
    def __init__(self, type, name, nodes):
        self.type = type
        self.control = False
        self.nodes = nodes
        super().__init__(name)

# Two-terminal elements
class TwoTerminal(Element):
    def __init__(self, name, buses, parameters):
        self.buses = buses
        self.control = False
        self.parameters = parameters
        super().__init__(name)

    def dss_line(self):
        self.params = [f'{param}={self.parameters.get(param)}' for param in self.parameters]
        if self.type == "LOAD":
            if self.TSeries == "1" and self.ldshp_exist == "0":
                if self.dssinterval == "0":
                    return (
                        f'new LoadShape.{str(self.name + "profile")}{" npts=" + str(self.loadshape.get("dssnpts"))}{" interval=" + str(self.loadshape.get("dssT"))}\n'
                        f'~ mult={str(self.loadshape.get("S_Ts"))}\n'
                        f'~ mult={str(self.loadshape.get("T_Ts"))}\n'
                        f'new {self.identifier()} Bus1={self.buses[0]}{" Bus2=" + self.buses[1] if len(self.buses) == 2 else ""} {" ".join(self.params)}\n')
                else:
                    return (
                        f'new LoadShape.{str(self.name + "profile")}{" npts=" + str(self.loadshape.get("dssnpts"))}{" interval=" + str(self.loadshape.get("dssT"))}\n'
                        f'~ mult={str(self.loadshape.get("S_Ts"))}\n'
                        f'new {self.identifier()} Bus1={self.buses[0]}{" Bus2=" + self.buses[1] if len(self.buses) == 2 else ""} {" ".join(self.params)}\n')

            else:
                return f'new {self.identifier()} Bus1={self.buses[0]}{" Bus2=" + self.buses[1] if len(self.buses) == 2 else ""} {" ".join(self.params)}\n'

        elif self.type == "GENERATOR":
            if self.TSeries == "1" and self.ldshp_exist == "0":
                if self.dssinterval == "0":
                    return (
                        f'new LoadShape.{str(self.name + "profile")}{" npts=" + str(self.loadshape.get("dssnpts"))}{" interval=" + str(self.loadshape.get("dssT"))}\n'
                        f'~ mult={str(self.loadshape.get("S_Ts"))}\n'
                        f'~ hour={str(self.loadshape.get("T_Ts"))}\n'
                        f'new {self.identifier()} Bus1={self.buses[0]}{" Bus2=" + self.buses[1] if len(self.buses) == 2 else ""} {" ".join(self.params)}\n')
                else:
                    return (
                        f'new LoadShape.{str(self.name + "profile")}{" npts=" + str(self.loadshape.get("dssnpts"))}{" interval=" + str(self.loadshape.get("dssT"))}\n'
                        f'~ mult={str(self.loadshape.get("S_Ts"))}\n'
                        f'new {self.identifier()} Bus1={self.buses[0]}{" Bus2=" + self.buses[1] if len(self.buses) == 2 else ""} {" ".join(self.params)}\n')

            else:
                return f'new {self.identifier()} Bus1={self.buses[0]}{" Bus2=" + self.buses[1] if len(self.buses) == 2 else ""} {" ".join(self.params)}\n'

        else:
            return f'new {self.identifier()} Bus1={self.buses[0]}{" Bus2=" + self.buses[1] if len(self.buses) == 2 else ""} {" ".join(self.params)}\n'

class Vsource(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):

        self.type = elem_type
        self.control = False
        self.ground_connected = init_data.pop("ground_connected")
        self.phases = 3
        self.tse_component = init_data.pop("tse_comp")
        self.ldshp = init_data.pop("loadshape_lib")

        init_data.pop("global_basefreq")

        if self.ground_connected == "False":
            self.num_buses = 2
        else:
            self.num_buses = 1

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)

        super().__init__(name, self.buses, init_data)


class Isource(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):

        self.type = elem_type
        self.control = False
        self.phases = 3
        self.num_buses = 1
        self.tse_component = init_data.pop("tse_comp")
        self.ldshp = init_data.pop("loadshape_lib")

        init_data.pop("global_basefreq")

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)

        super().__init__(name, self.buses, init_data)

class Capacitor(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):

        self.type = elem_type
        self.control = False
        self.phases = 3

        self.parameters = {"kv": init_data['Kv'],
                           "kvar": init_data['Kvar'],
                           "BaseFreq": init_data['BaseFreq']}

        if init_data['tp_connection'] == "Y" or init_data['tp_connection'] == "Y-grounded":
            self.num_buses = 1
        elif init_data['tp_connection'] == "Δ":
            self.num_buses = 1
            self.parameters.update({"conn": "delta"})
        elif init_data['tp_connection'] == "Series":
            self.num_buses = 2



        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)

        if init_data['tp_connection'] == "Y":
            self.buses.append(f'nbus_{name}.4.4.4')
            self.num_buses = 2

        super().__init__(name, self.buses, self.parameters)

class Line(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):

        self.type = elem_type
        self.name = name
        self.control = False
        self.init_data = init_data

        if self.init_data['input_type'] == "LineCode":
            self.parameters = {"LineCode": self.init_data['selected_object'],
                               "Length": self.init_data['Length'],
                               "BaseFreq": self.init_data['BaseFreq']}
        elif self.init_data['input_type'] == "Matrix":
            for p in ["rmatrix", "xmatrix", "cmatrix"]:
                self.init_data[p] = self.convert_matrix_format(self.init_data[p])
            self.parameters = {k: v for k, v in self.init_data.items() if
                               k in ["Length", "BaseFreq", "rmatrix", "xmatrix", "cmatrix"]}
        else:
            self.parameters = {k: v for k, v in self.init_data.items() if
                           k in ["Length", "BaseFreq", "R1", "R0", "X1", "X0", "C1", "C0"]}
        self.num_buses = 2
        self.phases = 3

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)

        super().__init__(name, self.buses, self.parameters)

    def convert_matrix_format(self, input_matrix):
        try:
            mat = ast.literal_eval(input_matrix)
            if type(mat) == list:
                rows = []
                for row in mat:
                    r = [str(e) for e in row]
                    conv_row = " ".join(r)
                    rows.append(conv_row)
                converted_matrix = '[' + " | ".join(rows) + ']'
            return converted_matrix
        except ValueError:
            return input_matrix
        except SyntaxError:
            return input_matrix
        except TypeError:
            raise Exception(f"Invalid matrix input format in component {self.name}")

class Fault(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):

        self.type = elem_type
        self.control = False
        self.num_buses = 1
        self.phases = 3

        self.parameters = {"R":init_data['resistance'], "phases":str(self.phases)}

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)

        self.fault_type = init_data["type"]

        if self.fault_type == "A-B-C-GND":
            self.buses.append(f'fbus_{name}.0.0.0')
        elif self.fault_type == "A-B-GND":
            self.buses.append(f'fbus_{name}.0.0.3')
        elif self.fault_type == "A-C-GND":
            self.buses.append(f'fbus_{name}.0.2.0')
        elif self.fault_type == "B-C-GND":
            self.buses.append(f'fbus_{name}.1.0.0')
        elif self.fault_type == "A-GND":
            self.buses.append(f'fbus_{name}.0.2.3')
        elif self.fault_type == "B-GND":
            self.buses.append(f'fbus_{name}.1.0.3')
        elif self.fault_type == "C-GND":
            self.buses.append(f'fbus_{name}.1.2.0')
        elif self.fault_type == "A-B":
            self.buses.append(f'fbus_{name}.1.1.3')
        elif self.fault_type == "A-C":
            self.buses.append(f'fbus_{name}.1.2.1')
        elif self.fault_type == "B-C":
            self.buses.append(f'fbus_{name}.1.2.2')
        elif self.fault_type == "A-B-C":
            self.buses.append(f'fbus_{name}.1.1.1')
        elif self.fault_type == "None":
            self.buses.append(f'fbus_{name}.1.2.3')

        super().__init__(name, self.buses, self.parameters)

class Switch(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):

        self.type = "LINE"
        self.control = False
        self.parameters = {"Switch":"true"}

        if init_data.get("switch_status") == "True":
            self.open_or_close = "Close"
        elif init_data.get("initial_state") == "on":
            self.open_or_close = "Close"
        else:
            self.open_or_close = "Open"
        self.num_buses = 2
        self.phases = 3

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)

        super().__init__(name, self.buses, self.parameters)

    def dss_line(self):
        return f"{super().dss_line()}{self.open_or_close} {self.identifier()}\n"


class SinglePhaseTransformer(Element):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):
        self.type = "TRANSFORMER"
        self.control = False
        self.init_data = init_data
        self.num_windings = int(init_data['num_windings'])
        self.phases = 2

        self.regcontrol_on = self.init_data['regcontrol_on']
        if self.regcontrol_on == "True":
            regcontrol_parameter_names = ["ctrl_winding", "vreg", "ptratio", "band", "delay"]
            self.regcontrol_parameters = {par: self.init_data[par] for par in regcontrol_parameter_names}
            regctrl_number = self.regcontrol_parameters.pop("ctrl_winding")[-1]
            self.regcontrol_parameters["vreg"] = self.regcontrol_parameters["vreg"]
            self.regcontrol_parameters["winding"] = regctrl_number
            self.regcontrol_parameters["maxtapchange"] = "1"
            self.control = True
            self.control_iters = int(self.init_data.get("numtaps"))
            self.tap_parameters = {"wdg": regctrl_number,
                                   "maxtap": self.init_data.get("maxtap"),
                                   "mintap": self.init_data.get("mintap"),
                                   "numtaps": self.init_data.get("numtaps")}

        parameter_names = ["KVs", "KVAs", "percentRs", "XscArray", "Basefreq", "percentNoloadloss", "percentimag"]
        self.parameters = {par: self.init_data[par] for par in parameter_names}
        # Update parameter names to match OpenDSS
        self.parameters[r"%Rs"] = self.parameters.pop("percentRs")
        self.parameters[r"%Noloadloss"] = self.parameters.pop("percentNoloadloss")
        self.parameters[r"%imag"] = self.parameters.pop("percentimag")
        super().__init__(name)

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_windings, self.phases)
        self.buses = ", ".join([bus_conn for bus_conn in self.buses])

    def dss_line(self):
        if self.regcontrol_on == "True":
            regctrl_name = f"regcontrol_{self.name}"
            regcontrol_pars = [f'{param}={self.regcontrol_parameters.get(param)}' for param in self.regcontrol_parameters]
            reg_ctrl_line = f'New RegControl.{regctrl_name} Transformer={self.name} {" ".join(regcontrol_pars)}\n'
            tap_pars = [f'{param}={self.tap_parameters.get(param)}' for param in self.tap_parameters]
        else:
            reg_ctrl_line = ""
            tap_pars = ""

        params = [f'{param}={self.parameters.get(param)}' for param in self.parameters]
        return f'new {self.identifier()} phases=1 windings={self.num_windings} ' \
               f'Buses=[{self.buses}] ' \
               f'{" ".join(params)}\n{" ".join(tap_pars)}\n{reg_ctrl_line}'

class ThreePhaseTransformer(Element):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):
        self.type = "TRANSFORMER"
        self.control = False
        self.phases = 3
        self.init_data = init_data
        self.num_windings = int(self.init_data['num_windings'])

        self.regcontrol_on = self.init_data['regcontrol_on']
        if self.regcontrol_on == "True":
            regcontrol_parameter_names = ["ctrl_winding", "vreg", "ptratio", "band", "delay"]
            self.regcontrol_parameters = {par: self.init_data[par] for par in regcontrol_parameter_names}
            regctrl_number = self.regcontrol_parameters.pop("ctrl_winding")[-1]
            self.regcontrol_parameters["winding"] = regctrl_number
            self.regcontrol_parameters["maxtapchange"] = "1"
            self.control = True
            self.control_iters = int(self.init_data.get("numtaps"))
            self.tap_parameters = {"wdg": regctrl_number,
                                   "maxtap": self.init_data.get("maxtap"),
                                   "mintap": self.init_data.get("mintap"),
                                   "numtaps": self.init_data.get("numtaps")}

        parameter_names = ["KVs", "KVAs", "percentRs", "XscArray", "Basefreq", "percentNoloadloss", "percentimag"]

        self.parameters = {par: self.init_data[par] for par in parameter_names}

        # Update parameter names to match OpenDSS
        self.parameters[r"%Rs"] = self.parameters.pop("percentRs")
        self.parameters[r"%Noloadloss"] = self.parameters.pop("percentNoloadloss")
        self.parameters[r"%imag"] = self.parameters.pop("percentimag")
        super().__init__(name)

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_windings, self.phases)
        self.buses = ", ".join([bus_conn for bus_conn in self.buses])

        conn_dict = {"Y": "wye", "Δ": "delta"}
        self.connections = []
        for idx, w in enumerate(["prim", "sec1", "sec2", "sec3"][:self.num_windings]):
            this_connection = conn_dict[init_data[w + "_conn"]]
            self.connections.append(this_connection)
            if self.regcontrol_on == "True":
                if idx + 1 == int(regctrl_number):
                    if this_connection == "delta":
                        self.regcontrol_parameters["vreg"] = round(float(self.regcontrol_parameters["vreg"])*np.sqrt(3), 2)

        self.connections = ", ".join([conn for conn in self.connections])


    def dss_line(self):
        if self.regcontrol_on == "True":
            regctrl_name = f"regcontrol_{self.name}"
            regcontrol_pars = [f'{param}={self.regcontrol_parameters.get(param)}' for param in self.regcontrol_parameters]
            reg_ctrl_line = f'New RegControl.{regctrl_name} Transformer={self.name} {" ".join(regcontrol_pars)}\n'
            tap_pars = [f'{param}={self.tap_parameters.get(param)}' for param in self.tap_parameters]
        else:
            reg_ctrl_line = ""
            tap_pars = ""

        params = [f'{param}={self.parameters.get(param)}' for param in self.parameters]
        return f'new {self.identifier()} phases={self.phases} windings={self.num_windings} ' \
               f'Buses=[{self.buses}] Conns=[{self.connections}] ' \
               f'{" ".join(params)}\n{" ".join(tap_pars)}\n{reg_ctrl_line}'


class Load(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):
        self.init_data = init_data
        self.gnd = self.init_data["ground_connected"] == "True"

        self.phases = int(init_data["phases"])
        self.type = elem_type
        self.control = False
        self.name = name
        self.ldshp_exist = "0"
        self.dssinterval = init_data["dssT"]
        self.ldshp = init_data["loadshape_lib"]
        if self.ldshp.is_file():
            f = open(self.ldshp, 'r')
            lines = f.readlines()
            for line in lines:
                if "new loadshape." in line:
                    line_elem = line.split()
                    # if str(init_data["loadshape_lib"]) in line_elem:
                    for wrd in line_elem:
                        if "loadshape." in wrd:
                            if str(init_data["loadshape_name"]) == str(wrd.split(".")[1]):
                                self.ldshp_exist = "1"


        self.TSeries = "0"
        if init_data["dssT"] == "0":
            self.loadshape = {k: v for k, v in self.init_data.items() if
                              k in ["S_Ts", "dssnpts", "dssT", "T_Ts"]}
        else:
            self.loadshape = {k: v for k, v in self.init_data.items() if
                              k in ["S_Ts", "dssnpts", "dssT"]}

        if self.init_data["Pow_ref_s"] == "Time Series":
            self.TSeries = "1"
            self.parameters = {k: v for k, v in self.init_data.items() if
                               k in ["phases", "kV", "pf", "model", "conn", "kVA", "basefreq"]}
            if self.ldshp_exist == "1":
                self.parameters.update({"daily": str(init_data["loadshape_name"])})
            else:
                self.parameters.update({"daily": str(self.name + "profile")})

        else:
            self.parameters = {k: v for k, v in self.init_data.items() if
                               k in ["phases", "kV", "pf", "model", "conn", "kVA", "basefreq"]}

        self.neutral = False
        if self.init_data["phases"] == "3":
            if not self.gnd:
                self.parameters["Rneut"] = "-1"
            self.num_buses = 1
        elif self.init_data["phases"] == "1":
            if self.gnd:
                self.num_buses = 1
            else:
                self.num_buses = 1
                self.phases = 2
        self.parameters["phases"] = self.phases
        # Update parameter names to match OpenDSS
        if self.gnd and self.init_data["phases"] == "1":
            self.parameters[r"kV"] = str(float(self.parameters.pop("kV")) / 3 ** (0.5))
        else:
            self.parameters[r"kV"] = self.parameters.pop("kV")

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases, self.neutral)

        super().__init__(name, self.buses, self.parameters)


class Generator(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):
        self.init_data = init_data
        self.type = elem_type
        self.control = False
        self.name = name
        self.ldshp_exist = "0"
        self.dssinterval = init_data["dssT"]
        self.ldshp = init_data["loadshape_lib"]
        if self.ldshp.is_file():
            f = open(self.ldshp, 'r')
            lines = f.readlines()
            for line in lines:
                if "new loadshape." in line:
                    line_elem = line.split()
                    # if str(init_data["loadshape_lib"]) in line_elem:
                    for wrd in line_elem:
                        if "loadshape." in wrd:
                            if str(init_data["loadshape_name"]) == str(wrd.split(".")[1]):
                                self.ldshp_exist = "1"



        self.TSeries = "0"
        if init_data["dssT"] == "0":
            self.loadshape = {k: v for k, v in self.init_data.items() if
                              k in ["S_Ts", "dssnpts", "dssT", "T_Ts"]}
        else:
            self.loadshape = {k: v for k, v in self.init_data.items() if
                              k in ["S_Ts", "dssnpts", "dssT"]}

        if self.init_data["gen_ts_en"] == "True":
            self.TSeries = "1"
            self.parameters = {k: v for k, v in init_data.items() if
                               k in ["Phases", "kv", "kw", "pf", "model", "Xd", "Xdp", "Xdpp", "XRdp", "H", "basefreq"]}
            if self.ldshp_exist == "1":
                self.parameters.update({"daily": str(init_data["loadshape_name"])})
            else:
                self.parameters.update({"daily": str(self.name + "profile")})
        else:
            self.parameters = {k: v for k, v in init_data.items() if
                               k in ["Phases", "kv", "kw", "pf", "model", "Xd", "Xdp", "Xdpp", "XRdp", "H", "basefreq"]}

        self.num_buses = 1
        self.phases = 3

        if init_data["tse_comp"] == "VSConverter":
            if init_data["model"] == "2":
                self.parameters = {k: v for k, v in init_data.items() if
                                 k in ["Frequency", "basekv", "Angle", "pu", "r1", "r0", "x1", "x0"]}
                self.type = "VSOURCE"

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)
        super().__init__(name, self.buses, self.parameters)


class Storage(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):
        self.type = elem_type
        self.control = False
        self.init_data = init_data
        self.name = name
        self.num_buses = 1
        self.phases = 3

        self.parameters = {k: v for k, v in init_data.items() if
                           k in ["kv", "kwhrated", "kwrated", "pct_effcharge", "snap_status",
                                 "pct_effdischarge", "pct_idlingkw", "pct_idlingkvar", "pct_reserve", "pct_stored",
                                 "chargetrigger", "dischargetrigger", "basefreq", "kva"]}

        self.parameters["phases"] = str(self.phases)
        self.parameters["dispmode"] = self.init_data['dispatch_p']
        self.parameters["%effcharge"] = self.parameters.pop('pct_effcharge')
        self.parameters["%effdischarge"] = self.parameters.pop('pct_effdischarge')
        self.parameters["%idlingkw"] = self.parameters.pop('pct_idlingkw')
        self.parameters["%idlingkvar"] = self.parameters.pop('pct_idlingkvar')
        self.parameters["%reserve"] = self.parameters.pop('pct_reserve')
        self.parameters["%stored"] = self.parameters.pop('pct_stored')
        self.parameters["state"] = self.parameters.pop('snap_status')
        self.parameters["daily"] = self.init_data['loadshape_name']

        if self.parameters.get("dispmode") == "Default":
            self.parameters["%discharge"] = self.init_data['pct_discharge']
            self.parameters["%charge"] = self.init_data['pct_charge']
        else:
            self.parameters.pop('chargetrigger')
            self.parameters.pop('dischargetrigger')

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)
        super().__init__(name, self.buses, self.parameters)

    def dss_line(self):
        return super().dss_line()


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
                                if node == bus_nodedict.get(letter + "1"):
                                    # In the current implementation, all buses are actually 3-phase
                                    node_numbers.append({"A": "1", "B": "2", "C": "3"}.get(letter))

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


################################################################################

# Buses
class Bus(Element):
    def __init__(self, type, name, nodes):
        self.type = type
        self.nodes = nodes
        super().__init__(name)


# Two-terminal elements
class TwoTerminal(Element):
    def __init__(self, name, buses, parameters):
        self.buses = buses
        self.parameters = parameters
        super().__init__(name)

    def dss_line(self):
        self.params = [f'{param}={self.parameters.get(param)}' for param in self.parameters]
        return f'new {self.identifier()} Bus1={self.buses[0]}{" Bus2=" + self.buses[1] if len(self.buses) == 2 else ""} {" ".join(self.params)}\n'


class Vsource(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):

        self.type = elem_type
        self.ground_connected = init_data.pop("ground_connected")
        self.phases = 3

        if self.ground_connected == "False":
            self.num_buses = 2
        else:
            self.num_buses = 1

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)

        super().__init__(name, self.buses, init_data)


class Isource(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):

        self.type = elem_type
        self.phases = 3
        self.num_buses = 1

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)

        super().__init__(name, self.buses, init_data)

class Line(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):

        self.type = elem_type
        self.parameters = {k: v for k, v in init_data.items() if
                           k in ["Length", "BaseFreq", "R1", "R0", "X1", "X0", "C1", "C0"]}
        self.num_buses = 2
        self.phases = 3

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)

        super().__init__(name, self.buses, self.parameters)

class Fault(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):

        self.type = elem_type
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
        self.num_windings = int(init_data['num_windings'])
        self.phases = 2
        parameter_names = ["KVs", "KVAs", "percentRs", "XscArray", "Basefreq", "percentNoloadloss", "percentimag"]
        self.parameters = {par: init_data[par] for par in parameter_names}
        # Update parameter names to match OpenDSS
        self.parameters[r"%Rs"] = self.parameters.pop("percentRs")
        self.parameters[r"%Noloadloss"] = self.parameters.pop("percentNoloadloss")
        self.parameters[r"%imag"] = self.parameters.pop("percentimag")
        super().__init__(name)

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_windings, self.phases)
        self.buses = ", ".join([bus_conn for bus_conn in self.buses])

    def dss_line(self):
        self.params = [f'{param}={self.parameters.get(param)}' for param in self.parameters]
        return f'new {self.identifier()} phases={self.phases-1} windings={self.num_windings} Buses=[{self.buses}] {" ".join(self.params)}\n'


class ThreePhaseTransformer(Element):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):
        self.type = "TRANSFORMER"
        self.phases = 3
        self.num_windings = int(init_data['num_windings'])
        parameter_names = ["KVs", "KVAs", "percentRs", "XscArray", "Basefreq", "percentNoloadloss", "percentimag"]
        self.parameters = {par: init_data[par] for par in parameter_names}
        # Update parameter names to match OpenDSS
        self.parameters[r"%Rs"] = self.parameters.pop("percentRs")
        self.parameters[r"%Noloadloss"] = self.parameters.pop("percentNoloadloss")
        self.parameters[r"%imag"] = self.parameters.pop("percentimag")
        super().__init__(name)

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_windings, self.phases)
        self.buses = ", ".join([bus_conn for bus_conn in self.buses])

        conn_dict = {"Y": "wye", "Δ": "delta"}
        self.connections = [conn_dict[init_data[a]] for a in
                            [w + "_conn" for w in ["prim", "sec1", "sec2", "sec3"][:self.num_windings]]]
        self.connections = ", ".join([conn for conn in self.connections])

    def dss_line(self):
        self.params = [f'{param}={self.parameters.get(param)}' for param in self.parameters]
        return f'new {self.identifier()} phases={self.phases} windings={self.num_windings} Buses=[{self.buses}] Conns=[{self.connections}] {" ".join(self.params)}\n'


class Load(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):
        self.init_data = init_data
        self.gnd = self.init_data["ground_connected"] == "True"

        self.phases = int(init_data["phases"])
        self.type = elem_type
        self.name = name
        self.parameters = {k: v for k, v in self.init_data.items() if
                           k in ["phases", "kV", "pf", "model", "conn", "kVA", "basefreq"]}

        if self.init_data["phases"] == "3":
            if not self.gnd:
                self.parameters["Rneut"] = "-1"
            self.neutral = False  # self.neutral means that there is a connection from N to a phase
            self.num_buses = 1
        elif self.init_data["phases"] == "1":
            if self.gnd:
                self.num_buses = 1
                self.neutral = False
            else:
                self.num_buses = 1
                self.phases = 2  # Neutral will be connected to a phase
                self.neutral = True

        # Update parameter names to match OpenDSS
        if self.gnd and self.init_data["phases"] == "1":
            self.parameters[r"kV"] = str(float(self.parameters.pop("kV")) / 3 ** (0.5))
        else:
            self.parameters[r"kV"] = self.parameters.pop("kV")

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases, self.neutral)

        super().__init__(name, self.buses, self.parameters)


class Generator(TwoTerminal):
    def __init__(self, elem_type, name, nodes, buses_dict, init_data):
        self.type = elem_type
        self.parameters = {k: v for k, v in init_data.items() if
                           k in ["Phases", "kv", "kw", "pf", "model", "Xd", "Xdp", "Xdpp", "XRdp", "H", "basefreq"]}
        self.num_buses = 1
        self.phases = 3

        self.buses = return_bus_connections(name, nodes, buses_dict, self.num_buses, self.phases)
        super().__init__(name, self.buses, self.parameters)

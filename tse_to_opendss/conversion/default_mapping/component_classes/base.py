class Circuit:

    def __init__(self, name, simulation_parameters):
        self.name = name
        self.components = []
        self.simulation_parameters = simulation_parameters


class Component:
    """ Circuit components base class. """

    def __init__(self, name, circuit):
        self.name = name
        self.circuit = circuit

    def identifier(self):
        # OpenDSS Example: VSOURCE.GRID1
        return f'"{self.type.upper()}.{self.name.upper()}"'


class GeneralObject(Component):
    """ General objects are not connected to circuit elements. """

    def __init__(self, name, circuit, dss_properties):
        self.name = name
        self.dss_properties = dss_properties

        super().__init__(name, circuit)

    def output_line(self):
        """ Text output to be written to a file. """

        line_props = [f'{k}={v}' for k, v in self.dss_properties.items()]
        return f'new {self.identifier()} {" ".join(line_props)}\n'


class Monitor(Component):
    """ Defines a monitor for a component. """

    def __init__(self, name, circuit, monitor_properties):
        self.type = "MONITOR"

        self.monitor_properties = monitor_properties

        super().__init__(name, circuit)

    def output_line(self):
        """ Text output to be written to a file. """
        self.params = [f'{k}={v}' for k, v in self.monitor_properties.items()]
        return f'new {self.identifier()} {" ".join(self.params)}\n'


class MultiTerminal(Component):
    """ Multi-terminal components """

    def __init__(self, name, circuit, buses, dss_properties):
        self.buses = buses
        self.dss_properties = dss_properties

        super().__init__(name, circuit)

    def output_line(self):
        """ Text output to be written to a file. """

        line_props = [f'{k}={v}' for k, v in self.dss_properties.items()]
        return f'new {self.identifier()} Buses=[{", ".join(self.buses)}] {" ".join(line_props)}\n'


class TwoTerminal(Component):
    """ Two-terminal components (connects to two buses by default) """

    def __init__(self, name, circuit, buses, dss_properties):
        self.buses = buses
        self.dss_properties = dss_properties

        super().__init__(name, circuit)

    def output_line(self):
        """ Text output to be written to a file. """

        params = [f'{param}={self.dss_properties.get(param)}' for param in self.dss_properties]
        return (f'new {self.identifier()} Bus1={self.buses[0]}'
                f'{" Bus2=" + self.buses[1] if len(self.buses) == 2 else ""} {" ".join(params)}\n')


def convert_matrix_format(input_matrix, phase_num):

    import re
    import ast

    phase_num = int(phase_num)
    matrix_rows = input_matrix.strip(" [](){}\"\'").split("|")

    # Generate Python like matrix (string) of one row or more
    converted_matrix_hil = "["
    for row_number in range(len(matrix_rows) - 1):
        converted_matrix_hil += f'[{matrix_rows[row_number].strip()}], '
    converted_matrix_hil += f'[{matrix_rows[-1].strip()}]]'
    converted_matrix_hil = re.sub(r"[\s,]+", ", ", converted_matrix_hil)

    try:
        evaluated_matrix = ast.literal_eval(converted_matrix_hil)
    except ValueError:
        raise Exception(f"Invalid matrix input")

    # truncate number of lines and the size of the last line to the number of phases
    if len(evaluated_matrix) > phase_num:
        evaluated_matrix = evaluated_matrix[:phase_num]
        evaluated_matrix[-1] = evaluated_matrix[-1][:phase_num]

    # Check if the matrix input is on the lower triangular form
    if not all([len(row) >= n + 1 for n, row in enumerate(evaluated_matrix)]):
        raise Exception(
            f"One or more rows of the matrix have dimension that does not match with the minimum entries "
            f"required for a lower triangular matrix.")
    elif any([len(row) < len(evaluated_matrix[-1]) for row in evaluated_matrix]):
        # Assume lower triangular matrix form
        for i in range(phase_num - 1):
            # Drop all entries above the matrix diagonal
            row = evaluated_matrix[i][:i + 1]
            for j in range(i, phase_num - 1):
                # add the entries below the diagonal to the symmetrical places above the diagonal
                row.append(evaluated_matrix[j + 1][i])
            # overwrite original row with the new full row
            evaluated_matrix[i] = row
    else:
        # Truncate the matrix row size to contain a number of entries equal to the number of phases
        for i in range(phase_num):
            evaluated_matrix[i] = evaluated_matrix[i][:phase_num]
    converted_matrix_hil = str(evaluated_matrix)
    converted_matrix_dss = re.sub(r"(?:\], \[)", " | ", converted_matrix_hil.strip("[]")).replace(",", " ")
    converted_matrix_dss = f"[{converted_matrix_dss}]"

    return converted_matrix_dss

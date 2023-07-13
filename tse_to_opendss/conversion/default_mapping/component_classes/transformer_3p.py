from .base import *
from ...output_functions import *


class ThreePhaseTransformer(MultiTerminal):
    """ Converted component class. """

    def __init__(self, converted_comp_type, name, circuit, tse_properties, tse_component):
        self.type = "TRANSFORMER"
        self.name = name
        self.circuit = circuit

        # Some TSE components require more than one instance/class
        self.created_instances_list = [self]

        # Number of phases
        self.num_phases = self.define_number_of_phases(self, tse_properties, tse_component)
        # Number of buses
        self.num_buses = self.define_number_of_buses(self, tse_properties, tse_component)
        # Floating neutral
        self.floating_neutral = self.is_neutral_floating(self, tse_properties, tse_component)

        # Get bus connections list
        self.buses = return_bus_connections(tse_component, self.num_buses, self.num_phases, self.floating_neutral)

        # Filter unused TSE properties and create new ones
        self.new_format_properties = self.create_new_format_properties_dict(self, tse_properties, tse_component)

        # Run parent initialization code
        super().__init__(name, circuit, self.buses, dss_properties=self.new_format_properties)

        # Create monitoring lines
        create_monitors(self, tse_properties, tse_component)

        # Apply extra necessary conversion steps
        self.extra_conversion_steps(self, tse_properties, tse_component)

    @staticmethod
    def create_new_format_properties_dict(self, tse_properties, tse_component):
        """ Filters unused TSE properties and creates new ones. Returns a dictionary with the new properties. """

        property_names = ["KVs", "KVAs", "XscArray"]
        new_format_properties = {par: tse_properties[par] for par in property_names}

        # Specify the base frequency if not inheriting the global value
        if tse_properties['global_basefreq'] == "False":
            new_format_properties["Basefreq"] = tse_properties['Basefreq']

        # Update property names to match OpenDSS
        new_format_properties[r"%Rs"] = tse_properties["percentRs"]
        new_format_properties[r"%Noloadloss"] = tse_properties["percentNoloadloss"]
        new_format_properties[r"%imag"] = tse_properties["percentimag"]
        new_format_properties[r"windings"] = tse_properties["num_windings"]

        regcontrol_on = tse_properties['regcontrol_on']
        if regcontrol_on == "True":
            regctrl_number = tse_properties["ctrl_winding"][-1]
            tap_parameters = {"wdg": regctrl_number,
                              "maxtap": tse_properties.get("maxtap"),
                              "mintap": tse_properties.get("mintap"),
                              "numtaps": tse_properties.get("numtaps")}

            new_format_properties.update(tap_parameters)

        conn_dict = {"Y": "wye", "Δ": "delta", "Y - Grounded": "wye"}
        connections_list = []
        num_windings = int(tse_properties['num_windings'])

        # Go through every winding checking the connection type
        wdg_names = ["prim", "sec1", "sec2", "sec3"]
        for idx, w in enumerate(wdg_names[:num_windings]):
            # Translate the connection
            this_connection = conn_dict[tse_properties[w + "_conn"]]
            connections_list.append(this_connection)
        connections = f'[{", ".join([conn for conn in connections_list])}]'
        new_format_properties.update({"conns": connections})

        # Rneut / Xneut
        neutral_impedances = {}
        new_format_properties["neutral_impedances"] = neutral_impedances
        for idx, wdg_name in enumerate(wdg_names[:num_windings]):
            this_connection = tse_properties[wdg_name + "_conn"]
            neutral_impedances[idx + 1] = {}
            if this_connection == "Y - Grounded":
                neutral_impedances[idx + 1] = {}
                neutral_impedances[idx + 1]["rneut"] = tse_properties[f"Rneut_{wdg_name}"]
                neutral_impedances[idx + 1]["xneut"] = tse_properties[f"Xneut_{wdg_name}"]

        return new_format_properties

    @staticmethod
    def define_number_of_phases(self, tse_properties, tse_component):
        """ Returns the number of phases of the component. """

        num_phases = 3

        return num_phases

    @staticmethod
    def define_number_of_buses(self, tse_properties, tse_component):
        """ Returns the number of buses the component is connected to. """

        num_buses = int(tse_properties['num_windings'])

        return num_buses

    @staticmethod
    def is_neutral_floating(self, tse_properties, tse_component):
        """ Floating neutrals connect to an unused bus node """

        return False

    @staticmethod
    def extra_conversion_steps(self, tse_properties, tse_component):
        """ Applies extra necessary conversion steps. """

        regcontrol_on = tse_properties['regcontrol_on']
        if regcontrol_on == "True":

            import numpy as np

            regcontrol_property_names = ["vreg", "ptratio", "band", "delay"]
            regcontrol_props = {par: tse_properties[par] for par in regcontrol_property_names}
            regcontrol_props["winding"] = tse_properties["ctrl_winding"][-1]
            regcontrol_props["maxtapchange"] = "1"
            regcontrol_props["control_iters"] = tse_properties.get("numtaps")

            num_windings = int(tse_properties['num_windings'])

            # Go through every winding checking the connection type
            for idx, w in enumerate(["prim", "sec1", "sec2", "sec3"][:num_windings]):
                this_connection = tse_properties[w + "_conn"]
                if idx + 1 == int(regcontrol_props["winding"]):  # If this is the controlled winding
                    if this_connection == "Δ":
                        # Use line voltage for delta connection
                        regcontrol_props["vreg"] = round(float(regcontrol_props["vreg"]) * np.sqrt(3), 2)

            from .regcontrol import RegControl

            new_regcontrol = RegControl(converted_comp_type="LOADSHAPE",
                                        name=self.name + "_REGCONTROL",
                                        circuit=self.circuit,
                                        tse_properties=regcontrol_props,
                                        tse_component=tse_component)

            self.created_instances_list.append(new_regcontrol)

    def output_line(self):
        """ Overrides parent output_line method. """

        windings = self.new_format_properties.pop("windings")

        impedances_str = ""
        neutral_impedances = self.new_format_properties.pop("neutral_impedances")
        for winding_n, impedance_dict in neutral_impedances.items():
            if impedance_dict:
                impedances_str += f" wdg={winding_n} rneut={impedance_dict['rneut']}" \
                                  f" xneut={impedance_dict['xneut'] }"

        line_props = [f'{k}={v}' for k, v in self.new_format_properties.items()]
        return f'new {self.identifier()} windings={windings} phases={self.num_phases} '\
               f'Buses=[{", ".join(self.buses)}] {" ".join(line_props)}' \
               f'{impedances_str}\n'

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

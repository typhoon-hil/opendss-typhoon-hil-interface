from .base import *
from ...output_functions import *


class SinglePhaseTransformer(MultiTerminal):
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
            new_format_properties["baseFreq"] = tse_properties['baseFreq']

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

        return new_format_properties

    @staticmethod
    def define_number_of_phases(self, tse_properties, tse_component):
        """ Returns the number of phases of the component. """

        num_phases = 2

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
            regcontrol_property_names = ["vreg", "ptratio", "band", "delay"]
            regcontrol_props = {par: tse_properties[par] for par in regcontrol_property_names}
            regcontrol_props["winding"] = tse_properties["ctrl_winding"][-1]
            regcontrol_props["maxtapchange"] = "1"
            regcontrol_props["control_iters"] = tse_properties.get("numtaps")

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
        line_props = [f'{k}={v}' for k, v in self.new_format_properties.items()]
        return f'new {self.identifier()} windings={windings} ' \
               f'phases={self.num_phases - 1} Buses=[{", ".join(self.buses)}]' \
               f' {" ".join(line_props)}\n'

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

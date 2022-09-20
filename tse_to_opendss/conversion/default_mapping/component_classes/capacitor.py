from .base import *
from ...output_functions import *


class Capacitor(TwoTerminal):
    """ Converted component class. """

    def __init__(self, converted_comp_type, name, circuit, tse_properties, tse_component):
        self.type = converted_comp_type
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
    def define_number_of_phases(self, tse_properties, tse_component):
        """ Returns the number of phases of the component. """

        num_phases = int(tse_properties['phases'])

        return num_phases

    @staticmethod
    def define_number_of_buses(self, tse_properties, tse_component):
        """ Returns the number of buses the component is connected to. """

        tp_connection = tse_properties['tp_connection']
        if tp_connection in ["Y-grounded", "Δ"]:
            num_buses = 1
        elif tp_connection in ["Y", "Series"]:
            num_buses = 2

        return num_buses

    @staticmethod
    def is_neutral_floating(self, tse_properties, tse_component):
        """ Floating neutrals connect to an unused bus node """

        if self.num_phases == 3:
            return tse_properties['tp_connection'] == "Y"
        else:
            return False

    @staticmethod
    def create_new_format_properties_dict(self, tse_properties, tse_component):
        """ Filters unused TSE properties and creates new ones. Returns a dictionary with the new properties. """

        new_format_properties = {}

        new_format_properties.update(
            {
                "kv": tse_properties['Kv'],
                "kvar": tse_properties['Kvar'],
                "phases": tse_properties['phases']
            }
        )

        if tse_properties['tp_connection'] == "Y-grounded" and tse_properties['phases'] == "1":
            new_format_properties[r"kv"] = str(float(new_format_properties.pop("kv")) / 3 ** 0.5)

        if tse_properties['tp_connection'] == "Δ":
            new_format_properties.update(
                {"conn": "delta"}
            )

        # Specify the base frequency if not inheriting the global value
        if tse_properties['global_basefreq'] == "False":
            new_format_properties["basefreq"] = tse_properties['BaseFreq']

        return new_format_properties



    @staticmethod
    def extra_conversion_steps(self, tse_properties, tse_component):
        """ Applies extra necessary conversion steps. """

        pass

    def output_line(self):
        """ Overrides parent output_line method. """

        return super().output_line()

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return [self]

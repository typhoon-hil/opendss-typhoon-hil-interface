from .base import *
from ...output_functions import *


class Vsource(TwoTerminal):
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
    def create_new_format_properties_dict(self, tse_properties, tse_component):
        """ Filters unused TSE properties and creates new ones. Returns a dictionary with the new properties. """

        new_format_properties = dict()

        tse_si_prop_names = ["r1", "x1", "r0", "x0"]
        dss_si_prop_names = ["R1", "X1", "R0", "X0"]
        tse_pu_prop_names = ["r1_pu", "x1_pu", "r0_pu", "x0_pu"]
        dss_pu_prop_names = ["puZ1", "puZ0", "puZ2"]
        tse_mva_prop_names = ["mva_sc3", "mva_sc1", "x1r1", "x0r0"]
        dss_mva_prop_names = ["MVAsc3", "MVAsc1", "x1r1", "x0r0"]
        tse_i_prop_names = ["i_sc3", "i_sc1", "x1r1", "x0r0"]
        dss_i_prop_names = ["Isc3", "Isc1", "x1r1", "x0r0"]
        tse_general_prop_names = ["baseFreq", "basekv", "baseMVA", "pu", "Angle", "Frequency"]
        dss_general_prop_names = ["baseFreq", "basekv", "baseMVA", "pu", "Angle", "Frequency"]

        if tse_properties['input_method'] == "Z":
            tse_values = [tse_properties.get(key) for key in tse_si_prop_names]
            new_format_properties = {key: value for key, value in zip(dss_si_prop_names, tse_values)}
        elif tse_properties['input_method'] == "Zpu":
            tse_values = [tse_properties.get(key) for key in tse_pu_prop_names]
            for count, value in enumerate(dss_pu_prop_names[0:2]):
                new_format_properties[value] = f"[{tse_values[2*count]}, {tse_values[2*count+1]}]"
            new_format_properties["puZ2"] = new_format_properties.get("puZ1")
        elif tse_properties['input_method'] == "MVAsc":
            tse_values = [tse_properties.get(key) for key in tse_mva_prop_names]
            new_format_properties = {key: value for key, value in zip(dss_mva_prop_names, tse_values)}
        elif tse_properties['input_method'] == "Isc":
            tse_values = [tse_properties.get(key) for key in tse_i_prop_names]
            new_format_properties = {key: value for key, value in zip(dss_i_prop_names, tse_values)}

        for count, value in enumerate(dss_general_prop_names):
            new_format_properties[value] = tse_properties.get(tse_general_prop_names[count])

        return new_format_properties

    @staticmethod
    def define_number_of_phases(self, tse_properties, tse_component):
        """ Returns the number of phases of the component. """

        num_phases = 3

        return num_phases

    @staticmethod
    def define_number_of_buses(self, tse_properties, tse_component):
        """ Returns the number of buses the component is connected to. """

        ground_connected = tse_properties.get("tp_connection") == "Y - Grounded"
        num_buses = 1 if ground_connected else 2

        return num_buses

    @staticmethod
    def is_neutral_floating(self, tse_properties, tse_component):
        """ Floating neutrals connect to an unused bus node """

        return False

    @staticmethod
    def extra_conversion_steps(self, tse_properties, tse_component):
        """ Applies extra necessary conversion steps. """

        pass

    def output_line(self):
        """ Overrides parent output_line method. """

        return super().output_line()

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

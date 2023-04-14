from .base import *
from ...output_functions import *


class VSConverter(TwoTerminal):
    """ Converted component class. """

    def __init__(self, converted_comp_type, name, circuit, tse_properties, tse_component):
        self.type = None
        self.name = name
        self.circuit = circuit

        # Some TSE components require more than one instance/class
        self.created_instances_list = [self]

        # Apply extra necessary conversion steps
        self.extra_conversion_steps(self, tse_properties, tse_component)

    @staticmethod
    def create_new_format_properties_dict(self, tse_properties, tse_component):
        """ Filters unused TSE properties and creates new ones. Returns a dictionary with the new properties. """

        new_format_properties = dict(tse_properties)

        return new_format_properties

    @staticmethod
    def define_number_of_phases(self, tse_properties, tse_component):
        """ Returns the number of phases of the component. """

        num_phases = 0

        return num_phases

    @staticmethod
    def define_number_of_buses(self, tse_properties, tse_component):
        """ Returns the number of buses the component is connected to. """

        num_buses = 0

        return num_buses

    @staticmethod
    def is_neutral_floating(self, tse_properties, tse_component):
        """ Floating neutrals connect to an unused bus node """

        return False

    @staticmethod
    def extra_conversion_steps(self, tse_properties, tse_component):
        """ Applies extra necessary conversion steps. """

        from .generator import Generator
        from .vsource import Vsource

        if tse_properties["model"] == "2":
            new_component = Vsource(converted_comp_type="VSOURCE",
                                    name=self.name,
                                    circuit=self.circuit,
                                    tse_properties=tse_properties,
                                    tse_component=tse_component)
        else:
            new_component = Generator(converted_comp_type="GENERATOR",
                                      name=self.name,
                                      circuit=self.circuit,
                                      tse_properties=tse_properties,
                                      tse_component=tse_component)

        self.created_instances_list.append(new_component)
        self.created_instances_list.remove(self)

    def output_line(self):
        """ Overrides parent output_line method. """

        return super().output_line()

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

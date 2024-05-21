from .base import *
from ...output_functions import *


class Storage(TwoTerminal):
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

        new_format_properties = {k: v for k, v in tse_properties.items() if
                                      k in ["kv", "kwhrated", "kwrated", "pct_effcharge", "snap_status",
                                            "pct_effdischarge", "pct_idlingkw",  # "pct_idlingkvar",
                                            "pct_reserve", "pct_stored", "chargetrigger", "dischargetrigger", "kva"]}

        new_format_properties["%effcharge"] = new_format_properties.pop('pct_effcharge')
        new_format_properties["%effdischarge"] = new_format_properties.pop('pct_effdischarge')
        new_format_properties["%idlingkw"] = new_format_properties.pop('pct_idlingkw')
        # new_format_properties["%idlingkvar"] = new_format_properties.pop('pct_idlingkvar')
        new_format_properties["%reserve"] = new_format_properties.pop('pct_reserve')
        new_format_properties["%stored"] = new_format_properties.pop('pct_stored')
        new_format_properties["state"] = new_format_properties.pop('snap_status')
        new_format_properties["phases"] = str(self.num_phases)
        new_format_properties["dispmode"] = tse_properties['dispatch_p']

        if self.circuit.simulation_parameters.get("sim_mode") == "Time Series":
            new_format_properties[tse_properties.get("timespan")] = tse_properties.get("loadshape_name")

        # Specify the base frequency if not inheriting the global value
        if tse_properties['global_basefreq'] == "False":
            new_format_properties["baseFreq"] = tse_properties['baseFreq']

        if new_format_properties.get("dispmode") == "Default":
            new_format_properties["%discharge"] = tse_properties['pct_discharge']
            new_format_properties["%charge"] = tse_properties['pct_charge']
        else:
            new_format_properties.pop('chargetrigger')
            new_format_properties.pop('dischargetrigger')

        if tse_properties["dispatch_q"] == "Constant PF":
            new_format_properties["pf"] = tse_properties['pf']
        elif tse_properties["dispatch_q"] == "Constant kVAr":
            new_format_properties["kvar"] = tse_properties['kvar']

        # Work Around: Container as Storage doesn't compute the kva (once there is no pre_compile handler)
        if new_format_properties["kva"] == "0":  # The default value is set to zero when the storage came from container
            # This code I used from the storage comp_script
            if tse_properties["dispatch_q"] == "Unit PF":
                kwrated = new_format_properties["kwrated"]
                kva = kwrated
            elif tse_properties["dispatch_q"] == "Constant PF":
                kwrated = new_format_properties["kwrated"]
                pf = new_format_properties["pf"]
                kva = float(kwrated) / float(pf)
            elif tse_properties["dispatch_q"] == "Constant kVAr":
                kwrated = new_format_properties["kwrated"]
                kvar = new_format_properties["kvar"]
                kva = (float(kwrated) ** 2 + float(kvar) ** 2) ** 0.5
            new_format_properties["kva"] = kva

        return new_format_properties

    @staticmethod
    def define_number_of_phases(self, tse_properties, tse_component):
        """ Returns the number of phases of the component. """

        num_phases = 3

        return num_phases

    @staticmethod
    def define_number_of_buses(self, tse_properties, tse_component):
        """ Returns the number of buses the component is connected to. """

        num_buses = 1

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

from .base import *
from ...output_functions import *


class PVSystem(TwoTerminal):
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
        tse_inverter_names = ["power", "voltage", "freq", "phases"]
        dss_inverter_names = ["kVA", "kV", "basefreq", "phases"]
        tse_pv_names = ["pmpp", "irrad", "temp"]
        dss_pv_names = ["Pmpp", "irradiance", "Temperature"]
        tse_curve_names = ["xycurve_name_eff", "xycurve_name_cf"]
        dss_curve_names = ["EffCurve", "P-TCurve"]

        tse_convert_props = tse_inverter_names + tse_pv_names + tse_curve_names
        dss_convert_props = dss_inverter_names + dss_pv_names + dss_curve_names
        for index, prop in enumerate(tse_convert_props):
            new_format_properties[dss_convert_props[index]] = tse_properties.get(prop)

        if self.circuit.simulation_parameters.get("sim_mode") == "Time Series":
            new_format_properties["daily"] = tse_properties.get("loadshape_name")
            new_format_properties["Tdaily"] = tse_properties.get("tshape_name")

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
        """
        xycurve_eff_props = {"npts": tse_properties.get("xycurve_npts_eff"),
                             "xarray": tse_properties.get("xycurve_xarray_eff"),
                             "yarray": tse_properties.get("xycurve_yarray_eff")
                             }

        xycurve_cf_props = {"npts": tse_properties.get("xycurve_npts_cf"),
                            "xarray": tse_properties.get("xycurve_xarray_cf"),
                            "yarray": tse_properties.get("xycurve_yarray_cf")
                            }

        
        xycurve_eff_exists = False  # TODO: GUI option
        xycurve_cf_exists = False   # TODO: GUI option
        tshape_temp_exists = False  # TODO: GUI option

        from .xycurve import XYCurve
        if not xycurve_eff_exists:
            new_xycurve = XYCurve(converted_comp_type="XYCURVE",
                                  name=self.name + "_" + tse_properties["xycurve_name_eff"].upper(),
                                  circuit=self.circuit,
                                  tse_properties=xycurve_eff_props,
                                  tse_component=None)
            self.created_instances_list.append(new_xycurve)

        if not xycurve_cf_exists:
            new_xycurve = XYCurve(converted_comp_type="XYCURVE",
                                  name=self.name + "_" + tse_properties["xycurve_name_cf"].upper(),
                                  circuit=self.circuit,
                                  tse_properties=xycurve_cf_props,
                                  tse_component=None)
            self.created_instances_list.append(new_xycurve)

        from .tshape import TShape
        if not tshape_temp_exists:
            new_tshape = TShape(converted_comp_type="TSHAPE",
                                name=self.name + "_" + tse_properties["tshape_name"].upper(),
                                circuit=self.circuit,
                                tse_properties=xycurve_eff_props,
                                tse_component=None)
            self.created_instances_list.append(new_tshape)
        """


    def output_line(self):
        """ Overrides parent output_line method. """

        return super().output_line()

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

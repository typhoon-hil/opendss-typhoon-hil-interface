from .base import *
from ...output_functions import *


class Load(TwoTerminal):
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

        if tse_properties['model'] == "8":
            filtered_list = ["phases", "kV", "pf", "model", "conn", "kVA", "Vminpu", "Vmaxpu", "ZIPV"]
        else:
            filtered_list = ["phases", "kV", "pf", "model", "conn", "kVA", "Vminpu", "Vmaxpu"]

        new_format_properties = {k: v for k, v in tse_properties.items() if k in filtered_list}

        # Specify the base frequency if not inheriting the global value
        if tse_properties['global_basefreq'] == "False":
            new_format_properties["basefreq"] = tse_properties['basefreq']

        if tse_properties["Pow_ref_s"] == "Time Series":
            new_format_properties["daily"] = tse_properties.get("loadshape_name")

        gnd = tse_properties["ground_connected"] == "True"
        if tse_properties["phases"] == "3":
            if not gnd:
                new_format_properties["Rneut"] = "-1"

        # For single phase use phase voltage instead of line voltage
        if gnd and tse_properties["phases"] == "1":
            new_format_properties[r"kV"] = str(float(new_format_properties.pop("kV")) / 3 ** 0.5)

        return new_format_properties

    @staticmethod
    def define_number_of_phases(self, tse_properties, tse_component):
        """ Returns the number of phases of the component. """

        gnd = tse_properties["ground_connected"] == "True"
        num_phases = int(tse_properties["phases"])

        if num_phases == 1 and not gnd:
            num_phases = 2

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

        loadshape_props = {
            "npts": tse_properties.get("dssnpts"),
            "useactual": tse_properties.get("useactual", "False"),
            "interval": tse_properties.get("loadshape_int", "1")
        }

        if tse_properties.get("loadshape_from_file") == "True":
            loadshape_from_file_path = tse_properties.get("loadshape_from_file_path")
            headers = "yes" if tse_properties.get("loadshape_from_file_headers") == "True" else "no"
            column = tse_properties.get("loadshape_from_file_column")
            loadshape_props["mult"] = f"""(file='{loadshape_from_file_path}', header={headers}, col={column})"""
        else:
            loadshape_props["mult"] = tse_properties.get("loadshape")

        #############

        # Check the if the provided loadshape (loadshape_name) exists. If not, create a new loadshape object.
        import json

        loadshape_exists = False
        obj_json_file = self.circuit.simulation_parameters.get("dss_data_path").joinpath("general_objects.json")
        if obj_json_file.is_file():
            with open(obj_json_file, 'r') as f:
                general_objects = json.loads(f.read())
                saved_loadshapes = general_objects.get("loadshapes")
                # Make dict search case insensitive
                for key in list(saved_loadshapes.keys()):
                    saved_loadshapes[key.upper()] = saved_loadshapes.pop(key)
                if saved_loadshapes.get(tse_properties["loadshape_name"].upper()):
                    loadshape_exists = True


        time_series_mode = tse_properties["Pow_ref_s"] == "Time Series"

        if time_series_mode and not loadshape_exists:

            # loadshape_props = {
            #     "npts": str(tse_properties.get("dssnpts")),
            #     "interval": str(tse_properties.get("dssT")),
            #     "mult": str(tse_properties.get("S_Ts"))
            # }
            # if tse_properties.get("dssT") == "0":
            #     loadshape_props.update({"mult": str(self.loadshape.get("T_Ts"))})
            from .loadshape import LoadShape

            new_loadshape = LoadShape(converted_comp_type="LOADSHAPE",
                                      name=self.name + "_PROFILE",
                                      circuit=self.circuit,
                                      tse_properties=loadshape_props,
                                      tse_component=None)

            self.created_instances_list.append(new_loadshape)

            self.new_format_properties.update({"daily": str(self.name + "_PROFILE")})

    def output_line(self):
        """ Overrides parent output_line method. """

        return super().output_line()

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

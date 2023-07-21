import ast

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

        # Workaround for load container - pre_compile functions don't run in Container.
        # Let's convert the properties here instead in pre_compile function
        """
        if tse_properties['model'] == "8":
            filtered_list = ["phases", "kV", "pf", "model", "conn", "kVA", "Vminpu", "Vmaxpu", "ZIPV"]
        else:
            filtered_list = ["phases", "kV", "pf", "model", "conn", "kVA", "Vminpu", "Vmaxpu"]

        new_format_properties = {k: v for k, v in tse_properties.items() if k in filtered_list}
        """

        new_format_properties = dict()
        # Phase Property
        new_format_properties["phases"] = tse_properties["phases"]
        kv = tse_properties["Vn_3ph"]
        new_format_properties["kV"] = kv
        # PF Property
        if tse_properties["pf_mode_3ph"] == "Unit":
            pf = 1.0
        elif tse_properties["pf_mode_3ph"] == "Lag":
            pf = tse_properties["pf_3ph"]
        else:
            pf = -1 * float(tse_properties["pf_3ph"])
        new_format_properties["pf"] = str(pf)
        # Model Property (Pre_Compile Function has not ZIP evaluation)
        if tse_properties["load_model"] == "Constant Power":
            model = 1
        elif tse_properties["load_model"] == "Constant Z,I,P":
            model = 8
        else:
            model = 2
        new_format_properties["model"] = model
        # Conn Property
        if tse_properties["tp_connection"] == 'Δ':
            conn = "delta"
        else:
            conn = "wye"
        new_format_properties["conn"] = conn
        # kVA Property
        new_format_properties["kVA"] = tse_properties["Sn_3ph"]
        # Vminpu and Vmaxpu Properties
        v_min_max = ast.literal_eval(tse_properties["v_min_max"])
        new_format_properties["Vminpu"] = str(v_min_max[0])
        new_format_properties["Vmaxpu"] = str(v_min_max[1])
        # ZIPV Property
        if model == 8:
            # zipv_p = ast.literal_eval(tse_properties["zip_vector"])
            # zipv_q = ast.literal_eval(tse_properties["zip_vector_Q"])
            # voltage_cutoff = 0.5  # power is zero below the threshold. Voltage in p.u.
            # zipv = (zipv_p + zipv_q).append(voltage_cutoff)
            new_format_properties["ZIPV"] = tse_properties['ZIPV']

        # Specify the base frequency if not inheriting the global value
        if tse_properties['global_basefreq'] == "False":
            new_format_properties["baseFreq"] = tse_properties['baseFreq']

        if tse_properties["Pow_ref_s"] == "Time Series":
            new_format_properties["daily"] = tse_properties.get("loadshape_name")

        #gnd = tse_properties["ground_connected"] == "True"
        if tse_properties["tp_connection"] == "Y - Grounded":
            gnd = True
        else:
            gnd = False

        if gnd:
            # Put the impedance between Neutral and Gnd
            new_format_properties["Rneut"] = tse_properties.get("Rneut")
            new_format_properties["Xneut"] = tse_properties.get("Xneut")
        else:
            # Neutral and Gnd are disconnected
            new_format_properties["Rneut"] = "-1"

        # For single phase use phase voltage instead of line voltage
        if gnd and tse_properties["phases"] == "1":
            new_format_properties[r"kV"] = str(float(new_format_properties.pop("kV")) / 3 ** 0.5)

        return new_format_properties

    @staticmethod
    def define_number_of_phases(self, tse_properties, tse_component):
        """ Returns the number of phases of the component. """

        gnd = tse_properties["tp_connection"] == "Y - Ground"

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

        if not obj_json_file.is_file():
            with open(obj_json_file, 'w') as f:
                f.write(json.dumps({"loadshapes": {}, "linecodes": {}}, indent=4))
        with open(obj_json_file, 'r') as f:
            general_objects = json.load(f)

        saved_loadshapes = general_objects.get("loadshapes")

        # Make dict search case insensitive
        if saved_loadshapes:
            for key in list(saved_loadshapes.keys()):
                saved_loadshapes[key.upper()] = saved_loadshapes.pop(key)

            if saved_loadshapes.get(tse_properties["loadshape_name"].upper()):
                loadshape_exists = True

        time_series_mode = tse_properties["Pow_ref_s"] == "Time Series"

        if time_series_mode and not loadshape_exists:

            from .loadshape import LoadShape

            new_loadshape = LoadShape(converted_comp_type="LOADSHAPE",
                                      name=self.name + "_PROFILE",
                                      circuit=self.circuit,
                                      tse_properties=loadshape_props,
                                      tse_component=None)

            self.created_instances_list.append(new_loadshape)

            self.new_format_properties.update({"daily": str(self.name + "_PROFILE")})

            if not saved_loadshapes:
                general_objects['loadshapes'] = {}
            general_objects['loadshapes'].update({tse_properties[self.name + "_PROFILE"]: loadshape_props})

            with open(obj_json_file, 'w') as f:
                f.write(general_objects, indent=4)

    def output_line(self):
        """ Overrides parent output_line method. """

        return super().output_line()

    def created_component_instances(self):
        """ Some TSE components may result in multiple converted components. """

        return self.created_instances_list

import opendssdirect as dss
from ast import literal_eval

counted_parts = []


def cast(vals: dict) -> dict:
    """
    Take a dict of mask properties, and convert the values from strings into their proper types.

    Returns the processed dict at the end
    """
    for k, v in vals.items():
        if isinstance(v, str):
            try:
                vals[k] = literal_eval(v)
            except:
                continue
        if isinstance(v, list):
            if len(v) == 1 and "|" in v[0]:
                vals[k] = convert_matrix(v[0])
            else:
                for i in range(len(v)):
                    try:
                        v[i] = literal_eval(v[i])
                    except:
                        continue
                vals[k] = v
    return vals


def convert_matrix(val: str):
    # Convert "[a |b c |d e f ]' -> [[a],[b,c],[d,e,f]]
    entries = [[float(e) for e in r.strip().split(" ")] for r in val.split("|")]

    def all_eq_len(arr):
        l = len(arr[0])
        for line in arr[1:]:
            if len(line) != l:
                return False
        return True

    # if len(sum(entries, [])):
    # return sum(entries, [])[0]
    if not all_eq_len(entries):
        max_len = len(entries[-1])
        for i, r in enumerate(entries):
            r += [0] * (max_len - i - 1)
    return entries


def set_global_basefrequency(mask_properties):
    #
    # Do not check the global base frequency box if the baseFreq value
    # is different from the global value
    #
    base_freq = mask_properties.get("baseFreq") or mask_properties.get(
        "fn"
    )  # Load case

    mask_properties["global_basefreq"] = "True"
    if base_freq and float(base_freq) != float(dss.Solution.Frequency()):
        mask_properties["global_basefreq"] = "False"


"""
def template(obj_name: str) -> dict:
    prop_name = ""
    mask_properties = {}
    properties_map = {
    }
    obj_properties = dss.utils.class_to_dataframe(f"{prop_name}").transpose()[obj_name]
    for prop in properties_map:
        typhoon_property = properties_map[prop]
        mask_properties[typhoon_property] = obj_properties[prop]
    return mask_properties
"""


def bus(obj_name: str) -> dict:
    """
    Buses aren't defined in DSS, they're references that get made and deleted as needed.
    Our "options" are all whether or not to measure different signals,
    and how the two ends are connected to each other
    """
    mask_properties = {}
    dss.Circuit.SetActiveBus(obj_name)

    nodes = dss.Bus.Nodes()

    if 1 in nodes:
        mask_properties["phase_a"] = True
    else:
        mask_properties["phase_a"] = False
    if 2 in nodes:
        mask_properties["phase_b"] = True
    else:
        mask_properties["phase_b"] = False
    if 3 in nodes:
        mask_properties["phase_c"] = True
    else:
        mask_properties["phase_c"] = False
    if any(n > 3 for n in nodes):
        mask_properties["phase_n"] = True
    else:
        mask_properties["phase_n"] = False

    return mask_properties


def capacitor(obj_name: str) -> dict:
    prop_name = "Capacitor"
    mask_properties = {}
    properties_map = {
        "kv": "Kv",
        "kvar": "Kvar",
        "phases": "phases",
        "basefreq": "baseFreq",
    }

    obj_properties = dss.utils.class_to_dataframe("Capacitor").transpose()[
        "Capacitor." + obj_name
    ]

    for prop in properties_map:
        typhoon_property = properties_map[prop]
        mask_properties[typhoon_property] = obj_properties[prop]

    #
    # Check bus 2 for series, grounded or floating connection
    #
    bus_2 = obj_properties["bus2"]
    if not bus_2:
        # No second bus in Delta case
        tp_connection = "Δ"
    else:
        bus_2_split = bus_2.split(".")

        # Only the Bus name and no numbers means a Series connection
        if len(bus_2_split) == 1:
            tp_connection = "Series"

        # There are explicit bus numbers
        else:
            bus_2_numbers = bus_2_split[1:]
            # Grounded connection is all zeros
            if all(int(n) == 0 for n in bus_2_numbers):
                tp_connection = "Y - Grounded"
            else:
                tp_connection = "Y"

    mask_properties["tp_connection"] = tp_connection

    # Global base frequency checkbox
    set_global_basefrequency(mask_properties)

    return mask_properties


def fault(obj_name: str) -> dict:
    prop_name = "Fault"
    mask_properties = {}
    properties_map = {"R": "resistance", "bus1": "type"}
    obj_properties = dss.utils.class_to_dataframe(f"{prop_name}").transpose()[obj_name]
    for prop in properties_map:
        if prop == "bus1":
            legs = obj_properties["bus2"].split(".")[1:]
            legmap = {1: "A", 2: "B", 3: "C"}
            fault_type = "-".join(
                [legmap[leg + 1] for leg in range(len(legs)) if legs[leg] == 0]
                + ["GND"]
            )
            if fault_type != "GND":
                mask_properties["type"] = fault_type
                continue
            out_of_place = [legmap[legs[i]] != legmap[i + 1] for i in range(len(legs))]
            oop_map = []
            for i in range(len(legs)):
                if out_of_place[i]:
                    oop_map.extend([legmap[i + 1], legmap[legs[i]]])
            oop_map = sorted(list(set(oop_map)))
            mask_properties["type"] = "-".join(oop_map)
        else:
            typhoon_property = properties_map[prop]
            mask_properties[typhoon_property] = obj_properties[prop]

    # Global base frequency checkbox
    set_global_basefrequency(mask_properties)

    return mask_properties


def generator(obj_name: str) -> dict:
    prop_name = "generator"
    mask_properties = {}
    properties_map = {
        "Phases": "phases",
        "Kv": "kv",
        "Kw": "kw",
        "Pf": "pf",
        "Model": "model",
        "Kvar": "",
        "Xd": "Xd",
        "Xdpp": "Xdpp",
        "XRdp": "XRdp",
        "Basefreq": "baseFreq",
        "model": "G_mod",
        "H": "H",
    }
    obj_properties = dss.utils.generators_to_dataframe().transpose()[obj_name]
    for prop in properties_map:
        if prop == "model":
            typhoon_property = properties_map[prop]
            mask_properties[typhoon_property] = {
                "1": "Constant kW",
                "2": "Constant admittance",
                "3": "Constant kW, Constant kV",
                "4": "Constant kW, Fixed Q",
                "5": "Constant kW, Fixed Q (constant reactance)",
            }[obj_properties[prop]]
        else:
            typhoon_property = properties_map[prop]
            mask_properties[typhoon_property] = obj_properties[prop]

    # Global base frequency checkbox
    set_global_basefrequency(mask_properties)

    return mask_properties


def isource(obj_name: str) -> dict:
    prop_name = "Isource"
    mask_properties = {}
    properties_map = {
        "amps": "amps",
        "angle": "Angle",
        "frequency": "Frequency",
        "basefreq": "baseFreq",
    }
    obj_properties = dss.utils.class_to_dataframe(f"{prop_name}").transpose()[obj_name]
    for prop in properties_map:
        typhoon_property = properties_map[prop]
        mask_properties[typhoon_property] = obj_properties[prop]

    # Global base frequency checkbox
    set_global_basefrequency(mask_properties)

    return mask_properties


def line(obj_name: str) -> dict:
    prop_name = "Line"
    mask_properties = {}
    properties = {
        "phases": "phases",
        "basefreq": "baseFreq",
        "length": "Length",
        "rmatrix": "rmatrix",
        "xmatrix": "xmatrix",
        "cmatrix": "cmatrix",
    }
    mask_properties["input_type"] = "Matrix"
    obj_properties = dss.utils.class_to_dataframe("Line").transpose()[
        "Line." + obj_name
    ]

    for prop in properties:
        typhoon_property = properties[prop]
        mask_properties[typhoon_property] = obj_properties[prop]

    len_conv = {"ft": 0.0003048, "mi": 1.609344, "kft": 0.3048, "km": 1}
    # mask_properties["has_switch"]= (obj_properties['Switch']=='Yes')
    if obj_properties["units"] != "none":
        mask_properties["Length"] = (
            float(mask_properties["Length"]) * len_conv[obj_properties["units"]]
        )

    # Global base frequency checkbox
    set_global_basefrequency(mask_properties)

    return mask_properties


# def get_load_legs(obj_name):
#     """
#     If a load is defined by 3 seperate legs, find and group them
#     """
#     mask_properties = {}
#     dss.Loads.Name(obj_name)
#     two_sides = dss.CktElement.BusNames()
#     dss.Circuit.SetActiveBus(two_sides[0])
#     incoming_loads = []
#     busses = []
#     loadDF = lambda name: dss.utils.class_to_dataframe("load").transpose()[
#         "load." + name
#     ]
#     prefix = lambda s, to_find: s[: s.find(to_find)]
#     suffix = lambda s, to_find: s[s.find(to_find) + 1 :]
#     all_equal = lambda l: len(set(l)) == 1
#     for x in dss.Bus.AllPCEatBus():
#         if x.startswith("Load."):
#             name = x[5:]
#             incoming_loads.append(name)
#             busses.append(loadDF(name).bus1)
#     # the set of transformers that not only share
#     # the same start and end nodes, but also have names that are
#     # only one letter apart
#     if all_equal([prefix(bus, ".") for bus in busses]):
#         # ['bus.1','bus.2','bus.3'] -> "bus.1.2.3"
#         new_bus = (
#             prefix(busses[0], ".")
#             + "."
#             + ".".join([suffix(bus, ".") for bus in busses])
#         )
#     if len(incoming_loads) != 3:
#         return {"phases": int(loadDF(obj_name).phases)}
#     obj_properties = dss.utils.class_to_dataframe("load").transpose()[
#         "load." + obj_name
#     ]
#     mask_properties["phases"] = 3
#     # mask_properties['type']= 'Load'
#     new_part_str = "New Load.{} phases=3 kW={}  PF={} bus1={} ".format(
#         obj_name[:-1], 0, 0, new_bus
#     )
#
#     if obj_name in counted_parts:
#         mask_properties["ignore"] = True
#         return None
#     else:
#         mask_properties["overlapping_parts"] = {
#             "names": list(incoming_loads),
#             "replacement_str": new_part_str,
#             "replacement_part": "Load." + obj_name[:-1],
#         }
#         counted_parts.extend(incoming_loads)
#
#     if "overlapping_parts" in mask_properties:
#         parts = mask_properties["overlapping_parts"]
#         del mask_properties["overlapping_parts"]
#         obj_full_name = parts["replacement_part"]
#         elements_to_remove[obj_name] = parts
#
#     return mask_properties


def load(obj_name: str) -> dict:
    prop_name = "Load"
    properties = {
        "phases": "phases",
        "kV": "Vn_3ph",
        "kVA": "Sn_3ph",
        "pf": "pf_3ph",
        "model": "load_model",  # Translate to an index
        "conn": "tp_connection",  # translate to Typhoon names
        "ZIPV": "zip_vector",
    }
    # Unaccounted for properties:
    # Ground-connected (bool)
    # Time Series (all)
    obj_properties = dss.utils.class_to_dataframe("Load").transpose()[
        "Load." + obj_name
    ]

    mask_properties = {}
    n_phases = int(obj_properties["phases"])

    for prop in properties:
        typhoon_property = properties[prop]
        if prop == "pf":
            pf = float(obj_properties["pf"])
            mask_properties[typhoon_property] = abs(pf)
            if pf == 1:
                mask_properties["pf_mode_3ph"] = "Unit"
            else:
                sign = lambda v: abs(v) / v
                mask_properties["pf_mode_3ph"] = {-1: "Lag", 1: "Lead"}[sign(pf)]
        elif prop == "conn":
            #
            # A floating Y is defined by a negative Rneut and
            # a bus definition with (phases + 1) node numbers
            #
            bus_numbers = len(obj_properties["bus1"].split(".")) - 1
            if obj_properties[prop] == "delta":
                tp_connection = "Δ"
            else:
                if int(obj_properties["Rneut"]) < 0 and bus_numbers == n_phases + 1:
                    tp_connection = "Y"
                else:
                    tp_connection = "Y - Grounded"
            mask_properties["tp_connection"] = tp_connection
        elif prop == "model":
            mask_properties[typhoon_property] = {
                "1": "Constant Power",
                "2": "Constant Impedance",
                "3": "Constant Z,I,P",
                # TODO not supported
                "4": "Constant Z,I,P",  #
                "5": "Constant Z,I,P",  #
                "6": "Constant Z,I,P",  #
                "7": "Constant Z,I,P",  #
                "8": "Constant Z,I,P",
            }[obj_properties[prop]]
        elif prop == "ZIPV":
            v = [float(f) for f in obj_properties["ZIPV"][0].split(" ")]
            mask_properties["zip_vector"] = v[0:3]
            mask_properties["zip_vector_Q"] = v[3:6]
            # TODO: what do I do about the last value?
        else:
            mask_properties[typhoon_property] = obj_properties[prop]

    # Fix unsupported number of phases
    if n_phases == 2:
        mask_properties["phases"] = "1"
    elif n_phases > 3:
        mask_properties["phases"] = "3"

    # Global base frequency checkbox
    set_global_basefrequency(mask_properties)

    return mask_properties


def storage(obj_name: str) -> dict:
    prop_name = "Storage"
    mask_properties = {}
    properties_map = {
        "DispMode": "dispatch_p",  # set both dispatch_p and q from this
        "State": "snap_status",  # Title-ify this
        "kv": "kv",
        "kvar": "kvar",
        "kKrated": "kwrated",
        "kWhrated": "lwhrated",
        "basefreq": "baseFreq",
        "ChargeTrigger": "chargetrigger",
        "DischargeTrigger": "dischargetrigger",
        "%Charge": "pct_charge",
        "%Discharge": "pct_discharge",
        "%EffCharge": "pct_effcharge",
        "%EffDischarge": "pct_effdischarge",
        "%Idlingkvar": "pct_idlingkvar",
        "%IdlingkW": "pct_idlingkw",
        "%reserve": "pct_reserve",
        "%stored": "pct_stored",
        "pf": "pf",
    }
    obj_properties = dss.utils.class_to_dataframe(f"{prop_name}").transpose()[obj_name]
    for prop in properties_map:
        if prop == "State":
            typhoon_property = properties_map[prop].title()
            mask_properties[typhoon_property] = obj_properties[prop]
        if prop == "DispMode":
            mask_properties["dispatch_p"] = obj_properties[prop]
            mask_properties["dispatch_q"] = obj_properties[prop]
        else:
            typhoon_property = properties_map[prop]
            mask_properties[typhoon_property] = obj_properties[prop]

    # Global base frequency checkbox
    set_global_basefrequency(mask_properties)

    return mask_properties


def get_regulators(obj_name: str) -> dict:
    """
    Find all Regulators attached to a Transformer (or transformer leg)
    """

    if obj_name in counted_parts:
        return

    mask_properties = {}
    dss.Transformers.Name(obj_name)
    two_sides = dss.CktElement.BusNames()
    dss.Circuit.SetActiveBus(two_sides[0])
    incoming_transformers = set(
        [x[12:] for x in dss.Bus.AllPDEatBus() if x.startswith("Transformer.")]
    )
    dss.Circuit.SetActiveBus(two_sides[1])
    outgoing_transformers = set(
        [x[12:] for x in dss.Bus.AllPDEatBus() if x.startswith("Transformer.")]
    )
    shared_elems = incoming_transformers & outgoing_transformers
    # the set of transformers that not only share the
    # same start and end nodes, but also have names that are
    # only one letter apart

    if len(shared_elems) != 3:
        phases = int(
            dss.utils.class_to_dataframe("transformer").transpose()[
                "transformer." + obj_name
            ]["phases"]
        )

        if phases == 3:
            mask_properties["type_name"] = "OpenDSS/Three-Phase Transformer"
        else:
            mask_properties["type_name"] = "OpenDSS/Single-Phase Transformer"

        return mask_properties

    # search for regulators
    regulators = dss.utils.class_to_dataframe("RegControl").transpose()
    for name in regulators:
        reg = regulators[name]
        if obj_name == reg.transformer:
            mask_properties["regcontrol_on"] = True
            mask_properties["ctrl_winding"] = "Winding " + reg.winding
            mask_properties["delay"] = reg.delay
            mask_properties["vreg"] = reg.vreg
            mask_properties["band"] = reg.band
            mask_properties["ptratio"] = reg.ptratio

    # mask_properties["phases"] = 3
    mask_properties["type_name"] = "OpenDSS/Three-Phase Transformer"
    # mask_properties['type'] = 'Transformer'
    transformer_vals = dss.utils.class_to_dataframe("Transformer").transpose()[
        "Transformer." + obj_name
    ]
    new_part_str = (
        f"Edit Transformer.{obj_name} "
        f"winding=2 phases=3 "
        f"XHL={'[' + ' '.join([str(val) for val in transformer_vals.XHL]) + ']'} "
        f"KVAs={'[' + ' '.join([str(val) for val in transformer_vals.kVAs]) + ']'} "
        f"Buses={'[' + ' '.join([val[:-2] for val in transformer_vals.buses]) + ']'} "
        f"KVs={'[' + ' '.join(transformer_vals.kVs) + ']'} "
        f"%LoadLoss={transformer_vals['%loadloss']}"
    )

    mask_properties["overlapping_parts"] = {
        "names": list(shared_elems),
        "replacement_str": new_part_str,
        "replacement_part": "Transformer." + obj_name,
    }
    counted_parts.extend(shared_elems)

    return mask_properties


def transformer(obj_name: str) -> dict:
    properties_map = {
        "windings": "num_windings",
        "kVs": "KVs",
        "kVAs": "KVAs",
        "%Rs": "percentRs",
        "XHL": "XArray",
        "Xscarray": "XscArray",
        "basefreq": "baseFreq",
        "%noloadloss": "percentNoloadloss",
        "%imag": "percentimag",
        # "conns": "conns",
        "MaxTap": "maxtap",
        "MinTap": "mintap",
        "NumTaps": "numtaps",
    }

    dss.Transformers.Name(obj_name)
    if not dss.CktElement.Enabled():
        return {}
    obj_properties = dss.utils.class_to_dataframe("Transformer").transpose()[
        "Transformer." + obj_name
    ]
    mask_properties = get_regulators(obj_name)
    if not mask_properties:
        return {}

    dss.Transformers.Name(obj_name)

    num_phases = 1 if "Single" in mask_properties.get("type_name") else 3

    for prop in properties_map:
        typhoon_property = properties_map[prop]

        if int(num_phases) == 3:
            if prop == "conns":
                res = obj_properties[prop]
                mask_properties["prim_conn"] = {"delta": "Δ", "wye": "Y"}[res[0]]
                dss.Transformers.Wdg(0)
                if dss.Transformers.Rneut() > 0 and res[0] == "Y":
                    mask_properties["prim_conn"] = "Y - Grounded"
                for i in range(1, len(obj_properties["conns"])):
                    name = f"sec{i}"
                    mask_properties[name + "_conn"] = {"delta": "Δ", "wye": "Y"}[res[i]]
                    dss.Transformers.Wdg(i)
                    mask_properties[name + "_conn"] = "Y - Grounded"

            elif prop == "XHL":
                if mask_properties["num_windings"] == 3:
                    collate = []
                    for con in ["X12", "X23", "X31"]:
                        collate.append(obj_properties[con])
                    mask_properties["XArray"] = collate
                else:
                    mask_properties["XArray"] = [
                        obj_properties["X13"],
                        obj_properties["X23"],
                    ]  # This doesn't feel right...
            else:
                mask_properties[typhoon_property] = obj_properties[prop]
        else:
            mask_properties[typhoon_property] = obj_properties[prop]

    if mask_properties.get("overlapping_parts"):
        for elem in mask_properties["overlapping_parts"]["names"]:
            dss.Text.Command(f"Disable Transformer.{elem}")
        dss.Text.Command(f"Enable Transformer.{obj_name}")
        dss.Text.Command(mask_properties["overlapping_parts"]["replacement_str"])
        dss.Text.Command("ReprocessBuses")
        del mask_properties["overlapping_parts"]

    set_global_basefrequency(mask_properties)

    return mask_properties


def vsource(obj_name: str) -> dict:
    prop_name = "Vsource"
    mask_properties = {}
    properties = {
        "basekv": "basekv",
        "baseMVA": "baseMVA",
        "basefreq": "baseFreq",
        "pu": "pu",
        "angle": "Angle",
        "frequency": "Frequency",
        "R1": "r1",
        "X1": "x1",
        "R0": "r0",
        "X0": "x0",
        "MVAsc3": "mva_sc3",
        "MVAsc1": "mva_sc1",
        "Isc3": "i_sc3",
        "Isc1": "i_sc1",
        "x1r1": "x1r1",
        "x0r0": "x0r0",
    }
    obj_properties = dss.utils.class_to_dataframe("Vsource").transpose()[
        f"Vsource.{obj_name}"
    ]
    for prop in properties:
        typhoon_property = properties[prop]
        mask_properties[typhoon_property] = obj_properties[prop]
    mask_properties["input_method"] = "Z"

    # Global base frequency checkbox
    set_global_basefrequency(mask_properties)

    return mask_properties


def convert_mask_properties(opendss_class: str, obj_name: str) -> dict:
    tse_conversion_warnings = []

    component_processing_functions = {
        "Capacitor": capacitor,
        "Generator": generator,
        "Vsource": vsource,
        "Isource": isource,
        "Line": line,
        "Storage": storage,
        "Load": load,
        "Fault": fault,
        "Transformer": transformer,
        "Bus": bus,
    }
    ############################
    # Standard openDSS blocks #
    ############################
    if opendss_class not in component_processing_functions:
        return {}

    mask_properties = cast(component_processing_functions[opendss_class](obj_name))

    return mask_properties

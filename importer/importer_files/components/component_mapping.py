""" Define the OpenDSS to TSE component mapping"""
import types
import opendssdirect as dss


def transformer(obj_name):
    dss.Circuit.SetActiveElement(f"Transformer.{obj_name}")
    phases = dss.CktElement.NumPhases()
    if phases == 3:
        return "OpenDSS/Three-Phase Transformer"
    elif phases in [1, 2]:
        return "OpenDSS/Single-Phase Transformer"


def get_component_conversion_dict(opendss_class, obj_name):
    supported_components = {
        "Bus": {"type_name": "OpenDSS/Bus"},
        "Line": {"type_name": "OpenDSS/Line"},
        "Transformer": {"type_name": transformer},
        "Load": {"type_name": "OpenDSS/Load"},
        "Vsource": {"type_name": "OpenDSS/Vsource"},
        "Isource": {"type_name": "OpenDSS/Isource"},
        "Fault": {"type_name": "OpenDSS/Fault"},
        "Storage": {"type_name": "OpenDSS/Storage"},
        "Capacitor": {"type_name": "OpenDSS/Capacitor Bank"},
        "Reactor": {"type_name": "OpenDSS/Reactor"}
    }

    return_dict = supported_components.get(opendss_class, {})
    for k, v in return_dict.items():
        # One item only as of now
        if isinstance(v, types.FunctionType):
            comp_type = v(obj_name)
            if comp_type:
                return {k: comp_type}
        else:
            return {k: v}

    # Return at least an empty dictionary
    return {}

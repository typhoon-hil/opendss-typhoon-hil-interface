from ..default_mapping.component_classes import *

classes_dict = {
    "VSOURCE": Vsource,
    "ISOURCE": Isource,
    "FAULT": Fault,
    "CAPACITOR": Capacitor,
    "REACTOR": Reactor,
    "LINE": Line,
    "SWLINE": Switch,
    "CSWLINE": Switch,
    "TRANSFORMER1P": SinglePhaseTransformer,
    "TRANSFORMER3P": ThreePhaseTransformer,
    "LOAD": Load,
    "GENERATOR": Generator,
    "STORAGE": Storage,
    "VSCONVERTER": VSConverter,
    "LINECODE": LineCode,
    "LOADSHAPE": LoadShape,
    "REGCONTROL": RegControl,
    "CONTAINER": Container,
    "COUPLING": Switch,
    "PVSYSTEM": PVSystem,
    "XYCURVE": XYCurve,
    "TSHAPE": TShape,
}


def create_comp_instance(converted_comp_type, comp_data):
    """Instantiates the appropriate class depending on converted_comp_type."""

    return classes_dict[converted_comp_type](converted_comp_type, **comp_data)

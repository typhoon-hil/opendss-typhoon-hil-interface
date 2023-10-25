from ..default_mapping.component_classes import *


def create_comp_instance(converted_comp_type, comp_data):
    """Instantiates the appropriate class depending on converted_comp_type."""

    if converted_comp_type == "VSOURCE":
        return Vsource(converted_comp_type, **comp_data)
    elif converted_comp_type == "ISOURCE":
        return Isource(converted_comp_type, **comp_data)
    elif converted_comp_type == "FAULT":
        return Fault(converted_comp_type, **comp_data)
    elif converted_comp_type == "CAPACITOR":
        return Capacitor(converted_comp_type, **comp_data)
    elif converted_comp_type == "REACTOR":
        return Reactor(converted_comp_type, **comp_data)
    elif converted_comp_type == "LINE":
        return Line(converted_comp_type, **comp_data)
    elif converted_comp_type == "SWLINE":
        return Switch(converted_comp_type, **comp_data)
    elif converted_comp_type == "CSWLINE":
        return Switch(converted_comp_type, **comp_data)
    elif converted_comp_type == "TRANSFORMER1P":
        return SinglePhaseTransformer(converted_comp_type, **comp_data)
    elif converted_comp_type == "TRANSFORMER3P":
        return ThreePhaseTransformer(converted_comp_type, **comp_data)
    elif converted_comp_type == "LOAD":
        return Load(converted_comp_type, **comp_data)
    elif converted_comp_type == "GENERATOR":
        return Generator(converted_comp_type, **comp_data)
    elif converted_comp_type == "STORAGE":
        return Storage(converted_comp_type, **comp_data)
    elif converted_comp_type == "VSCONVERTER":
        return VSConverter(converted_comp_type, **comp_data)
    elif converted_comp_type == "LINECODE":
        return LineCode(converted_comp_type, **comp_data)
    elif converted_comp_type == "LOADSHAPE":
        return LoadShape(converted_comp_type, **comp_data)
    elif converted_comp_type == "REGCONTROL":
        return RegControl(converted_comp_type, **comp_data)
    elif converted_comp_type == "CONTAINER":
        return Container(converted_comp_type, **comp_data)
    elif converted_comp_type == "COUPLING":
        return Switch(converted_comp_type, **comp_data)
    elif converted_comp_type == "PVSYSTEM":
        return PVSystem(converted_comp_type, **comp_data)
    elif converted_comp_type == "XYCURVE":
        return XYCurve(converted_comp_type, **comp_data)
    elif converted_comp_type == "TSHAPE":
        return TShape(converted_comp_type, **comp_data)

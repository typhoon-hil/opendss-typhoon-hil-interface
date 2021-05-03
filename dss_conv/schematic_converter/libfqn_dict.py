def determine_elem(libfqn):
    ''' Uses the lib_fqn JSON entry to return the element type '''

    elem_dict = {
        "Bus":"BUS",
        "Vsource":"VSOURCE",
        "Isource":"ISOURCE",
        "Fault":"FAULT",
        "":"CAPACITOR",
        "Line":"LINE",
        "Manual Switch":"SWLINE",
        "Controlled Switch": "CSWLINE",
        "Single-Phase Transformer":"TRANSFORMER1P",
        "Three-Phase Transformer":"TRANSFORMER3P",
        "":"GICTRANSFORMER",
        "":"GICLINE",
        "Load":"LOAD",
        "Generator":"GENERATOR",
        "VSConverter":"GENERATOR",
        "":"INDMACH012",
        "":"STORAGE",
        "":"CAPCONTROL",
        "":"REGCONTROL",
        "":"ENERGYMETER",
        "":"MONITOR",
    }

    if libfqn in elem_dict.keys():
        return elem_dict.get(libfqn)

def collapse_nodes(libfqn):
    collapse_dict = {
        "Measurements.Current Measurement": {"p_node": ["n_node"]},
        "Measurements.Current RMS": {"p_node": ["n_node"]},
        "Microgrid.Meter.Three-phase Meter": {"A-": ["A+"], "B-": ["B+"], "C-": ["C+"]},
        "Model Partitioning.Core Partitioning.Electrical.Three Phase Core Coupling":
                {"a_in": ["a_out"], "b_in": ["b_out"], "c_in": ["c_out"]},
        "Model Partitioning.Core Partitioning.Electrical.Three Phase TLM Core Coupling":
            {"a_in": ["a_out"], "b_in": ["b_out"], "c_in": ["c_out"]},
        "Model Partitioning.Core Partitioning.Electrical.Three Phase Device Coupling":
            {"a_in": ["a_out"], "b_in": ["b_out"], "c_in": ["c_out"]},
        "Model Partitioning.Core Partitioning.Electrical.Three Phase TLM Device Coupling":
            {"a_in": ["a_out"], "b_in": ["b_out"], "c_in": ["c_out"]},

    #"Fault": {"A1": ["A2"], "B1": ["B2"], "C1": ["C2"]},
    }

    return collapse_dict.get(libfqn)

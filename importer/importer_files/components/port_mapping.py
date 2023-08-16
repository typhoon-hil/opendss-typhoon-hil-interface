def get_port_mapping(opendss_class, obj_name, component_properties):
    # Default port mapping
    port_mapping = {
        1: ["A1", "B1", "C1"],
        2: ["A2", "B2", "C2"],
    }
    mask_properties = component_properties["mask_properties"]
    schematic_properties = component_properties["schematic_properties"]

    if opendss_class == "Bus":
        pass
    elif opendss_class == "Line":
        pass
    elif opendss_class == "Load":
        port_mapping.pop(2)

        tp_connection = mask_properties.get("tp_connection")
        if tp_connection == "Y":
            port_mapping[1].append("N1")
    elif opendss_class == "Vsource":
        port_mapping.pop(2)
    elif opendss_class == "Transformer":
        pass
    elif opendss_class == "Capacitor":
        tp_connection = mask_properties.get("tp_connection")
        if tp_connection is not "Series":
            port_mapping.pop(2)

    return port_mapping

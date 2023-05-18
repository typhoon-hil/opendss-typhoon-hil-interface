# Single phase Neutral to Ground Impedance
# According to OpenDSS manual, the Neutral to Ground impedance is a Resistor (Rneut) in series with a Reactance (Xneut)
# If the reactance Xneut is a positive value, it is implemented as an inductor in series with the Rneut resistor.
# Otherwise, for a negative values of Xneut, it is implemented using a capacitor in series with the resistor.
# If a zero value is provided for Xneut, the inductor or capacitor are replaced by a short-circuit.
# If a zero value is provided for Rneut, the resistor is replaced by a short-circuit.
# https://youtu.be/OI-DZEIlX6g?list=RDgqQertPg9wI


from typhoon.api.schematic_editor.const import ITEM_JUNCTION, ITEM_CONNECTION, ITEM_PORT, ITEM_COMPONENT

M_PI = 3.14159265358979323846       # pi value constant

def build_gnd_z(mdl, container_handle):
    comp_handle = mdl.get_parent(container_handle)

    x_neut = float(mdl.get_property_value(mdl.prop(container_handle, "Xneut")))
    f = mdl.get_property_value(mdl.prop(container_handle, "f"))
    r_neut = float(mdl.get_property_value(mdl.prop(container_handle, "Rneut")))
    omega = float(f)*2.0*M_PI   # Convert to float and [Hz] -> [rad/s]

    port_n = mdl.get_item("N", parent=comp_handle, item_type="port")
    port_g = mdl.get_item("G", parent=comp_handle, item_type="port")
    jun_jrx = mdl.get_item("JRX", parent=comp_handle, item_type="junction")
    Xneut = mdl.get_item("Xneut", parent=comp_handle, item_type=ITEM_COMPONENT)
    #conn_g = mdl.find_connections(port_g, jun_jrx)
    conn_g = mdl.get_item("Conn_JG", parent=comp_handle, item_type=ITEM_CONNECTION)
    conn_n = mdl.get_item("Conn_NJ", parent=comp_handle, item_type=ITEM_CONNECTION)
    Rneut = mdl.get_item("Rneut", parent=comp_handle, item_type="component")

    # First, remove the components and connections that may exist
    # And after build the circuit according the mask settings
    if Rneut:
        mdl.delete_item(Rneut)

    # if the inductor or the capacitor is present, delete it
    if Xneut:
        mdl.delete_item(Xneut)

    if conn_g:
        mdl.delete_item(conn_g) #mdl.delete_item(conn_g[0])

    if conn_n:
        mdl.delete_item(conn_n)

    # Now implement the reactive component, a capacitor or an inductor, depending on the signal of the x_neut
    if x_neut > 0.0:
        l_val = x_neut/omega
        Xneut = mdl.create_component("Inductor", parent=comp_handle, name="Xneut", position=(8192, 8256), rotation="right")
        mdl.set_property_value(mdl.prop(Xneut, "inductance"), l_val)
        mdl.create_connection(mdl.term(Xneut, "p_node"), jun_jrx, name="Conn_LJ")
        mdl.create_connection(mdl.term(Xneut, "n_node"), port_g, name = "Conn_LG")

    elif x_neut < 0.0:
        x_neut = abs(x_neut)
        c_val = 1.0/(x_neut*omega)
        Xneut = mdl.create_component("Capacitor", parent=comp_handle, name="Xneut", position=(8192, 8256), rotation="right")
        mdl.set_property_value(mdl.prop(Xneut, "capacitance"), c_val)
        mdl.create_connection(mdl.term(Xneut, "p_node"), jun_jrx, name = "Conn_CJ")
        mdl.create_connection(mdl.term(Xneut, "n_node"), port_g, name = "Conn_CG")

    else:
        # if the reactance is zero, just connect the junction JRX to the G port.
        mdl.create_connection(jun_jrx, port_g, name = "Conn_JG")

    # Now take care of the resistor component. If the value of Rneut is zero,
    # replace the resistor by a short-circuit between N port and the junction JRX
    if r_neut > 0.0:
        Rneut = mdl.create_component("Resistor", parent=comp_handle, name="Rneut", position=(8192, 8128), rotation="right")
        mdl.create_connection(mdl.term(Rneut, "p_node"), port_n, name="Conn_RN")
        mdl.create_connection(mdl.term(Rneut, "n_node"), jun_jrx, name="Conn_RJ")
        mdl.set_property_value(mdl.prop(Rneut, "resistance"), r_neut)

    # if the Rneut value is <= 0, short-circuit the path
    else:
        mdl.create_connection(port_n, jun_jrx, "Conn_NJ")




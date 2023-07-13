# Single phase Neutral to Ground Impedance
# According to OpenDSS manual, the Neutral to Ground impedance is a
# Resistor (Rneut) in series with a Reactance (Xneut)
# If the reactance Xneut is a positive value, it is implemented as an
# inductor in series with the Rneut resistor.
# Otherwise, for a negative values of Xneut, it is implemented using
# a capacitor in series with the resistor.
# If a zero value is provided for Xneut,
# the inductor or capacitor are replaced by a short-circuit.
# If a zero value is provided for Rneut, the resistor is replaced by a short-circuit.

M_PI = 3.14159265358979323846       # pi value constant


def build_gnd_z(mdl, mask_handle):
    comp_handle = mdl.get_parent(mask_handle)

    # Values
    x = mdl.get_property_value(mdl.prop(mask_handle, "Xneut"))
    r = mdl.get_property_value(mdl.prop(mask_handle, "Rneut"))
    f = mdl.get_property_value(mdl.prop(mask_handle, "f"))
    omega = f * 2.0 * M_PI  # Convert to float and [Hz] -> [rad/s]

    # Components
    port_g = mdl.get_item("G", parent=comp_handle, item_type="port")
    jun_jrx = mdl.get_item("JRX", parent=comp_handle, item_type="junction")
    x_neut_comp = mdl.get_item("Xneut", parent=comp_handle, item_type="component")
    r_neut_comp = mdl.get_item("Rneut", parent=comp_handle, item_type="component")

    #
    # Negative values of R become and open circuit
    #
    if r < 0:
        mdl.set_property_value(mdl.prop(r_neut_comp, "resistance"), "inf")
    elif r == 0:
        mdl.set_property_value(mdl.prop(r_neut_comp, "resistance"), 1e-9)

    #
    # The reactive component is either a capacitor or an inductor,
    # depending on the sign of x
    #

    if x == 0.0:
        # When zero, replace with a short-circuiting wire
        mdl.delete_item(x_neut_comp)
        mdl.create_connection(jun_jrx, port_g, name="Conn_LJ")
    elif x > 0.0:
        # Set the new inductance value
        l_val = x/omega
        mdl.set_property_value(mdl.prop(x_neut_comp, "inductance"), l_val)
    else:
        # Replace the inductor with a capacitor
        mdl.delete_item(x_neut_comp)
        cap = mdl.create_component("Capacitor", parent=comp_handle, name="Xneut",
                                   position=(8192, 8256), rotation="right")

        # Connect the capacitor
        mdl.create_connection(jun_jrx, mdl.term(cap, "p_node"))
        mdl.create_connection(port_g, mdl.term(cap, "n_node"))

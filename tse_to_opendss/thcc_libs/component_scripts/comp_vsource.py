import numpy as np
from math import log10, floor


x0, y0 = (8192, 8192)


def toggle_frequency_prop(mdl, container_handle, init=False):
    frequency_prop = mdl.prop(container_handle, "BaseFreq")
    global_frequency_prop = mdl.prop(container_handle, "global_basefreq")
    use_global = mdl.get_property_disp_value(global_frequency_prop)

    if use_global:
        if "simdss_basefreq" in mdl.get_ns_vars():
            mdl.set_property_disp_value(frequency_prop, mdl.get_ns_var("simdss_basefreq"))
            mdl.hide_property(frequency_prop)
        else:
            mdl.set_property_disp_value(global_frequency_prop, False)
            mdl.info("Add a SimDSS component to define the global frequency value.")
    else:
        mdl.show_property(frequency_prop)


def update_connections(mdl, container_handle, ports):
    comp_handle = mdl.get_parent(container_handle)

    # Source handles
    va = mdl.get_item("Va", parent=comp_handle)
    vb = mdl.get_item("Vb", parent=comp_handle)
    vc = mdl.get_item("Vc", parent=comp_handle)

    ground_connected = mdl.get_property_value(mdl.prop(container_handle, "ground_connected"))
    if ground_connected:
        gnd = mdl.create_component(
            "core/Ground",
            name="gnd1",
            parent=comp_handle,
            position=(8000, 8400)
        )

        mdl.create_connection(mdl.term(gnd, "node"), mdl.term(va, 'n_node'))
        mdl.create_connection(mdl.term(gnd, "node"), mdl.term(vb, 'n_node'))
        mdl.create_connection(mdl.term(gnd, "node"), mdl.term(vc, 'n_node'))
    else:
        # Ground handle
        gnd = mdl.get_item("gnd1", parent=comp_handle)
        mdl.delete_item(gnd)

        mdl.create_connection(ports.get("A2"), mdl.term(va, 'n_node'))
        mdl.create_connection(ports.get("B2"), mdl.term(vb, 'n_node'))
        mdl.create_connection(ports.get("C2"), mdl.term(vc, 'n_node'))


def port_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):
    comp_handle = mdl.get_parent(container_handle)
    deleted_ports = []
    created_ports = {}

    ground_connected = mdl.get_property_value(mdl.prop(container_handle, "ground_connected"))
    if ground_connected:
        # Delete A2-C2 ports
        a2 = mdl.get_item("A2", parent=comp_handle, item_type="port")
        b2 = mdl.get_item("B2", parent=comp_handle, item_type="port")
        c2 = mdl.get_item("C2", parent=comp_handle, item_type="port")

        for port in [a2, b2, c2]:
            if port:
                deleted_ports.append(mdl.get_name(port))
                mdl.delete_item(port)

    else:

        a2 = mdl.create_port(
            name="A2",
            parent=comp_handle,
            terminal_position=[-32, -32],
            position=(x0 - 200, y0 - 100)
        )
        b2 = mdl.create_port(
            name="B2",
            parent=comp_handle,
            terminal_position=[-32, 0],
            position=(x0 - 200, y0 - 0)
        )
        c2 = mdl.create_port(
            name="C2",
            parent=comp_handle,
            terminal_position=[-32, 32],
            position=(x0 - 200, y0 + 100)
        )

        created_ports.update({
            "A2": a2,
            "B2": b2,
            "C2": c2
        })

    return created_ports, deleted_ports


def mask_dialog_dynamics(mdl, container_handle, caller_prop_handle=None, init=False):

    old_value = None
    new_value = None
    prop_name = None
    if caller_prop_handle:
        old_value = mdl.get_property_value(caller_prop_handle)
        new_value = mdl.get_property_disp_value(caller_prop_handle)
        prop_name = mdl.get_name(caller_prop_handle)

    # Property Routines:
    # ------------------------------------------------------------------------------------------------------------------
    # Global Base Frequency
    # ------------------------------------------------------------------------------------------------------------------
    if prop_name == "global_basefreq":
        toggle_frequency_prop(mdl, container_handle)

    # ------------------------------------------------------------------------------------------------------------------
    # Input Method Frequency
    # ------------------------------------------------------------------------------------------------------------------
    elif prop_name == "input_method":

        si_names = ["r1", "r0", "x1", "x0"]
        si_props = [mdl.prop(container_handle, name) for name in si_names]
        pu_names = ["r1_pu", "r0_pu", "x1_pu", "x0_pu"]
        pu_props = [mdl.prop(container_handle, name) for name in pu_names]
        mvasc_names = ["mva_sc3", "mva_sc1"]
        mvasc_props = [mdl.prop(container_handle, name) for name in mvasc_names]
        isc_names = ["i_sc3", "i_sc1"]
        isc_props = [mdl.prop(container_handle, name) for name in isc_names]
        xr_names = ["x1r1", "x0r0"]
        xr_props = [mdl.prop(container_handle, name) for name in xr_names]

        v_base = float(mdl.get_property_disp_value(mdl.prop(container_handle, "basekv"))) * 1e3
        s_base = float(mdl.get_property_disp_value(mdl.prop(container_handle, "baseMVA"))) * 1e6
        z_base = v_base*v_base/s_base
        si_values = [float(mdl.get_property_disp_value(prop)) for prop in si_props]
        z1 = si_values[0] + si_values[2]*1j
        z0 = si_values[1] + si_values[3]*1j
        zp = z0/3 + (2/3)*z1

        if new_value == "Z":
            # Hide/Show properties
            [mdl.show_property(prop) for prop in si_props]
            [mdl.hide_property(prop) for prop in pu_props + mvasc_props + isc_props + xr_props]
        elif new_value == "Zpu":
            # Hide/Show properties
            [mdl.show_property(prop) for prop in pu_props]
            [mdl.hide_property(prop) for prop in si_props + mvasc_props + isc_props + xr_props]
        elif new_value == "MVAsc":
            # Hide/Show properties
            [mdl.show_property(prop) for prop in mvasc_props + xr_props]
            [mdl.hide_property(prop) for prop in si_props + pu_props + isc_props]
        elif new_value == "Isc":
            # Hide/Show properties
            [mdl.show_property(prop) for prop in isc_props + xr_props]
            [mdl.hide_property(prop) for prop in si_props + pu_props + mvasc_props]


def define_icon(mdl, container_handle):
    ground_connected = mdl.get_property_value(mdl.prop(container_handle, "ground_connected"))
    if ground_connected:
        mdl.set_component_icon_image(container_handle, 'images/vsource_gnd.svg')
    else:
        mdl.set_component_icon_image(container_handle, 'images/vsource.svg')


def sc_notation(val, num_decimals=2, exponent_pad=2):
    exponent_template = "{:0>%d}" % exponent_pad
    mantissa_template = "{:.%df}" % num_decimals

    order_of_magnitude = floor(log10(abs(val)))
    nearest_lower_third = 3 * (order_of_magnitude // 3)
    adjusted_mantissa = val * 10 ** (-nearest_lower_third)
    adjusted_mantissa_string = mantissa_template.format(adjusted_mantissa)
    adjusted_exponent_string = "+-"[nearest_lower_third < 0] + exponent_template.format(abs(nearest_lower_third))
    return adjusted_mantissa_string + "e" + f"{int(adjusted_exponent_string)}"


def get_r_l_matrices(mdl, container_handle):

    comp_handle = mdl.get_parent(container_handle)
    z_si_names = ["r1", "x1", "r0", "x0"]
    z_si_props = [mdl.prop(container_handle, prop_name) for prop_name in z_si_names]
    z_pu_names = ["r1_pu", "x1_pu", "r0_pu", "x0_pu"]
    z_pu_props = [mdl.prop(container_handle, prop_name) for prop_name in z_pu_names]
    basekv = mdl.get_property_value(mdl.prop(container_handle, "basekv"))
    basemva = mdl.get_property_value(mdl.prop(container_handle, "baseMVA"))
    z_base = basekv*basekv/basemva
    basefreq = mdl.get_property_value(mdl.prop(container_handle, "BaseFreq"))

    input_method = mdl.get_property_value(mdl.prop(container_handle, "input_method"))
    if input_method == "Z":
        r1, x1, r0, x0 = [mdl.get_property_value(prop) for prop in z_si_props]
    elif input_method == "Zpu":
        r1, x1, r0, x0 = [mdl.get_property_value(prop)*z_base for prop in z_si_props]
    elif input_method == "MVAsc":
        mva_sc3 = mdl.get_property_value(mdl.prop(container_handle, "mva_sc3"))
        mva_sc1 = mdl.get_property_value(mdl.prop(container_handle, "mva_sc1"))
        x1r1 = mdl.get_property_value(mdl.prop(container_handle, "x1r1"))
        x0r0 = mdl.get_property_value(mdl.prop(container_handle, "x0r0"))
        z1 = basekv*basekv/mva_sc3
        r1 = np.cos(np.arctan(x1r1))*z1
        x1 = r1*x1r1
        i_sc1 = mva_sc1*1e3/(np.sqrt(3)*basekv)
        # from the DSS Source Code
        proots = np.roots([1+x0r0*x0r0, 4*(r1+x1*x0r0), 4*(r1*r1 + x1*x1)-np.power(1e3*basekv*3/(np.sqrt(3)*i_sc1), 2)])
        r0 = proots.max()
        x0 = r0 * x0r0
    elif input_method == "Isc":
        i_sc3 = mdl.get_property_value(mdl.prop(container_handle, "i_sc3"))
        i_sc1 = mdl.get_property_value(mdl.prop(container_handle, "i_sc1"))
        x1r1 = mdl.get_property_value(mdl.prop(container_handle, "x1r1"))
        x0r0 = mdl.get_property_value(mdl.prop(container_handle, "x0r0"))
        z1 = 1e3*basekv/(np.sqrt(3)*i_sc3)
        r1 = np.cos(np.arctan(x1r1))*z1
        x1 = r1*x1r1
        # from the DSS Source Code
        proots = np.roots([1+x0r0*x0r0, 4*(r1+x1*x0r0), 4*(r1*r1 + x1*x1)-np.power(1e3*basekv*3/(np.sqrt(3)*i_sc1), 2)])
        r0 = proots.max()
        x0 = r0 * x0r0

    if r0 <= 0 or x0 <= 0:
        msg = "R0 or X0 is negative."
        mdl.error(msg, kind='Bad input arguments', context=comp_handle)
    elif r0 < r1 or x0 < x1:
        msg = "Zero Sequence impedance is lower than positive sequence. " \
              "The source have negative mutual impedances."
        mdl.warning(msg, kind='Bad input arguments', context=comp_handle)


    rs = (2*r1 + r0)/3
    xs = (2*x1 + x0)/3
    ls = xs/(2*np.pi*basefreq)
    rm = (r0 - r1)/3
    xm = (x0 - x1)/3
    lm = xm/(2*np.pi*basefreq)

    rmatrix = [[rs, rm, rm], [rm, rs, rm], [rm, rm, rs]]
    lmatrix = [[ls, lm, lm], [lm, ls, lm], [lm, lm, ls]]
    # For two-phase systems, we can use just the 2x2 matrix from that

    return rmatrix, lmatrix


def get_source_values(mdl, container_handle):

    basekv = mdl.get_property_value(mdl.prop(container_handle, "basekv"))
    pu = mdl.get_property_value(mdl.prop(container_handle, "pu"))
    Angle = mdl.get_property_value(mdl.prop(container_handle, "Angle"))
    Frequency = mdl.get_property_value(mdl.prop(container_handle, "Frequency"))

    source_voltage = 1e3*basekv*pu/np.sqrt(3)
    source_phase = Angle
    source_frequency = Frequency

    return source_voltage, source_phase, source_frequency

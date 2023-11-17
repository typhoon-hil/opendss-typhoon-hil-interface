from typhoon.api.impl.schematic_editor import multiline_to_sld as sld
import importlib

importlib.reload(sld)

def convert_to_sld(mdl, mask_handle, sld_info):
    """
    Converts the multiline component to single-line representation

    See multiline_to_sld docstring for more information on sld_info
    """

    comp_handle = mdl.get_parent(mask_handle)

    port_info, tag_info, terminal_positions = sld_info

    terminal_positions = sld.multiline_to_sld(
        mdl,
        comp_handle,
        port_info,
        tag_info_dict=tag_info
    )

    return terminal_positions


def convert_to_multiline(mdl, mask_handle, sld_info, hide_names=True):
    """
    Converts the single-line represented component to multiline

    See multiline_to_sld docstring for more information on sld_info
    """

    comp_handle = mdl.get_parent(mask_handle)

    port_info, tag_info, terminal_positions = sld_info

    sld.multiline_to_sld(
        mdl,
        comp_handle,
        port_info,
        tag_info_dict=tag_info,
        reverse=True,
        terminal_positions=terminal_positions
    )

    #
    # Hide names of restored ports
    #
    if hide_names:
        for bus_port_info in port_info.values():
            multiline_ports = bus_port_info.get("multiline_ports")

            for port_name in multiline_ports:
                port_handle = mdl.get_item(port_name, parent=comp_handle, item_type="port")
                mdl.set_port_properties(port_handle, hide_term_label=True)


def set_component_library_version(mdl, mask_handle):
    ver = 51  # 0.5.0 = 50, 1.1.5 = 115
    version_prop = mdl.prop(mask_handle, "library_version")
    mdl.set_property_value(version_prop, ver)


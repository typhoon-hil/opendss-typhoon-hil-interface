from typhoon.api.impl.schematic_editor import multiline_to_sld as sld
import importlib

importlib.reload(sld)


def convert_to_sld(mdl, mask_handle, sld_info):
    """
    Converts the multiline component to single-line representation

    See multiline_to_sld docstring for more information on sld_info
    """

    comp_handle = mdl.get_parent(mask_handle)
    importlib.reload(sld)

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
    importlib.reload(sld)

    port_info, tag_info, terminal_positions = sld_info

    sld.multiline_to_sld(
        mdl,
        comp_handle,
        port_info,
        tag_info_dict=tag_info,
        reverse=True,
        terminal_positions=terminal_positions
    )


def is_float(str_input):
    if "." not in str_input:
        return False

    new_str = str_input.replace(".", "")
    new_str = new_str.replace("e", "")
    new_str = new_str.replace("-", "")
    new_str = new_str.replace("+", "")
    if new_str.isnumeric():
        return True
    else:
        return False


def set_component_library_version(mdl, mask_handle):
    ver = 51  # 0.5.0 = 50, 1.1.5 = 115
    version_prop = mdl.prop(mask_handle, "library_version")
    mdl.set_property_value(version_prop, ver)


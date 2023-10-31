from typhoon.api.impl.schematic_editor import multiline_to_sld as sld


def convert_to_sld(mdl, mask_handle, sld_info):
    comp_handle = mdl.get_parent(mask_handle)

    port_info, tag_info, terminal_positions = sld_info

    terminal_positions = sld.multiline_to_sld(
        mdl,
        comp_handle,
        port_info,
        tag_info_dict=tag_info
    )

    return terminal_positions


def convert_to_multiline(mdl, mask_handle, sld_info):
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
import os
import pathlib
import re
from typhoon.api.schematic_editor import SchematicAPI


def generate_api_calls(component_list):
    # Path to example model
    model_path = str(pathlib.Path(__file__).parent.joinpath("all_components.tse"))

    # Load model
    mdl = SchematicAPI()
    mdl.reload_libraries()
    mdl.load(model_path)

    default_values_dict = {}  # Properties default values
    for comp in mdl.get_items(item_type="masked_component"):
        # Get properties default values
        all_props = mdl.get_items(parent=comp, item_type="property")
        default_values_dict[mdl.get_name(comp).replace(" ", "_").replace("-", "_")] = \
            {mdl.get_name(prop): mdl.get_property_default_value(prop) for prop in all_props}
        # Unlink component
        mdl.unlink_component(comp)

    complete_string = mdl.model_to_api()

    with open(f"output.txt", 'w', encoding="utf-8") as f:
        f.write(complete_string)

    ignored_properties_lists = {
        "Vsource": [],
        "Line": [],
        "Load": [],
        "Capacitor_Bank": [],
        "Controlled_Switch": [],
        "Fault": [],
        "Isource": [],
        "Three_Phase_Transformer": [],
        "Single_Phase_Transformer": [],
        "Generator": [],
        "Storage": [],
        "VSConverter": []
    }

    ignored_edited_lists = {
        "Vsource": [],
        "Line": [],
        "Load": [],
        "Capacitor_Bank": [],
        "Controlled_Switch": [],
        "Fault": [],
        "Isource": [],
        "Three_Phase_Transformer": [],
        "Single_Phase_Transformer": [],
        "Generator": [],
        "Storage": [],
        "VSConverter": []
    }

    ignored_button_lists = {
        "Vsource": [],
        "Line": [],
        "Load": [],
        "Capacitor_Bank": [],
        "Controlled_Switch": [],
        "Fault": [],
        "Isource": [],
        "Three_Phase_Transformer": [],
        "Single_Phase_Transformer": [],
        "Generator": [],
        "Storage": [],
        "VSConverter": []
    }

    port_update_lists = {
        "Vsource": ["ground_connected"],
        "Line": ["input_type", "phases", "dC1", "dC0", "cmatrix", "coupling"],
        "Load": ["conn_type", "ground_connected", "phases", "Pow_ref_s", "S_Ts_mode"],
        "Capacitor_Bank": ["tp_connection", "phases"],
        "Controlled_Switch": ["enable_fb_out", "phases"],
        "Fault": ["type"],
        "Isource": [],
        "Three_Phase_Transformer": ["num_windings", "prim_conn", "grounded_prim", "sec1_conn",
                                    "grounded_sec1", "sec2_conn", "grounded_sec2",
                                    "sec3_conn", "grounded_sec3"],
        "Single_Phase_Transformer": ["num_windings"],
        "Generator": ["S_Ts_mode", "gen_ts_en", "Init_En"],
        "Storage": [],
        "VSConverter": []
    }

    icon_update_lists = {
        "Vsource": ["ground_connected"],
        "Line": ["phases"],
        "Load": ["conn_type", "ground_connected", "phases", "Pow_ref_s", "S_Ts_mode", "Ts_switch"],
        "Capacitor_Bank": ["tp_connection", "phases"],
        "Controlled_Switch": ["initial_state", "phases"],
        "Fault": ["type"],
        "Isource": [],
        "Three_Phase_Transformer": ["num_windings", "prim_conn", "grounded_prim", "sec1_conn",
                                    "grounded_sec1", "sec2_conn", "grounded_sec2",
                                    "sec3_conn", "grounded_sec3"],
        "Single_Phase_Transformer": ["num_windings"],
        "Generator": ["S_Ts_mode", "gen_ts_en", "Init_En"],
        "Storage": [],
        "VSConverter": []
    }

    for comp_type in component_list:
        # create_property
        results_create = re.findall(
            rf"_{comp_type}_mask_[A-z0-9 \-_]+ = mdl.create_property\([\S\s]*?=[\S\s]*?\n\)\n*?",
            complete_string, flags=re.MULTILINE | re.ASCII)

        # property_edited handlers
        results_edited_handlers = re.findall(rf"_{comp_type}_mask_[A-z0-9-_ ]+value_edited = \"\"\"[\s\S]*?_edited\)",
                                             complete_string, flags=re.MULTILINE | re.ASCII)

        # button_clicked handlers
        results_button = re.findall(
            rf"_{comp_type}_mask_[A-z0-9-_ ]+_button_clicked = [\S\s]*?=[\S\s]*?_button_clicked\)\n*?",
            complete_string, flags=re.MULTILINE | re.ASCII)

        # initialization ports
        init_ports = re.findall(
            rf"^_{comp_type}_[A-z0-9-_ ]+ = mdl\.create_port\(\n(?:    .+=.+\,\n)+    parent=_{comp_type}\,\n(?:    .+=.+\,*\n)+\)",
            complete_string, flags=re.MULTILINE | re.ASCII)

        # generate property_changed handlers
        changed_handler_lines = []
        port_list = port_update_lists.get(comp_type, [])
        icon_list = icon_update_lists.get(comp_type, [])
        for prop in port_list + [value for value in icon_list if value not in port_list]:
            ig_load = True if comp_type in ["Three_Phase_Transformer", "Single_Phase_Transformer"] else False # Ignore port_dynamics on model load
            changed_handler_lines.append(f'    _{comp_type}_mask_{prop}_property_value_changed = """\n'
                                 '    comp_script = return_comp_script(mdl, container_handle)\n'
                                 f'{"    if not new_value == old_value: # If the model is not being loaded." + chr(10) if ig_load else ""}'
                                 f'{("    " if ig_load else "")}{"    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)" + chr(10) if prop in port_list else  ""}'
                                 f'{"    mdl.refresh_icon(container_handle)" + chr(10) if prop in icon_list else  ""}'
                                 '    """\n'
                                 f'    mdl.set_handler_code(_{comp_type}_mask_{prop}, "property_value_changed",\n'
                                 f'                         _{comp_type}_mask_{prop}_property_value_changed)\n\n')


        with open(f"../{comp_type.lower()}_container.py", 'w', encoding="utf-8") as f:
            f.write(f"def update_properties(mdl, _{comp_type}_mask):\n")

            f.write("    ## PROPERTIES\n\n")
            f.writelines(["    " + sep + "\n" for line in results_create for sep in line.splitlines()
                          if not any(prop in line for prop in ignored_properties_lists.get(comp_type))])

            f.write("\n\n    ## SET PROPERTIES TO DEFAULT VALUES\n\n")
            f.writelines([f'    mdl.set_property_value(mdl.prop(_{comp_type}_mask, "{prop_name}"), "{prop_value}")\n'
                          for prop_name, prop_value in {k: v for k, v in default_values_dict[comp_type].items()
                                                        if k not in ignored_properties_lists.get(comp_type)}.items()])

            f.write("\n\n    ## EDITED HANDLERS\n\n")
            f.writelines(["    " + sep + "\n" for line in results_edited_handlers for sep in line.splitlines()
                          if not any(prop in line for prop in ignored_edited_lists.get(comp_type))])

            f.write("\n\n    ## BUTTON HANDLERS\n\n")
            f.writelines(["    " + sep + "\n" for line in results_button for sep in line.splitlines()
                          if not any(prop in line for prop in ignored_button_lists.get(comp_type))])

            f.write("\n\n    ## CHANGED HANDLERS\n\n")
            f.writelines(changed_handler_lines)

            f.write(f"def ports_initialization(mdl, _{comp_type}_mask):\n")
            f.write(f"    _{comp_type} = mdl.get_parent(_{comp_type}_mask)\n")
            f.write("\n\n    ## CREATE INITIALIZATION PORTS \n\n")
            f.writelines(["    " + sep + "\n" for line in init_ports for sep in line.splitlines()])

    mdl.close_model()


component_list = [c.replace(" ", "_").replace("-", "_") for c in [
    "Vsource",
    "Load",
    "Line",
    "Capacitor Bank",
    "Controlled Switch",
    "Fault",
    "Isource",
    "Three-Phase Transformer",
    "Single-Phase Transformer",
    "Generator",
    "Storage",
    "VSConverter"
]]

generate_api_calls(component_list)

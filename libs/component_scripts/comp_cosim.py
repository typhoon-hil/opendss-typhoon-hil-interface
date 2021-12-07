def pre_compilation(mdl, mask_handle):

    comp_handle = mdl.get_parent(mask_handle)
    model_path = mdl.get_property_value(mdl.prop(mask_handle, "model_path"))
    saved_selected_interface_points = mdl.get_property_value(mdl.prop(mask_handle, "saved_selected_interface_points"))
    saved_position_dict = mdl.get_property_value(mdl.prop(mask_handle, "saved_position_dict"))

    for item in mdl.get_items():
        if item.item_type == "masked_component"  and not item == comp_handle:
            type_name = mdl.get_component_type_name(item)
            if type_name == "Co-simulation Interface":
                raise Exception("Only one Co-simulation component is supported.")
                pass

    mdl.set_ns_var("dsscosim-tse_file_path", mdl.get_model_file_path())
    mdl.set_ns_var("dsscosim-dss_model_path", model_path)
    mdl.set_ns_var("dsscosim-component_name", mdl.get_name(mdl.get_parent(mask_handle)))
    mdl.set_ns_var("dsscosim-saved_selected_interface_points", saved_selected_interface_points)
    mdl.set_ns_var("dsscosim-saved_position_dict", saved_position_dict)

def open_mask(mdl, mask_handle, cosim):
    _, selected_interface_points = get_saved_properties(mdl, mask_handle)
    dss_model_path = mdl.get_property_value(mdl.prop(mask_handle, "model_path"))
    execution_rate = mdl.get_property_disp_value(mdl.prop(mask_handle, "execution_rate"))

    dss = load_dss_api(mdl, mask_handle)
    cosim_window = cosim.CoSimulation(dss, selected_interface_points, dss_model_path, execution_rate)
    if cosim_window.exec():
        new_selected_points = cosim_window.selected_interface_points
        _, selected_interface_points = get_saved_properties(mdl, mask_handle)
        if not selected_interface_points == new_selected_points:
            mdl.set_property_value(mdl.prop(mask_handle, "saved_selected_interface_points"), str(new_selected_points))
            apply_configuration(mdl, mask_handle, dss)
        mdl.set_property_value(mdl.prop(mask_handle, "model_path"), cosim_window.dss_model)
        mdl.set_property_value(mdl.prop(mask_handle, "f"), cosim_window.frequency)
        mdl.set_property_value(mdl.prop(mask_handle, "execution_rate"), cosim_window.execution_rate)
        mdl.refresh_icon(mask_handle)

def get_saved_properties(mdl, mask_handle):
    import ast

    saved_position_dict_prop = mdl.prop(mask_handle, "saved_position_dict")
    saved_selected_interface_points_prop = mdl.prop(mask_handle, "saved_selected_interface_points")

    position_dict = ast.literal_eval(mdl.get_property_value(saved_position_dict_prop))
    try:
        selected_interface_points = ast.literal_eval(mdl.get_property_value(saved_selected_interface_points_prop))
        # literal_eval may return ints
        if isinstance(selected_interface_points, int):
            selected_interface_points = [str(selected_interface_points)]
        else:
            selected_interface_points = [str(point) for point in selected_interface_points]
    except:
        selected_interface_points = [mdl.get_property_value(saved_selected_interface_points_prop)]


    return [position_dict, selected_interface_points]

def load_dss_api(mdl, mask_handle):
    import typhoon.api.hil as hil
    import os, sys

    SW_VERS = hil.get_sw_version()
    appdata_path = os.getenv('APPDATA')
    dss_direct_path = fr"{appdata_path}\typhoon\{SW_VERS}\python_portables\python3_portable\Lib\site-packages"
    if not dss_direct_path in sys.path:
        sys.path.append(dss_direct_path)

    import opendssdirect as dss

    return dss

def restore_configuration(mdl, mask_handle):
    position_dict, _ = get_saved_properties(mdl, mask_handle)

    for phase_id in position_dict.keys():
        create_phase(mdl, mask_handle, phase_id, position_dict)


def apply_configuration(mdl, mask_handle, api):
    comp_handle = mdl.get_parent(mask_handle)
    saved_position_dict_prop = mdl.prop(mask_handle, "saved_position_dict")

    _, selected_interface_points = get_saved_properties(mdl, mask_handle)

    position_dict = {}

    # Delete all
    for item in mdl.get_items(parent=comp_handle):
        keep_list = ["vref", "gnd_tag", "gnd1", "Goto2", "Goto1", "f"]
        if not item.item_type in ["connection", "junction"]:
            if not mdl.get_name(item) in keep_list:
                mdl.delete_item(item)

    for interface_point in selected_interface_points:
        if interface_point and not interface_point == "None":
            dss = api
            dss.Circuit.SetActiveBus(interface_point)
            n_phases = len(dss.Bus.Nodes())

            start_x = 1000
            end_x = 15000
            for x in range(start_x, end_x, 400):
                all_x = tuple(x + n * 400 for n in range(n_phases))

                if not position_dict:  # First added
                    break

                occupied_spaces = set()
                for pid, val in position_dict.items():
                    occupied_spaces = occupied_spaces | {val.get('x')}
                if set(all_x) & occupied_spaces:
                    pass  # At least one space is occupied
                else:
                    break

            for phase in range(1, n_phases + 1):
                x = all_x[phase - 1]
                phase_id = f"{interface_point}-{phase}"
                position_dict.update({phase_id: {"x": x, "phase": phase}})
                create_phase(mdl, mask_handle, phase_id, position_dict)

    mdl.set_property_value(saved_position_dict_prop, str(position_dict))


def create_phase(mdl, mask_handle, phase_id, position_dict):
    y0 = 8192
    x0 = position_dict.get(phase_id).get("x")
    comp_handle = mdl.get_parent(mask_handle)

    # Components
    components_dict = {
        f"{phase_id}": {"pos": (0, 0), "comp_type": "port", "rot": "right", "flip": "flip_none"},
        f"imeas {phase_id}": {"pos": (0, 168), "comp_type": "Current Measurement", "rot": "right",
                              "flip": "flip_horizontal"},
        f"V {phase_id}": {"pos": (0, 320), "comp_type": "Signal Controlled Sinusoidal Voltage Source", "rot": "up",
                          "flip": "flip_none"},
        f"gnd {phase_id}": {"pos": (0, 664), "comp_type": "tag", "rot": "left", "tagname": "gnd", "flip": "flip_none"},
        f"Vph {phase_id}": {"pos": (-104, 384), "comp_type": "SCADA Input", "rot": "up", "flip": "flip_none"},
        f"f {phase_id}": {"pos": (-104, 320), "comp_type": "tag", "rot": "up", "dir": "out", "tagname": "f",
                          "flip": "flip_none"},
        f"Vref {phase_id}": {"pos": (-70, 80), "comp_type": "tag", "rot": "up", "dir": "out", "tagname": "vref",
                             "flip": "flip_horizontal"},
        f"Vmag {phase_id}": {"pos": (-104, 256), "comp_type": "SCADA Input", "rot": "up", "flip": "flip_none"},
        f"Phasor {phase_id}": {"pos": (-160, 160), "comp_type": "Single Phase Phasor", "rot": "up",
                               "flip": "flip_horizontal"},
        f"Imag {phase_id}": {"pos": (-272, 104), "comp_type": "Probe", "rot": "up", "flip": "flip_horizontal"},
        f"Iph {phase_id}": {"pos": (-272, 216), "comp_type": "Probe", "rot": "up", "flip": "flip_horizontal"}
    }
    connections_dict = {
        f"imeas {phase_id}": {"p_node": (phase_id, 'port')},
        f"Phasor {phase_id}": {
            "in": (f'imeas {phase_id}', "out"),
            "in_ref": (f'Vref {phase_id}', "port"),
            "out": (f'Imag {phase_id}', "in"),
            "phase": (f'Iph {phase_id}', "in")
        },
        f"V {phase_id}": {
            "p": (f'imeas {phase_id}', "n_node"),
            "n": (f'gnd {phase_id}', "port"),
            "Rms": (f'Vmag {phase_id}', "out"),
            "f": (f'f {phase_id}', "port"),
            "Ph": (f'Vph {phase_id}', "out")
        }
    }

    component_handles = {}
    for comp, props in components_dict.items():
        comp_type = props.get("comp_type")
        if comp_type == "port":
            ph_port = mdl.create_port(parent=comp_handle,
                                      name=comp,
                                      rotation=props.get("rot"),
                                      position=(x0 + props.get("pos")[0], y0 + props.get("pos")[1])
                                      )
            component_handles.update({comp: ph_port})
        elif comp_type == "tag":
            tag = mdl.create_tag(value=props.get("tagname"),
                                 parent=comp_handle,
                                 scope='local',
                                 kind='pe' if not props.get("dir") else 'sp',
                                 name=comp,
                                 direction=props.get("dir"),
                                 flip=props.get("flip"),
                                 rotation=props.get("rot"),
                                 position=(x0 + props.get("pos")[0], y0 + props.get("pos")[1])
                                 )
            component_handles.update({comp: tag})
        else:
            new_comp = mdl.create_component(comp_type,
                                            parent=comp_handle,
                                            name=comp,
                                            rotation=props.get("rot"),
                                            flip=props.get("flip"),
                                            position=(x0 + props.get("pos")[0], y0 + props.get("pos")[1])
                                            )
            if comp_type == "Current Measurement":
                mdl.set_property_value(mdl.prop(new_comp, "sig_output"), "True")
            elif comp_type == "Single Phase Phasor":
                mdl.set_property_value(mdl.prop(new_comp, "f3db"), "1000")
            elif comp_type == "SCADA Input":
                mdl.set_property_value(mdl.prop(new_comp, "min"), "-3e38")
                mdl.set_property_value(mdl.prop(new_comp, "max"), "3e38")
            if mdl.prop(comp_handle, "execution_rate"):
                mdl.set_property_value(mdl.prop(new_comp, "execution_rate"), "execution_rate")
            component_handles.update({comp: new_comp})

    for comp, conns in connections_dict.items():
        for term1, term2 in conns.items():
            if term2[1] == 'port':
                mdl.create_connection(mdl.term(component_handles.get(comp), term1),
                                      component_handles.get(term2[0]))
            else:
                mdl.create_connection(mdl.term(component_handles.get(comp), term1),
                                      mdl.term(component_handles.get(term2[0]), term2[1]))


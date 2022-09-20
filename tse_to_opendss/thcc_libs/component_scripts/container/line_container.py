def update_properties(mdl, _Line_mask):
    ## PROPERTIES

    _Line_mask_input_type = mdl.create_property(
        item_handle=_Line_mask,
        name="input_type",
        label="Parameter input",
        widget="combo",
        combo_values=['Symmetrical', 'Matrix', 'LineCode'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Line Parameters:1",
        unit=""
    )
    _Line_mask_Load = mdl.create_property(
        item_handle=_Line_mask,
        name="Load",
        label="Load parameters",
        widget="button",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        button_label="Choose",
        unit=""
    )
    _Line_mask_selected_object = mdl.create_property(
        item_handle=_Line_mask,
        name="selected_object",
        label="Selected",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit=""
    )
    _Line_mask_Length = mdl.create_property(
        item_handle=_Line_mask,
        name="Length",
        label="Line Length",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Line Parameters:1",
        unit="km"
    )
    _Line_mask_global_basefreq = mdl.create_property(
        item_handle=_Line_mask,
        name="global_basefreq",
        label="Global base frequency",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit=""
    )
    _Line_mask_BaseFreq = mdl.create_property(
        item_handle=_Line_mask,
        name="BaseFreq",
        label="Base frequency",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="Line Parameters",
        unit="Hz"
    )
    _Line_mask_phases = mdl.create_property(
        item_handle=_Line_mask,
        name="phases",
        label="Phases",
        widget="combo",
        combo_values=['3', '2', '1'],
        evaluate=False,
        enabled=False,
        visible=True,
        tab_name="Line Parameters",
        unit=""
    )
    _Line_mask_R1 = mdl.create_property(
        item_handle=_Line_mask,
        name="R1",
        label="R1",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit="Ω/km"
    )
    _Line_mask_R0 = mdl.create_property(
        item_handle=_Line_mask,
        name="R0",
        label="R0",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit="Ω/km"
    )
    _Line_mask_X1 = mdl.create_property(
        item_handle=_Line_mask,
        name="X1",
        label="X1",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit="Ω/km"
    )
    _Line_mask_X0 = mdl.create_property(
        item_handle=_Line_mask,
        name="X0",
        label="X0",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit="Ω/km"
    )
    _Line_mask_dC1 = mdl.create_property(
        item_handle=_Line_mask,
        name="dC1",
        label="C1",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit="nF/km"
    )
    _Line_mask_dC0 = mdl.create_property(
        item_handle=_Line_mask,
        name="dC0",
        label="C0",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit="nF/km"
    )
    _Line_mask_rmatrix = mdl.create_property(
        item_handle=_Line_mask,
        name="rmatrix",
        label="Rmatrix",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit="Ω/km"
    )
    _Line_mask_xmatrix = mdl.create_property(
        item_handle=_Line_mask,
        name="xmatrix",
        label="Xmatrix",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit="Ω/km"
    )
    _Line_mask_cmatrix = mdl.create_property(
        item_handle=_Line_mask,
        name="cmatrix",
        label="Cmatrix",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Line Parameters",
        unit="nF/km"
    )
    _Line_mask_obj_mode = mdl.create_property(
        item_handle=_Line_mask,
        name="obj_mode",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_Len = mdl.create_property(
        item_handle=_Line_mask,
        name="Len",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_Fr = mdl.create_property(
        item_handle=_Line_mask,
        name="Fr",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_d_R = mdl.create_property(
        item_handle=_Line_mask,
        name="d_R",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_d_L = mdl.create_property(
        item_handle=_Line_mask,
        name="d_L",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_d_C = mdl.create_property(
        item_handle=_Line_mask,
        name="d_C",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_d_X = mdl.create_property(
        item_handle=_Line_mask,
        name="d_X",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_C1 = mdl.create_property(
        item_handle=_Line_mask,
        name="C1",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_C0 = mdl.create_property(
        item_handle=_Line_mask,
        name="C0",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_L1 = mdl.create_property(
        item_handle=_Line_mask,
        name="L1",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_L0 = mdl.create_property(
        item_handle=_Line_mask,
        name="L0",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_R1_one = mdl.create_property(
        item_handle=_Line_mask,
        name="R1_one",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_L1_one = mdl.create_property(
        item_handle=_Line_mask,
        name="L1_one",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_C1_one = mdl.create_property(
        item_handle=_Line_mask,
        name="C1_one",
        label="",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=False,
        tab_name="",
        unit=""
    )
    _Line_mask_coupling = mdl.create_property(
        item_handle=_Line_mask,
        name="coupling",
        label="Enable coupling",
        widget="combo",
        combo_values=['None', 'Core coupling', 'Device coupling'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Coupling:2",
        unit=""
    )
    _Line_mask_enable_monitoring = mdl.create_property(
        item_handle=_Line_mask,
        name="enable_monitoring",
        label="Enable monitoring",
        widget="checkbox",
        combo_values=[],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Monitoring",
        unit=""
    )


    ## SET PROPERTIES TO DEFAULT VALUES

    mdl.set_property_value(mdl.prop(_Line_mask, "input_type"), "Symmetrical")
    mdl.set_property_value(mdl.prop(_Line_mask, "Load"), "Choose")
    mdl.set_property_value(mdl.prop(_Line_mask, "selected_object"), "")
    mdl.set_property_value(mdl.prop(_Line_mask, "Length"), "100")
    mdl.set_property_value(mdl.prop(_Line_mask, "global_basefreq"), "True")
    mdl.set_property_value(mdl.prop(_Line_mask, "BaseFreq"), "60")
    mdl.set_property_value(mdl.prop(_Line_mask, "phases"), "3")
    mdl.set_property_value(mdl.prop(_Line_mask, "R1"), "0.1903")
    mdl.set_property_value(mdl.prop(_Line_mask, "R0"), "0.5853")
    mdl.set_property_value(mdl.prop(_Line_mask, "X1"), "0.3957")
    mdl.set_property_value(mdl.prop(_Line_mask, "X0"), "1.3278")
    mdl.set_property_value(mdl.prop(_Line_mask, "dC1"), "11.155")
    mdl.set_property_value(mdl.prop(_Line_mask, "dC0"), "5.2493")
    mdl.set_property_value(mdl.prop(_Line_mask, "rmatrix"), "[[0.0981, 0.0401, 0.0401], [0.0401, 0.0981, 0.0401], [0.0401, 0.0401, 0.0981]]")
    mdl.set_property_value(mdl.prop(_Line_mask, "xmatrix"), "[[0.2153, 0.0947, 0.0947], [0.0947, 0.2153, 0.0947], [0.0947, 0.0947, 0.2153]]")
    mdl.set_property_value(mdl.prop(_Line_mask, "cmatrix"), "[[2.8, -0.6, -0.6], [-0.6, 2.8, -0.6], [-0.6, -0.6, 2.8]]")
    mdl.set_property_value(mdl.prop(_Line_mask, "obj_mode"), "")
    mdl.set_property_value(mdl.prop(_Line_mask, "Len"), "0")
    mdl.set_property_value(mdl.prop(_Line_mask, "Fr"), "0")
    mdl.set_property_value(mdl.prop(_Line_mask, "d_R"), "0")
    mdl.set_property_value(mdl.prop(_Line_mask, "d_L"), "0")
    mdl.set_property_value(mdl.prop(_Line_mask, "d_C"), "0")
    mdl.set_property_value(mdl.prop(_Line_mask, "d_X"), "0")
    mdl.set_property_value(mdl.prop(_Line_mask, "C1"), "12.74e-9")
    mdl.set_property_value(mdl.prop(_Line_mask, "C0"), "7.751e-9")
    mdl.set_property_value(mdl.prop(_Line_mask, "L1"), "99999")
    mdl.set_property_value(mdl.prop(_Line_mask, "L0"), "99999")
    mdl.set_property_value(mdl.prop(_Line_mask, "R1_one"), "0.01")
    mdl.set_property_value(mdl.prop(_Line_mask, "L1_one"), "0.01e-3")
    mdl.set_property_value(mdl.prop(_Line_mask, "C1_one"), "0.1e-6")
    mdl.set_property_value(mdl.prop(_Line_mask, "coupling"), "None")
    mdl.set_property_value(mdl.prop(_Line_mask, "enable_monitoring"), "False")


    ## EDITED HANDLERS

    _Line_mask_input_type_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Line_mask_input_type, "property_value_edited", _Line_mask_input_type_property_value_edited)
    _Line_mask_selected_object_property_value_edited = """
    old_value = mdl.get_property_value(prop_handle)
    mdl.set_property_disp_value(prop_handle, old_value)
    
    """
    mdl.set_handler_code(_Line_mask_selected_object, "property_value_edited", _Line_mask_selected_object_property_value_edited)
    _Line_mask_global_basefreq_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Line_mask_global_basefreq, "property_value_edited", _Line_mask_global_basefreq_property_value_edited)
    _Line_mask_phases_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Line_mask_phases, "property_value_edited", _Line_mask_phases_property_value_edited)


    ## BUTTON HANDLERS

    _Line_mask_Load_button_clicked = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.load_line_parameters(mdl, container_handle)
    
    """
    mdl.set_handler_code(_Line_mask_Load, "button_clicked", _Line_mask_Load_button_clicked)


    ## CHANGED HANDLERS

    _Line_mask_phases_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Line_mask_phases, "property_value_changed",
                         _Line_mask_phases_property_value_changed)

    _Line_mask_dC0_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    """
    mdl.set_handler_code(_Line_mask_dC0, "property_value_changed",
                         _Line_mask_dC0_property_value_changed)

    _Line_mask_cmatrix_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    """
    mdl.set_handler_code(_Line_mask_cmatrix, "property_value_changed",
                         _Line_mask_cmatrix_property_value_changed)

def ports_initialization(mdl, _Line_mask):
    _Line = mdl.get_parent(_Line_mask)


    ## CREATE INITIALIZATION PORTS 

    _Line_A1 = mdl.create_port(
        name="A1",
        parent=_Line,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(-32, -32),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(7512, 7976)
    )
    _Line_B1 = mdl.create_port(
        name="B1",
        parent=_Line,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(-32, 0),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(7512, 8032)
    )
    _Line_C1 = mdl.create_port(
        name="C1",
        parent=_Line,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(-32, 32),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(7512, 8088)
    )
    _Line_A2 = mdl.create_port(
        name="A2",
        parent=_Line,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32, -32),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8008, 7936)
    )
    _Line_B2 = mdl.create_port(
        name="B2",
        parent=_Line,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32, 0),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8008, 8032)
    )
    _Line_C2 = mdl.create_port(
        name="C2",
        parent=_Line,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=(32, 32),
        rotation="down",
        flip="flip_none",
        hide_name=False,
        position=(8008, 8128)
    )
    _Line_N = mdl.create_port(
        name="N",
        parent=_Line,
        label="",
        kind="pe",
        dimension=(1,),
        terminal_position=('bottom', 'left'),
        rotation="up",
        flip="flip_none",
        hide_name=False,
        position=(7728, 8144)
    )

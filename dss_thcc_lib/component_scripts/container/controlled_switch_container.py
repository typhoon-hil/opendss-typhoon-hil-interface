def update_properties(mdl, _Controlled_Switch_mask):
    ## PROPERTIES

    _Controlled_Switch_mask_enable_fb_out = mdl.create_property(
        item_handle=_Controlled_Switch_mask,
        name="enable_fb_out",
        label="Feedback output",
        widget="combo",
        combo_values=['True', 'False'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="General:1",
        unit=""
    )
    _Controlled_Switch_mask_fb_out_type = mdl.create_property(
        item_handle=_Controlled_Switch_mask,
        name="fb_out_type",
        label="Signal type",
        widget="combo",
        combo_values=['real', 'int', 'uint'],
        evaluate=False,
        enabled=True,
        visible=False,
        tab_name="General:1",
        unit=""
    )
    _Controlled_Switch_mask_phases = mdl.create_property(
        item_handle=_Controlled_Switch_mask,
        name="phases",
        label="Phases",
        widget="combo",
        combo_values=['1', '2', '3'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="General",
        unit=""
    )
    _Controlled_Switch_mask_execution_rate = mdl.create_property(
        item_handle=_Controlled_Switch_mask,
        name="execution_rate",
        label="Execution rate",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="General",
        unit=""
    )
    _Controlled_Switch_mask_initial_state = mdl.create_property(
        item_handle=_Controlled_Switch_mask,
        name="initial_state",
        label="Initial state",
        widget="combo",
        combo_values=['off', 'on'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="Initial state:2",
        unit=""
    )
    _Controlled_Switch_mask_on_delay = mdl.create_property(
        item_handle=_Controlled_Switch_mask,
        name="on_delay",
        label="On delay",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Timing:3",
        unit="s"
    )
    _Controlled_Switch_mask_off_delay = mdl.create_property(
        item_handle=_Controlled_Switch_mask,
        name="off_delay",
        label="Off delay",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="Timing",
        unit="s"
    )


    ## SET PROPERTIES TO DEFAULT VALUES

    mdl.set_property_value(mdl.prop(_Controlled_Switch_mask, "enable_fb_out"), "False")
    mdl.set_property_value(mdl.prop(_Controlled_Switch_mask, "fb_out_type"), "real")
    mdl.set_property_value(mdl.prop(_Controlled_Switch_mask, "phases"), "3")
    mdl.set_property_value(mdl.prop(_Controlled_Switch_mask, "execution_rate"), "inherit")
    mdl.set_property_value(mdl.prop(_Controlled_Switch_mask, "initial_state"), "on")
    mdl.set_property_value(mdl.prop(_Controlled_Switch_mask, "on_delay"), "0")
    mdl.set_property_value(mdl.prop(_Controlled_Switch_mask, "off_delay"), "0")


    ## EDITED HANDLERS

    _Controlled_Switch_mask_enable_fb_out_property_value_edited = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.mask_dialog_dynamics(mdl, container_handle, prop_handle)
    
    """
    mdl.set_handler_code(_Controlled_Switch_mask_enable_fb_out, "property_value_edited", _Controlled_Switch_mask_enable_fb_out_property_value_edited)


    ## BUTTON HANDLERS



    ## CHANGED HANDLERS

    _Controlled_Switch_mask_enable_fb_out_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    """
    mdl.set_handler_code(_Controlled_Switch_mask_enable_fb_out, "property_value_changed",
                         _Controlled_Switch_mask_enable_fb_out_property_value_changed)

    _Controlled_Switch_mask_phases_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Controlled_Switch_mask_phases, "property_value_changed",
                         _Controlled_Switch_mask_phases_property_value_changed)

    _Controlled_Switch_mask_initial_state_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Controlled_Switch_mask_initial_state, "property_value_changed",
                         _Controlled_Switch_mask_initial_state_property_value_changed)

def ports_initialization(mdl, _Controlled_Switch_mask):
    _Controlled_Switch = mdl.get_parent(_Controlled_Switch_mask)


    ## CREATE INITIALIZATION PORTS 

    _Controlled_Switch_ctrl = mdl.create_port(
        name="ctrl",
        parent=_Controlled_Switch,
        label="ctrl",
        kind="sp",
        direction="in",
        dimension=(1,),
        terminal_position=('top', 'center'),
        rotation="right",
        flip="flip_none",
        hide_name=True,
        position=(7688, 7800)
    )
    _Controlled_Switch_A1 = mdl.create_port(
        name="A1",
        parent=_Controlled_Switch,
        label="A1",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(-32.0, -32.0),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(7600, 7856)
    )
    _Controlled_Switch_B1 = mdl.create_port(
        name="B1",
        parent=_Controlled_Switch,
        label="B1",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(-32.0, 0.0),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(7600, 7952)
    )
    _Controlled_Switch_C1 = mdl.create_port(
        name="C1",
        parent=_Controlled_Switch,
        label="C1",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(-32.0, 32.0),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(7600, 8048)
    )
    _Controlled_Switch_A2 = mdl.create_port(
        name="A2",
        parent=_Controlled_Switch,
        label="A2",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(32.0, -32.0),
        rotation="up",
        flip="flip_horizontal",
        hide_name=True,
        position=(7872, 7856)
    )
    _Controlled_Switch_B2 = mdl.create_port(
        name="B2",
        parent=_Controlled_Switch,
        label="B2",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(32.0, 0.0),
        rotation="up",
        flip="flip_horizontal",
        hide_name=True,
        position=(7872, 7952)
    )
    _Controlled_Switch_C2 = mdl.create_port(
        name="C2",
        parent=_Controlled_Switch,
        label="C2",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=(32.0, 32.0),
        rotation="up",
        flip="flip_horizontal",
        hide_name=True,
        position=(7872, 8048)
    )

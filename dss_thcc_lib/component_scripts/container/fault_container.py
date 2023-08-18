def update_properties(mdl, _Fault_mask):
    ## PROPERTIES

    _Fault_mask_fault_type = mdl.create_property(
        item_handle=_Fault_mask,
        name="fault_type",
        label="Fault type",
        widget="combo",
        combo_values=['A-B-C-GND', 'A-B-GND', 'A-C-GND', 'B-C-GND', 'A-GND', 'B-GND', 'C-GND', 'A-B-C', 'A-B', 'A-C', 'B-C', 'None'],
        evaluate=False,
        enabled=True,
        visible=True,
        tab_name="",
        unit=""
    )
    _Fault_mask_resistance = mdl.create_property(
        item_handle=_Fault_mask,
        name="resistance",
        label="Resistance (phase)",
        widget="edit",
        combo_values=[],
        evaluate=True,
        enabled=True,
        visible=True,
        tab_name="",
        unit="Ω"
    )


    ## SET PROPERTIES TO DEFAULT VALUES

    mdl.set_property_value(mdl.prop(_Fault_mask, "fault_type"), "A-B-C-GND")
    mdl.set_property_value(mdl.prop(_Fault_mask, "resistance"), "0.0001")


    ## EDITED HANDLERS



    ## BUTTON HANDLERS



    ## CHANGED HANDLERS

    _Fault_mask_fault_type_property_value_changed = """
    comp_script = return_comp_script(mdl, container_handle)
    comp_script.port_dynamics(mdl, container_handle, caller_prop_handle=prop_handle)
    mdl.refresh_icon(container_handle)
    """
    mdl.set_handler_code(_Fault_mask_fault_type, "property_value_changed",
                         _Fault_mask_fault_type_property_value_changed)

def ports_initialization(mdl, _Fault_mask):
    _Fault = mdl.get_parent(_Fault_mask)


    ## CREATE INITIALIZATION PORTS 

    _Fault_A1 = mdl.create_port(
        name="A1",
        parent=_Fault,
        label="A1",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=('left', 'top'),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(7600, 7856)
    )
    _Fault_B1 = mdl.create_port(
        name="B1",
        parent=_Fault,
        label="B1",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=('left', 'center'),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(7600, 7952)
    )
    _Fault_C1 = mdl.create_port(
        name="C1",
        parent=_Fault,
        label="C1",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=('left', 'bottom'),
        rotation="up",
        flip="flip_none",
        hide_name=True,
        position=(7600, 8048)
    )
    _Fault_A2 = mdl.create_port(
        name="A2",
        parent=_Fault,
        label="A2",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=('right', 'top'),
        rotation="up",
        flip="flip_horizontal",
        hide_name=True,
        position=(7872, 7856)
    )
    _Fault_B2 = mdl.create_port(
        name="B2",
        parent=_Fault,
        label="B2",
        kind="pe",
        direction="out",
        dimension=(1,),
        terminal_position=('right', 'center'),
        rotation="up",
        flip="flip_horizontal",
        hide_name=True,
        position=(7872, 7952)
    )
    _Fault_C2 = mdl.create_port(
        name="C2",
        parent=_Fault,
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

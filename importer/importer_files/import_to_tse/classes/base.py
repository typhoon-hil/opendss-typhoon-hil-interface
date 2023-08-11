"""
TSE: Typhoon Schematic Editor

"""

from import_to_tse.constants import CANVAS_CENTER, TSE_GRID_RESOLUTION
from typhoon.api.schematic_editor import SchematicAPI
from tqdm import tqdm
from import_to_tse import aux_functions
import pathlib


def move_to_center(original_position):
    if original_position:
        return (
            original_position[0] + CANVAS_CENTER[0],
            original_position[1] + CANVAS_CENTER[1],
        )
    else:
        return original_position


def back_from_center(original_position):
    if original_position:
        return (
            original_position[0] - CANVAS_CENTER[0],
            original_position[1] - CANVAS_CENTER[1],
        )
    else:
        return original_position


class Schematic:
    """ """

    def __init__(self, schematic_properties: dict = None):
        self.schematic_properties = schematic_properties if schematic_properties else {}
        self.mdl = SchematicAPI()
        self.mdl.create_new_model()

        # Schematic items
        self._nodes = []
        self._components = []

    def set_model_properties(self):
        """
        From the schematic_properties dictionary, use the SchematicAPI to set all the TSE model properties.
        """
        for prop_name, prop_value in self.schematic_properties.items():
            self.mdl.set_model_property_value(prop_name, prop_value)

    def add_component(self, component):
        """
        Add the component to the list of components of the schematic.
        """
        self._components.append(component)

    @property
    def components(self):
        return self._components

    def add_node(self, node):
        """
        Add the node to the list of nodes of the schematic.
        """
        self._nodes.append(node)

    @property
    def nodes(self):
        return self._nodes

    def create_connections(self):
        """
        Iterate over all nodes, check all terminals that are connected to the node and connect them.
        """
        for node in tqdm(self._nodes):
            # If the connections are not predefined, generate them
            if not node.connections:
                node_terminals = node.terminals

                # Connect two terminals directly
                if len(node_terminals) == 2:
                    t1 = node.terminals[0]
                    t2 = node.terminals[1]
                    if isinstance(t1.parent, (Port, Tag)):
                        t1_tse = t1.parent.tse_instance
                        t1_comp = t1_tse
                    else:
                        t1_tse = self.mdl.term(
                            t1.parent.tse_instance, t1.destination_name
                        )
                        t1_comp = self.mdl.get_parent(t1_tse)
                    if isinstance(t2.parent, (Port, Tag)):
                        t2_tse = t2.parent.tse_instance
                        t2_comp = t2_tse
                    else:
                        t2_tse = self.mdl.term(
                            t2.parent.tse_instance, t2.destination_name
                        )
                        t2_comp = self.mdl.get_parent(t2_tse)

                    t1_comp_parent = self.mdl.get_parent(t1_comp)
                    t2_comp_parent = self.mdl.get_parent(t2_comp)

                    if t1_comp and t2_comp:
                        if not t1_comp_parent and not t2_comp_parent:
                            # Components are on the root of the schematic
                            self.mdl.create_connection(t1_tse, t2_tse)
                        if t1_comp_parent and t2_comp_parent:
                            if self.mdl.get_name(t1_comp_parent) == self.mdl.get_name(
                                t2_comp_parent
                            ):
                                self.mdl.create_connection(t1_tse, t2_tse)

                # elif len(node_terminals) == 3:
                #     # Choose the terminal that is the closest to every other
                #     shortest_distance = 3 * CANVAS_CENTER[0]
                #     ref_terminal = None
                #
                #     for terminal in node_terminals:
                #         if terminal.parent.terminal_defining_junctions:
                #             ref_terminal = terminal
                #             # The parent component of the reference terminal
                #             ref_comp = ref_terminal.parent
                #             ref_comp.terminal_defining_junctions = True
                #             break
                #
                #     if not ref_terminal:
                #         for terminal in node_terminals:
                #             for other_terminal in node_terminals:
                #                 if not terminal == other_terminal:
                #                     dist_x = abs(
                #                         terminal.schematic_position[0]
                #                         - other_terminal.schematic_position[0]
                #                     )
                #                     dist_y = abs(
                #                         terminal.schematic_position[1]
                #                         - other_terminal.schematic_position[1]
                #                     )
                #                     distance = (dist_x**2 + dist_y**2) ** 0.5
                #                     if distance < shortest_distance:
                #                         shortest_distance = distance
                #                         ref_terminal = terminal
                #         # The parent component of the reference terminal
                #         ref_comp = ref_terminal.parent
                #         ref_comp.terminal_defining_junctions = True
                #
                #     term_x = ref_terminal.schematic_position[0]
                #     term_y = ref_terminal.schematic_position[1]
                #
                #     # Define the order of the terminals on the same side as the reference by their schematic position
                #     side_terminals = [
                #         t
                #         for t in ref_comp.terminals
                #         if t.get_side() == ref_terminal.get_side()
                #     ]
                #     terminal_order = sorted(
                #         side_terminals, key=lambda t: t.schematic_position
                #     )
                #     if ref_terminal.get_side(True) == "right":
                #         x_offset = (
                #             3
                #             * TSE_GRID_RESOLUTION
                #             * (
                #                 len(terminal_order)
                #                 - 1
                #                 - terminal_order.index(ref_terminal)
                #             )
                #         )
                #         y_pos = term_y
                #         junc_position = (term_x + 64 + x_offset, y_pos)
                #     elif ref_terminal.get_side(True) == "left":
                #         x_offset = (
                #             3 * TSE_GRID_RESOLUTION * terminal_order.index(ref_terminal)
                #         )
                #         y_pos = term_y
                #         junc_position = (term_x - 64 - x_offset, y_pos)
                #     elif ref_terminal.get_side(True) == "top":
                #         y_offset = (
                #             3
                #             * TSE_GRID_RESOLUTION
                #             * (
                #                 len(terminal_order)
                #                 - 1
                #                 - terminal_order.index(ref_terminal)
                #             )
                #         )
                #         x_pos = term_x
                #         junc_position = (x_pos, term_y - 64 - y_offset)
                #     else:
                #         y_offset = (
                #             3 * TSE_GRID_RESOLUTION * terminal_order.index(ref_terminal)
                #         )
                #         x_pos = term_x
                #         junc_position = (x_pos, term_y + 64 + y_offset)
                #
                #     # Create the junction
                #     junc = self.mdl.create_junction(
                #         position=junc_position, parent=ref_terminal.parent.parent
                #     )
                #     # Connect all terminals
                #     for term in node_terminals:
                #         self.mdl.create_connection(junc, term.tse_instance)

                elif len(node_terminals) > 2:
                    #
                    # Verify component positions to determine
                    # if they are spread horizontally or vertically
                    #
                    highest_x, highest_y = 0, 0
                    lowest_x, lowest_y = 3 * CANVAS_CENTER[0], 3 * CANVAS_CENTER[0]
                    positions = {}
                    for terminal in node_terminals:
                        comp_x = terminal.parent.position[0]
                        comp_y = terminal.parent.position[1]
                        positions[terminal] = [comp_x, comp_y]
                        if comp_x > highest_x:
                            highest_x = comp_x
                        elif comp_x < lowest_x:
                            lowest_x = comp_x
                        if comp_y > highest_y:
                            highest_y = comp_y
                        elif comp_y < lowest_y:
                            lowest_y = comp_y

                    if (highest_x - lowest_x) > (highest_y - lowest_y):
                        direction = "horizontal"
                    else:
                        direction = "vertical"

                    # Order the terminals by the defined direction
                    if direction == "horizontal":
                        ordered_terminals = sorted(
                            list(positions), key=lambda term: positions.get(term)[0]
                        )
                    else:
                        ordered_terminals = sorted(
                            list(positions), key=lambda term: positions.get(term)[1]
                        )

                    # Components on both extremes won't define junctions
                    first_terminal = ordered_terminals[0]
                    last_terminal = ordered_terminals[-1]
                    ordered_terminals = ordered_terminals[1:-1]

                    # Create the junctions
                    created_junctions = []
                    for terminal in ordered_terminals:
                        comp = terminal.parent
                        side_terminals = [
                            t
                            for t in comp.terminals
                            if t.get_side() == terminal.get_side()
                        ]
                        terminal_order = sorted(
                            side_terminals, key=lambda t: t.schematic_position
                        )
                        x_pos = terminal.schematic_position[0]
                        y_pos = terminal.schematic_position[1]

                        new_junction = None
                        if terminal.get_side(True) == "right":
                            for junction in created_junctions:
                                if comp.rotation in ["up", "down"]:
                                    comp_top_y = (
                                        comp.position[1]
                                        - comp.size[1] / 2
                                        - 2 * TSE_GRID_RESOLUTION
                                    )
                                    comp_bottom_y = (
                                        comp.position[1]
                                        + comp.size[1] / 2
                                        + 2 * TSE_GRID_RESOLUTION
                                    )
                                else:
                                    comp_top_y = (
                                        comp.position[1]
                                        - comp.size[0] / 2
                                        - 2 * TSE_GRID_RESOLUTION
                                    )
                                    comp_bottom_y = (
                                        comp.position[1]
                                        + comp.size[0] / 2
                                        + 2 * TSE_GRID_RESOLUTION
                                    )
                                if comp_top_y < junction.position[1] < comp_bottom_y:
                                    new_junction = junction
                                    break
                            if not new_junction:
                                x_offset = (
                                    4
                                    * TSE_GRID_RESOLUTION
                                    * (
                                        len(terminal_order)
                                        - 1
                                        - terminal_order.index(terminal)
                                    )
                                )
                                junc_position = (x_pos + 64 + x_offset, y_pos)
                        elif terminal.get_side(True) == "left":
                            for junction in created_junctions:
                                if comp.rotation in ["up", "down"]:
                                    comp_top_y = (
                                        comp.position[1]
                                        - comp.size[1] / 2
                                        - 2 * TSE_GRID_RESOLUTION
                                    )
                                    comp_bottom_y = (
                                        comp.position[1]
                                        + comp.size[1] / 2
                                        + 2 * TSE_GRID_RESOLUTION
                                    )
                                else:
                                    comp_top_y = (
                                        comp.position[1]
                                        - comp.size[0] / 2
                                        - 2 * TSE_GRID_RESOLUTION
                                    )
                                    comp_bottom_y = (
                                        comp.position[1]
                                        + comp.size[0] / 2
                                        + 2 * TSE_GRID_RESOLUTION
                                    )
                                if comp_top_y < junction.position[1] < comp_bottom_y:
                                    new_junction = junction
                                    break
                            if not new_junction:
                                x_offset = (
                                    4
                                    * TSE_GRID_RESOLUTION
                                    * terminal_order.index(terminal)
                                )
                                junc_position = (x_pos - 64 - x_offset, y_pos)
                        elif terminal.get_side(True) == "top":
                            for junction in created_junctions:
                                if comp.rotation in ["up", "down"]:
                                    comp_left_x = (
                                        comp.position[0]
                                        - comp.size[0] / 2
                                        - 2 * TSE_GRID_RESOLUTION
                                    )
                                    comp_right_x = (
                                        comp.position[0]
                                        + comp.size[0] / 2
                                        + 2 * TSE_GRID_RESOLUTION
                                    )
                                else:
                                    comp_left_x = (
                                        comp.position[0]
                                        - comp.size[1] / 2
                                        - 2 * TSE_GRID_RESOLUTION
                                    )
                                    comp_right_x = (
                                        comp.position[0]
                                        + comp.size[1] / 2
                                        + 2 * TSE_GRID_RESOLUTION
                                    )
                                if comp_left_x < junction.position[0] < comp_right_x:
                                    new_junction = junction
                                    break
                            if not new_junction:
                                y_offset = (
                                    4
                                    * TSE_GRID_RESOLUTION
                                    * (
                                        len(terminal_order)
                                        - 1
                                        - terminal_order.index(terminal)
                                    )
                                )
                                junc_position = (x_pos, y_pos - 64 - y_offset)
                        else:
                            for junction in created_junctions:
                                if comp.rotation in ["up", "down"]:
                                    comp_left_x = (
                                        comp.position[0]
                                        - comp.size[0] / 2
                                        - 2 * TSE_GRID_RESOLUTION
                                    )
                                    comp_right_x = (
                                        comp.position[0]
                                        + comp.size[0] / 2
                                        + 2 * TSE_GRID_RESOLUTION
                                    )
                                else:
                                    comp_left_x = (
                                        comp.position[0]
                                        - comp.size[1] / 2
                                        - 2 * TSE_GRID_RESOLUTION
                                    )
                                    comp_right_x = (
                                        comp.position[0]
                                        + comp.size[1] / 2
                                        + 2 * TSE_GRID_RESOLUTION
                                    )
                                if comp_left_x < junction.position[0] < comp_right_x:
                                    new_junction = junction
                                    break
                            if not new_junction:
                                y_offset = (
                                    4
                                    * TSE_GRID_RESOLUTION
                                    * terminal_order.index(terminal)
                                )
                                junc_position = (x_pos, y_pos + 64 + y_offset)

                        if not new_junction:
                            # Create the junction
                            junc_props = {
                                "position": back_from_center(junc_position),
                                "kind": terminal.kind,
                            }
                            new_junction = Junction(
                                self, junc_props, parent=comp.parent
                            )
                            new_junction.set_node(node)
                            new_junction.add_to_schematic()
                            created_junctions.append(new_junction)

                        # Connect the respective terminal
                        self.mdl.create_connection(
                            new_junction.tse_instance, terminal.tse_instance
                        )

                    # Connect the junctions
                    for idx in range(len(created_junctions)):
                        if idx < len(created_junctions) - 1:
                            self.mdl.create_connection(
                                created_junctions[idx].tse_instance,
                                created_junctions[idx + 1].tse_instance,
                            )

                    # Connect the missing two terminals to the junctions
                    self.mdl.create_connection(
                        created_junctions[0].tse_instance, first_terminal.tse_instance
                    )
                    self.mdl.create_connection(
                        created_junctions[-1].tse_instance, last_terminal.tse_instance
                    )
            else:
                for conn in node.connections:
                    conn.add_to_schematic()

    def save_model(self, file_path):
        """
        Save the schematic model.
        """
        print(f'Saving model to "{pathlib.Path.cwd().joinpath(file_path)}"')
        self.mdl.save_as(file_path)

    def close_model(self):
        """
        Close the schematic model.
        """
        self.mdl.close_model()


class Node:
    """
    Basic virtual connection point for the elements of the schematic.

    Attributes:
        schematic (Schematic): The schematic this node belongs to.
    """

    def __init__(self, schematic: Schematic):
        """
        Initialization.
        """
        self.schematic = schematic

        # List of terminals
        self._terminals = []
        self._connections = []
        self._junctions = []

        # Add node to the schematic
        if self not in self.schematic.nodes:
            self.schematic.add_node(self)

    def add_terminal(self, terminal):
        """
        A node is a virtual point of connection of component terminals. Add the specified terminal to the list.

        Args:
            terminal (Terminal): The terminal that is connected to the node.
        """
        self._terminals.append(terminal)

    @property
    def terminals(self):
        """
        Returns the list of terminals of this node.

        Returns:
            _terminals (list): list of Terminal objects currently added to the node.
        """
        return self._terminals

    def add_connection(self, connection):
        """
        Add the node to the list of connections of the node.
        """
        self._connections.append(connection)

    @property
    def connections(self):
        return self._connections

    def add_junction(self, junction):
        """
        Add the junction to the list of junctions of the node.
        """
        self._junctions.append(junction)

    @property
    def junctions(self):
        return self._junctions

    def get_connected_components(self):
        """
        Returns:
            connected_components: a list of components that have at least one Terminal connected to this Node
        """
        connected_components = []
        for terminal in self.terminals:
            if terminal.parent not in connected_components:
                connected_components.append(terminal.parent)
        return connected_components


class Junction:
    def __init__(self, schematic: Schematic, schematic_properties: dict, parent=None):
        self.schematic = schematic
        self.mdl = schematic.mdl
        self.parent = parent
        self._schematic_properties = schematic_properties
        self.position = schematic_properties["position"]

        self.tse_instance = None
        self._kind = schematic_properties["kind"]
        self._node = None

    def add_to_schematic(self, to_center=True):
        parent = self.parent.tse_instance if self.parent else None
        pos = move_to_center(self.position) if to_center else self.position
        self.tse_instance = self.mdl.create_junction(
            position=pos, kind=self.kind, parent=parent
        )

    @property
    def parent_subsystem(self):
        return self.parent

    @property
    def kind(self):
        return self._kind

    def set_node(self, node):
        """
        Set the Node this Junction should be part of
        """

        self._node = node

    @property
    def node(self):
        """
        Returns the Node this Junction is part of
        """

        return self._node


class Connection:
    def __init__(self, schematic: Schematic, start, end, breakpoints=[], parent=None):
        self._node = None
        self.schematic = schematic
        self.mdl = schematic.mdl
        self._breakpoints = breakpoints
        self._parent = parent
        self._start = start
        self._end = end
        # self.kind = schematic_properties["kind"]

    @property
    def start(self):
        """
        Returns the connection start point

        Returns:
            _start: connection start point.
        """
        return self._start

    @property
    def end(self):
        """
        Returns the connection end point

        Returns:
            _end: connection end point.
        """
        return self._end

    @property
    def breakpoints(self):
        """
        Returns the connection breakpoints

        Returns:
            _breakpoints (list): breakpoints of the connection line.
        """
        return self._breakpoints

    def set_node(self, node):
        """
        Set the Node this Connection should be part of
        """

        self._node = node

    @property
    def node(self):
        """
        Returns the Node this Connection is part of
        """

        return self._node

    def add_to_schematic(self):
        """
        Realize the connection in the Schematic Editor
        """

        if not (self.start.parent_subsystem is self.end.parent_subsystem):
            pass
        else:
            if isinstance(self.start.parent, Port):
                start_tse = self.start.parent.tse_instance
            else:
                start_tse = self.start.tse_instance

            if isinstance(self.end.parent, Port):
                end_tse = self.end.parent.tse_instance
            else:
                end_tse = self.end.tse_instance

            if start_tse and end_tse:
                self.mdl.create_connection(start_tse, end_tse)


class Component:
    """
    Basic circuit schematic component class. Each destination component (that belongs to a TSE library) must
    inherit from this class.

    Attributes:
        schematic (Schematic): The schematic this node belongs to.
        schematic_properties (dict): The visual and identification properties of the component.
        mask_properties (dict): The properties of the TSE component mask.
    """

    def __init__(
        self,
        schematic: Schematic,
        schematic_properties: dict,
        mask_properties: dict,
        parent=None,
        mask_codes={},
        create_mask=False,
    ):
        self.schematic = schematic
        self.mdl = schematic.mdl
        self.schematic_properties = schematic_properties
        self.parent = parent

        # Object instance in TSE
        self.tse_instance = None

        # Mandatory properties
        self._name = schematic_properties["name"]
        self.type_name = schematic_properties["type_name"]

        # Optional properties
        self._rotation = schematic_properties.get("rotation", "up")
        self._flip = schematic_properties.get("flip", "flip_none")
        self._position = schematic_properties.get("position", CANVAS_CENTER)
        self._size = schematic_properties.get("size", (None, None))
        self._hide_name = schematic_properties.get("hide_name", False)

        #
        # Mask
        #
        self.mask = None
        self.create_mask = create_mask
        self.mask_properties = mask_properties
        self.mask_codes = mask_codes
        self.image_code = mask_codes.get("tse_image_code")
        self.description = mask_codes.get("tse_description_code")
        self.init_code = mask_codes.get("tse_init_code")
        self.pre_compile_code = mask_codes.get("tse_pre_compile_code")
        self.property_handlers = mask_codes.get("property_handlers")
        self.property_parameters = mask_codes.get("property_parameters")

        # List of terminals
        self._terminals = []
        self.terminal_defining_junctions = None

        # Add to the Schematic
        self.schematic.add_component(self)

    def add_to_schematic(self, to_center=True):
        """
        Creates a new component in the SchematicAPI model.

        Returns:
            None
        """
        pos = move_to_center(self.position) if to_center else self.position
        self.tse_instance = self.mdl.create_component(
            type_name=self.type_name,
            parent=self.parent.tse_instance if self.parent else None,
            name=self._name,
            rotation=self._rotation,
            flip=self._flip,
            position=pos,
            size=self._size,
            hide_name=self._hide_name,
        )
        # Mask
        if self.type_name == "core/Empty Subsystem":
            self.create_mask_properties()
        else:
            self.set_mask_properties_values()

        if not self.size:
            self._size = self.mdl.get_size(self.tse_instance)
        self.write_mask_codes()

    def create_mask_properties(self):
        """
        If the TSE component is a Subsystem, create the mask and its properties.

        Returns:
            None

        """

        if self.type_name == "core/Empty Subsystem":
            if self.create_mask and not self.mask:
                self.mask = self.mdl.create_mask(self.tse_instance)
                for prop_name, prop_value in self.mask_properties.items():
                    parameters = (
                        self.property_parameters.get(prop_name, {})
                        if self.property_parameters
                        else {}
                    )
                    self.mdl.create_property(
                        self.mask,
                        prop_name,
                        label=parameters.get("label")
                        if parameters.get("label")
                        else "",
                        widget=parameters.get("widget")
                        if parameters.get("widget")
                        else "edit",
                        combo_values=parameters.get("combo_values")
                        if parameters.get("combo_values")
                        else (),
                        evaluate=parameters.get("evaluate")
                        if parameters.get("evaluate")
                        else True,
                        enabled=parameters.get("enabled")
                        if parameters.get("enabled")
                        else True,
                        visible=parameters.get("visible")
                        if parameters.get("visible")
                        else True,
                        tab_name=parameters.get("tab_name")
                        if parameters.get("tab_name")
                        else "",
                        unit=parameters.get("unit") if parameters.get("unit") else "",
                        button_label=parameters.get("button_label")
                        if parameters.get("button_label")
                        else "",
                        previous_names=parameters.get("previous_names")
                        if parameters.get("previous_names")
                        else (),
                        description=parameters.get("description")
                        if parameters.get("description")
                        else "",
                        type=parameters.get("type") if parameters.get("type") else "",
                        default_value=parameters.get("default_value")
                        if parameters.get("default_value")
                        else None,
                        min_value=parameters.get("min_value")
                        if parameters.get("min_value")
                        else None,
                        max_value=parameters.get("max_value")
                        if parameters.get("max_value")
                        else None,
                        keepline=parameters.get("keepline")
                        if parameters.get("keepline")
                        else False,
                        skip=parameters.get("skip") if parameters.get("skip") else None,
                        skip_step=parameters.get("skip_step")
                        if parameters.get("skip_step")
                        else None,
                        vector=parameters.get("vector")
                        if parameters.get("vector")
                        else False,
                        tunable=parameters.get("tunable")
                        if parameters.get("tunable")
                        else False,
                    )

    def set_mask_properties_values(self):
        """
        Set all the TSE component mask property values from the mask_properties dictionary.
        The component must be already added to the Schematic.

        Returns:
            None

        """
        if self.tse_instance:
            self.mdl.set_property_values(self.tse_instance, self.mask_properties)
        else:
            raise Exception(
                AttributeError,
                "Properties values cannot be initialized before the "
                "component is added to the schematic",
            )

    def write_mask_codes(self):
        if self.image_code:
            self.mdl.set_handler_code(self.mask, "define_icon", self.image_code)
        if self.description:
            self.mdl.set_description(self.mask, self.description)

    def write_property_codes(self):
        for property in self.mask_properties:
            property_handle = self.mdl.prop(self.mask, property)
            if property_handle and self.property_handlers:
                value_edited_code = self.property_handlers.get(
                    f"{property}_value_edited"
                )
                value_changed_code = self.property_handlers.get(
                    f"{property}_value_changed"
                )

                if value_edited_code:
                    self.mdl.set_handler_code(
                        property_handle, "property_value_edited", value_edited_code
                    )
                if value_changed_code:
                    self.mdl.set_handler_code(
                        property_handle, "property_value_changed", value_changed_code
                    )

    def add_terminal(self, terminal):
        """
        Adds the specified terminal object to the list of terminals.

        Returns:
            None
        """
        self._terminals.append(terminal)

    def create_ports(self):
        """
        Creates ports that are listed but are not present in the Subsystem component.

        Returns:
            None
        """
        # Order terminals by kind
        ordered_terminals = sorted(self.terminals, key=lambda f: f.kind)

        for terminal in ordered_terminals:
            if terminal.create_port:
                port_name = terminal.destination_name

                self.mdl.create_port(
                    name=port_name,
                    parent=self.tse_instance,
                    kind=terminal.kind,
                    position=move_to_center(terminal.port_position),
                    direction=terminal.direction,
                    terminal_position=terminal.position,
                )

    @property
    def terminals(self):
        """
        Returns the list of terminals of this Component.

        Returns:
            _terminals: list of terminals that belong to this component.
        """
        return self._terminals

    @property
    def position(self):
        """
        Returns:
            _position: Position of the component on the Schematic.
        """
        return self._position

    @position.setter
    def position(self, position):
        """
        Sets a new schematic position for the Component.
        """
        self._position = position

    @property
    def rotation(self):
        """
        Returns:
            _rotation: Rotation of the component on the Schematic.
        """
        return self._rotation

    @rotation.setter
    def rotation(self, rotation):
        """
        Sets a new schematic rotation for the Component.
        """
        if rotation in ["0", 0]:
            rotation = "up"
        elif rotation in ["90", 90]:
            rotation = "left"
        elif rotation in ["180", 180]:
            rotation = "down"
        elif rotation in ["270", 270]:
            rotation = "right"

        self._rotation = rotation

    @property
    def flip(self):
        """
        Returns:
            _flip: Flip status of the component on the Schematic.
        """
        return self._flip

    @flip.setter
    def flip(self, flip):
        """
        Sets a new schematic flip status for the Component.
        """
        if not flip:
            flip = "flip_none"

        self._flip = flip

    @property
    def size(self):
        """
        Returns:
            _size: Size of the component on the Schematic.
        """
        return self._size

    @property
    def needed_terminals(self):
        """
        Must be overriden by each specific component child class.

        Returns:
            needed_terminals: list of mandatory terminals (name) for a valid conversion
        """
        needed_terminals = None
        return needed_terminals

    @property
    def name(self):
        """
        Returns:
            name: The name of the component
        """
        return self._name

    def parent_subsystem(self):
        return self.parent

    @property
    def terminals_relative_positions(self):
        rel_positions = {}

        comp_size_x, comp_size_y = self.mdl.get_size(self.tse_instance)

        if comp_size_x and comp_size_y:
            rel_positions = aux_functions.calculate_terminals_relative_positions(
                comp_size_x, comp_size_y, self.terminals
            )
        return rel_positions

    def get_connected_components(self):
        """
        Returns:
            connected_components: a list of Components that are connected to this instance
        """
        connected_components = []

        for node in [terminal.node for terminal in self.terminals]:
            for other_component in [
                comp for comp in node.get_connected_components() if not comp == self
            ]:
                if other_component not in connected_components:
                    connected_components.append(other_component)

        return connected_components


class Port(Component):
    def __init__(
        self,
        schematic: Schematic,
        schematic_properties: dict,
        mask_properties: dict,
        parent=None,
    ):
        super().__init__(schematic, schematic_properties, mask_properties, parent)

        self._kind = schematic_properties["kind"]
        self._terminal_position = schematic_properties["terminal_position"]
        self._direction = schematic_properties["direction"]
        self._rotation = schematic_properties["rotation"]

    def add_to_schematic(self, to_center=True):
        pos = move_to_center(self.position) if to_center else self.position
        self.tse_instance = self.mdl.create_port(
            name=self.name,
            parent=self.parent.tse_instance,
            kind=self._kind,
            position=pos,
            direction=self._direction,
            rotation=self._rotation,
            terminal_position=self._terminal_position,
        )


class Tag(Component):
    def __init__(
        self,
        schematic: Schematic,
        schematic_properties: dict,
        mask_properties: dict,
        parent=None,
    ):
        super().__init__(schematic, schematic_properties, mask_properties, parent)

        self.value = schematic_properties["value"]
        self.scope = schematic_properties["scope"]
        self.kind = schematic_properties["kind"]
        self.direction = schematic_properties["direction"]
        self.rotation = schematic_properties["rotation"]

    def add_to_schematic(self, to_center=True):
        pos = move_to_center(self.position) if to_center else self.position
        self.tse_instance = self.mdl.create_tag(
            value=self.value,
            name=self.name,
            scope=self.scope,
            parent=self.parent.tse_instance if self.parent else None,
            kind=self.kind,
            position=pos,
            direction=self.direction,
            rotation=self.rotation,
        )


class Terminal:
    """
    Terminals are the points of connection of each component. Each terminal must belong to a single Component
    and must have an associated Node (which may be shared with other terminals).

    Attributes:
        origin_name (dict): The properties of the TSE component mask.
        destination_name (dict): The properties of the TSE component mask.
    """

    def __init__(
        self,
        schematic: Schematic,
        node: Node,
        parent: Component,
        origin_name: str,
        destination_name: str,
        kind="pe",
        direction="in",
        position=("left", "auto"),
        port_position=None,
        create_port=False,
    ):
        """
        Terminals are the points of connection of each component. Each terminal must belong to a single Component
        and must have an associated Node (which may be shared with other terminals).

        Args:
            node (Schematic): The node associated with this terminal.
            parent (Component): The component associated with this terminal.
            origin_name (str): The name of the terminal on the original tool.
            destination_name (str): The name of the terminal on the TSE component this object will represent.
        """

        self.schematic = schematic
        self.mdl = schematic.mdl
        self.origin_name = origin_name
        self.destination_name = destination_name
        self._parent = parent
        self._node = node
        self._kind = kind
        self._direction = direction
        self._position = position
        self._port_position = port_position
        self.create_port = create_port

        # Add terminal to the related Component and Node
        if self not in self.parent.terminals:
            self.parent.add_terminal(self)
        if self not in self.node.terminals:
            self.node.add_terminal(self)

        # After a port is created on the component it is saved to this attribute
        self.port = None

    @property
    def node(self):
        """
        Returns the Node associated with this terminal.
        """
        return self._node

    @property
    def parent(self):
        """
        Returns the Component associated with this terminal.
        """
        return self._parent

    def get_side(self, visual_position=False):
        """
        Returns the side this terminal is on the parent Component. Can return the current visual position
        if visual_position is set to True (considering rotation and flip status).

        Args:
            visual_position (bool): return the current visual position instead

        Returns:
            side (str): the side of the component the Terminal belongs to
        """

        if self.position[0] in ["right", "left", "top", "bottom"]:
            side = self.position[0]
        else:
            if (
                abs(self.parent.size[0] / 2 - float(self.position[0]))
                < TSE_GRID_RESOLUTION
            ):
                side = "right"
            elif (
                abs(-self.parent.size[0] / 2 - float(self.position[0]))
                < TSE_GRID_RESOLUTION
            ):
                side = "left"
            elif (
                abs(self.parent.size[1] / 2 - float(self.position[1]))
                < TSE_GRID_RESOLUTION
            ):
                side = "bottom"
            elif (
                abs(-self.parent.size[1] / 2 - float(self.position[1]))
                < TSE_GRID_RESOLUTION
            ):
                side = "top"

        if visual_position:
            rotation = self.parent.rotation
            flip = self.parent.flip
            side = aux_functions.terminal_side_after_rotation_and_flip(
                side, rotation, flip
            )

        return side

    @property
    def kind(self):
        return self._kind

    @property
    def direction(self):
        return self._direction

    @property
    def port_position(self):
        return self._port_position

    @property
    def position(self):
        return self._position

    @property
    def tse_instance(self):
        if isinstance(self.parent, (Port, Tag)):
            return self.parent.tse_instance
        else:
            return self.mdl.term(self.parent.tse_instance, self.destination_name)

    @property
    def parent_subsystem(self):
        return self.parent.parent

    @property
    def schematic_position(self):
        """
        The position is calculated based on the component's size if the terminal relative position is not
        defined as a tuple of ints. Otherwise, the relative position can be directly summed to the position of the
        component.

        Returns:
            schematic_position (tuple): (x, y) position of the terminal on the TSE schematic
        """

        comp_x, comp_y = self.mdl.get_position(self.parent.tse_instance)

        # Determine the relative position input format
        is_int = False
        try:
            int(self.position[0])
            is_int = True
        except ValueError:
            pass

        #
        # If int, directly sum to the center position of the component
        #
        if is_int:
            rel_x, rel_y = self.position
            tx = comp_x + rel_x
            ty = comp_y + rel_y
            schematic_position = (tx, ty)
        #
        # If not int, calculate from the component's size
        #
        else:
            relative_position = self.parent.terminals_relative_positions.get(self, {})
            if relative_position:
                rel_x, rel_y = relative_position

                if self.parent.rotation == "left":
                    rel_x, rel_y = rel_y, -rel_x
                elif self.parent.rotation == "right":
                    rel_x, rel_y = -rel_y, rel_x
                elif self.parent.rotation == "down":
                    rel_x, rel_y = -rel_x, -rel_y

                if self.parent.flip == "flip_horizontal":
                    rel_x, rel_y = -rel_x, rel_y
                elif self.parent.flip == "flip_vertical":
                    rel_x, rel_y = rel_x, -rel_y
                elif self.parent.flip == "flip_both":
                    rel_x, rel_y = -rel_x, -rel_y

                tx = comp_x + rel_x
                ty = comp_y + rel_y
                schematic_position = (tx, ty)

            else:
                schematic_position = (comp_x, comp_y)

        return schematic_position

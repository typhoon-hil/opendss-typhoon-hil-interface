import numpy as np
from PIL import Image, ImageDraw
from tqdm import tqdm
import random
from import_to_tse import aux_functions
import itertools
from import_to_tse.constants import CANVAS_CENTER

import sys
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyqtgraph as pg
import time
import multiprocessing

# Functions

def calculate_charge_force_on_component(components_data_dict, component, other_component):

    x0, y0 = components_data_dict[component]["position"]
    x1, y1 = components_data_dict[other_component]["position"]

    if abs(x1 - x0) > 128 * 8 or abs(y1 - y0) > 128 * 8:  # GRID SIZE
        charge_force = np.array([0.0, 0.0])
    else:
        charge_force = np.array([x0 - x1, y0 - y1]) * (max([0.1, (x0 - x1) ** 2 + (y0 - y1) ** 2])) ** (-3 / 2)

    if component in components_data_dict[other_component]['neighbors']:
        charge_force *= 10

    return {component: charge_force}

def calculate_charge_forces(components_data_dict, all_zeros=False, against_component=None):
    def conditional_product():
        if against_component:
            comp1 = against_component
            for comp2 in components_data_dict.keys():
                if comp1 is not comp2:
                    if not (all_zeros or components_data_dict[comp1]["locked_position"]):
                        yield components_data_dict, comp1, comp2
        else:
            for comp1 in components_data_dict.keys():
                for comp2 in components_data_dict.keys():
                    if comp1 is not comp2:
                        if not (all_zeros or components_data_dict[comp1]["locked_position"]):
                            yield components_data_dict, comp1, comp2

    zero_force = np.array([0.0, 0.0])
    charge_forces = {comp: zero_force for comp in components_data_dict}
    # Calculate all charge forces
    charge_forces_dict = itertools.starmap(calculate_charge_force_on_component, conditional_product())

    # Sum forces to the dictionary item
    for comp_force_dict in charge_forces_dict:
        for comp, force in comp_force_dict.items():
            charge_forces[comp] += force

    return charge_forces

def calculate_charge_force(components_data_dict, component1, component2):

    x0, y0 = components_data_dict[component1]["position"]
    x1, y1 = components_data_dict[component2]["position"]

    charge_force = np.array([x0 - x1, y0 - y1]) * (max([0.1, (x0 - x1) ** 2 + (y0 - y1) ** 2])) ** (-3 / 2)

    return charge_force

def calculate_spring_force(element, neighbors):
    # Calculate spring force
    x0, y0 = element['position']
    spring_force = np.array([0.0, 0.0])
    for neighbor in neighbors:
        x1, y1 = neighbor['position']
        spring_force += np.array([(x0 - x1), (y0 - y1)])

    return spring_force

def calculate_side_forces(component_data, against_component=False):
    all_spring_forces = {}
    all_rotational_forces = {}
    
    def calculate_spring_forces(component, comp_data):
        
        spring_forces = {
            "left": np.array([0.0, 0.0]),
            "right": np.array([0.0, 0.0]),
            "top": np.array([0.0, 0.0]),
            "bottom": np.array([0.0, 0.0]),
        }

        neighbors = component_data[component].get("neighbors")

        if not (component_data[component].get("locked_position") or component_data[component].get("locked_sides")):
            for neighbor in neighbors:

                spring_force = np.array([0.0, 0.0])
                neighbor_data = component_data[neighbor]
                comp_side, neighbor_side = aux_functions.get_connection_side(component, neighbor)

                if comp_side and neighbor_side:
                    x0, y0 = component_data[component]["side_charges"][comp_side].position
                    x1, y1 = neighbor_data["side_charges"][neighbor_side].position

                    # Calculate spring force
                    spring_force += np.array([(x0 - x1), (y0 - y1)])
                    if neighbor_data["locked_position"]:
                        spring_force *= 5
                    spring_forces[comp_side] += spring_force

        all_spring_forces[component] = dict(spring_forces)

        return spring_forces
    
    def calculate_rotational_forces(component, comp_data, spring_forces):
        
        rotational_forces = {}
        if not component_data[component].get("locked_sides"):
            right_charge = component_data[component]["side_charges"]["right"]

            # Transfer spring forces
            ang_force_left = np.arctan2(spring_forces["left"][1], spring_forces["left"][0])
            rotational_forces["left"] = \
                -np.sqrt(spring_forces["left"].dot(spring_forces["left"])) * -np.sin(ang_force_left - right_charge.angle)

            ang_force_right = np.arctan2(spring_forces["right"][1], spring_forces["right"][0])
            rotational_forces["right"] = \
                -np.sqrt(spring_forces["right"].dot(spring_forces["right"])) * np.sin(ang_force_right - right_charge.angle)

            ang_force_top = np.arctan2(spring_forces["top"][1], spring_forces["top"][0])
            rotational_forces["top"] = \
                -np.sqrt(spring_forces["top"].dot(spring_forces["top"])) * -np.cos(ang_force_top - right_charge.angle)

            ang_force_bottom = np.arctan2(spring_forces["bottom"][1], spring_forces["bottom"][0])
            rotational_forces["bottom"] = \
                -np.sqrt(spring_forces["bottom"].dot(spring_forces["bottom"])) * np.cos(
                    ang_force_bottom - right_charge.angle)
        else:
            rotational_forces["left"] = np.array([0.0, 0.0])
            rotational_forces["right"] = np.array([0.0, 0.0])
            rotational_forces["top"] = np.array([0.0, 0.0])
            rotational_forces["bottom"] = np.array([0.0, 0.0])

        all_rotational_forces[component] = dict(rotational_forces)


    if against_component:
        spring_forces = calculate_spring_forces(against_component, component_data[against_component])
        calculate_rotational_forces(against_component, component_data[against_component], spring_forces)
    else:
        for component, comp_data in component_data.items():
            spring_forces = calculate_spring_forces(component, comp_data)
            calculate_rotational_forces(component, comp_data, spring_forces)


    return all_spring_forces, all_rotational_forces

def initialize_sides(component_data_dict, sides_radius):
    component_data_dict["side_charges"] = {}
    component_data_dict["side_charges"]["left"] = SideCharge(side="left", angle=np.pi,
                                                   radius=sides_radius, position=None)
    component_data_dict["side_charges"]["left"].reposition_from_angle(center=component_data_dict["position"])
    component_data_dict["side_charges"]["right"] = SideCharge(side="right", angle=0.0,
                                                    radius=sides_radius, position=None)
    component_data_dict["side_charges"]["right"].reposition_from_angle(center=component_data_dict["position"])
    component_data_dict["side_charges"]["top"] = SideCharge(side="top", angle=np.pi / 2,
                                                  radius=sides_radius, position=None)
    component_data_dict["side_charges"]["top"].reposition_from_angle(center=component_data_dict["position"])
    component_data_dict["side_charges"]["bottom"] = SideCharge(side="bottom", angle=-np.pi / 2,
                                                     radius=sides_radius, position=None)
    component_data_dict["side_charges"]["bottom"].reposition_from_angle(center=component_data_dict["position"])

class SideCharge:
    def __init__(self, side, position, radius, angle=0.0, angular_velocity=0.0):
        self.side = side
        self.position = position
        self.radius = radius
        self.angle = angle
        self.angular_velocity = angular_velocity

    def reposition_from_angle(self, center):
        """
        Changing the angle sets new positions
        """

        vector = self.radius * np.array([np.cos(self.angle), np.sin(self.angle)])
        self.position = center + vector

class ChargeGraph(pg.GraphItem):

    def __init__(self):
        super().__init__()
        self.scatter.sigClicked.connect(self.clicked)
        self.texts = []
        self.displayed_text = None

    def clicked(self, scatter, pts):
        data_list = scatter.data.tolist()
        mypoint = [tup for tup in data_list if pts[0] in tup][0]

        if self.displayed_text:
            self.displayed_text.scene().removeItem(self.displayed_text)

        text_item = pg.TextItem(f"{self.texts[data_list.index(mypoint)]}")
        text_item.setParentItem(self)
        text_item.setPos(PyQt5.QtCore.QPointF(mypoint[0], mypoint[1]))
        text_item.setFont(PyQt5.QtGui.QFont("Times", 20, QFont.Bold))
        self.displayed_text = text_item

class AutoPlacerGUI(QMainWindow):

    def __init__(self, auto_placer_data, component_id_dict, start_placer=False):
        super().__init__()

        self.setWindowTitle("Automatic component placement")
        self.setGeometry(100, 100, 600, 500)
        icon = QIcon("skin.png")
        self.setWindowIcon(icon)
        self.UiComponents()

        # Initial data
        self.pos = []
        self.item_ids = {}
        self.adj = []
        self.symbols = []
        self.lines = []
        self.sizes = []
        self.symbolbrushes = []

        # Component placer instance
        self.placer = None
        self.final_positions = None

        self.auto_placer_data = auto_placer_data
        self.component_id_dict = component_id_dict

        # Iteration sequence timer
        self.placer_timer = QTimer()
        self.placer_timer.setInterval(20)
        self.placer_timer.timeout.connect(self.show_iterations_sequence)
        if start_placer:
            self.show_iterations = False
            self.start_component_placer()

        # All iteration sequences
        self.all_iterations_timer = QTimer()
        self.all_iterations_timer.setInterval(200)
        self.all_iterations_timer.timeout.connect(self.show_all_iterations)
        self.all_position_iterations = []
        self.all_component_data_statuses = []

        # Display refresh timer
        self.display_timer = QTimer()
        self.display_timer.setInterval(20)
        self.display_timer.timeout.connect(self.update_graph)

        # Show widgets
        self.show()

    def UiComponents(self):

        widget = QWidget()
        pg.setConfigOptions(antialias=True)
        win = pg.GraphicsLayoutWidget()
        view = win.addViewBox()

        # Lock the aspect ratio
        view.setAspectLocked()
        self.resize(1280, 720)

        # Creating a graph item
        self.graph_item = ChargeGraph()

        # Grid
        self.grid_item = pg.GridItem()
        self.grid_item.setPen(pg.mkPen(color=(255, 255, 255, 190)))

        # Add graph item to the view box
        view.addItem(self.graph_item)
        view.addItem(self.grid_item)

        layout = QGridLayout()
        widget.setLayout(layout)
        layout.addWidget(win, 0, 1, 3, 1)

        self.setCentralWidget(widget)

    def set_graph_elements(self, component_data):

        tse_components = self.auto_placer_data["tse_components"]
        neighbors_dict = self.auto_placer_data["neighbors_dict"]

        component_ids = {}
        for idx, component in enumerate(tse_components):
            component_ids[component] = idx

        self.adj = np.array([[component_ids.get(component), component_ids.get(neighbor)] for component, neighbors in
                             neighbors_dict.items() for neighbor in neighbors])

        self.symbols = ['x' if component_data[comp]["locked_position"] else 'o' for comp in tse_components]
        self.lines = np.array([(255, 255, 255, 255, 3), ] * len(self.adj),
                              dtype=[('red', np.ubyte), ('green', np.ubyte), ('blue', np.ubyte), ('alpha', np.ubyte),
                                     ('width', float)])

    def set_graph_elements_side_charges(self, component_data):

        # tse_components = self.auto_placer_data["tse_components"]

        side_charges = []
        for component, data in component_data.items():
            side_charges.append(data["side_charges"]["left"])
            side_charges.append(data["side_charges"]["right"])
            side_charges.append(data["side_charges"]["top"])
            side_charges.append(data["side_charges"]["bottom"])

        item_ids = {}
        for idx, item in enumerate(list(component_data.keys()) + side_charges):
            item_ids[item] = idx
        self.item_ids = item_ids

        adj = []

        for component, comp_data in component_data.items():
            for neighbor in comp_data["neighbors"]:
                neighbor_data = component_data[neighbor]
                comp_side, neighbor_side = aux_functions.get_connection_side(component, neighbor)
                adj.append([item_ids[comp_data["side_charges"][comp_side]],
                            item_ids[neighbor_data["side_charges"][neighbor_side]]])

        self.adj = np.array(adj)

        # Nodes
        symbols = []
        symbol_brushes = []
        sizes = []
        texts = []
        for item in item_ids:
            if isinstance(item, SideCharge):
                symbols.append("o")
                symbol_brushes.append(pg.mkBrush(color=(0, 255, 0)))
                sizes.append(30)
                texts.append("")
            elif item in component_data:
                texts.append(f"{item.name}")
                if component_data[item]["locked_position"]:
                    symbols.append("s")
                    symbol_brushes.append(pg.mkBrush(color=(0, 255, 255, 100)))
                    sizes.append(64)
                else:
                    symbols.append("o")
                    symbol_brushes.append(pg.mkBrush(color=(0, 255, 255, 255)))
                    sizes.append(64)

        self.symbols = symbols
        self.symbolbrushes = symbol_brushes
        self.sizes = sizes
        self.texts = texts

        # self.symbols = ['x' if component_data[comp]["locked_position"] else 'o' for comp in tse_components]

        self.lines = np.array([(255, 255, 255, 180, 2),] * len(self.adj),
                              dtype=[('red', np.ubyte), ('green', np.ubyte), ('blue', np.ubyte), ('alpha', np.ubyte),
                                     ('width', float)])

    def start_component_placer(self, canvas_scale=32, fork_component_type=None):
        # 4 charges for sides

        component_data = {}

        tse_components = self.auto_placer_data["tse_components"]
        neighbors_dict = self.auto_placer_data["neighbors_dict"]
        iterations = self.auto_placer_data["iterations"]
        gains = self.auto_placer_data["gains"]

        component_ids = {}
        for idx, component in enumerate(tse_components):
            component_ids[component] = idx

        for component in tse_components:
            component_data[component] = {
                "neighbors": neighbors_dict.get(component, []),
                "initialize_pos": True,
                "initialize_velocity": True,
                "locked_position": False
            }

        self.placer = ComponentPlacer(component_data, iterations=iterations, gains=gains, canvas_scale=canvas_scale)
        self.placer.filter_parallel_components(fork_component_type="OpenDSS/Bus")
        cycles, paths = self.placer.find_cycles_and_paths()
        # self.placer.pre_position_longest_paths(paths)
        self.placer.break_cycles(cycles, paths)
        self.placer.grow_tree(paths)

        placement_info = self.placer.force_directed_graph_sides_mode(component_data)
        for component, data in component_data.items():
            data["initialize_pos"] = False
        self.positions_iterations = iter(placement_info)

        self.set_graph_elements_side_charges(component_data)
        self.final_positions = self.placer.final_positions

        pos_list = []
        for item, id in self.item_ids.items():
            pos_list.append(self.final_positions[item])
        self.pos = np.array(pos_list)

        self.show_iterations = True
        self.placer_timer.start()

    def show_iterations_sequence(self):
        if self.show_iterations:
            old_pos = self.pos
            iter_list = next(self.positions_iterations, None)
            positions = next(self.positions_iterations, None)

            if positions:
                pos_list = []
                for item, id in self.item_ids.items():
                    pos_list.append(positions[item])
                self.pos = np.array(pos_list)

            else:
                # self.close()
                self.display_timer.stop()
                self.placer_timer.stop()
                # self.placer.snap_to_grid(0.25)
                # self.pos = np.array([pos for pos in self.placer.final_positions.values()])


    def show_all_iterations(self):

        if not self.placer_timer.isActive():

            positions_iterations_status = next(self.all_position_iterations, None)
            temp_data_status = next(self.all_component_data_statuses, None)

            if positions_iterations_status:
                # Create neighbors dict
                neighbors_dict = {}
                for comp, data in temp_data_status.items():
                    comp_nbs = []
                    for nb in data['neighbors']:
                        if nb in temp_data_status:
                            comp_nbs.append(nb)
                    neighbors_dict[comp] = comp_nbs

                comps = temp_data_status.keys()

                gui_data = {
                    "tse_components": comps,
                    "neighbors_dict": neighbors_dict
                }

                self.auto_placer_data = gui_data
                self.set_graph_elements_side_charges(temp_data_status)
                self.show_iterations = True
                self.positions_iterations = iter(positions_iterations_status)
                self.display_timer.start()
                self.placer_timer.start()
            else:
                self.all_iterations_timer.stop()


    def update_graph(self):
        self.graph_item.texts = self.texts
        self.graph_item.setData(pos=np.array(self.pos), adj=np.array(self.adj),
                                pen=self.lines, size=self.sizes, symbol=self.symbols,
                                symbolBrush=self.symbolbrushes, pxMode=False)


class ComponentPlacer:
    """
    Automatically places components on the schematic canvas (by subsystem level) when there is no position information.
    """

    def __init__(self, component_data, gains, canvas_scale=32, iterations=None,
                 pbar_in=None, grid_size=0, sides_radius=64, seed_component_type=None):

        self.component_data = component_data
        self.final_positions = {}
        self.gains = gains
        self.iterations = iterations
        self.canvas_scale = canvas_scale
        self.progress_bar = pbar_in
        self.grid_size = grid_size
        self.sides_radius = sides_radius
        self.seed_component_type = seed_component_type
        self.cycles = []
        self.paths = []

    def snap_to_grid(self, original_position):
        """
        Reposition all the components to a grid defined by grid_size.
        """

        x = original_position[0]
        y = original_position[1]

        new_x = aux_functions.snap_to_grid(x, self.grid_size)
        new_y = aux_functions.snap_to_grid(y, self.grid_size)

        return np.array([new_x, new_y])

    def filter_parallel_components(self, fork_component_type=None):
        """
        Connections between parallel components add extra unnecessary springs. This method will look for such
        situations and remove neighbors from components.

        If a fork component type is passed, the first component of that type in the parallel block will
        retain all neighbors.
        """

        def remove_neighbors(component, data_dict):
            this_comp_neighbors = data_dict["neighbors"]
            for neighbor in this_comp_neighbors:
                # If the neighbor is connected to components already in the evaluated component's neighbors, remove
                # the spring
                neighbor_neighbors = self.component_data[neighbor]["neighbors"]
                for neighbor_neighbor in neighbor_neighbors[:]:
                    remove = False
                    for term1 in component.terminals:
                        for term2 in neighbor.terminals:
                            for term3 in neighbor_neighbor.terminals:
                                if term1.node == term2.node == term3.node:
                                    remove = True

                    if remove and neighbor_neighbor in this_comp_neighbors and not neighbor_neighbor == component:
                        neighbor_neighbors.remove(neighbor_neighbor)

        if fork_component_type:
            for component, data_dict in self.component_data.items():
                if component.schematic_properties["type_name"] == fork_component_type:
                    remove_neighbors(component, data_dict)

        for component, data_dict in self.component_data.items():
            remove_neighbors(component, data_dict)

    def find_cycles_and_paths(self):
        """
        Searches the graph for unique paths and cycles. Parallel components must already have been filtered through
        filter_parallel_components to remove small, meaningless cycles.

        Returns:
            cycles: List of unique paths in the graph.
            paths: List of unique cycles in the graph.
        """

        def traverse_neighbor(paths, path, start_component, start_neighbor):

            neighbors_nbs = [nb for nb in self.component_data[start_neighbor]["neighbors"] if nb is not start_component
                             and nb not in self.component_data[start_component]["neighbors"]]

            # If this is the last component in the path, just add it
            if len(neighbors_nbs) == 0:
                path.append(start_neighbor)
                paths.append(path)

            # If the length is one, add and keep moving
            elif len(neighbors_nbs) == 1:
                nb = neighbors_nbs[0]
                if start_neighbor not in path:
                    path.append(start_neighbor)
                    traverse_neighbor(paths, path, start_neighbor, nb)
                else:
                    if set(path[path.index(start_neighbor):]) not in [set(c) for c in cycles]:
                        cycles.append(path[path.index(start_neighbor):])

            # If there is a fork, add each path independently
            else:
                if start_neighbor in path:
                    if set(path[path.index(start_neighbor):]) not in [set(c) for c in cycles]:
                        cycles.append(path[path.index(start_neighbor):])
                else:
                    path.append(start_neighbor)
                    for nb in neighbors_nbs:
                        traverse_neighbor(paths, path[:], start_neighbor, nb)

            return paths

        start_component = None
        for component, comp_data in self.component_data.items():
            if len(comp_data["neighbors"]) == 1:
                start_component = component
                break

        if not start_component:
            start_component = next(iter(self.component_data))

        start_path = [start_component]
        paths = []
        cycles = []
        for neighbor in self.component_data[start_component]["neighbors"]:
            traverse_neighbor(paths, start_path[:], start_component, neighbor)

        self.cycles = cycles
        self.paths = paths

    def find_complete_tree(self):

        def find_cycle_breaking_points():

            breaking_points = []
            broken_cycles = []
            ordered_cycles = sorted(self.cycles, key= lambda c: len(c), reverse=True)
            for cycle in [c for c in ordered_cycles if len(c) > 5]:
                for breaking_comp in cycle[len(cycle) // 2 - 2:len(cycle) // 2 + 2]:
                    free_to_break = True
                    for c in broken_cycles:
                        if breaking_comp in c:
                            free_to_break = False
                            break

                    if free_to_break:
                        breaking_points.append(breaking_comp)
                        broken_cycles.append(cycle)

            return breaking_points

        def traverse_component(component, tree, branch):

            branch.append(component)
            if component not in tree["all_components"]:
                tree["all_components"].append(component)

            new_neighbors = [nb for nb in self.component_data[component]["neighbors"] if
                             nb not in tree["all_components"]]
            if len(new_neighbors) == 1:
                if new_neighbors[0] not in tree["all_components"]:
                    if new_neighbors[0] in cycle_breaking_points:
                        tree[branch[0]] = {"branch": branch[:], "sub_branches": []}
                    else:
                        traverse_component(new_neighbors[0], tree, branch)

            elif len(new_neighbors) > 1:
                tree[branch[0]] = {"branch": branch[:], "sub_branches": []}
                if component not in tree["all_components"]:
                    tree["all_components"].extend(new_neighbors)
                for neighbor in new_neighbors:
                    tree[branch[0]]["sub_branches"].append(neighbor)
                    traverse_component(neighbor, tree, branch=[])
            else:
                # Finalize the branch
                tree[branch[0]] = {"branch": branch, "sub_branches": []}

        start_component = None

        # Try to find the preferred seed
        if self.seed_component_type:
            for component, comp_data in self.component_data.items():
                if component.type_name == self.seed_component_type:
                    start_component = component
                    break

        # Try to find a terminal component
        if not start_component:
            for component, comp_data in self.component_data.items():
                if len(comp_data["neighbors"]) == 1:
                    start_component = component
                    break

        # Just use the first one
        if not start_component:
            start_component = next(iter(self.component_data))

        cycle_breaking_points = find_cycle_breaking_points()

        # Start
        complete_tree = {"seed": start_component, "all_components": [start_component]}
        traverse_component(start_component, tree=complete_tree, branch=[])

        return complete_tree

    def grow_tree(self, tree):

        app = PyQt5.QtWidgets.QApplication(sys.argv)
        def count_future_splits(branch):

            def sum_branches(b, total_splits, total_levels):
                sub_branches = tree[b].get("sub_branches")
                total_splits += len(sub_branches)
                if sub_branches:
                    total_splits -= 1
                    total_levels += 1
                for sub_branch in sub_branches:
                    sub_branch_splits = sum_branches(sub_branch, total_splits=0, total_levels=0)
                    total_splits += sub_branch_splits[0]
                    total_levels += sub_branch_splits[1]

                return total_splits, total_levels

            return sum_branches(branch, total_splits=1, total_levels=0)


        def place_start_components_of_branches(splitting_branch, temp_data, branch_level):

            # Determine direction of the growth
            second_to_last_added_component = tree[splitting_branch]["branch"][-2]
            last_added_component = tree[splitting_branch]["branch"][-1]

            ref_x, ref_y = temp_data[last_added_component]["position"]
            prev_x, prev_y = temp_data[second_to_last_added_component]["position"]

            dif_x = ref_x - prev_x
            dif_y = ref_y - prev_y

            if abs(dif_x) >= abs(dif_y):
                if dif_x > 0:
                    direction = "right"
                else:
                    direction = "left"
            else:
                if dif_y > 0:
                    direction = "up"
                else:
                    direction = "down"

            sub_branches = tree[splitting_branch].get("sub_branches")
            split_counts = {sub_branch: count_future_splits(sub_branch) for sub_branch in sub_branches}
            ordered_sub_branches = sorted(sub_branches, key=lambda n: split_counts.get(n), reverse=True)

            # Place the starting components of each sub branch
            positions = {}

            # Branches are ordered by number of splits, so alternate by level to avoid moving too far up or down
            next_side = "up" if aux_functions.odd(branch_level) else "down"
            sum_space_up = 0
            sum_space_down = 0
            x_pos = self.grid_size
            y0_pos_is_free = True
            for idx, sub_branch in enumerate(ordered_sub_branches):

                # Move a little so wires don't go through the previous component
                clear_y0_pos = False
                connection_sides = aux_functions.get_connection_side(sub_branch, last_added_component)
                right_side_angle = temp_data[last_added_component]["side_charges"]["right"].angle

                if direction == "right":
                    if ((right_side_angle == np.pi and connection_sides[1] == "right") or
                            (right_side_angle == 0.0 and connection_sides[1] == "left")):
                        clear_y0_pos = True
                elif direction == "left":
                    if ((right_side_angle == np.pi and connection_sides[1] == "left") or
                            (right_side_angle == 0.0 and connection_sides[1] == "right")):
                        clear_y0_pos = True
                elif direction == "up":
                    if ((right_side_angle == np.pi / 2 and connection_sides[1] == "left") or
                            (right_side_angle == -np.pi / 2 and connection_sides[1] == "right")):
                        clear_y0_pos = True
                elif direction == "down":
                    if ((right_side_angle == -np.pi / 2 and connection_sides[1] == "left") or
                            (right_side_angle == np.pi / 2 and connection_sides[1] == "right")):
                        clear_y0_pos = True


                half_splits = split_counts[sub_branch][0] // 2
                if idx == 0:
                    sum_space_up += half_splits
                    sum_space_down += half_splits

                    # Move a little so wires don't go through the previous component
                    if next_side == "up":
                        if clear_y0_pos:
                            sum_space_up += 1
                            y_pos = self.grid_size
                        else:
                            y_pos = 0
                            y0_pos_is_free = False
                    else:
                        if clear_y0_pos:
                            sum_space_down += 1
                            y_pos = -self.grid_size
                        else:
                            y_pos = 0
                            y0_pos_is_free = False
                else:
                    if next_side == "up":
                        sum_space_up += split_counts[sub_branch][0]
                        if len(tree[sub_branch]["branch"]) == 1:
                            if y0_pos_is_free and not clear_y0_pos:
                                y_pos = 0
                                y0_pos_is_free = False
                            else:
                                sum_space_down += 1
                                y_pos = -self.grid_size
                        else:
                            y_pos = self.grid_size * sum_space_up
                        next_side = "down"

                    elif next_side == "down":
                        sum_space_down += split_counts[sub_branch][0]
                        if len(tree[sub_branch]["branch"]) == 1:
                            if y0_pos_is_free and not clear_y0_pos:
                                y_pos = 0
                                y0_pos_is_free = False
                            else:
                                sum_space_up += 1
                                y_pos = self.grid_size
                        else:
                            y_pos = -self.grid_size * sum_space_down
                        next_side = "up"

                # Save the position
                positions[sub_branch] = [x_pos, y_pos]

            # Change position values depending on the direction
            for sub_branch, position in positions.items():
                connection_side = aux_functions.get_connection_side(last_added_component, sub_branch)

                new_position = position
                if direction == "right":
                    new_position[0], new_position[1] = ref_x + position[0], ref_y + position[1]
                    while new_position in position_slots:
                        new_position[1] += np.random.choice([-1, 1]) * self.grid_size
                    if connection_side[1] == "right":
                        sub_branch.flip = "flip_horizontal"
                    elif connection_side[1] == "top":
                        sub_branch.rotation = "left"
                        sub_branch.flip = "flip_vertical"
                    elif connection_side[1] == "bottom":
                        sub_branch.rotation = "right"
                elif direction == "up":
                    new_position[0], new_position[1] = -position[1], position[0]
                    new_position[0], new_position[1] = ref_x + new_position[0], ref_y + new_position[1]
                    while new_position in position_slots:
                        new_position[0] += np.random.choice([-1, 1]) * self.grid_size
                    if connection_side[1] == "top":
                        sub_branch.flip = "flip_vertical"
                    elif connection_side[1] == "left":
                        sub_branch.rotation = "left"
                    elif connection_side[1] == "right":
                        sub_branch.rotation = "right"
                        sub_branch.flip = "flip_horizontal"
                elif direction == "left":
                    new_position[0], new_position[1] = -position[0], position[1]
                    new_position[0], new_position[1] = ref_x + new_position[0], ref_y + new_position[1]
                    while new_position in position_slots:
                        new_position[1] += np.random.choice([-1, 1]) * self.grid_size
                    if connection_side[1] == "left":
                        sub_branch.flip = "flip_horizontal"
                    elif connection_side[1] == "top":
                        sub_branch.rotation = "right"
                    elif connection_side[1] == "bottom":
                        sub_branch.rotation = "left"
                        sub_branch.flip = "flip_vertical"
                elif direction == "down":
                    new_position[0], new_position[1] = position[1], -position[0]
                    new_position[0], new_position[1] = ref_x + new_position[0], ref_y + new_position[1]
                    while new_position in position_slots:
                        new_position[0] += np.random.choice([-1, 1]) * self.grid_size
                    if connection_side[1] == "bottom":
                        sub_branch.flip = "flip_horizontal"
                    elif connection_side[1] == "left":
                        sub_branch.rotation = "right"
                        sub_branch.flip = "flip_horizontal"
                    elif connection_side[1] == "right":
                        sub_branch.rotation = "left"

                positions[sub_branch] = new_position
                position_slots.append(new_position)

            return positions

        def grow_branch(branch, temp_data, level=0):

            progress_bar.update(1)

            for comp_idx, component in enumerate(tree[branch]["branch"]):

                if component not in temp_data:
                    progress_bar.update(1)
                    temp_data[component] = dict(self.component_data[component])


                    saved_neighbors = {}
                    for comp in temp_data:
                        all_neighbors = self.component_data[comp]["neighbors"][:]
                        saved_neighbors[comp] = all_neighbors[:]
                        for neighbor in temp_data[comp]["neighbors"][:]:
                            # Remove any neighbors that have not been added
                            if neighbor not in temp_data:
                                temp_data[comp]["neighbors"].remove(neighbor)

                    # Remove neighbors that represent cycle connections
                    for neighbor in temp_data[component]["neighbors"][:]:
                        if neighbor not in tree[branch]["branch"]:
                            if neighbor in temp_data[component]["neighbors"]:
                                temp_data[component]["neighbors"].remove(neighbor)

                    if level == 0 and comp_idx == 0:
                        center = [0, 0]
                    elif comp_idx == 0:
                        center = temp_data[branch]["position"]
                    else:
                        center = temp_data[tree[branch]["branch"][comp_idx - 1]]["position"]

                    # Save status for GUI display
                    positions_iteration_lists.append(list(self.force_directed_graph_sides_mode(temp_data, center=center,
                                                                                single_component=component)))

                    copy_data = dict(temp_data)
                    for comp in copy_data:
                        copy_data[comp] = dict(temp_data[comp])
                    temp_datas.append(copy_data)

                    position_slots.append(list(temp_data[component]["position"]))


                    # Lock side angles to horizontal / vertical
                    right_charge = temp_data[component]["side_charges"]["right"]
                    top_charge = temp_data[component]["side_charges"]["top"]
                    left_charge = temp_data[component]["side_charges"]["left"]
                    bottom_charge = temp_data[component]["side_charges"]["bottom"]

                    if np.pi / 4 <= right_charge.angle % (2 * np.pi) < 3 * np.pi / 4:
                        right_charge.angle = np.pi / 2
                    elif 3 * np.pi / 4 <= right_charge.angle % (2 * np.pi) < 5 * np.pi / 4:
                        right_charge.angle = np.pi
                    elif 5 * np.pi / 4 <= right_charge.angle % (2 * np.pi) < 7 * np.pi / 4:
                        right_charge.angle = 3 * np.pi / 2
                    else:
                        right_charge.angle = 0.0
                    top_charge.angle = right_charge.angle + np.pi / 2
                    left_charge.angle = right_charge.angle + np.pi
                    bottom_charge.angle = right_charge.angle + 3 * np.pi / 2

                    right_charge.reposition_from_angle(center=temp_data[component]["position"])
                    top_charge.reposition_from_angle(center=temp_data[component]["position"])
                    left_charge.reposition_from_angle(center=temp_data[component]["position"])
                    bottom_charge.reposition_from_angle(center=temp_data[component]["position"])

                    temp_data[component].update({
                        "initialize_pos": False,
                        "initialize_sides": False,
                        "initialize_velocity": False,
                        "locked_position": True,
                        "locked_sides": True
                    })

                    # Restore the neighbors previously removed
                    for comp, neighbors in saved_neighbors.items():
                        temp_data[comp]["neighbors"] = neighbors

                    self.component_data[component]["side_charges"] = temp_data[component]["side_charges"]


            # Use the number of splits to create spacing between neighbors
            sub_branches = tree[branch].get("sub_branches")
            if sub_branches:
                level += 1
                positions = place_start_components_of_branches(splitting_branch=branch,
                                                               temp_data=temp_data, branch_level=level)
                for sub_branch in sub_branches:
                    temp_data[sub_branch] = dict(self.component_data[sub_branch])
                    temp_data[sub_branch].update({
                        "initialize_pos": False,
                        "initialize_sides": False,
                        "locked_sides": True,
                        "initialize_velocity": False,
                        "locked_position": True,
                        "position": np.array(positions.get(sub_branch)),
                        "velocity": np.array([0.0, 0.0]),
                        "neighbors": []
                    })
                    initialize_sides(temp_data[sub_branch], self.sides_radius)
                    self.final_positions[sub_branch] = np.array(positions.get(sub_branch))
                for sub_branch in sub_branches:

                    temp_data[sub_branch]["neighbors"] = self.component_data[sub_branch]["neighbors"][:]
                    grow_branch(sub_branch, temp_data, level)



        placed_components = []
        component_data = {}

        progress_bar = tqdm(total=len(tree.get("all_components")))

        # Occupied position slots
        position_slots = []

        # Statuses for GUI display
        positions_iteration_lists = []
        temp_datas = []

        # Position the components. Start growing the first branch.
        grow_branch(tree["seed"], component_data)

        if self.gui_mode:
            # GUI setup
            gui_data = {
                "tse_components": [],
                "neighbors_dict": {}
            }
            gui = AutoPlacerGUI(gui_data, {})
            gui.all_position_iterations = iter(positions_iteration_lists)
            gui.all_component_data_statuses = iter(temp_datas)
            gui.grid_item.setTickSpacing([self.grid_size], [self.grid_size])

            # Skip first one (no neighbors)
            next(gui.all_position_iterations)
            next(gui.all_component_data_statuses)
            gui.all_iterations_timer.start()
            app.exec()

        if self.progress_bar is None:
            progress_bar.close()

        for component, comp_data in component_data.items():
            if comp_data["neighbors"]:
                conn_side = aux_functions.get_connection_side(component, comp_data["neighbors"][0])[0]
                if np.pi / 4 <= comp_data["side_charges"]["right"].angle % (2 * np.pi) < 3 * np.pi / 4:
                    if conn_side in ["top", "bottom"]:
                        component.flip = "flip_vertical"
                    component.rotation = aux_functions.rotate_tse_object(component.rotation, direction="left", times=1)
                elif 3 * np.pi / 4 <= comp_data["side_charges"]["right"].angle % (2 * np.pi) < 5 * np.pi / 4:
                    component.rotation = aux_functions.rotate_tse_object(component.rotation, direction="left", times=2)
                    if conn_side in ["right", "left"]:
                        component.flip = "flip_vertical"
                    if conn_side in ["bottom", "top"]:
                        component.flip = "flip_horizontal"
                elif 5 * np.pi / 4 <= comp_data["side_charges"]["right"].angle % (2 * np.pi) < 7 * np.pi / 4:
                    component.rotation = aux_functions.rotate_tse_object(component.rotation, direction="right", times=1)
                    if conn_side in ["left", "right"]:
                        component.flip = "flip_horizontal"
                # else:
                #     if conn_side == "bottom":
                #         component.flip = "flip_horizontal"
                #     elif conn_side == "left":
                #         component.flip = "flip_vertical"

    def break_cycles(self):
        """
        Opens cycles by removing neighbor references.

        Args:
            paths: List of unique paths in the graph.
            cycles: List of unique cycles in the graph.
        """

        cycles = self.cycles
        paths = self.paths

        broken_cycles = {id(c): False for c in cycles}

        for cycle in cycles:
            if not broken_cycles[id(cycle)]:
                # Break this cycle
                comp = cycle[0]
                neighbor = cycle[1]
                self.component_data[comp]["neighbors"].remove(neighbor)
                self.component_data[neighbor]["neighbors"].remove(comp)
                broken_cycles[id(cycle)] = True

                for p in paths:
                    if comp in p:
                        comp_idx = p.index(comp)
                        if comp_idx < len(p):
                            # If the neighbor is in the sequence, split the path
                            if neighbor is p[comp_idx + 1]:
                                paths.append(p[:comp_idx])
                                paths.append(p[comp_idx + 1:])
                                paths.remove(p)
                        elif comp_idx > len(p):
                            # If the neighbor is behind, split too
                            if neighbor is p[comp_idx - 1]:
                                paths.append(p[comp_idx - 1:])
                                paths.append(p[:comp_idx])
                                paths.remove(p)

                # Check if the operation broke other cycles
                other_cycles = [c for c in cycles if c is not cycle]
                for other_cycle in other_cycles:
                    if comp in other_cycle and neighbor in other_cycle:
                        broken_cycles[id(other_cycle)] = True





    def force_directed_graph_sides_mode(self, component_data, center=[0.0, 0.0], single_component=None):
        """

        Args:
            component_data:
            center:
            single_component:

        Returns:

        """
        # Simulate force-directed graph evolution
        
        charge_gain, spring_gain, friction_gain, t = self.gains
        position_iter_compare = 0.1
        angle_iter_compare = (0.1 * np.pi / 180)
        average_size = 50
        charge_position_average = [position_iter_compare * 2] * average_size
        angle_average = [angle_iter_compare * 2] * average_size
        def update_forces_on_component(comp, comp_data_dict, charge_forces, all_spring_forces):
            force_vectors = {}

            # Forces on the component
            total_charge_force = np.array([0.0, 0.0])
            total_side_charges_force = np.array([0.0, 0.0])

            if comp_data_dict.get("locked_position"):
                # Ignore forces if the component is locked into place
                pass
            else:
                total_charge_force = charge_forces[comp]

            spring_forces = all_spring_forces[comp]
            total_side_charges_force += sum([force for force in spring_forces.values()])

            total_force = (charge_gain * total_charge_force
                           - spring_gain * total_side_charges_force
                           - friction_gain * comp_data_dict['velocity'])

            force_x, force_y = total_force
            force_x_limited = -150 if force_x < -150 else 150 if force_x > 150 else force_x
            force_y_limited = -150 if force_y < -150 else 150 if force_y > 150 else force_y

            force_vectors[comp] = np.array([force_x_limited, force_y_limited])

            return force_vectors

        def calculate_new_positions_and_velocities(comp, comp_data_dict, force_vectors):

            stop_iter = False

            # Calculate new positions and velocities
            old_pos = np.array(comp_data_dict['position'])
            old_vel = np.array(comp_data_dict['velocity'])
            force = force_vectors[comp]

            # Calculate position and limit it to the size of the schematic canvas
            if not comp_data_dict["locked_position"]:
                new_position = old_pos + old_vel * t + 1 / 2 * force * t ** 2
                new_pos_x, new_pos_y = new_position
                x_limited = x_min if new_pos_x < x_min else x_max if new_pos_x > x_max else new_pos_x
                y_limited = y_min if new_pos_y < y_min else y_max if new_pos_y > y_max else new_pos_y
                comp_data_dict['position'] = np.array([x_limited, y_limited])
                pos_dif = comp_data_dict['position'] - old_pos
                if pos_dif[0] > pos_dif[1]:
                    charge_position_average.append(pos_dif[0])
                else:
                    charge_position_average.append(pos_dif[1])
                if len(charge_position_average) > average_size:
                    charge_position_average.pop(0)

            # Calculate velocity
            if not comp_data_dict["locked_position"]:
                new_vel = old_vel + force * t
                # Saturate velocity
                new_vel_x, new_vel_y = new_vel
                vx_limited = -50 if new_vel_x < -50 else 50 if new_vel_x > 50 else new_vel_x
                vy_limited = -50 if new_vel_y < -50 else 50 if new_vel_y > 50 else new_vel_y
                comp_data_dict['velocity'] = np.array([vx_limited, vy_limited])

            right_charge = comp_data_dict["side_charges"]["right"]
            top_charge = comp_data_dict["side_charges"]["top"]
            left_charge = comp_data_dict["side_charges"]["left"]
            bottom_charge = comp_data_dict["side_charges"]["bottom"]

            if not comp_data_dict["locked_sides"]:
                # Set position for side charges

                rotational_forces = all_rotational_forces[comp]
                # Torque (saturated)
                torque = 1 / 2 * sum([force for force in rotational_forces.values()])
                torque = 1 if torque > 1else -1 if torque < -1 else torque
                # Angular velocity (saturated)
                ang_v = right_charge.angular_velocity + torque * t
                ang_v = 0.05 if ang_v > 0.05 else -0.05 if ang_v < -0.05 else ang_v

                # New angular velocities
                right_charge.angular_velocity = ang_v
                top_charge.angular_velocity = ang_v
                left_charge.angular_velocity = ang_v
                bottom_charge.angular_velocity = ang_v

                # New angles
                old_angle = right_charge.angle
                right_charge.angle = right_charge.angle + ang_v * t + 1 / 2 * torque * t ** 2 + 2 * np.pi
                top_charge.angle = right_charge.angle + np.pi / 2
                left_charge.angle = right_charge.angle + np.pi
                bottom_charge.angle = right_charge.angle - np.pi / 2

                angle_average.append(old_angle + 2 * np.pi - right_charge.angle)
                if len(angle_average) > average_size:
                    angle_average.pop(0)

                right_charge.reposition_from_angle(center=comp_data_dict["position"])
                top_charge.reposition_from_angle(center=comp_data_dict["position"])
                left_charge.reposition_from_angle(center=comp_data_dict["position"])
                bottom_charge.reposition_from_angle(center=comp_data_dict["position"])

            # Stop iterations if the charges are moving / spinning too slowly

            if (sum(angle_average) / average_size < angle_iter_compare and
                sum(charge_position_average) / average_size < position_iter_compare):
                stop_iter = True

            return stop_iter

        def update_position(comp, comp_data_dict):
            comp_position = comp_data_dict['position']
            self.final_positions[comp] = self.canvas_scale * np.array(comp_position)

            # Set position for side charges
            for side, side_charge in comp_data_dict["side_charges"].items():
                self.final_positions[side_charge] = self.canvas_scale * np.array(side_charge.position)

        def snap_to_grid_and_reposition_sides(comp, comp_data_dict):
            if self.grid_size:
                comp_data_dict["position"] = self.snap_to_grid(comp_data_dict["position"])
                for side, side_charge in comp_data_dict["side_charges"].items():
                    side_charge.reposition_from_angle(center=comp_data_dict["position"])


        # Position initialization information (circle of connected components)
        number_of_components = len(component_data)
        step_angle = max(2 * np.pi / number_of_components, np.pi / 8)
        rot_mult = 0
        # Order the components, trying to bring neighbors close
        ordered_components = []
        for component, data_dict in component_data.items():
            if component not in ordered_components:
                ordered_components.append(component)
            for neighbor in data_dict["neighbors"]:
                if neighbor not in ordered_components:
                    ordered_components.append(neighbor)

        # Side charges initialization information
        for component in ordered_components:
            data_dict = component_data[component]
            if data_dict.get("initialize_pos"):
                rot_matrix = np.array(
                    [[np.cos(rot_mult * step_angle), -np.sin(rot_mult * step_angle)],
                     [np.sin(rot_mult * step_angle), np.cos(rot_mult * step_angle)]]
                )
                new_x, new_y = np.matmul(rot_matrix, np.array([128, 0.0])) + np.array(center)
                data_dict['position'] = np.array([new_x.round(5), new_y.round(5)])

            if data_dict.get("initialize_sides"):
                initialize_sides(data_dict, self.sides_radius)

        # Initialize velocities
        for component, data_dict in component_data.items():
            if data_dict.get("initialize_velocity"):
                data_dict["velocity"] = np.array([0.0, 0.0])

        positions_iterations = []
        x_min, x_max = y_min, y_max = (-2 * CANVAS_CENTER[0] * self.canvas_scale,
                                       2 * CANVAS_CENTER[0] * self.canvas_scale)

        # Do the iterations
        stop_iter = True
        iter_compare = 0.5
        for k in range(self.iterations):

            # Calculate charge forces
            charge_forces = calculate_charge_forces(component_data, against_component=single_component)
            # Forces on the sides
            all_spring_forces, all_rotational_forces = calculate_side_forces(component_data,
                                                                             against_component=single_component)

            if single_component:
                force_vectors = update_forces_on_component(single_component, component_data[single_component],
                                                           charge_forces, all_spring_forces)
                stop_iter = calculate_new_positions_and_velocities(single_component,
                                                                   component_data[single_component], force_vectors)
            else:
                for c, c_data in component_data.items():
                    force_vectors = update_forces_on_component(c, c_data,
                                                               charge_forces, all_spring_forces)
                    stop_iter = calculate_new_positions_and_velocities(c, c_data, force_vectors)

            for c, c_data in component_data.items():
                update_position(c, c_data)
            positions_iterations.append(dict(self.final_positions))

            if stop_iter:
                break

        if single_component:
            snap_to_grid_and_reposition_sides(single_component, component_data[single_component])
        else:
            for comp, comp_data_dict in component_data.items():
                snap_to_grid_and_reposition_sides(comp, comp_data_dict)

        return positions_iterations

    def force_directed_graph(self, component_data, center=[0.0, 0.0]):
        charge_gain, spring_gain, friction_gain, t = self.gains

        # Initialize positions (circle of connected components)
        number_of_components = len([comp for comp, data in component_data.items() if not data["locked_position"]])
        step_angle = 2 * np.pi / number_of_components
        radius = (charge_gain / spring_gain) ** (1 / 8)
        rot_mult = 0

        # Order the components, trying to bring neighbors close
        ordered_components = []
        for component, data_dict in component_data.items():
            if component not in ordered_components:
                ordered_components.append(component)
            for neighbor in data_dict["neighbors"]:
                if neighbor not in ordered_components:
                    ordered_components.append(component)

        for component in ordered_components:
            data_dict = component_data[component]
            if data_dict.get("initialize_pos"):
                rot_matrix = np.array(
                    [[np.cos(rot_mult * step_angle), -np.sin(rot_mult * step_angle)],
                     [np.sin(rot_mult * step_angle), np.cos(rot_mult * step_angle)]]
                )
                new_x, new_y = np.matmul(rot_matrix, np.array([radius, 0.0])) + np.array(center)
                data_dict['position'] = np.array([new_x.round(5), new_y.round(5)])
                rot_mult += 1

        # Initialize velocities
        for component, data_dict in component_data.items():
            if data_dict.get("initialize_velocity"):
                data_dict["velocity"] = np.array([0.0, 0.0])

        # Initialize progress bar
        if self.progress_bar is None:
            pbar = tqdm(total=self.iterations)
        else:
            pbar = self.progress_bar

        # Simulate force-directed graph evolution
        positions_iterations = []
        x_min, x_max = y_min, y_max = (-CANVAS_CENTER[0] / self.canvas_scale, CANVAS_CENTER[0] / self.canvas_scale)
        for k in range(self.iterations):
            force_vectors = {}

            # Calculate charge forces
            charge_forces = calculate_charge_forces(component_data)

            for comp1, comp1_data_dict in component_data.items():
                total_charge_force = np.array([0.0, 0.0])
                total_spring_force = np.array([0.0, 0.0])

                if comp1_data_dict.get("locked_position"):
                    # Ignore forces if the component is locked into place
                    pass
                else:
                    total_charge_force = charge_forces[comp1]
                    neighbors = [component_data[comp] for comp in comp1_data_dict.get("neighbors", [])]
                    total_spring_force -= calculate_spring_force(comp1_data_dict, neighbors)

                total_force = (charge_gain * total_charge_force
                               + spring_gain * total_spring_force
                               - friction_gain * comp1_data_dict['velocity'])

                force_vectors[comp1] = total_force

            # Calculate new positions and velocities
            stop_iter = True
            iter_compare = (charge_gain / spring_gain) / 2000
            for comp, comp_data_dict in component_data.items():
                old_pos = np.array(comp_data_dict['position'])
                old_vel = np.array(comp_data_dict['velocity'])
                force = force_vectors[comp]

                # Calculate position and limit it to the size of the schematic canvas
                if not comp_data_dict["locked_position"]:
                    new_position = old_pos + old_vel * t + 1 / 2 * force * t ** 2
                    new_pos_x, new_pos_y = new_position
                    x_limited = x_min if new_pos_x < x_min else x_max if new_pos_x > x_max else new_pos_x
                    y_limited = y_min if new_pos_y < y_min else y_max if new_pos_y > y_max else new_pos_y
                    comp_data_dict['position'] = x_limited, y_limited

                # Calculate velocity
                new_vel = old_vel
                if not comp_data_dict["locked_position"]:
                    new_vel = old_vel + force * t
                    comp_data_dict['velocity'] = new_vel

                if (abs(force[0]) > iter_compare or abs(force[1]) > iter_compare
                        or abs(new_vel[0]) > iter_compare or abs(new_vel[1]) > iter_compare):
                    stop_iter = False

            for comp, comp_data_dict in component_data.items():
                comp_position = comp_data_dict['position']
                self.final_positions[comp] = self.canvas_scale * np.array(comp_position)

            positions_iterations.append(dict(self.final_positions))

            pbar.update(1)

            if stop_iter:
                break

        if self.progress_bar is None:
            pbar.close()

        return positions_iterations



if __name__ == '__main__':
    import sys

    # create pyqt5 app
    app = QApplication(sys.argv)

    # create the instance of our Window
    window = AutoPlacerGUI({}, {})
    window.place_random_data_set(n_components=40)

    # start the app
    sys.exit(app.exec())

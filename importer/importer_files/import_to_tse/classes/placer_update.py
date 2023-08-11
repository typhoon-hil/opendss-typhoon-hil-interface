from typing import Any, TypeAlias, Callable, Generator
import numpy as np
from dataclasses import dataclass
from itertools import accumulate
from import_to_tse.classes.base import *
from import_to_tse.constants import CANVAS_CENTER, TSE_GRID_RESOLUTION
from typhoon.api.schematic_editor import SchematicAPI
from enum import Flag

#############################
########## Classes ##########
#############################

allcomp_t: TypeAlias = Component | Junction | Terminal


class Point:
    x: int
    y: int

    def __init__(self, a: "int|Point|tuple[int,int]", b: int = 0):
        if isinstance(a, Point):
            self.x = a.x
            self.y = a.y
        elif isinstance(a, tuple):
            self.x = a[0]
            self.y = a[1]
        else:
            self.x = a
            self.y = b

    def __repr__(self) -> str:
        return f"({self.x},{self.y}) (Point)"

    def to_tuple(self):
        return (self.x, self.y)

    def from_center(self) -> "Point":
        return Point(self.x - CANVAS_CENTER[0], self.y - CANVAS_CENTER[1])

    def to_center(self) -> "Point":
        return Point(self.x + CANVAS_CENTER[0], self.y + CANVAS_CENTER[1])

    def __add__(self, rhs: "Point|tuple[int,int]") -> "Point":
        if isinstance(rhs, tuple):
            return Point(self.x + rhs[0], self.y + rhs[1])
        return Point(self.x + rhs.x, self.y + rhs.y)

    def __iadd__(self, rhs: "Point|tuple[int,int]") -> "Point":
        return self + rhs

    def __getitem__(self, idx):
        if idx == 0:
            return self.x
        if idx == 1:
            return self.y
        raise IndexError("Only 2 indices are available!")


class Direction(Flag):
    """Represents the direction in which a component is placed"""

    UP = 0x1
    RIGHT = 0x2
    DOWN = 0x4
    LEFT = 0x8

    def __add__(self, __value: int) -> "Direction":
        curr_val = [0x1, 0x2, 0x4, 0x8].index(self._value_)
        s = (curr_val + __value) % 4
        return Direction(1 << s)

    def __contains__(self, member: "Direction|int") -> bool:
        if isinstance(member, Direction):
            return bool(self._value_ & member._value_)
        return bool(self._value_ & member)

    @property
    def sign(self) -> int:
        if self._value_ in Direction.LEFT | Direction.UP:
            return -1
        return 1

    def __or__(self, __value: "Direction|int") -> "Direction":
        if isinstance(__value, Direction):
            return Direction(self._value_ | (__value._value_ & 0xF))
        return Direction(self._value_ | (__value & 0xF))

    def __ior__(self, __value: "Direction|int") -> "Direction":
        if isinstance(__value, Direction):
            return Direction(self._value_ | (__value._value_ & 0xF))
        return Direction(self._value_ | (__value & 0xF))

    @property
    def bearing(self) -> "Direction":
        if self._value_ & (int((LEFT | RIGHT).value)):
            return LEFT | RIGHT
        return UP | DOWN


LEFT = Direction.LEFT
RIGHT = Direction.RIGHT
UP = Direction.UP
DOWN = Direction.DOWN


class Comp:
    """
    A class that represents the component within this engine - namely, it records
    ONLY information relevant to its position in the system
    """

    dist: int
    """ Distance (in # of components) to the closest terminal component """
    closest: "Component|None"
    """ The closest terminal component (that dist refers to) """
    idx: int
    """ The index of this component in the V vector """
    name: str
    """ The FQN of this component """
    comp: Component
    """ The `import_to_tse.classes.base.Component` instance that this represents """
    top: str
    """What terminal to consider the *top* of the component. Defaults to A1, but may change"""

    def __init__(
        self,
        comp: Component,
        closest=None,
        dist: int = 999999,
        idx: int = -1,
        name: str = "",
    ):
        self.dist = dist
        self.closest = closest
        self.idx = idx
        self.name = name
        self.comp = comp
        self.placed = False
        self.top = "A"

    def __lt__(self, rhs: "Comp") -> bool:
        return self.dist < rhs.dist

    def __eq__(self, rhs: "int|str|Comp") -> bool:
        if isinstance(rhs, int):
            return rhs == self.idx
        if isinstance(rhs, str):
            return rhs == self.name
        if isinstance(rhs, Comp):
            return rhs.idx == self.idx or rhs.name == self.name

    def __repr__(self) -> str:
        return f"{self.name} (Comp)"


class PNode:
    """
    Represents an abstract box that a component is placed into, recording
    what component is in this spot and the flow of components from it to the
    edges of the graph


    """

    comp: Comp
    """ The component that is contained in this placement """
    leaves: dict[Direction, list["PNode"]]
    """ The children of this node """
    orientation: Direction
    """ Which direction this node is facing """
    preferred_dir: dict[Direction, list[Direction]]
    """ A map saying which orientation to place children as they are added """
    parent: "PNode|None"
    """ A pointer to the PNode that is one further in """
    _placed: bool
    """ A flag saying whether or not this component has been
    placed yet. If so, it won't be placed a second time"""

    def __init__(self, comp: Comp, orientation: Direction, parent: "PNode|None"):
        self.comp = comp
        self.leaves = {LEFT: [], RIGHT: [], UP: [], DOWN: []}
        self.orientation = orientation
        self.preferred_dir = {
            LEFT: [LEFT, UP, DOWN],
            RIGHT: [RIGHT, DOWN, UP],
            UP: [UP, LEFT, RIGHT],
            DOWN: [DOWN, RIGHT, LEFT],
        }
        self.parent = parent
        set_rotation(self)
        self._placed = False

    def add_comp(self, comp: Comp):
        """
        Take a component, and based on what is already placed and this node's orientation, place it in the next available direction
        """
        pref = self.preferred_dir[self.orientation]
        leaves = [self.leaves[p] for p in pref]
        min_len = min([len(l) for l in leaves])
        for leaf, dir in zip(leaves, pref):
            if len(leaf) == min_len:
                temp = PNode(comp, dir, self)
                leaf.append(temp)
                return

    @property
    def len_left(self) -> int:
        """The number of nodes to the left (including branches past this)"""
        if self.leaves[LEFT] != []:
            return len(self.leaves[LEFT]) + sum([len(n) for n in self.leaves[LEFT]])
        return 0

    @property
    def len_right(self) -> int:
        """The number of nodes to the right (including branches past this)"""
        if self.leaves[RIGHT] != []:
            return len(self.leaves[RIGHT]) + sum([len(n) for n in self.leaves[RIGHT]])
        return 0

    @property
    def len_up(self) -> int:
        """The number of nodes upwards (including branches past this)"""
        if self.leaves[UP] != []:
            return len(self.leaves[UP]) + sum([len(n) for n in self.leaves[UP]])
        return 0

    @property
    def len_down(self) -> int:
        """The number of nodes downwards (including branches past this)"""
        if self.leaves[DOWN] != []:
            return len(self.leaves[DOWN]) + sum([len(n) for n in self.leaves[DOWN]])
        return 0

    @property
    def strict_lengths(self) -> dict[Direction, int]:
        """The maximum length from this node to a terminal in STRICTLY each dimention.
        (even if a closer terminal exists in a branch going a different direction, it is not counted)
        """
        strict_len = {k: 0 for k in Direction}
        for k in strict_len:
            if len(self.leaves[k]) > 0:
                lens = [n.strict_lengths[k] for n in self.leaves[k]]
                strict_len[k] = 1 + max(lens)
        return strict_len

    def lens(self) -> dict[Direction, int]:
        return {
            LEFT: self.len_left,
            RIGHT: self.len_right,
            UP: self.len_up,
            DOWN: self.len_down,
        }

    def __len__(self):
        """
        The total number of branches outwards from this node to all terminal nodes downstream
        """
        l = 0
        if self.leaves[LEFT] != []:
            l += self.len_left
        if self.leaves[RIGHT] != []:
            l += self.len_right
        if self.leaves[UP] != []:
            l += self.len_up
        if self.leaves[DOWN] != []:
            l += self.len_down
        return l

    def __repr__(self):
        return self.comp.name + " (PNode)"

    def __getitem__(self, idx) -> "PNode":
        list_of_nodes: "list[PNode]" = [self]
        for d in self.preferred_dir:
            list_of_nodes.extend(self.leaves[d])
        if idx > len(list_of_nodes):
            raise IndexError("Subscript {idx} larger than number of children!")
        return list_of_nodes[idx]

    def place(self):
        if not self._placed:
            self.comp.comp.add_to_schematic()
            self._placed = True

    def __eq__(self, rhs):
        if isinstance(rhs, PNode) or isinstance(rhs, str) or isinstance(rhs, int):
            return self.comp == rhs
        return False

    def get_all_leaves(self):
        all_nodes = [self]
        for dir in self.preferred_dir[self.orientation]:
            all_nodes.extend(self.leaves[dir])
        for n in all_nodes:
            yield n

    def pairwise(self) -> "Generator[tuple[PNode,PNode],None,None]":
        """
        A generator to get all pairs of (self,leaf), for all leaf in leaves
        """
        dirs = self.preferred_dir[self.orientation]
        for dir in dirs:
            for leaf in self.leaves[dir]:
                yield from leaf.pairwise()
            for leaf in self.leaves[dir]:
                yield (self, leaf)

    def get_node(self, c: Comp) -> "PNode":
        """
        Find and return the node containing a given component, if
        it is within this node's leaves
        """
        for leaf in list(self.leaves.values()):
            leaf_comps = [l.comp for l in leaf]
            if c in leaf_comps:
                idx = leaf_comps.index(c)
                return leaf[idx]
        raise KeyError(f"{c.name} was not found in the leaves of {self.comp.name}!")

    def to_dict(self, V: list[Component]) -> dict[str, Any]:
        """
        Create a dictionary (recursively) containing
           - The name of the component in this position
           - a list of each of the branches which have components in them
              - Each list element is itself a dictionary of the same
        """
        comp = V[self.comp.idx]
        temp: dict[Any, Any] = {"comp": comp}
        if len(self.leaves[LEFT]) > 0:
            temp[LEFT] = [c.to_dict(V) for c in self.leaves[LEFT]]
        if len(self.leaves[RIGHT]) > 0:
            temp[RIGHT] = [c.to_dict(V) for c in self.leaves[RIGHT]]
        if len(self.leaves[UP]) > 0:
            temp[UP] = [c.to_dict(V) for c in self.leaves[UP]]
        if len(self.leaves[DOWN]) > 0:
            temp[DOWN] = [c.to_dict(V) for c in self.leaves[DOWN]]
        return temp


def translate_comp(comp: Comp) -> tuple[Point, Point]:
    """
    The component's position is assumed to be in the upper-left corner,
    but adding rotation and flipping changes where that corner actually lies.
    This compensates for that, returning the true upper-left and lower-right coordinates
    of the component
    """
    WIDTH = 10
    HEIGHT = 40
    rotation_translation: dict[str, dict[str, tuple[Point, Point]]] = {
        "flip_none": {
            "up": (Point(0, 0), Point(WIDTH, HEIGHT)),
            "right": (Point(-HEIGHT, 0), Point(0, WIDTH)),
            "down": (Point(-WIDTH, -HEIGHT), Point(0, 0)),
            "left": (Point(0, -WIDTH), Point(HEIGHT, 0)),
        },
        "flip_vertical": {
            "up": (Point(0, -HEIGHT), Point(WIDTH, 0)),
            "right": (Point(-HEIGHT, -WIDTH), Point(0, 0)),
            "down": (Point(-WIDTH, 0), Point(0, HEIGHT)),
            "left": (Point(0, 0), Point(HEIGHT, WIDTH)),
        },
        "flip_horizontal": {
            "up": (Point(-WIDTH, 0), Point(0, HEIGHT)),
            "right": (Point(0, 0), Point(HEIGHT, WIDTH)),
            "down": (Point(0, -HEIGHT), Point(WIDTH, 0)),
            "left": (Point(-HEIGHT, -WIDTH), Point(0, 0)),
        },
    }
    flip = comp.comp.flip
    rot = comp.comp.rotation
    pos = comp.comp.position
    rt = rotation_translation[flip][rot]
    top = Point(pos) + Point(rt[0])
    bot = Point(pos) + Point(rt[1])
    return top, bot


class BoundingBox:
    """Represents the bounding box of a chain of components"""

    start: Point
    """The Upper-Left coordinate of this box"""
    stop: Point
    """The Lower-Right coordinate of this box"""
    comps: "list[PNode]"
    """The components that belong inside this box"""
    height: int
    """The assumed default height of a component"""
    width: int
    """The assumed default width of a component"""
    orientation: Direction
    parent: "BoundingBox|None"
    """The box that this box spawned off of"""

    def __init__(self, parent: "BoundingBox|None", seed: PNode):
        self.parent = parent
        self.orientation = seed.orientation
        if seed is not None:
            self.comps = [seed]
            (self.start, self.stop) = translate_comp(seed.comp)

    def collides(self, neighbor: "BoundingBox") -> bool:
        cond1 = self.start.x < neighbor.start.x < self.stop.x
        cond2 = self.start.x < neighbor.stop.x < self.stop.x
        cond3 = self.start.y < neighbor.start.y < self.stop.y
        cond4 = self.start.y < neighbor.stop.y < self.stop.y
        return (cond1 or cond2) and (cond3 or cond4)

    def add_component(self, comp: PNode) -> None:
        self.comps.append(comp)
        (top, bot) = translate_comp(comp.comp)
        if top.x < self.start.x:
            self.start = top
        elif bot.y > self.stop.y:
            self.stop = bot

    def size(self) -> tuple[int, int]:
        return (abs(self.start.x - self.stop.x), abs(self.start.y - self.stop.y))


bounding_boxes: list[BoundingBox] = []


def test_collisions(elem: PNode) -> BoundingBox | None:
    """
    Check if a newly-placed component `elem` collides with any
    previously placed component chains, and if so returns the chain that
    it intersects with
    """
    temp_bb = BoundingBox(None, seed=elem)
    for box in bounding_boxes[::-1]:
        if (elem not in box.comps) and box.collides(temp_bb):
            return box
    return None


@dataclass
class Graph:
    """
    An object that holds a Graph. The Adjacency matrix is stored in A, and the vertex list is
    stored in V
    """

    A: np.ndarray
    V: list[Component]

    def __init__(self, comps: list[Component]):
        self.V = comps
        neighbors = {}
        self.A = np.zeros((len(comps), len(comps)))
        for i, comp in enumerate(comps):
            neighbors[comp] = comp.get_connected_components()
            for c in comp.get_connected_components():
                j = comps.index(c)
                self.A[i, j] = 1
                self.A[j, i] = 1


################################
######## Digest circuit ########
################################
def place_components(sch: Schematic) -> None:
    """
    Generates placement information, assigns it to each part, then connects the parts
    and all terminals
    """
    G = Graph(sch.components)
    print("Determining positions for all components")
    root = create_component_placements(G)
    print("Adding components to the TSE schematic")
    create_connections(root, sch)


def create_component_placements(G: Graph) -> PNode:
    """
    The main function of the placement engine. This algorithm works as follows:
      - Find the endpoints of the Graph (I call them *terminals*), then work backwards
        to find how far each component is from its closest terminal
      - Designate the component that is the furthest from all terminals as the central component
      - Separate the components into chains, from any terminal to the central component
      - Put the longest chain to the left, second longest to the right, third upwards,
        fourth downwards
      - If there are more than that, repeat that orientation as needed
      - Flow the component chains outwards from there, i.e.
         - If the chain is going left, the longest branch will always keep going left.
         - If a fork shows up, it will go its own direction and form a sub-chain, which
           will follow that direction until it ends or forks again
    Return
    ------
    root:PNode
        The central-most element in the grid. Within its leaves are every other component within this
        circuit
    """
    terminals: list[Component] = []
    # We consider a "terminal component" as any which is only connected on 1 side (Either 1 node, or 3 nodes each labeled (a,b,c) or (a1,b1,c1) or something similar)
    for v in G.V:
        term_side = [int(t.destination_name[1]) for t in v.terminals]
        if len(v.terminals) in [1, 3] or (term_side[0] != term_side[1]):
            terminals.append(v)
    comp_dict = {
        comp: Comp(idx=G.V.index(comp), name=comp.name, comp=comp) for comp in G.V
    }
    for term in terminals:
        idx = G.V.index(term)
        unvisited = [True for i in G.V]
        unvisited[idx] = False
        comp_dict = walk(G, idx, comp_dict, idx, unvisited, 0)
    comps_sorted = sorted(comp_dict.values())
    return form_tree(G, comps_sorted)


def walk(
    G: Graph,
    origin_idx: int,
    cd: dict[Component, Comp],
    comp_idx: int,
    unvisited: list[bool],
    dist: int,
) -> dict[Component, Comp]:
    """
    walk the graph in its entirety, from some supplied terminal vertex to every other node. If
    the number of steps taken from the terminal vertex to that node than is recorded in the
    Comp vertex, update that and record what the closest terminal vertex is.

    Parameters
    ----------
    G:Graph
        The Graph Theory representation of this circuit
    origin_idx:int
        The index of the current edge vertex in G.V
    cd:dict[Component,Comp]
        The mapping between Components (Typhoon objects) and Comps (as used specifically by this algorithm)
    comp_idx: int
        The index of the current vertex in G.V
    unvisited: list[bool]
        A list of True or False saying whether or not some component has been seen yet. Shares indices
        with G.V
    dist: int
        The number of steps away from the starting edge vertex we are

    Returns:
    dict[Component, Comp]
        The `cd` parameter, but updated
    """
    comp = G.V[comp_idx]
    if cd[comp].dist > dist:
        cd[comp].dist = dist
        cd[comp].closest = G.V[origin_idx]
    neighbors = G.A[:, comp_idx]
    to_visit = [bool(n and u) for n, u in zip(neighbors, unvisited)]
    for i, flag in enumerate(to_visit):
        if flag:
            temp_unvisited = unvisited
            temp_unvisited[i] = False
            cd = walk(G, origin_idx, cd, i, temp_unvisited, dist + 1)
    return cd


def form_tree(G: Graph, queue: list[Comp]) -> PNode:
    """
    Make the tree of the components. A setup function for the `create_branch` function, essentially

    Parameters
    ----------
    G:Graph
        The Graph representation of this system
    comp_idx:int
        The index of the current component in V
    queue:list
        The list of components, sorted by length of path to the nearest terminal node
    """
    root_comp = queue.pop()
    root = PNode(root_comp, LEFT, None)
    all_n_idx = np.where(G.A[:, root_comp.idx] == 1)[0]
    all_neighbors = [elem for elem in queue if elem.idx in all_n_idx]
    sorted_neighbors = sorted(
        all_neighbors, key=lambda n: n.dist, reverse=True
    )  # The list of all indices of neighbors of Root, within queue, sorted highest to lowest by number of neighbors
    sorted_n_idx = [queue.index(n) for n in sorted_neighbors]
    root.preferred_dir[LEFT].insert(1, RIGHT)
    for i in sorted(sorted_n_idx, reverse=True):
        queue.pop(i)
    for neighbor in sorted_neighbors:
        root.add_comp(neighbor)
        neighbor_node = root.get_node(neighbor)
        print()
        create_branch(G, queue, neighbor_node)
    root.comp.comp.position = Point((0, 0))
    bounding_boxes.append(BoundingBox(parent=None, seed=root))
    generate_all_coordinates(root, Point(0, 0), box=bounding_boxes[0])
    return root


def create_branch(G: Graph, queue: list[Comp], comp: PNode) -> None:
    """
    Given a component, find all of its children and place them (recursively). The
    `PNode.leaves` are set.

    Parameters
    ----------
    G:Graph
        The Graph of this circuit
    queue: list[Comp]
        The list of components that are yet to be placed. Each recursive call recieves a copy of this but with any components already taken care of missing
    comp:PNode
        The node to treat as the central component at this instant

    Returns
    -------
    None
        This function operates on pointers, and thus nothing needs to be returned
    """
    index = comp.comp.idx
    all_n_idx = np.where(G.A[:, index] == 1)[0]
    all_neighbors = [elem for elem in queue if elem.idx in all_n_idx]
    sorted_neighbors = sorted(
        all_neighbors, key=lambda n: n.dist, reverse=True
    )  # The list of all indices of neighbors of Root, within queue, sorted highest to lowest by number of neighbors
    sorted_n_idx = [queue.index(n) for n in sorted_neighbors]
    for i in sorted(sorted_n_idx, reverse=True):
        queue.pop(i)
    for elem in sorted_neighbors:
        comp.add_comp(elem)
        next_node = comp.get_node(elem)
        create_branch(G, queue, next_node)


##################################
## Create Placement information ##
##################################
def set_rotation(n: PNode) -> None:
    """Determine the `Rotation` and `Flip` properties of a component wrapped by `n`"""
    terminals = n.comp.comp.terminals[0].node.terminals
    external_terms = [term for term in terminals if term.parent != n.comp.comp]
    settings_dict = {"flip": "flip_none", "rotation": "up"}
    if n.parent is not None:
        feed_fwd = n.parent.comp.comp in [e.parent for e in external_terms]
        shared_terms = get_adjacent_terminals(n.parent.comp, n.comp)
        # Convert terminal names (A1, etc.) to (A->0,B->1,C->2)
        bus_numbers = [
            (ord(t[0].destination_name[0]) - 65, ord(t[1].destination_name[0]) - 65)
            for t in shared_terms
        ]
        if (ord(n.parent.comp.top) - 65) in [b[0] for b in bus_numbers]:
            name_map = {chr(c[0] + 65): chr(c[1] + 65) for c in bus_numbers}
            n.comp.top = name_map[n.parent.comp.top]
        if all(b[0] <= b[1] for b in bus_numbers):
            n.comp.top = min([chr(b[1] + 65) for b in bus_numbers])
        else:
            n.comp.top = max([chr(b[1] + 65) for b in bus_numbers])
    else:
        feed_fwd = False  # TODO: For now
    if (feed_fwd and n.orientation == LEFT) or (
        not feed_fwd and n.orientation == RIGHT
    ):
        settings_dict["rotation"] = "down"
        settings_dict["flip"] = "flip_vertical"
    if n.orientation in UP | DOWN:
        settings_dict["rotation"] = "right"
        if (feed_fwd and n.orientation == UP) or (
            not feed_fwd and n.orientation == DOWN
        ):
            settings_dict["flip"] = "flip_vertical"
    if n.comp.comp.type_name in ["OpenDSS/Load", "OpenDSS/Capacitor Bank"]:
        settings_dict = {
            LEFT: {"rotation": "right", "flip": "flip_none"},
            RIGHT: {"rotation": "right", "flip": "flip_horizontal"},
            UP: {"rotation": "down", "flip": "flip_none"},
            DOWN: {"rotation": "down", "flip": "flip_vertical"},
        }[n.orientation]
    if n.comp.comp.type_name == "OpenDSS/Vsource":
        settings_dict = {
            LEFT: {"rotation": "up", "flip": "flip_none"},
            RIGHT: {"rotation": "up", "flip": "flip_horizontal"},
            UP: {"rotation": "right", "flip": ""},
            DOWN: {"rotation": "left", "flip": "flip_horizontal"},
        }[n.orientation]
    if n.orientation in UP | DOWN and n.comp.top == "C":
        flip = settings_dict["flip"].split("_")[1]
        flip = "flip_" + ("vertical" if flip == "none" else "none")
        settings_dict["flip"] = flip
    n.comp.comp.flip = settings_dict["flip"]
    n.comp.comp.rotation = settings_dict["rotation"]


def shift_all_comps(n: PNode, delta_p: Point) -> None:
    """
    Given some `(delta x,delta y)`, recursively shift this component and
    every component after this one by that amount
    """
    for node in n.get_all_leaves():
        p0 = node.comp.comp.position
        p = tuple((p0[0] + delta_p.x, p0[1] + delta_p.y))
        node.comp.comp.position = p


def shift_if_collision(bb: BoundingBox) -> None:
    """
    Determine if a collision is going to happen because of the given bounding box. It
    iterates through the complete list of bounding boxes, and tests each one. If there
    is a collision, find the path that connects them, and shift all components within
    those boxes so that the collision is prevented
    """

    def find_collision_child(bb: BoundingBox, collided: BoundingBox) -> BoundingBox:
        if bb.parent == None:
            return bb
        if bb.parent == collided:
            return bb
        return find_collision_child(bb.parent, collided)

    collided = test_collisions(bb.comps[-1])
    delta_p = {
        LEFT: Point(100, 0),
        RIGHT: Point(-100, 0),
        UP: Point(0, 100),
        DOWN: Point(0, -100),
    }[bb.orientation]
    if collided != None:
        base_bb = find_collision_child(bb, collided)
        last_child = base_bb.comps[-1]
        shift_all_comps(last_child, delta_p)


def generate_all_coordinates(n: PNode, p: Point, box: BoundingBox) -> None:
    """
    Calculate where to place this node's children. Takes the current position,
    assigns that to the current node, then for each branch calculates where the
    next node needs to be placed. Recursively iterates through all nodes this way.
    This function operates on pointers, and thus nothings needs to be returned, but
    the `PNode.comp.comp.position`, `Node.comp.comp.flip` and `Node.comp.comp.rotation`
    properties are set.

    Parameters
    ----------
    n: PNode
        The node to generate components for
    p: Point
        The point that this component should be placed at
    box:BoundingBox
        The bounding box that this node is a part of
    """
    delta: Callable[[list[Any]], int] = lambda l: 100 * (len(l) - 1)
    n.comp.comp.position = p
    next_place: dict[Direction, Callable[[Point, int], Point]] = {
        LEFT: lambda p, d: Point(p.x - d, p.y),
        RIGHT: lambda p, d: Point(p.x + d, p.y),
        UP: lambda p, d: Point(p.x, p.y - d),
        DOWN: lambda p, d: Point(p.x, p.y + d),
    }

    side_1_len = len(n.leaves[n.preferred_dir[n.orientation][-1]])
    side_2_len = len(n.leaves[n.preferred_dir[n.orientation][-2]])
    a = delta(n.leaves[n.orientation])
    b = 200 * max(side_1_len, side_2_len)
    shift_if_collision(box)

    for orientation in n.preferred_dir[n.orientation]:
        if orientation in n.orientation.bearing:
            if not n in box.comps:
                box.add_component(n)
            x1_offset = b + 110
            x2_offset = 100
            if n.strict_lengths[orientation] > 0:
                xs_2 = accumulate(
                    [x2_offset for _ in n.leaves[orientation][1:]],
                    initial=delta(n.leaves[orientation]),
                )
                for comp, x2 in zip(n.leaves[orientation], xs_2):
                    delta_x1 = next_place[orientation]
                    delta_x2 = next_place[n.preferred_dir[orientation][-2]]
                    new_p = delta_x2(delta_x1(p, x1_offset), x2)
                    generate_all_coordinates(comp, new_p, box)
        else:
            new_bb = BoundingBox(seed=n, parent=box)
            x1_offset = 100
            x2_offset = a + 200
            if n.strict_lengths[orientation] > 0:
                bounding_boxes.append(new_bb)
                xs_1 = accumulate(
                    [x1_offset for _ in n.leaves[orientation]], initial=x1_offset
                )
                for comp, x1 in zip(n.leaves[orientation], xs_1):
                    delta_x1 = next_place[n.orientation]
                    delta_x2 = next_place[orientation]
                    new_p = delta_x2(delta_x1(p, x1), x2_offset)
                    generate_all_coordinates(comp, new_p, new_bb)


#####################################
########### Connect wires ###########
#####################################


def get_adjacent_terminals(c1: Comp, c2: Comp) -> "list[tuple[Terminal,Terminal]]":
    """
    Between two components `c1` and `c2`, find the set of terminals between the two.
    `c1` represents the parent node, and `c2` the child (more/less central to the graph).
    Parameters
    ----------
    c1:Comp
        The parent node (that which is more central to the graph)
    c2:Comp
        The child node (that which is less central to the graph)

    Returns
    -------
    pairs:list[tuple[Terminal,Terminal]]
        The pairs of terminals between the two components.  The order of the pairs is
        not guaranteed, but the order of each element in that pair is. I.e., if
        `(c1.A1<->c2.A2,c1.B1<->c2.B2,c1.C1<->c2.C2)`, then the pairs ((c1.A1,c2.A2),
        (c1.B1,c2.B2),(c1.C1,c2.C2)) may be in whatever order, but the first entry of
        each pair will always be that of the parent component, and the second entry will always
        be that of the child component.
    """
    (small, large) = sorted([c1, c2], key=lambda c: len(c.comp.terminals))
    flip = large == c1
    terminal_pairs: "list[tuple[Terminal,Terminal]]" = []
    all_nodes = [t.node for t in small.comp.terminals]
    for node in all_nodes:
        if large.comp not in [t.parent for t in node.terminals]:
            continue
        other_terms = [t for t in node.terminals if t.parent != small.comp]
        t1 = [t for t in node.terminals if t.parent == small.comp][0]
        for t2 in other_terms:
            if t2.parent == large.comp:
                tup = (t1, t2) if not flip else (t2, t1)
                terminal_pairs.append(tup)
    if len(terminal_pairs) == 0:
        raise KeyError(
            f"Cound not find a pair of terminals between {c1.name} and {c2.name}!"
        )
    return terminal_pairs


def create_connections(n: PNode, sch: Schematic) -> None:
    """
    Recurse through the connections between this node and all its children,
    placing each component and generating a Junction between them if need be
    for cleaner wire-routing
    """
    for n1, n2 in n.pairwise():
        n1.place()
        n2.place()
        phases = get_adjacent_terminals(n1.comp, n2.comp)
        new_connections: "list[tuple[allcomp_t,allcomp_t]]" = []
        print(f"connecting {n1.comp.name} and {n2.comp.name}")
        for phase in phases:
            if n1.orientation not in n2.orientation.bearing:
                if n1.orientation in LEFT | RIGHT:
                    junc_pos = Point(
                        phase[1].schematic_position[0], phase[0].schematic_position[1]
                    )
                    props = {"position": junc_pos.from_center(), "kind": phase[0].kind}
                    temp = Junction(sch, props, parent=n1.comp.comp.parent)
                    temp.set_node(phase[0].node)
                    temp.add_to_schematic()
                    new_connections.append((temp, phase[0]))
                    new_connections.append((temp, phase[1]))
                else:
                    junc_pos = Point(
                        phase[0].schematic_position[0], phase[1].schematic_position[1]
                    )
                    temp = Junction(
                        sch, {"position": junc_pos.from_center(), "kind": phase[0].kind}
                    )
                    temp.set_node(phase[0].node)
                    temp.add_to_schematic()
                    new_connections.append((temp, phase[0]))
                    new_connections.append((temp, phase[1]))
            else:
                new_connections.append(phase)
        for nc in new_connections:
            sch.mdl.create_connection(*[comp.tse_instance for comp in nc])

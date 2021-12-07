import os
import re
import shutil
import opendssdirect as dss
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import numpy as np
import itertools
import statistics
import random
from typhoon.api.schematic_editor import SchematicAPI
import time
import bisect
from tqdm import tqdm
import elements
import json

### For graph drawing
from PIL import Image, ImageDraw


def loadDSS(cwd=None, temp_dir=None):
    ## Open a file explorer for the user to locate a .dss file, then set up a temporary directory
    ## and place a copy of the .dss file in that location. Return the location of the temporary
    ## copy. In order to accomodate "Redirect" functionality, all .dss files in the specified
    ## directory will be copied into the temporary environement.
    
    # Get starting directory
    if cwd is None:
        cwd = os.getcwd()
        
    # Open a file explorer for the user to select the target file.
    root = Tk()
        
    root.withdraw()
    title = 'DSS file selection'

    try:
        dss_file = askopenfilename(
            initialdir = os.path.join(cwd,'dss_files'),
            filetypes = (("DSS files","*.dss"),("all files","*.*")),
            title = title
            )
        if not dss_file:
            print('No DSS file selected. Exiting...')
            exit()
    except:
        root.destroy()
        print('File window crashed. Unable to load DSS file. Please try again.')
    finally:
        pass

    # Check for temp directory and copy .dss files
    if not temp_dir is None:
        dss_dir = os.path.dirname(dss_file)
        dss_files = [f for f in os.listdir(dss_dir) if os.path.isfile(os.path.join(dss_dir,f)) and f.lower().endswith('.dss')]
        for file in dss_files:
            shutil.copy(os.path.join(dss_dir, file), os.path.join(temp_dir, file))
        filename = os.path.basename(dss_file)
        temp_file = os.path.join(temp_dir, filename)
        dss_file = temp_file
    return dss_file





def getElements(file):
    dss_dict = {}
    comp_dict = {}
    
    dss.Basic.AllowEditor(0)
    comm_result = dss.run_command(f'Compile "{file}"')
    if comm_result:
        print(comm_result)
    else:
        print('Successfully compiled model')

    # Get circuit name
    circuit_name = dss.Circuit.Name()
    
    # Get names of all circuit elements and buses
    ckt_elements = dss.Circuit.AllElementNames()
    buses = dss.Circuit.AllBusNames()

    # Add all buses to component dictionary
    comp_dict['Bus'] = {bus: set() for bus in buses}
    
    # Populate a dictionary of all circuit elements with classes as keys
    # Each entry is a list of dss components of type corresponding to key
    for element in ckt_elements:
        name_parts = element.split('.')
        comp_class = name_parts[0]
        comp_name = '_'.join(name_parts[1:])
        if comp_class not in dss_dict:
            dss_dict[comp_class] = []
        dss_dict[comp_class].append(comp_name)

    # Using importation methods from the elements.py module, generate a .tse compatible component dictionary
    for key in dss_dict:
        try:
            method = getattr(elements, key)
        except AttributeError:
            print(f'Failed to import components of class {key}. No importation module found.')

##        try:
##            for component in dss_dict[key]:
##                print(f'Attempting to import {component}')
##                tse_key, properties, buslist, comp_name = method(component)
##
##                if tse_key not in comp_dict:
##                    comp_dict[tse_key] = {}
##
##                if comp_name in comp_dict[tse_key]:
##                    comp_dict[tse_key][comp_name]['properties'].update(properties)
##                    if buslist:
##                        comp_dict[tse_key][comp_name]['buslist'] = buslist
##                else:
##                    comp_dict[tse_key][comp_name] = {'properties': properties,
##                                                     'buslist': buslist}
##                for b in buslist:
##                    bb = b[0]
##                    pp = b[1].split('.')
##                    [comp_dict['Bus'][bb].add(p) for p in pp]
##
##        except:
##            print(f'Failed to import {key} {component}.')
##            continue

        
        for component in dss_dict[key]:
            try:
                tse_key, properties, buslist, comp_name = method(component)
                
                if tse_key not in comp_dict:
                    comp_dict[tse_key] = {}

                if comp_name in comp_dict[tse_key]:
                    comp_dict[tse_key][comp_name]['properties'].update(properties)
                    if buslist:
                        comp_dict[tse_key][comp_name]['buslist'] = buslist
                else:
                    comp_dict[tse_key][comp_name] = {'properties': properties,
                                                     'buslist': buslist}
                for b in buslist:
                    bb = b[0]
                    pp = b[1].split('.')
                    [comp_dict['Bus'][bb].add(p) for p in pp]

            except:
                print(f'Failed to import {key} {component}')
                continue
    # Import any load shape objects
    loadshapes = importLoadShapes()

    return comp_dict, circuit_name, loadshapes

dss.Basic.AllowEditor(0)



def generatePlacementInfo(comp_dict):
    # Generates placement information for TSE components. Takes a dictionary of components containing
    # component type, component name, and information about bus connections.

    # Initialize timer
    t0 = time.time()
    
    # Set iteration counts
    iter1 = 1000
    iter2 = 500
    iter3 = 100
    iter4 = 100
    iter5 = 300

    # Set gains for placement optimization
    kc = 50     # Charge definition gain
    ks = 0.1    # Spring definition gain
    b = 0.7     # Friction coefficient
    t = 0.015   # Time step
    
    DRAW_GRAPHS = False
    GAINS = [kc, ks, b, t]
    s = 5       # Random shift in position when placing new components
    nc = 7      # Number of compression stages
    
    # Initialize variable for image output
    images = []

    # Scale and offset info for TSE
    TSECENTER = np.array((8192,8192))
    TSESCALE = 256
     
    # Create lists of components
    # list_of_buses: buses, comps: all components, icomps: components connected to buses on both sides
    list_of_buses = [f'Bus_{bus}' for bus in comp_dict['Bus']]    
    comps = [f'{comp_type}_{comp_name}' for comp_type in comp_dict for comp_name in comp_dict[comp_type]]
##    icomps = list_of_buses + [f'{comp_type}_{comp_name}' for comp_type in comp_dict if not comp_type=='Bus' for comp_name in comp_dict[comp_type] if len(comp_dict[comp_type][comp_name]['buslist'])>1]
    icomps = list_of_buses + [f'{comp_type}_{comp_name}' for comp_type in comp_dict if not comp_type=='Bus' for comp_name in comp_dict[comp_type] if len(np.unique([b[0] for b in comp_dict[comp_type][comp_name]['buslist']]))>1]
    
    # Instantiate variable for output
    placement_info = {key:{} for key in comps}
    
    # Generate lists of neighbors
    bus_neighbors = []
    comp_neighbors = []
    icomp_neighbors = []
    
    for comp_type in comp_dict:
        if not comp_type == 'Bus':
            for comp_name in comp_dict[comp_type]:
                comp = f'{comp_type}_{comp_name}'
                buslist = comp_dict[comp_type][comp_name]['buslist']
                
                list_of_neighbors = [f'Bus_{bus_name}' for bus_name, phases in buslist]

    ##                bus_neighbor_list = [n for n in itertools.combinations(list_of_neighbors,2)]
    ##                bus_neighbor_list = [n for n in bus_neighbor_list if n[0]!=n[1]]
                bus_neighbor_list = [n for n in itertools.combinations(list_of_neighbors,2) if n[0]!=n[1]]
##                print(bus_neighbor_list)
                bus_neighbors += bus_neighbor_list
##                print(bus_neighbors)

                neighbor_list = [(comp, f'Bus_{bus_name}') for bus_name, phases in buslist]
                comp_neighbors += neighbor_list
                if bus_neighbor_list:
                    icomp_neighbors += neighbor_list
            
    # Run optimization with just buses
    print('Optimizing for bus placement')
    bus_positions, velocities, bus_images = forceDirectedGraph(list_of_buses, bus_neighbors, gains=GAINS, iterations=iter1, draw_graphs=DRAW_GRAPHS)
    images += bus_images

    # Add components which connect between buses
    print('Placing components between buses')
    positions = []
    for comp in icomps:
        # If the component is a bus, pull its position from previous optimization
        if comp in list_of_buses:
            comp_pos = bus_positions[list_of_buses.index(comp)]
        # If not, initialize between buses
        else:
            neighbor_positions = [bus_positions[list_of_buses.index(b)] for c,b in icomp_neighbors if c==comp]
            comp_pos = np.mean(neighbor_positions,0)+(s*(random.random()-0.5),s*(random.random()-0.5))
        positions.append(comp_pos)
    positions, velocities, comp_images = forceDirectedGraph(icomps, icomp_neighbors, gains=GAINS, positions=positions, iterations=iter2, draw_graphs=DRAW_GRAPHS)
    images += comp_images

    
    # Add remaining components
    print('Placing all remaining components')
    all_positions = []
    for comp in comps:
        # If the component has already been placed, grab its position
        if comp in icomps:
            comp_pos = positions[icomps.index(comp)]
        # If not, place the component
        else:
            neighbor_positions = [positions[icomps.index(b)] for c,b in comp_neighbors if c==comp]
            comp_pos = np.mean(neighbor_positions,0)+(s*(random.random()-0.5),s*(random.random()-0.5))
        all_positions.append(comp_pos)
    positions, velocities, comp_images = forceDirectedGraph(comps, comp_neighbors, gains=GAINS, positions=all_positions, iterations=iter3, draw_graphs=DRAW_GRAPHS)
    images += comp_images


    # Contract and relax graph
    print('Compressing graph')
    compression_vector = list(2**np.arange(1,nc+1)*ks)
    compression_vector += compression_vector[-2::-2]

    pbar = tqdm(total=len(compression_vector)*iter4)
    for k in range(len(compression_vector)):
        ks = compression_vector[k]
        positions, velocities, comp_images = forceDirectedGraph(comps, comp_neighbors, gains=[kc, ks, b, t], positions=positions, iterations=iter4, draw_graphs=DRAW_GRAPHS, pbar_in=pbar)
        images += comp_images
    pbar.close()
    
    
    print('Relaxing graph')
    ks = 3
    positions, velocities, comp_images = forceDirectedGraph(comps, comp_neighbors, gains=[kc, ks, b, t], positions=positions, iterations=iter5, draw_graphs=DRAW_GRAPHS)
    images += comp_images

    # Lock components to grid
    locked = [0]*len(comps)
    im = drawGraph(comps, positions, comp_neighbors, locked)
    im.show()
    
    print('Rotating graph to minimize diagonality')
    positions = rotateGraph(comps, comp_neighbors, positions)
    im = drawGraph(comps, positions, comp_neighbors, locked)
    im.show()
    
    print('Locking components to grid')
    int_positions = [np.array([round(x),round(y)]) for x,y in positions]
    xvals = [x for x,y in int_positions]
    yvals = [y for x,y in int_positions]
    xrange = (min(xvals),max(xvals))
    yrange = (min(yvals),max(yvals))
    ncomps = len(int_positions)

    xspacing = np.ceil((xrange[1]-xrange[0])/(ncomps**0.5))
    yspacing = np.ceil((yrange[1]-yrange[0])/(ncomps**0.5))

    yspace_thresh = 0.75
    if yspacing < yspace_thresh:
        yspacing = 0
##    xvec0 = np.arange(xrange[0], xrange[1]+xspacing, xspacing)
##    yvec0 = np.arange(yrange[0], yrange[1]+yspacing, yspacing)

    if yspacing:
        yvec0 = np.arange(yrange[0], yrange[1]+yspacing, yspacing)
    else:
        yvec0 = np.array([0])
        xspacing = np.ceil((xrange[1]-xrange[0])/(ncomps))
        
    if xspacing:
        xvec0 = np.arange(xrange[0], xrange[1]+xspacing, xspacing)
    else:
        xvec0 = np.array([0])
        
        

    
    nx0 = len(xvec0)
    ny0 = len(yvec0)
    
    x_positions = [xy[0] for xy in positions]
    y_positions = [xy[1] for xy in positions]
    x_ord = np.argsort(x_positions)
    y_ord = np.argsort(y_positions)

    unique_positions = False

    max_iter = 100
    count = 0

    # Add necessary grid lines to ensure unique grid locations for all components
    while not unique_positions:

        count += 1
        
        # Reset starting grid
        xvec = [x for x in xvec0]
        yvec = [y for y in yvec0]
        
        # Instantiate a dictionary to track component locations
        grid_positions = {key:[0,0] for key in comps}

        # For each component:
        for k in range(ncomps):

            # Get the index for the next left-most and top-most components
            jx = x_ord[k]
            jy = y_ord[k]

            # Get the y position of the left-most component, adjust the grid, and record the y-position
            y = y_positions[jx]
            closest_row = min(enumerate(yvec), key=lambda yy: abs(yy[1]-y))[0]
            yvec[closest_row] = y        
            grid_positions[comps[jx]][1] = closest_row

            # Get the x position of the top-most component, adjust the grid, and record the x-position  
            x = x_positions[jy]
            closest_col = min(enumerate(xvec), key=lambda xx: abs(xx[1]-x))[0]
            xvec[closest_col] = x
            grid_positions[comps[jy]][0] = closest_col
            
        # Check for any duplicate values
        duplicates = []
        arr = []
        new_grid_xlocs = []
        new_grid_ylocs = []
        for key in grid_positions:
            xy = grid_positions[key]
            if not xy in arr:
                arr.append(xy)
            else:
                duplicates.append(key)

        if count <= max_iter:
            if duplicates:
                for d in duplicates:

                    # Idenfity new grid locations
                    x,y = positions[comps.index(d)]

                    xidx = max([1,np.searchsorted(xvec0,x)])
                    yidx = max([1,np.searchsorted(yvec0,y)])
                    
                    xx = xvec0[xidx-1:xidx+1]
                    yy = yvec0[yidx-1:yidx+1]

                    xdist = min(abs(np.array(xx)-x))
                    ydist = min(abs(np.array(yy)-y))

                    x_val = np.mean(xx)
                    y_val = np.mean(yy)
                    
                    if xdist < ydist:
                        if not x_val in new_grid_xlocs:
                            new_grid_xlocs.append(x_val)
                    else:
                        if not y_val in new_grid_ylocs:
                            new_grid_ylocs.append(y_val)

                n_new = len(new_grid_xlocs)+len(new_grid_ylocs)
                print(f'Overlapping components detected: adding {n_new} new grid line{"s"*min([1,n_new-1])} to starting grid')

                if new_grid_xlocs:
                    xidxs = np.searchsorted(xvec0, new_grid_xlocs)
                    xvec0 = np.insert(xvec0, xidxs, new_grid_xlocs)
                if new_grid_ylocs:
                    yidxs = np.searchsorted(yvec0, new_grid_ylocs)
                    yvec0 = np.insert(yvec0, yidxs, new_grid_ylocs)
            else:
                unique_positions = True
        else:
            print('Max iteration count reached')
            unique_positions = True

    # Re-distribute grid lines to ensure even alignment
    nx = len(xvec0)
    ny = len(yvec0)
    xspacing *= nx0/nx
    yspacing *= ny0/ny
    new_positions = [np.array(grid_positions[comp])*np.array([xspacing,yspacing])+np.array([xrange[0],yrange[0]]) for comp in comps]

    im = drawGraph(comps, new_positions, comp_neighbors, locked)
    im.show()
    
    # Center for conversion to TSE coordinates
    position_list = [np.array(grid_positions[comp]) for comp in comps]
    center_xy = np.round(np.ptp(position_list,0)/2)
    for key in grid_positions:
        grid_positions[key] -= center_xy

    # Shift bus components and set rotation
    for bus in list_of_buses:
        x_bus,y_bus = grid_positions[bus]
        x_aligned = []
        y_aligned = []
        neighbors = [comp for comp,b in comp_neighbors if b==bus]
        n_xy_list = []

        for n in neighbors:
            x_n,y_n = grid_positions[n]
            n_xy_list.append([x_n,y_n])
            if x_n==x_bus:
                y_aligned.append(n)
            if y_n==y_bus:
                x_aligned.append(n)

        new_x = x_bus
        bus_r = 0
        if y_aligned:

            # When both x- and y-aligned, shift the component toward an x-neighbor
            if x_aligned:
                x_c,y_c = grid_positions[random.choice(x_aligned)]

                new_x -= 0.5*np.sign(x_bus-x_c)

            # When y-aligned but not x-aligned, rotate or shift the component
            else:
                # If neighbors are exclusively above or below, shift in the x direction
                n_sides = [xy[1]>y_bus for xy in np.array(n_xy_list)]
                if all(n_sides) or not any(n_sides):
                    shift_toward = random.choice(neighbors)
                    x_c,y_c = grid_positions[shift_toward]
                    new_x -= 0.5*np.sign(x_bus-x_c)

                # If neighbors are both above and below, rotate
                else: 
                    bus_r = 90

        placement_info[bus]['position'] = (new_x,y_bus)
        placement_info[bus]['rotation'] = bus_r

    # Generate rotation info for all components
    comp_list = [f'{comp_type}_{comp_name}' for comp_type in comp_dict if not comp_type=='Bus' for comp_name in comp_dict[comp_type]]

    for comp in comp_list:
        x_comp,y_comp = grid_positions[comp]
        x_aligned = []
        y_aligned = []
        neighbors = [bus for c,bus in comp_neighbors if c==comp]

        new_y = y_comp
        # For one neighbor, point toward neighbor
        if len(neighbors) == 1:
            x_bus,y_bus = grid_positions[neighbors[0]]
            vec = np.array([x_bus-x_comp, y_bus-y_comp])
            xy = np.argsort(abs(vec))[-1]    # get index of larger dimension
            pn = np.sign(vec[xy])
            comp_r = (90*(1+3*xy-pn))%360

        # For two neighbors, move and rotate as appropriate
        else:
            neighbor_xy = []
            # Get neighbor positions
            for n in neighbors:
                x_n,y_n = grid_positions[n]
                if x_n==x_comp:
                    x_aligned.append(n)
                if y_n==y_comp:
                    y_aligned.append(n)
                neighbor_xy.append([x_n,y_n])

            # If both x and y aligned: shift toward y-aligned component and point toward it
            if x_aligned and y_aligned:
                x_b,y_b = grid_positions[x_aligned[0]]
                new_y -= 0.5*np.sign(y_comp-y_b)
                side = neighbors.index(y_aligned[0])
                dy = np.sign(y_b-y_comp)
                comp_r = 90*(2-dy+2*side*dy)

            # If aligned with one, point toward that one
            elif x_aligned or y_aligned:
                aligned = x_aligned+y_aligned
                x_b,y_b = grid_positions[aligned[0]]
                side = neighbors.index(aligned[0])
                dx = np.sign(x_b-x_comp)
                dy = np.sign(y_b-y_comp)

                print()
                print(f'Component {comp}')
                print(f'Rotating {comp} side {side+1} toward {aligned[0]}')
                comp_r = 180*side
                comp_r += 180*(dx>0)
                comp_r += dy*90
                comp_r = (360+comp_r)%360

            # If no directly aligned buses, align with bus-bus vector
            else:
                n_xy = np.array(neighbor_xy)
                vec = n_xy[1]-n_xy[0]
                xy = np.argsort(abs(vec))[-1]    # get index of larger dimension
                pn = np.sign(vec[xy])

                if xy:
                    comp_r = (360-pn*90)%360
                else:
                    comp_r = 90*(1+xy-pn)

        placement_info[comp]['position'] = (x_comp,new_y)
        placement_info[comp]['rotation'] = comp_r

    for comp in placement_info:
        print(f"{comp}: {placement_info[comp]['position']} {placement_info[comp]['rotation']}")
        pos = np.array(placement_info[comp]['position'])
        new_pos = np.round(pos*TSESCALE+TSECENTER)
        placement_info[comp]['position'] = new_pos
    print()


    # Save image frames
    if DRAW_GRAPHS:
        temp_dir = os.getcwd()
        base_dir = os.path.abspath(os.path.join(temp_dir, '..'))
        image_dir = base_dir+'\\images'
        if not os.path.isdir(image_dir):
            os.mkdir(image_dir)
        image_file = os.path.join(image_dir,'schematic_optimization.gif')
        k = 0
        while os.path.isfile(image_file):
            k+=1
            image_file = os.path.join(image_dir,f'schematic_optimization({k}).gif')
        print(f'Saving {len(images)} image frames to {image_file}...')
        images[0].save(image_file, save_all=True, append_images=images[1:], optimize=True, duration=20, loop=0)

    # Report run time
    t1 = time.time()
    duration = t1-t0
    mins,secs = divmod(duration,60)
    print(f'Script executed in {mins} minutes and {round(secs)} seconds')

    if images:
        images[-1].show()
    
    return placement_info





def generateSchematic(comp_dict, placement_info):
    # Define map of phases
    phase_map = ['A','B','C','N']
    
    # Create SchematicAPI object
    model = SchematicAPI()

    # Create new model
    model.create_new_model()

    flip_dict = {0:'flip_none',
                 90:'flip_none',
                 180:'flip_vertical',
                 270:'flip_horizontal'}
    rot_dict = {0:'up',
                90:'left',
                180:'down',
                270:'right'}
    
    comp_rot_dict = {
                    'Load':90,
                    'Capacitor Bank':90,
                    'Storage':180,
                    'Vsource':180,
                    'Isource':180,
                    }
    print('Placing components on canvas...')
    tcomp_dict = {}
    failed_to_place = []

    pbar = tqdm(total=len(placement_info))       
    
    for comp_type in comp_dict:
        typhoon_comp_type = f'OpenDSS/{comp_type}'

        comp_r0 = comp_rot_dict.get(comp_type, 0)

        for comp_name in comp_dict[comp_type]:
            comp = comp_dict[comp_type][comp_name]
            new_comp_name = f'{comp_type}_{comp_name}'
            try:
##                print(f'Placing {new_comp_name}...')
                comp_r = placement_info[new_comp_name]['rotation']
                r = rot_dict[(comp_r-comp_r0+360)%360]
                f = flip_dict[comp_r]
                p = placement_info[new_comp_name]['position']
                tcomp_dict[new_comp_name] = model.create_component(
                    typhoon_comp_type,
                    name = new_comp_name,
                    position = tuple(p),
                    rotation = r,
                    flip = f
                    )
            except:
##                print(f'Failed to place {new_comp_name}!')
                failed_to_place.append(new_comp_name)

            if new_comp_name in tcomp_dict:
                comp_handle = tcomp_dict[new_comp_name]

                if comp_type == 'Bus':
                    bus_phases = comp
                    bus_type = ''
                    bus_type += 'A' if '1' in bus_phases else ''
                    bus_type += 'B' if '2' in bus_phases else ''
                    bus_type += 'C' if '3' in bus_phases else ''
                    model.set_property_value(model.prop(comp_handle, 'type'), bus_type)
                    if '0' in bus_phases:
                        model.set_property_value(model.prop(comp_handle, 'ground'), True)
                        
                else:
                    comp_props = comp['properties']

                    for attr in comp_props:

                        val = comp_props[attr]
                        try:
                            model.set_property_value(model.prop(comp_handle, attr), val)
                        except:
                            print(f'Unable to assign property {attr}')
                            pass
                    
            pbar.update(1)
    pbar.close()
    if any(failed_to_place):
        print(f'Failed to place: {failed_to_place}')
            
    print('\nConnecting components...')

    for comp_type in comp_dict:
        if not comp_type == 'Bus':
            for comp_name in comp_dict[comp_type]:

                comp = comp_dict[comp_type][comp_name]
                buslist = comp['buslist']
                alias = f'{comp_type}_{comp_name}'
                tcomp = tcomp_dict[alias]

                for j in range(len(buslist)):

                    try:
                        bus = buslist[j][0]
                        phase_str = buslist[j][1]
                        tbus = tcomp_dict[f'Bus_{bus}']
                        
                        try:
                            p = phase_str.split('.')

                            try:
                                ### Optimally select bus side
                                x_bus,y_bus = placement_info[f'Bus_{bus}']['position']
                                r_bus = placement_info[f'Bus_{bus}']['rotation']
                                x,y = placement_info[alias]['position']
                                # If bus is facing up-down, compare y
                                if r_bus:
                                    bus_side = (1 if y>y_bus else 2)
                                # If bus is facing left-right, compare x
                                else:
                                    bus_side = (1 if x<x_bus else 2)
                                ###
                            except:
                                print('Unable to automatically select bus side. Connecting to side 1')
                                bus_side = 1
                                    
                            ### Modified to handle ground connections
                            for k in range(len(p)):

                                # Get phase character: 0->A, 1->B, 2->C, 3->N (k>3, E,F,G...)
                                try:
                                    phase_character = phase_map[k]
                                except IndexError:
                                    phase_character = chr(k+65)
                                c_term = model.term(tcomp, f'{phase_character}{j+1}')
                                
                                phase = p[k]
                                bus_term_name = '0' if phase=='0' else f'{chr(ord(phase)+16)}{bus_side}'
                                b_term = model.term(tbus, bus_term_name)

                                model.create_connection(c_term, b_term)

                            #########################################
                        except:
                            print(f'Failed to connect one or more terminals of {alias} to {bus}')
                    except:
                        print(f'Unable to successfully identify bus "{bus}"')

    ## Set up generator controls
    genctrl_offset = 176

    try:
        generators = comp_dict['Generator']
        names = [f'Generator_{g}' for g in generators.keys()]
        
        if generators: print()
        
        for gen in generators:
            name = f'Generator_{gen}'
            try:
                print(f'Generator: {name}')

                gen_r = placement_info[name]['rotation']
                gen_p = placement_info[name]['position']
                gen_h = tcomp_dict[name]
                r = rot_dict[gen_r]
                f = flip_dict[gen_r]

                xy = (gen_r/90)%2==1
                pn = np.sign(gen_r - 135)

                xshift = pn if not xy else 0
                yshift = -pn if xy else 0

                cont_pos = (gen_p[0]+xshift*genctrl_offset, gen_p[1]+yshift*genctrl_offset)
                
                j = 1
                while f'{name}_control{j}' in names:
                    j += 1
                    
                controller = f'{name}_control{j}'
                names.append(controller)
                
                print(f'Placing controller for {name}...')
                cont_h = model.create_component(
                    'OpenDSS/Generator Control',
                    name = controller,
                    position = cont_pos,
                    rotation = r,
                    flip = f
                    )

                try:
                    gen_mode = comp_dict['Generator'][gen]['properties']['G_mod']
                    ctrl_mode = 'PV' if gen_mode == 'Constant kW, Constant kV' else 'PQ'
                    print(f'Control mode: {ctrl_mode}')
                    model.set_property_value(model.prop(cont_h, 'ctrl_mode_str'), ctrl_mode)
                except:
                    print(f'Failed to set control mode for {controller}')
                    
                model.create_connection(model.term(cont_h, 'del_vfd'), model.term(gen_h, 'Vfd_in'))
                model.create_connection(model.term(cont_h, 'del_Tm'), model.term(gen_h, 'Tm_in'))
                model.create_connection(model.term(gen_h, 'meas'), model.term(cont_h, 'Gen_meas'))
                model.create_connection(model.term(gen_h, 'ctrl'), model.term(cont_h, 'Gen_ctrl'))
            except:
                print(f'Failed to place controller for {controller}')
    except KeyError:
        print('No generators detected...')
              
    return model





def rotateGraph(comps, neighbors, positions):

    # Get average neighbor direction
    total_nx_vec = complex(0,0)
    total_ny_vec = complex(0,0)
    for n in neighbors:
        n0,n1 = n
        x0,y0 = positions[comps.index(n0)]
        x1,y1 = positions[comps.index(n1)]
        
        total_nx_vec += complex(abs(x1-x0), (1 if x1>x0 else -1)*(y1-y0))
        total_ny_vec += complex(abs(y1-y0), (1 if y1>y0 else -1)*(x1-x0))

    xvec_mag = abs(total_nx_vec)
    yvec_mag = abs(total_ny_vec)

    if xvec_mag > yvec_mag:
        total_n_vec = total_nx_vec
    else:
        print('Rotating for y')
        total_n_vec = total_ny_vec.conjugate()*1j
    n_vec = total_n_vec.conjugate()/abs(total_n_vec)
    rotated_positions = []
    for xy in positions:
        cxy = complex(xy[0],xy[1])
        rxy = cxy*n_vec
        rotated_positions.append(np.array([rxy.real,rxy.imag]))
    return rotated_positions





def forceDirectedGraph(comps, neighbors, gains=[], positions=None, iterations=None, velocities=None, locked=None, draw_graphs=False, pbar_in=None):

    images = []
    
    # Initialize gains: kc, ks, b, t
    set_gains = [1,1,1,1]
    for j,g in enumerate(gains):
        if j>len(set_gains):
            print(f'Expected {len(set_gains)} gain values but {len(gains)} were provided. Only first {len(set_gains)} will be used.')
            break
        else:
            set_gains[j]=g
    kc, ks, b, t = set_gains

    
    # Initialize positions
    if not positions:

        # Place buses in a circle
        n = len(comps)
        positions = []
        
        if n==1:
            positions.append([0,0])
        else:
            
            phi = 2*np.pi/n
            u_rot = complex(np.cos(phi).round(10), np.sin(phi).round(10))
            s = (kc/ks)**(1/3)
            doc = s/np.sin(np.pi/n)
            v = complex(doc,0)
            for comp in comps:
                positions.append([v.real, v.imag])
                v = v*u_rot

        # Reorder components by neighbors
        ordered_comps = []
        unordered_comps = [c for c in comps]
        remaining_neighbors = [n for n in neighbors]
        
        comp_found = False
        while unordered_comps:
            if not comp_found:
                next_comp = random.choice(unordered_comps)
            comp = next_comp
            ordered_comps.append(comp)
            unordered_comps.remove(comp)
            comp_found = False
            for n_pair in remaining_neighbors:
                if comp in n_pair:
                    n = [nn for nn in n_pair if not nn is comp][0]
                    if n in unordered_comps:
                        next_comp = n
                        comp_found = True
                        remaining_neighbors.remove(n_pair)
                        break

        positions = [positions[comps.index(c)] for c in ordered_comps]


    # Initialize velocities
    if not velocities:
        velocities = np.array([[0,0]]*len(comps))


    # Initialize locked components
    if not locked:
        locked = [0]*len(comps)


    # Initialize iteration count
    if not iterations:
        iterations = 20*len(comps)
        
    # Initialize progress bar
    if pbar_in is None:
        pbar = tqdm(total=iterations)
    else:
        pbar = pbar_in
        
    # Simulate force-directed graph evolution
    for k in range(iterations):
                
        # Compute forces from charge definition        
        f_vecs = [sum([np.array([x0-x1,y0-y1])*kc*(max([0.01,(x0-x1)**2+(y0-y1)**2]))**(-3/2) for j,(x1,y1) in enumerate(positions) if not i==j]) for i,(x0,y0) in enumerate(positions)]
        
        # Add forces from spring definition
        for n in neighbors:
            n0,n1 = n
            x0,y0 = positions[comps.index(n0)]
            x1,y1 = positions[comps.index(n1)]
            f_spring = ks*np.array([x0-x1,y0-y1])
            f_vecs[comps.index(n0)] -= f_spring
            f_vecs[comps.index(n1)] += f_spring

        # Add friction forces
        for j in range(len(f_vecs)):
            f_vecs[j] -= velocities[j]*b

        if any(locked):
            for ll in range(len(locked)):
                if locked[ll]:
                    velocities[ll]=np.array([0,0])
                    f_vecs[ll]=np.array([0,0])

        # Update positions: use mass=1 therefore f=a
        positions = [p + v*t + 1/2*a*t**2 for p,v,a in zip(positions, velocities, f_vecs)]
        velocities = [v + a*t for v,a in zip(velocities, f_vecs)]
        
        # Generate image frame for later animation
        if draw_graphs:
            images.append(drawGraph(comps, positions, neighbors, locked))

        pbar.update(1)
    if pbar_in is None:
        pbar.close()
        
    return positions, velocities, images




         
def drawGraph(comps, positions, neighbors, locked):
    g = 255
    c = 0
    x,y = 1000,800

    color_free =(c,c,c)
    color_locked = (180,50,50)

    center = np.array([x/2,y/2])
    scale = 10
    size = 10
    lw = 1
    
    im = Image.new('RGB', (x, y), (g, g, g))
    draw = ImageDraw.Draw(im)

    for n in neighbors:
        n1,n2 = n

        x1,y1 = (positions[comps.index(n1)]*scale+center)
        x2,y2 = (positions[comps.index(n2)]*scale+center)
        draw.line((x1,y1,x2,y2), fill=(c,c,c,c), width = lw)
        
    for k in range(len(comps)):
        comp = comps[k]
        pos = positions[k]

        xc,yc = center+pos*scale
        draw_pos = (xc-size/2, yc-size/2, xc+size/2, yc+size/2)

        if locked[k]:
            color = color_locked
        else:
            color = color_free
        draw.ellipse(draw_pos, fill=color, outline=color)

    return im    





def importLoadShapes():
    
    loadshapes = {}

    shape = dss.LoadShape.First()

    while shape:
        name = dss.LoadShape.Name()
        npts = str(dss.LoadShape.Npts())
        interval = str(dss.LoadShape.HrInterval())
        mult = str(dss.LoadShape.PMult())
        hour = str(dss.LoadShape.TimeArray())
        loadshapes[name] = {
                            "npts":npts,
                            "interval":interval,
                            "mult":mult,
                            "hour":hour,
                            }
        shape = dss.LoadShape.Next()

    return loadshapes



def writeLoadShapes(loadshapes_dict, save_dir, circuit_name):
    from pathlib import Path
    
    targ_dir = os.path.abspath(os.path.join(save_dir, f'{circuit_name} Target files\dss\data'))
    if not os.path.exists(targ_dir):
        # Create missing directories
        Path(targ_dir).mkdir(parents=True)

    fname = os.path.abspath(os.path.join(targ_dir, 'general_objects.json'))

    try:
        with open(fname, 'r') as f:
            obj_dicts = json.load(f)
    except FileNotFoundError:
        obj_dicts = {"loadshapes" : {}}

    obj_dicts["loadshapes"].update(loadshapes_dict)

    with open(fname, 'w') as f:
        f.write(json.dumps(obj_dicts, indent=4))

    
    

###########################################################################################
###################################### Local Functions ####################################
###########################################################################################



def readFile(file, newlines=False):
    ## Read file and return contents as a list of strings.
    fo = open(file, 'r')
    text = fo.read()
    fo.close()
    if newlines:
        all_lines = [line.strip() for line in text.split('\n')]
    else:
        all_lines = [line.strip() for line in text.split('\n') if line]
    return all_lines



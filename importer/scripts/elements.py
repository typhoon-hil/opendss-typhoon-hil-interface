import opendssdirect as dss
import sys
import numpy as np

# This module contains information on how to import components of each
# importable class.

def busPhase(bus,phases):
    # Identify bus and phase order from bus information. Generate phase order
    # assuming phases are connected 1.2.3...n for n phases if no phase order
    # is explicitly given.
    bus_arr = bus.split('.')
    bus_list = [bus_arr[0].lower(), '.'.join(bus_arr[1:])]
    if not bus_list[1]:
        bus_list[1] = '.'.join([str(c) for c in list(range(1,phases+1))])
    return bus_list





def Line(name):
    print(f'Importing line component {name}')
    tse_comp = 'Line'               # Typhoon OpenDSS library component type
    dss.Lines.Name(name)            # Update DSS object to reference current component
    # Read parameters from dss
    Phases = dss.Lines.Phases()
    RMatrix = dss.Lines.RMatrix()
    XMatrix = dss.Lines.XMatrix()
    CMatrix = dss.Lines.CMatrix()
    Length = dss.Lines.Length()
    baseFreq = dss.Properties.Value('baseFreq')
    # Use input type 'Matrix' for .tse
    input_type = 'Matrix'
    # Generate .tse compatible matrices
    rmatrix = []
    xmatrix = []
    cmatrix = []
    for k in range(Phases):
        rmatrix.append(RMatrix[k*Phases:(k+1)*Phases])
        xmatrix.append(XMatrix[k*Phases:(k+1)*Phases])
        cmatrix.append(CMatrix[k*Phases:(k+1)*Phases])
    # Get connection info
    Bus1 = busPhase(dss.Lines.Bus1(),Phases)
    Bus2 = busPhase(dss.Lines.Bus2(),Phases)
    # Write properties to dictionary
    properties = {
                    'input_type':'Matrix',
                    'Length': Length,
                    'rmatrix': rmatrix,
                    'xmatrix': xmatrix,
                    'cmatrix': cmatrix,
                    'baseFreq': baseFreq,
                  }
    return tse_comp, properties, [Bus1,Bus2], name





def Vsource(name):
    print(f'Importing Vsource component {name}')
    tse_comp = 'Vsource'            # Typhoon OpenDSS library component type
    dss.Vsources.Name(name)         # Update DSS object to reference current component
    # Read parameters from dss
    enabled = dss.Properties.Value('enabled')
    if enabled=='true':
        Frequency = dss.Vsources.Frequency()
        BasekV = dss.Vsources.BasekV()
        PU = dss.Vsources.PU()
        AngleDeg = dss.Vsources.AngleDeg()
        r1 = dss.Properties.Value('R1')
        r0 = dss.Properties.Value('R0')
        x1 = dss.Properties.Value('X1')
        x0 = dss.Properties.Value('X0')
        Phases = int(dss.Properties.Value('Phases'))
        # Get connection info
        Bus1 = busPhase(dss.Properties.Value('Bus1'),Phases)
        Bus2 = busPhase(dss.Properties.Value('Bus2'),Phases)
        ground_connected = Bus2[1]=='.'.join(['0']*Phases)
        if name == "source":
            ground_connected = True
        # Write properties to dictionary
        properties = {
                        'basekv': BasekV,
                        'pu': PU,
                        'Angle': AngleDeg,
                        'Frequency': Frequency,
                        'ground_connected': ground_connected,
                        'r1': r1,
                        'r0': r0,
                        'x1': x1,
                        'x0': x0,
                      }
        return tse_comp, properties, [Bus1, Bus2], name
    else:
        print(f'Vsource "{name}" is not enabled')
        return





def Isource(name):
    print(f'Importing Isource component {name}')
    tse_comp = 'Isource'            # Typhoon OpenDSS library component type
    dss.Isources.Name(name)         # Update DSS object to reference current component
    # Read parameters from dss
    Amps = dss.Isources.Amps()
    AngleDeg = dss.Isources.AngleDeg()
    Frequency = dss.Isources.Frequency()
    phases = int(dss.Properties.Value('phases'))
    # Get connection info
    Bus1 = busPhase(dss.Properties.Value('bus1'),phases)
    Bus2 = busPhase(dss.Properties.Value('Bus2'),phases)
    # Write properties to dictionary
    properties = {
                    'amps': Amps,
                    'Angle': AngleDeg,
                    'Frequency': Frequency,
                  }
    return tse_comp, properties, [Bus1, Bus2], name




def Transformer(name):
    print(f'Importing Transformer component {name}')
    tse_comp = 'Single-Phase Transformer'   #Typhoon OpenDSS library component type (updated later if phases>1
    dss.Transformers.Name(name)             # Update DSS object to reference current component
    # Read parameters from dss
    baseFreq = dss.Properties.Value('baseFreq')
    percentRs = dss.Properties.Value('%Rs')
    KVs = dss.Properties.Value('KVs')
    KVAs = dss.Properties.Value('KVAs')
    XscArray = dss.Properties.Value('XscArray')
    NumWindings = dss.Transformers.NumWindings()
    Phases = int(dss.Properties.Value('Phases'))
    percentNoloadloss = dss.Properties.Value('%noloadloss')
    percentimag = dss.Properties.Value('%imag')
    
    # Compute possible reactances
    Xsc = [float(x) for x in XscArray.strip('][').split(', ') if x]
    if NumWindings==2:
        Xsc = Xsc[0]
        pRs = [float(x) for x in percentRs.strip('][').split(', ') if x]
        sumpRs = sum(pRs)
        ratios = [p/sumpRs for p in pRs]
        x = [r*Xsc for r in ratios]
    else:
        xmatrix = [[1]+[0]*k+[1]+[0]*(NumWindings-k-2) for k in range(NumWindings-1)]+[[0,1,1]+[0]*(NumWindings-3)]
        A = np.array(xmatrix)
        b = np.array(Xsc)[range(NumWindings)]
        x = np.linalg.solve(A,b)
    XArray = str(list(x))
    # Get connection info
    Buses = [busPhase(bus.strip(),Phases) for bus in dss.Properties.Value('Buses').strip('[] ,').split(',')]

    # Add relevant neutral connections
    if Phases == 1:
        Buses = [[B[0],B[1]+'.0'] for B in Buses]
    
    # Write properties to dictionary
    properties = {
                    'percentNoloadloss': percentNoloadloss,
                    'percentimag': percentimag,
                    'KVs': KVs,
                    'KVAs': KVAs,
                    'num_windings': NumWindings,
                    'baseFreq': baseFreq,
                    'percentRs': percentRs,
                    'XscArray': XscArray,
                    'XArray': XArray,
                  }

    n_phases = []
    if Phases > 1:
        tse_comp = 'Three-Phase Transformer'
        IsDelta = []
        Rneut = []
        Xneut = []
        for k in range(1, NumWindings+1):
            delta = dss.Transformers.IsDelta()
            IsDelta.append(delta)
            Rn = dss.Transformers.Rneut()
            Xn = dss.Transformers.Xneut()
            Rneut.append(Rn)
            Xneut.append(Xn)
            
            n_phases.append('' if delta or Rn<0 else '.0')

        Buses = [[B[0],B[1]+n_phases[k]] for k,B in enumerate(Buses)]

        prim_conn = chr(916) if IsDelta[0] else 'Y'
        properties['prim_conn'] = prim_conn
        maxtap = dss.Transformers.MaxTap()
        mintap = dss.Transformers.MinTap()
        numtaps = dss.Transformers.NumTaps()
        properties['maxtap'] = maxtap
        properties['mintap'] = mintap
        properties['numtaps'] = numtaps
        # Add secondary windings to properties dictionary
        for k in range(1,NumWindings):
            wdg = f'sec{k}_conn'
            conn = chr(916) if IsDelta[k] else 'Y'
            properties[wdg]=conn
    return tse_comp, properties, Buses, name





def Load(name):
    print(f'Importing load component {name}')
    tse_comp = 'Load'           # Tphoon OpenDSS library component type
    dss.Loads.Name(name)        # Update DSS object to reference current component
    # Read parameters from dss
    kV = dss.Loads.kV()
    PF = dss.Loads.PF()
    pf_3ph = np.abs(float(PF))
    pf_dict = {1:'Lag',0:'Unit',-1:'Lead'}
    pf_mode_3ph = pf_dict[np.sign(float(PF))]
    Model = dss.Loads.Model()
    DY = chr(916) if dss.Loads.IsDelta() else 'Y'
    kVA = dss.Loads.kVABase()
    baseFreq = dss.Properties.Value('baseFreq')
    Phases = dss.Loads.Phases()
    
    # Get connection info
    Bus1 = busPhase(dss.Properties.Value('bus1'), Phases)

    GND=False if len(Bus1[1].split('.'))>Phases else dss.Loads.Rneut()<0
        
    # Write properties to dictionary
    properties = {
                    'phases': Phases,
                    'Vn_3ph': kV,
                    'pf_3ph': pf_3ph,
                    'pf_mode_3ph': pf_mode_3ph,
                    'model': Model,
                    'conn_type': DY,
                    'ground_connected': GND,
                    'Sn_3ph': kVA,
                    'fn': baseFreq,
                  }
    return tse_comp, properties, [Bus1], name





def Generator(name):
    print(f'Importing generator component {name}')
    tse_comp = 'Generator'      # Typhoon OpenDSS library component type
    dss.Generators.Name(name)   # Update DSS object to reference current component
    # Read parameters from dss
    kV = dss.Generators.kV()
    baseFreq = float(dss.Properties.Value('baseFreq'))
    kVARated = dss.Generators.kVARated()
    PF = dss.Generators.PF()
    Xd = dss.Properties.Value('Xd')
    Xdp = dss.Properties.Value('Xdp')
    Xdpp = dss.Properties.Value('Xdpp')
    XRdp = dss.Properties.Value('XRdp')   
    H = dss.Properties.Value('H')
    Phases = dss.Loads.Phases()
    models = {
            1:'Constant kW',
            2:'Constant admittance',
            3:'Constant kW, Constant kV',
            4:'Constant kW, Fixed Q',
            5:'Constant kW, Fixed Q (constant reactance)',
            }
    try:
        Model = models[dss.Generators.Model()]
    except:
        print(f"Unable to assign operating mode for generator model {props['model']}. Assigning Constant kW...")
        Model = 'Constant kW'
    # Get connection info
    Bus1 = busPhase(dss.Properties.Value('bus1'), Phases)
    # Write properties to dictionary               
    properties = {
                    'kv': kV,
                    'baseFreq': baseFreq,
                    'kVA': kVARated,
                    'pf': PF,
                    'Xd': Xd,
                    'Xdp': Xdp,
                    'Xdpp': Xdpp,
                    'XRdp': XRdp,
                    'H': H,
                    'G_mod': Model,
                    'nom_rpm': baseFreq/2*60,
                    'Init_En': False,
                 }
    return tse_comp, properties, [Bus1], name






def Storage(name):
    print(f'Importing storage component {name}')
    tse_comp = 'Storage'    # Typhoon OpenDSS library component type
    # Get Pandas dataframe for storage element from dss
    storage_frame = dss.utils.class_to_dataframe('Storage')
    storage = storage_frame.loc[f'Storage.{name}']
    # Get parameters from dataframe
    kv = storage.loc['kv']
    kwrated = storage.loc['kWrated']
    kwhrated = storage.loc['kWhrated']
    pct_effcharge = storage.loc['%EffCharge']
    pct_effdischarge = storage.loc['%EffDischarge']
    kvar = storage.loc['kvar']
    pf = storage.loc['pf']
    pct_idlingkvar = storage.loc['%Idlingkvar']
    pct_idlingkw = storage.loc['%IdlingkW']
    pct_reserve = storage.loc['%reserve']
    baseFreq = storage.loc['baseFreq']
    snap_status = storage.loc['State'].lower().capitalize()
    dispatch_modes = ['Default', 'Follow']
    DispMode = storage.loc['DispMode'].lower().capitalize()
    dispatch_p = DispMode if DispMode in dispatch_modes else dispatch_modes[0]
    if pf == '1':
        dispatch_q = 'Constant kVAr' if float(kvar) else 'Unit PF'
    else:
        dispatch_q = 'Constant PF'
    chargetrigger = storage.loc['ChargeTrigger']
    dischargetrigger = storage.loc['DischargeTrigger']
    pct_charge = storage.loc['%Charge']
    pct_discharge = storage.loc['%Discharge']
    pct_stored = storage.loc['%stored']
    vmaxpu = storage.loc['Vmaxpu']
    vminpu = storage.loc['Vminpu']
    kva = storage.loc['kVA']
    # Get connection info
    Bus1 = busPhase(storage.loc['bus1'], 3)
    # Write properties to dictionary
    properties = {
                    'kv': kv,
                    'kwrated': kwrated,
                    'kwhrated': kwhrated,
                    'pct_effcharge': pct_effcharge,
                    'pct_effdischarge': pct_effdischarge,
                    'kvar': kvar,
                    'pf': pf,
                    'pct_idlingkvar': pct_idlingkvar,
                    'pct_idlingkw': pct_idlingkw,
                    'pct_reserve': pct_reserve,
                    'baseFreq': baseFreq,
                    'snap_status': snap_status,
                    'dispatch_p': dispatch_p,
                    'dispatch_q': dispatch_q,
                    'chargetrigger': chargetrigger,
                    'dischargetrigger': dischargetrigger,
                    'pct_charge': pct_charge,
                    'pct_discharge': pct_discharge,
                    'pct_stored': pct_stored,
                    'vmaxpu': vmaxpu,
                    'vminpu': vminpu,
                    'kva': kva,
                 }
    # Get load profile information
    loadshape_name = storage.loc['yearly']
    if not loadshape_name:
        loadshape_name = storage.loc['daily']
    if not loadshape_name:
        loadshape_name = storage.loc['duty']
    if loadshape_name:
        properties.update({'loadshape_name':loadshape_name})
    return tse_comp, properties, [Bus1], name





def Capacitor(name):
    print(f'Importing capacitor component {name}')
    tse_comp = 'Capacitor Bank' # Typhoon OpenDSS library component type
    dss.Capacitors.Name(name)   # Update DSS object to reference current component
    # Read parameters from dss
    Kv = dss.Capacitors.kV()
    Kvar = dss.Capacitors.kvar()
    isdelta = dss.Capacitors.IsDelta()
    if isdelta:
        tp_connection = chr(916)
    else:
        Phases = int(dss.Properties.Value('Phases'))
        Bus1 = busPhase(dss.Properties.Value('bus1'), Phases)
        Bus2 = busPhase(dss.Properties.Value('bus2'), Phases)
        if Bus2[1]=='.'.join(['0']*len(Bus2[1].split('.'))):
            tp_connection = 'Y-grounded'
        else:
            tp_connection = 'Series'
    baseFreq = float(dss.Properties.Value('baseFreq'))
    # Write properties to dictionary               
    properties = {
                    'tp_connection': tp_connection,
                    'baseFreq': baseFreq,
                    'Kv': Kv,
                    'Kvar': Kvar,
                 }
    if tp_connection == 'Series':
        return tse_comp, properties, [Bus1, Bus1], name
    else:
        return tse_comp, properties, [Bus1], name




def RegControl(name):
    print(f'Importing RegControl object {name}')
    
    dss.RegControls.Name(name)              # Update DSS object to reference current component
    # Set transformer object to modify
    name = dss.RegControls.Transformer()

    # Read parameters from dss
    ctrl_winding = f'Winding {dss.RegControls.Winding()}'
    vreg = dss.Properties.Value('vreg')
    ptratio = dss.Properties.Value('ptratio')
    band = dss.Properties.Value('band')
    delay = dss.RegControls.TapDelay()
    
    properties = {
                    'regcontrol_on':True,
                    'ctrl_winding':ctrl_winding,
                    'vreg':vreg,
                    'ptratio':ptratio,
                    'band':band,
                    'delay':delay,
                 }
    # Typhoon OpenDSS library component type
    dss.Transformers.Name(name)
    Phases = int(dss.Properties.Value('Phases'))
    if Phases == 1:
        tse_comp = 'Single-Phase Transformer'
    else:
        tse_comp = 'Three-Phase Transformer'
        
    return tse_comp, properties, [], name



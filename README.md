# OpenDSS integration library

The purpose of this library is to build, run and interact with OpenDSS models through the Typhoon HIL interface.

## Getting started

Follow this guide to set up everything needed to build circuit schematics with Typhoon HIL software and simulate using the OpenDSS open-source engine.

There are three main steps:
1) Downloading and installing Typhoon HIL Control Center
2) Setting up the Typhoon Schematic Editor to OpenDSS interface
3) Building a circuit model

### 1) Typhoon HIL Control Center

If you already have Control Center installed you can ignore these steps, but we highly recommend an update to the latest version

1) Go to https://www.typhoon-hil.com/products/hil-software/
2) Click *Download Control Center*
3) Register and get a download link
4) Install Typhoon HIL Control Center

### 2) OpenDSS interface

1) Open Typhoon HIL Control Center (close existing Schematic Editor windows) and click on *Additional tools*
2) Click on *Package Manager*
3) In the *Marketplace* tab, locate OpenDSS
4) Click the *Install* button

### 3) Running your first model

On the *Library explorer* panel to the left a new folder called *OpenDSS* appears. This folder contains the supported
components for OpenDSS simulations. For this example, drag and drop the following components:

- Vsource
- Bus (x2)
- Line
- Load

Connect the components as in the image:

![First model](docs/img/first_mdl_conns.png?raw=true "First model")

You can double-click the components to change their parameters if you would like to.

The next step is adding a *SimDSS* component. This is the component that controls the simulation and lets you interact
with the system. Before proceeding, **save the model to disk.**

![SimDSS](docs/img/first_mdl_simdss.png?raw=true "SimDSS")

Double-click the SimDSS component and click on *Run*. If everything was set up properly, **Sim1 complete** will appear
in the *Last simulation status* field.

You can display the OpenDSS calculation results by going to the *Show* tab and selecting the desired output.
Alternatively, you can generate an automatic report from the *Report* tab.

As a last exercise, go to the *Advanced* tab and in the *Command* field:
   * Type **edit vsource.vsource1 pu=0** and click *Run*
   * Type **solve** and click *Run*

Now show the voltages to observe that the issued commands interacted with OpenDSS and changed the loaded model. Clicking on *Solve* in the
*Simulation* tab will reset the model and undo any changes performed by the manual commands. You can also append DSS
commands (or files) before and after the model is solved by opening *Append DSS commands*.


## Running the model in the time domain

You may also run the same model using the HIL time-domain solver. Add a *Three-phase Meter* from the *core* library as in
the image:

![TPM](docs/img/first_mdl_3pm.png?raw=true "Three-phase Meter")

Next, double-click the *Three-phase Meter* and check the RMS line voltages and RMS currents boxes. Click OK and then
compile and load the model into HIL SCADA.

![Compile](docs/img/first_mdl_compile.png?raw=true "Compile and send to SCADA")

After the compilation process is finished, create a new SCADA panel and click on the *Model explorer* tab on the left
side.

![Explorer](docs/img/first_mdl_explorer.png?raw=true "Model explorer")

Find the *Three-phase Meter1* folder and place the RMS currents and voltages as *Digital Display*-type widgets.
You can start the simulation now and compare the results to the OpenDSS Load-flow analysis counterpart.

![Widgets](docs/img/first_mdl_widgets.png?raw=true "Digital Display widgets")

- You can also find circuit examples in the *Examples* tool on THCC after installing the package

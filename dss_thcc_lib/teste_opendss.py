import opendssdirect as dss

dss_file = r"c:\users\felipe\onedrive - tajfun hil d.o.o\repos\opendss\testes\core coupling\aux_lib Target files\dss\aux_lib_master.dss"
dss_circuit = dss.Circuit
dss_ckt_element = dss.CktElement
dss_bus = dss.Bus
dss.run_command(f'Compile "{dss_file}"')

dss.Circuit.AllElementNames()
dss_circuit.SetActiveElement('Line.coupling')

print(dss.Circuit.Name())


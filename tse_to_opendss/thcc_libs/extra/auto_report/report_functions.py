import subprocess
import opendssdirect as dss
import numpy as np
import pathlib

VIRTUAL_ZERO = 10 ** (-9)
ALL_OBJ_TYPES = ["BUS", "VSOURCE", "GENERATOR", "LINE", "LOAD", "TRANSFORMER"]

image_path = pathlib.Path(__file__).parent.parent.parent.joinpath("images")


def limit_name_chars(org_name):
    # Limit to 12 characters
    new_name = org_name[:6] + "…" + org_name[-6:]
    if len(org_name) > 12:
        return new_name.upper()
    else:
        return org_name.upper()

def round_mod(number, n):
    if len(str(round(number, n))) > n + 3:
        rounded_number = round(number, 1)
    else:
        rounded_number = round(number, n)
    return rounded_number

def calculate_line_voltage(v1_mag, v1_ang, v2_mag, v2_ang):

    # Convert to cartesian
    v1_x, v1_y = pol2cart(v1_mag, v1_ang)
    v2_x, v2_y = pol2cart(v2_mag, v2_ang)

    # Subtract the coordinates
    v12_x = v1_x - v2_x
    v12_y = v1_y - v2_y

    # Convert back to polar
    return cart2pol(v12_x, v12_y)


def cart2pol(x, y):
    # From cartesian to polar
    rho = np.sqrt(x ** 2 + y ** 2)
    phi = np.arctan2(x, y) * 180 / np.pi
    return rho, phi


def pol2cart(rho, phi):
    # From polar to cartesian
    x = rho * np.cos(phi / 180 * np.pi)
    y = rho * np.sin(phi / 180 * np.pi)
    return x, y

def get_bus_power_loads_and_sources(dss_data_dict, phase, loads, vsources, isources):
    total_load_kw = 0
    total_load_kvar = 0
    total_src_kw = 0
    total_src_kvar = 0

    for load in loads:
        load_power_list = dss_data_dict.get("LOAD").get(load).get("powers")  # Exclude GND
        if len(load_power_list) > 2 * phase + 2:
            load_kw = load_power_list[2 * phase]
            load_kvar = load_power_list[2 * phase + 1]
            total_load_kw += load_kw
            total_load_kvar += load_kvar

    for src in vsources:
        src_power_list = dss_data_dict.get("VSOURCE").get(src).get("powers")
        if len(src_power_list) > 2 * phase + 2:
            src_kw = src_power_list[2 * phase]
            src_kvar = src_power_list[2 * phase + 1]
            total_src_kw += src_kw
            total_src_kvar += src_kvar

    for src in isources:
        src_power_list = dss_data_dict.get("ISOURCE").get(src).get("powers")
        if len(src_power_list) > 2 * phase + 2:
            src_kw = src_power_list[2 * phase]
            src_kvar = src_power_list[2 * phase + 1]
            total_src_kw += src_kw
            total_src_kvar += src_kvar

    return round_mod(total_src_kw, 2), round_mod(total_src_kvar, 2), round_mod(total_load_kw, 2), round_mod(total_load_kvar, 2)

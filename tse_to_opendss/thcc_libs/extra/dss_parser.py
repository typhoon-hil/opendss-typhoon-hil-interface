import re
import pathlib
import pandas as pd

def print_debug(debug_str, debug_mode=False):
    if debug_mode:
        print(debug_str)


def preprocess_lines(dss_path, debug_mode=False):

    with open(dss_path, "r") as f:
        all_dss_lines = f.readlines()

    # First non-comment line:
    for num, line in enumerate(all_dss_lines):
        if line.strip() and not line.strip()[0] == "!":
            first_line = num
            break

    reorganized_dss_lines = []

    for num in range(first_line, len(all_dss_lines)):
        # Empty line
        if not all_dss_lines[num].strip():
            pass
        # Comment (!)
        elif all_dss_lines[num].strip()[0] == "!":
            pass
        # Line continuation (~)
        elif all_dss_lines[num].strip()[0] == "~":
            # last list element           last list element without the newline character
            line_continuation = reorganized_dss_lines[-1] +\
                                         " " + all_dss_lines[num].split("!")[0].strip().replace("~", "")
            line_continuation = re.sub(' +', ' ', line_continuation)
            reorganized_dss_lines[-1] = line_continuation
        # New line
        else:
            new_line = all_dss_lines[num].strip()
            new_line = re.sub(' +', ' ', new_line)
            reorganized_dss_lines.append(new_line)

    return reorganized_dss_lines


def get_linecodes_dict(dss_lines, dss_path, debug_mode=False):

    # Filter the lines
    linecode_lines = []
    for line in dss_lines:
        linecode_match_1 = re.match(r"new[\W]+linecode.", line, re.IGNORECASE)
        if linecode_match_1:
            linecode_lines.append(line)
        linecode_match_2 = re.match(r"new[\W]+object=[\W]*linecode.", line, re.IGNORECASE)
        if linecode_match_2:
            linecode_lines.append(line)

    linecode_param_names = ["r1", "x1", "r0", "x0", "c1", "c0", "units", "rmatrix", "xmatrix", "cmatrix",
                       "basefreq", "normamps", "emergams", "faultrate", "pctperm", "repair", "kron",
                       "rg", "xg", "rho", "neutral", "b1", "b0", "seasons", "ratings", "linetype"]

    linecodes_dict = {}

    for linecode in linecode_lines:
        # LineCode name with spaces (uses quotes)
        linecode_match_quotes = re.search(r'\"linecode\.([^\n\"]+)\"([^\n]+)', linecode, re.IGNORECASE)
        if linecode_match_quotes:
            linecode_name = linecode_match_quotes.group(1)
            linecode_params = linecode_match_quotes.group(2)

        else:
            # LineCode name without quotes
            linecode_match_quotes = re.search(r'linecode\.([^\s]+)([^\n]+)', linecode, re.IGNORECASE)
            if linecode_match_quotes:
                linecode_name = linecode_match_quotes.group(1)
                linecode_params = linecode_match_quotes.group(2)

        linecode_params_fixed = re.findall((r'((?![\s|,])(?:\S+\s*?=\s*?[\[\(\{\"\'].+?[\]\)\}\"\'])|'
                                            r'(?![\s|,])(?:\S+\s*?=\s*?\S+))'), linecode_params)

        # Create the linecodes dictionary
        linecode_dict = {linecode_name: {}}

        for idx, param in enumerate(linecode_params_fixed):
            if "=" in param and param.split("=")[0] in linecode_params:
                linecode_dict.get(linecode_name).update({param.split("=")[0].lower().strip():
                                                         param.split("=")[1].strip()})
            else:
                linecode_dict.get(linecode_name).update({linecode_param_names[idx].lower().strip(): param})

        # Define the parameter input mode
        if any(p in par for p in ["rmatrix", "xmatrix", "cmatrix"] for par in linecode_params_fixed):
            linecode_dict.get(linecode_name).update({"mode": "matrix"})
        elif any(p in par for p in ["r1", "x1", "r0", "x0", "c1", "c0"] for par in linecode_params_fixed):
            linecode_dict.get(linecode_name).update({"mode": "symmetrical"})
        else:
            linecode_dict.get(linecode_name).update({"mode": "symmetrical"})

        linecodes_dict.update(linecode_dict)

    print_debug(linecodes_dict, debug_mode)

    return linecodes_dict


def get_loadshapes_dict(dss_lines, dss_path, from_gui=False, debug_mode=False):

    # Filter the lines
    loadshape_lines = []
    for line in dss_lines:
        loadshape_match_1 = re.match(r"new[\W]+loadshape.", line, re.IGNORECASE)
        if loadshape_match_1:
            loadshape_lines.append(line)
        loadshape_match_2 = re.match(r"new[\W]+object=[\W]*loadshape.", line, re.IGNORECASE)
        if loadshape_match_2:
            loadshape_lines.append(line)

    loadshape_param_names = ["npts", "interval", "sinterval", "minterval", "mult", "hour"]

    loadshapes_dict = {}

    for loadshape in loadshape_lines:
        # loadshape name with spaces (uses quotes)
        loadshape_match_quotes = re.search(r'\"loadshape\.([^\n\"]+)\"([^\n]+)', loadshape, re.IGNORECASE)
        if loadshape_match_quotes:
            loadshape_name = loadshape_match_quotes.group(1).lower()
            loadshape_params = loadshape_match_quotes.group(2)

        else:
            # loadshape name without quotes
            loadshape_match_quotes = re.search(r'loadshape\.([^\s]+)([^\n]+)', loadshape, re.IGNORECASE)
            if loadshape_match_quotes:
                loadshape_name = loadshape_match_quotes.group(1).lower()
                loadshape_params = loadshape_match_quotes.group(2)

        loadshape_params_fixed = re.findall((r'((?![\s|,])(?:\S+\s*?=\s*?[\[\(\{].+?[\]\)\}])|(?![\s|,])(?:\S+\s*?=\s*?\S+))'), loadshape_params)

        # Create the loadshapes dictionary
        loadshape_dict = {loadshape_name: {}}

        for idx, param in enumerate(loadshape_params_fixed):
            if "=" in param and param.split("=")[0] in loadshape_params:
                if param.split("=")[0].lower().strip() == "minterval":
                    loadshape_dict.get(loadshape_name).update({"interval": param.split("=")[1].strip()})
                    loadshape_dict.get(loadshape_name).update({"interval_unit": "min"})
                elif param.split("=")[0].lower().strip() == "sinterval":
                    loadshape_dict.get(loadshape_name).update({"interval": param.split("=")[1].strip()})
                    loadshape_dict.get(loadshape_name).update({"interval_unit": "s"})
                elif param.split("=")[0].lower().strip() == "interval":
                    loadshape_dict.get(loadshape_name).update({"interval": param.split("=")[1].strip()})
                    loadshape_dict.get(loadshape_name).update({"interval_unit": "h"})
                elif param.split("=")[0].lower().strip() == "mult":
                    if "file" not in param.lower():  # If it's a vector directly
                        mod_mult = param.split("=")[1].strip(" [](){}\"\'")
                        mod_mult = re.sub(r"[\s,]+", ", ", mod_mult)
                        pythonized_mult = f"[{mod_mult}]"
                        loadshape_dict.get(loadshape_name).update({param.split("=")[0].lower().strip():
                                                                   pythonized_mult})
                    else:
                        file_match = re.search(r'''file=\"*'*([^'",)}\]]+)\"*'*''', param, re.IGNORECASE)

                        if file_match:
                            filepath = str(pathlib.Path(dss_path).parent.joinpath(file_match.group(1)))
                            loadshape_dict.get(loadshape_name).update({
                                "csv_file": "True",
                                "csv_path": filepath,
                                "headers": "False",
                                "column": "1",
                                "useactual": "False"
                            })
                            col_match = re.search(r'''col=\"*'*([^,\"')}\]]+)\"*'*''', param, re.IGNORECASE)
                            header_match = re.search(r'''header=\"*'*([^,\"')}\]]+)\"*'*''', param, re.IGNORECASE)
                            func_parameters = {"filepath": filepath, "dss_path": dss_path}

                            if col_match:
                                column = col_match.group(1)
                                func_parameters.update({"column": column})
                                loadshape_dict.get(loadshape_name).update({"column": str(column)})
                            if header_match:
                                header = header_match.group(1).lower() == "yes" or header_match.group(1).lower() == "true"
                                func_parameters.update({"header": header})
                                loadshape_dict.get(loadshape_name).update({"headers": str(header)})
                            points = get_points_from_file(**func_parameters) if not from_gui else []
                            loadshape_dict.get(loadshape_name).update({param.split("=")[0].lower().strip():
                                                                       str(points)})

                else:
                    loadshape_dict.get(loadshape_name).update({param.split("=")[0].lower().strip():
                                                               param.split("=")[1].strip()})
            else:
                loadshape_dict.get(loadshape_name).update({loadshape_param_names[idx].lower().strip(): param.strip()})

        loadshapes_dict.update(loadshape_dict)
        print_debug(loadshape_dict, debug_mode)

    return loadshapes_dict

def get_points_from_file(filepath, dss_path, column=1, header=False):

    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            if header:
                table = pd.read_csv(f)
            else:
                table = pd.read_csv(f, header=None)
            table = table.fillna(0)
    except FileNotFoundError:
        return f'File "{filepath}" could not be found.'

    points = list(table.iloc[:, int(column) - 1])

    return points

def parse_linecodes(dss_path, debug_mode=False):
    pre_processsed = preprocess_lines(dss_path, debug_mode=debug_mode)
    return get_linecodes_dict(pre_processsed, dss_path, debug_mode=debug_mode)


def parse_loadshapes(dss_path, from_gui=False, debug_mode=False):
    pre_processsed = preprocess_lines(dss_path, debug_mode=debug_mode)
    return get_loadshapes_dict(pre_processsed, dss_path, from_gui=from_gui, debug_mode=debug_mode)


if __name__ == "__main__":
    #dss_path = r"D:\Dropbox\Typhoon HIL\Repository\opendss_integration\dev_models\randomtest Target files\randomtest.dss"
    dss_path = r"C:\Users\MarcosPauloMoccelini\Downloads\loadshape.DSS"

    parse_loadshapes(dss_path, debug_mode=True)


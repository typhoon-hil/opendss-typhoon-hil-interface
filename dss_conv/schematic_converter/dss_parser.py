import re

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

def get_linecodes_dict(dss_lines, debug_mode=False):

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

        splitted = re.findall('\"([^\n]+)\"|([^\s\"\,]+)', linecode_params)
        linecode_params_fixed = []

        splitted = [a[0] if a[0] else a[1] for a in splitted]

        # There may be spaces between brackets or quotes
        bracket_found = False
        for entry in splitted:
            if bracket_found:
                linecode_params_fixed[-1] += " " + entry
            else:
                linecode_params_fixed.append(entry)
            if "[" in entry:
                bracket_found = True
            if "]" in entry:
                bracket_found = False

        # Remove bad entries
        for entry in linecode_params_fixed[:]:
            # At least one alphanumeric character in a property
            if all(not character.isalnum() for character in entry):
                linecode_params_fixed.remove(entry)

        # Create the linecodes dictionary
        linecode_dict = {linecode_name: {}}

        for idx, param in enumerate(linecode_params_fixed):
            if "=" in param and param.split("=")[0] in linecode_params:
                linecode_dict.get(linecode_name).update({param.split("=")[0].lower(): param.split("=")[1]})
            else:
                linecode_dict.get(linecode_name).update({linecode_param_names[idx].lower(): param})

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

def get_loadshapes_dict(dss_lines, debug_mode=False):

    # Filter the lines
    loadshape_lines = []
    for line in dss_lines:
        loadshape_match_1 = re.match(r"new[\W]+loadshape.", line, re.IGNORECASE)
        if loadshape_match_1:
            loadshape_lines.append(line)
        loadshape_match_2 = re.match(r"new[\W]+object=[\W]*loadshape.", line, re.IGNORECASE)
        if loadshape_match_2:
            loadshape_lines.append(line)

    loadshape_param_names = ["npts", "interval", "sinterval", "minterval", "mult", "hour", "interval_unit"]

    loadshapes_dict = {}

    for loadshape in loadshape_lines:
        # loadshape name with spaces (uses quotes)
        loadshape_match_quotes = re.search(r'\"loadshape\.([^\n\"]+)\"([^\n]+)', loadshape, re.IGNORECASE)
        if loadshape_match_quotes:
            loadshape_name = loadshape_match_quotes.group(1)
            loadshape_params = loadshape_match_quotes.group(2)

        else:
            # loadshape name without quotes
            loadshape_match_quotes = re.search(r'loadshape\.([^\s]+)([^\n]+)', loadshape, re.IGNORECASE)
            if loadshape_match_quotes:
                loadshape_name = loadshape_match_quotes.group(1)
                loadshape_params = loadshape_match_quotes.group(2)

        splitted = re.findall('\"([^\n]+)\"|([^\s\"\,]+)', loadshape_params)
        loadshape_params_fixed = []

        splitted = [a[0] if a[0] else a[1] for a in splitted]

        # There may be spaces between brackets or quotes
        bracket_found = False
        for entry in splitted:
            if bracket_found:
                if "]" in entry:
                    loadshape_params_fixed[-1] += entry
                else:
                    loadshape_params_fixed[-1] += entry+", "
            else:
                loadshape_params_fixed.append(entry)
            if "[" in entry:
                bracket_found = True
            if "]" in entry:
                bracket_found = False

        # Remove bad entries
        for entry in loadshape_params_fixed[:]:
            # At least one alphanumeric character in a property
            if all(not character.isalnum() for character in entry):
                loadshape_params_fixed.remove(entry)

        # Create the loadshapes dictionary
        loadshape_dict = {loadshape_name: {}}

        for idx, param in enumerate(loadshape_params_fixed):
            if "=" in param and param.split("=")[0] in loadshape_params:
                if param.split("=")[0].lower() == "minterval":
                    loadshape_dict.get(loadshape_name).update({"interval": param.split("=")[1]})
                    loadshape_dict.get(loadshape_name).update({"interval_unit": "min"})
                elif param.split("=")[0].lower() == "sinterval":
                    loadshape_dict.get(loadshape_name).update({"interval": param.split("=")[1]})
                    loadshape_dict.get(loadshape_name).update({"interval_unit": "s"})
                elif param.split("=")[0].lower() == "interval":
                    loadshape_dict.get(loadshape_name).update({"interval": param.split("=")[1]})
                    loadshape_dict.get(loadshape_name).update({"interval_unit": "h"})
                else:
                    loadshape_dict.get(loadshape_name).update({param.split("=")[0].lower(): param.split("=")[1]})
            else:
                loadshape_dict.get(loadshape_name).update({loadshape_param_names[idx].lower(): param})

        loadshapes_dict.update(loadshape_dict)

    return loadshapes_dict

def parse_linecodes(dss_path, debug_mode=False):
    pre_processsed = preprocess_lines(dss_path, debug_mode=True)
    return get_linecodes_dict(pre_processsed, debug_mode=True)

def parse_loadshapes(dss_path, debug_mode=False):
    pre_processsed = preprocess_lines(dss_path, debug_mode=True)
    return get_loadshapes_dict(pre_processsed, debug_mode=True)

if __name__ == "__main__":
    dss_path = r"D:\Dropbox\Typhoon HIL\Repository\opendss_integration\dev_models\randomtest Target files\randomtest.dss"
    #dss_path = r"C:/Program Files/OpenDSS-G/Examples/IEEE_123_FLISR_Case/LineCode.DSS"

    parse_linecodes(dss_path, debug_mode=True)


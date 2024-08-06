# Imports
import tse_to_opendss
print(f"{tse_to_opendss.__file__=}")
print(f"{dir(tse_to_opendss.tse2tpt_base_converter)=}")

from tests import utils
import pytest
from typhoon.api.schematic_editor import model as mdl
# import tse_to_opendss
# import pathlib
import os


@pytest.fixture()
def pre_cleanup(request):
    clean_files_dict = request.param
    for filepath in clean_files_dict.values():
        if os.path.isfile(str(filepath)):
            os.remove(filepath)
            print(f"Removed {filepath}")
        else:
            print(f"File {filepath} doesn't exist.")
    return True


@pytest.fixture(scope='session')
def reload_hil_libraries(request):
    utils.reload_hil_libraries()
    print("Reloaded libraries")
    return True


@pytest.fixture(scope='module')
def convert_to_tpt(request):
    parent_dir_path, filename = request.param
    # Name (stem) of the TSE file should be the same as the test file name
    tse_file = str(parent_dir_path.joinpath(f"{filename}.tse"))
    master_tpt_file_path = utils.convert_to_dss(tse_file)
    return str(master_tpt_file_path)


@pytest.fixture(scope='module')
def compile_tpt_model(request):
    tpt_file_path = request.param
    result = utils.compile_dss_model(tpt_file_path)
    return result


@pytest.fixture(scope='module')
def import_tpt_model(request):
    parent_dir_path, filename = request.param
    # Name (stem) of the third-party tool file should be the same as the test file name
    tpt_file = str(parent_dir_path.joinpath(f"{filename}.dss"))
    result = utils.import_dss_model(tpt_file)
    return result


# Load and compile a TSE file
@pytest.fixture(scope='module')
def load_and_compile_to_hil(request):
    parent_dir_path_and_filename, use_vhil = request.param
    parent_dir_path, filename = parent_dir_path_and_filename
    # Name (stem) of the TSE file should be the same as the test file name
    tse_file = str(parent_dir_path.joinpath(f"{filename}.tse"))
    utils.load_tse_model(tse_file)
    utils.compile_model_and_load_to_hil(tse_file, use_vhil)
    yield
    mdl.close_model()

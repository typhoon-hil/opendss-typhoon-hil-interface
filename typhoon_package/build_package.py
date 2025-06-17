from typhoon.api.package_manager import package_manager as pkm
import os
import shutil
import distutils.core

# Remember to run this after changing/creating a component
"""
from dss_thcc_lib.component_scripts.container.api_calls_generation import update_mask_properties
update_mask_properties.generate_api_calls()
"""

package_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(package_folder)
opendss_folder = os.path.join(package_folder, "../")
python_packages_folder = os.path.join(package_folder, 'python_packages')

if not os.path.exists(python_packages_folder):
    os.makedirs(python_packages_folder)

os.chdir(opendss_folder)
build_args = ['build', '--build-base', f'{python_packages_folder}/build',
              'bdist_wheel', '--dist-dir', f'{python_packages_folder}/dist']
distutils.core.run_setup("setup.py", script_args=build_args)

dist_folder = os.path.join(python_packages_folder, 'dist')
wheel_file = os.listdir(dist_folder)[0]
os.chdir(package_folder)


# -------------------------------------Parameters related to Package title and basic information------------------------
package_name = "OpenDSS"
version = "0.5.1"
author = "Typhoon HIL"
author_website = "https://github.com/typhoon-hil/opendss-typhoon-hil-interface"
description = ("A library of special components that can be automatically converted to the OpenDSS format and simulated. "
               "The same components are also ready for HIL-simulation.<br><br>\n\n"
               "The Open Distribution System Simulator (OpenDSS) is a comprehensive electrical system simulation tool for electric utility distribution systems, and is maintained by the Electronic Power Research Institue (EPRI)."
               "The program basically supports all RMS steady-state (frequency domain) analyses commonly performed for utility distribution systems."
               "More information can be found on: <a href=\"https://www.epri.com/pages/sa/opendss\">https://www.epri.com/pages/sa/opendss.</a><br><br>\n\n"
               "The current version of the package supports Power Flow and Fault Study analyses.<br><br>\n\n"
               "This package is open-source and maintained on GitHub: <a href=\"https://github.com/typhoon-hil/opendss-typhoon-hil-interface\">https://github.com/typhoon-hil/opendss-typhoon-hil-interface</a>")

library_paths = [os.path.join(package_folder, "../dss_thcc_lib")]
resource_paths = []
example_paths = [os.path.join(package_folder, "../examples", "Package Examples")]
additional_files_paths = [os.path.join(package_folder, "../importer")]
python_packages_paths = [os.path.join(package_folder, "python_packages", "dist", wheel_file)]
documentation_paths = [os.path.join(package_folder, "../dss_thcc_lib", "help", "OpenDSSManual.pdf")]
documentation_landing_page = os.path.join(package_folder, "../dss_thcc_lib", "help", "OpenDSSManual.pdf")
release_notes_path = os.path.join(package_folder, "release_notes", "release_notes.pdf")
output_path = os.path.join(package_folder, "output")
icon_path = os.path.join(package_folder, "dss_icon.png")

try:
    package_path = pkm.create_package(package_name=package_name,
                                      version=version,
                                      output_path=output_path,
                                      author=author,
                                      website=author_website,
                                      description=description,
                                      library_paths=library_paths,
                                      resource_paths=resource_paths,
                                      example_paths=example_paths,
                                      additional_files_paths=additional_files_paths,
                                      python_packages_paths=python_packages_paths,
                                      documentation_paths=documentation_paths,
                                      documentation_landing_page=documentation_landing_page,
                                      release_notes_path=release_notes_path,
                                      icon_path=icon_path)

    print(f"1) Package successfully created at: {os.path.relpath(package_path, package_folder)}")

    # Renaming Typhoon Package File
    old_tpkg_name = os.path.join(output_path, f"{package_name.lower()}.tpkg")
    new_tpkg_name = os.path.join(output_path, f"{package_name.lower()}_{version.replace('.', '')}.tpkg")
    if os.path.isfile(new_tpkg_name):
        os.remove(new_tpkg_name)
    os.rename(old_tpkg_name, new_tpkg_name)

    # # deleting wheel files
    # try:
    #     shutil.rmtree(python_packages_folder)
    #     print(f"2) Wheel files deleted successfully.")
    # except OSError as e:
    #     # If an error occurs (e.g., file not found), handle it
    #     print(f"2) Error deleting wheel files: {e}")

except Exception as e:
    print(f"Exception occurred: {e}")

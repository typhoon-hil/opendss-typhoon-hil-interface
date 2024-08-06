from typhoon.api.schematic_editor import model as mdl
import os

package_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(package_folder)
opendss_folder = os.path.join(package_folder, "../")
dss_tlib_folder = os.path.join(opendss_folder, "/dss_thcc_lib")

mdl.add_library_path(library_path=dss_tlib_folder, add_subdirs=True, persist=True)

print(f"Reloading...")
mdl.reload_libraries()
print(f"Reloaded.")

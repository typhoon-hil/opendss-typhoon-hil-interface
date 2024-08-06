from typhoon.api.schematic_editor import model as mdl
import os

package_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(package_folder)
opendss_folder = os.path.join(package_folder, "../")
dss_tlib_folder = os.path.join(opendss_folder, "/dss_thcc_lib")

print(f"{package_folder=}")
print(f"{opendss_folder=}")
print(f"{dss_tlib_folder=}")

# Get all current library paths and remove them
old_paths = mdl.get_library_paths()
print(f"Removing previous library paths...")
for path in old_paths:
    mdl.remove_library_path(path)
    print(f"{path} removed.")

# Add OpenDSS library path
print(f"Adding OpenDSS library path...")
mdl.add_library_path(library_path=dss_tlib_folder, add_subdirs=True, persist=True)
print(f"{dss_tlib_folder} Added.")

print(f"Reloading Libraries...")
mdl.reload_libraries()
print(f"Reloaded.")

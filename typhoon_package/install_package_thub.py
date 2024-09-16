from typhoon.api.schematic_editor import model as mdl
from typhoon.api.package_manager import package_manager as pkm
import os
import sys

package_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(package_folder)
opendss_folder = os.path.join(package_folder, "../")
thub_package_folder = os.path.join(opendss_folder, 'package')


for pkg in pkm.get_installed_packages():
    print(f"Removing: {pkg.package_name}")
    pkm.uninstall_package(pkg.package_name)

if os.path.exists(thub_package_folder):
    for package_file in os.listdir(thub_package_folder):
        if package_file.endswith(".tpkg"):
            print(f"{package_file=}")
            pkm.install_package(os.path.join(thub_package_folder, package_file))
    print(f"Reloading...")
    mdl.reload_libraries()
    print(f"Reloaded.")
    all_packages = pkm.get_installed_packages()
    print(f"All installed packages: {all_packages}")
else:
    print("There is no package folder")

# Add DSS site-packages to the sys.path
print(f"{sys.path=}")
path_to_python = sys.executable
print(f"{path_to_python=}")
python_dir = os.path.dirname(path_to_python)
print(f"{python_dir=}")
typhoon_dir = os.path.join(python_dir, "../", "../")
print(f"{typhoon_dir=}")
dss_dir = os.path.join(typhoon_dir, "package-environments", "OpenDSS", "venv", "Lib", "site-packages")
print(f"{dss_dir=}")
sys.path.append(dss_dir)
print(f"{sys.path=}")

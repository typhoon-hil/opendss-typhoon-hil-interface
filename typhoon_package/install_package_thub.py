from typhoon.api.schematic_editor import model as mdl
from typhoon.api.package_manager import package_manager as pkm
import os

package_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(package_folder)
opendss_folder = os.path.join(package_folder, "../")
thub_package_folder = os.path.join(package_folder, 'package')

if os.path.exists(thub_package_folder):
        pkm.install_package(thub_package_folder)
        mdl.reload_libraries()

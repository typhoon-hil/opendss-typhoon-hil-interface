from setuptools import setup, find_packages

setup(
    name='tse_to_opendss',
    version='0.5.1',
    packages=find_packages(exclude=['tests', 'importer']),
    package_data={"images": [r'dss_thcc_lib/images/*.png']},
    install_requires=["opendssdirect.py==0.8.0", "dss-python==0.13.0", "reportlab==4.0.8"],
    url='https://www.typhoon-hil.com/',
    include_package_data=True,
    license='MIT',
    author='Typhoon HIL',
    author_email=f'marcos.moccelini@typhoon-hil.com',
    description='Typhoon HIL Schematic Editor to OpenDSS converter'
)

# SLD functions must be added to import_hooks
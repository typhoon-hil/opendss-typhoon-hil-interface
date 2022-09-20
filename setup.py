from setuptools import setup, find_packages

setup(
    name='tse_to_opendss',
    version='0.3.0',
    packages=find_packages(exclude=['tests', ]),
    install_requires=["typhoon-hil-api"],
    url='https://www.typhoon-hil.com/',
    include_package_data=True,
    license='MIT',
    author='Marcos Moccelini',
    author_email=f'marcos.moccelini@typhoon-hil.com',
    description='Typhoon HIL Schematic Editor to OpenDSS converter'
)

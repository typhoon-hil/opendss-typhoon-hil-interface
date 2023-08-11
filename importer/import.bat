@echo off
set /p "dss_path=Enter the path to the master DSS file: "
set /p "place=Choose placement mode (1)charge-spring (2)center-expanding: "
call typhoon-python main.py %dss_path% %place%
pause

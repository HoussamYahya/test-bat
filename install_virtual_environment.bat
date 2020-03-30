@echo off
set "$py=0"
call:getPythonVersion

Rem Check python major version
for /f "delims=" %%a in ('python #.py ^| findstr "2"') do set "$py=2"
for /f "delims=" %%a in ('python #.py ^| findstr "3"') do set "$py=3"
del #.py
goto:%$py%

Rem No python is installed in path
echo python 32bit is not installed or python's path Path is not in the %%$path%% env. var
exit/b

Rem Python exe in path is 2.x version
:2
echo please install the python 3.x 32bit version
exit/b

Rem Python exe in path is 3.x version
:3
echo running with PY 3
python -c "import platform;import sys;archi = platform.architecture()[0];sys.exit(archi!='32bit')"
IF %ERRORLEVEL% NEQ 0 Echo please install the python 3.x 32bit version
IF %ERRORLEVEL% == 0 (goto:installPackages)
exit/b

Rem Get the major function of python
:getPythonVersion
echo import sys; print('{0[0]}.{0[1]}'.format(sys.version_info^)^) >#.py
exit/b

Rem Create virtual environment and Install the python packages with pip install
:installPackages
Echo Python version is correct --- installing packages
python -m venv ./venv
.\venv\Scripts\activate.bat & python -m pip install --upgrade pip & pip install -r requirements.txt
exit/b

Rem Install the libraries needed by the testbench
Rem pip install -r requirements.txt



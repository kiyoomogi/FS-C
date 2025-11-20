@echo off

set flac6=""C:/Program Files/Itasca/Flac3d600/exe64/python27/Scripts/pip.exe""
set flac7=""C:/Program Files/Itasca/FLAC3D700/exe64/python36/Scripts/pip.exe""

echo +----------------------------------------------+
echo ^|   Python library installer for TOUGH3-FLAC   ^|
echo ^|          Version 1.1.0 (March 2020)          ^|
echo +----------------------------------------------+
echo.
echo [1] Install/update for FLAC3D v6
echo [2] Install/update for FLAC3D v6 (full)
echo [3] Install/update for FLAC3D v7
echo [4] Install/update for FLAC3D v7 (full)
echo [5] Uninstall from FLAC3D v6
echo [6] Uninstall from FLAC3D v7
echo [7] Abort
echo.
choice /c 1234567 /m "Select an option: "

set case=%errorlevel%
if %case% == 1 goto case1
if %case% == 2 goto case2
if %case% == 3 goto case3
if %case% == 4 goto case4
if %case% == 5 goto case5
if %case% == 6 goto case6
if %case% == 7 goto case7
goto end

:case1
cmd /C %flac6% install pip==9.0.3 --user
cmd /C %flac6% install -U . --user
goto end

:case2
cmd /C %flac6% install pip==9.0.3 --user
cmd /C %flac6% install -U .[full] --user
goto end

:case3
cmd /C %flac7% install -U . --user
goto end

:case4
cmd /C %flac7% install -U .[full] --user
goto end

:case5
cmd /C %flac6% uninstall toughflac
goto end

:case6
cmd /C %flac7% uninstall toughflac
goto end

:case7
goto end

:end
echo.
pause
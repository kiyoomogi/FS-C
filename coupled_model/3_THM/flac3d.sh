#!/usr/bin/env bash

# FLAC3D version (default 7)
flac=${1:-7}

# FLAC3D commands to run
echo "echo off" >> flac3d.dat
echo "call 'flac3d.py'" >> flac3d.dat
echo "exit" >> flac3d.dat

# Detect if running under WSL or native Linux
if grep -qi microsoft /proc/version; then
    IS_WSL=true
else
    IS_WSL=false
fi

# Determine the terminal to use and the appropriate options
if [ "$IS_WSL" = false ]; then
    if [ "$DESKTOP_SESSION" = "gnome" ]; then
        TERMINAL="gnome-terminal"
        TERMINAL_OPTS="-- sh -c"
    elif [ "$DESKTOP_SESSION" = "xfce" ]; then
        TERMINAL="xfce4-terminal"
        TERMINAL_OPTS="--command"
    else
        # Default to gnome-terminal if the session is not explicitly gnome or xfce
        TERMINAL="gnome-terminal"
        TERMINAL_OPTS="-- sh -c"
    fi
fi

# Call FLAC3D console
case "$(uname -s)" in
    Linux )
        if [ "$IS_WSL" = true ]; then
            case "${flac}" in
                6 )
                    cmd.exe /c start cmd.exe /c wsl.exe /mnt/c/Program\ Files/Itasca/flac3d600/exe64/flac3d600_console.exe flac3d.dat;;
                7 )
                    cmd.exe /c start cmd.exe /c wsl.exe /mnt/c/Program\ Files/Itasca/FLAC3D700/exe64/flac3d700_console.exe flac3d.dat;;
            esac
        else
            case "${flac}" in
                6 )
                    $TERMINAL $TERMINAL_OPTS "bash /opt/itascasoftware/v600/flac3d600_console.sh flac3d.dat";;
                7 )
                    $TERMINAL $TERMINAL_OPTS "bash /opt/itascasoftware/v700/flac3d700_console.sh flac3d.dat";;
            esac
        fi;;
    CYGWIN* )
        case "${flac}" in
            6 )
                cygstart --minimize "C:\Program Files\Itasca\flac3d600\exe64\flac3d600_console.exe" "flac3d.dat";;
            7 )
                cygstart --minimize "C:\Program Files\Itasca\FLAC3D700\exe64\flac3d700_console.exe" "flac3d.dat";;
        esac;;
    * )
        echo "TOUGH3-FLAC only supports WSL and Cygwin.";;
esac

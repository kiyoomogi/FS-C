#!/usr/bin/env bash

# FLAC3D version (default 7)
flac=${1:-7}

# FLAC3D commands to run
echo "echo off" >> flac3d.dat
echo "call 'flac3d.py'" >> flac3d.dat
echo "exit" >> flac3d.dat

# Call FLAC3D console
case "$(uname -s)" in
	Linux )
		case "${flac}" in
			6 )
				cmd.exe /c start cmd.exe /c wsl.exe /mnt/c/Program\ Files/Itasca/flac3d600/exe64/flac3d600_console.exe flac3d.dat;;
			7 )
				gnome-terminal -- sh -c "bash /opt/itascasoftware/v700/flac3d700_console.sh flac3d.dat";;
		esac;;
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
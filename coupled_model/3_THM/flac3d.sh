#!/usr/bin/env bash

# FLAC3D version (default 9)
flac=${1:-9}

echo ${flac}

# FLAC3D commands to run
echo "echo off" >> flac3d.dat
echo "call 'flac3d.py'" >> flac3d.dat
echo "exit" >> flac3d.dat

# Call FLAC3D console
case "$(uname -s)" in
	Linux )
		case "${flac}" in
			7 )
                                xfce4-terminal --command="/opt/itascasoftware/v700/flac3d7_console.sh flac3d.dat" ;;
			9 )
                                xfce4-terminal --command="/opt/itascasoftware/subscription/flac3d9_console.sh flac3d.dat" ;;
		esac;;
esac

#!/bin/bash
################################################################################
# Copyright 2017 Ingo Hornberger <ingo_@gmx.net>
#
# This software is licensed under the MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in all copies
# or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
#
################################################################################

WINE=wine-development
CDS_LINK="https://store.codesys.com/ftp_download/3S/CODESYS/300000/3.5.15.0/CODESYS%203.5.15.0.exe"
TRICKS_LINK="https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks"
ADDITIONAL_PACKAGES=https://forge.codesys.com/svn/tol,cforge,code/trunk/cforge.package
export WINEPREFIX=~/.wine.cds
export WINEARCH=win32

# kill current and subprocesses on exit
trap "kill 0" EXIT

# this should be running in the background to close rundll32 dialogs
function handle_rundll
{
    while true; do
	#
	# rundll32 error
	#
	while ! xdotool search --name 'rundll32'; do
	    sleep 1
	done
	echo "rundll32 error found"
	(
	    # next
	    sleep 2
	    echo "-> sending key sequence"
	    xdotool key "Tab"; xdotool key "space";
	)
	sleep 1
    done

}

function handle_codemeter
{
    while true; do
	#
	# CodeMeter setup
	#
	while ! xdotool search --name 'codemeter'; do
	    sleep 1
	done
	echo "codemeter found"
	(
	    # next
	    sleep 5
	    echo "-> sending key sequence"
	    xdotool key "space"; 
	    # check license
	    sleep 1
	    xdotool key "space";
	    # next
	    sleep 1
	    xdotool key "Tab"; xdotool key "Tab"; xdotool key "space";
	    # next
	    sleep 1
	    xdotool key "Tab"; xdotool key "Tab"; xdotool key "Tab"; xdotool key "Tab"; xdotool key "space";
	    # next
	    sleep 1
	    xdotool key "Tab"; xdotool key "Tab"; xdotool key "Tab"; xdotool key "Tab"; xdotool key "Tab"; xdotool key "space";
	    # install
	    sleep 1
	    xdotool key "space";
	    # finish
	    sleep 5
	    xdotool key "space";
	)
	sleep 1
    done

}

function kill_systray
{
    while true; do
	while ! pgrep -f SysTray.exe; do
	    sleep 1
	done
	echo "SysTrays running - kill them..."
	pgrep -f SysTray.exe | xargs -n 1 kill
	sleep 1
    done
}

function get
{
    wget --no-verbose --output-document=setup.exe -c "${CDS_LINK}"
    wget --no-verbose --output-document=winetricks -c "${TRICKS_LINK}" 
    chmod 755 winetricks 
    (
	mkdir -p Packages
	cd Packages
	for i in ${ADDITIONAL_PACKAGES}; do
		wget --no-verbose -c "${i}" 
	done
    )
}

function prereq
{
    echo -n "Checking prerequisite '${WINE}'"
    if which ${WINE}; then
	echo "=> OK"
    else
	echo "ERROR: Please install wine32-development and wine64-development"
	exit 1
    fi
}

function switch_to_win7
{
    # call wine to create new WINEPREFIX
    ${WINE} dir
    sleep 5
    # patch win version
    cp system.reg ${WINEPREFIX}
}

function winetricks
{
    ./winetricks -q vcrun2005 vcrun2008 vcrun2013 vcrun2015 dotnet46 &> /dev/zero
    wineserver-development -w
    ./winetricks nocrashdialog
    wineserver-development -w
}

function install
{
    ${WINE} setup.exe /v/qn /s /v'INSTALLDIR=C:\\CODESYS' /v"ADDLOCAL=Basic,CODESYS,cforge Tool" /v"CDS_INSTALL_SERVICES=0"
    wineserver-development -w
}

function post_install
{
    ${WINE} reg add "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\S-1-5-21-0-0-0-1000"
    wineserver-development -w
}

no_check="y"
no_dl="y"
no_winetricks="y"
no_install="y"
no_postinstall="y"
no_xvfb="y"
case ${1} in
    --winetricks)
	no_winetricks=""
	;;
    --install)
	no_install=""
	;;
    --postinstall)
	no_postinstall=""
	;;
    --xvfb)
	no_check=""
	no_dl=""
	no_winetricks=""
	no_install=""
	no_postinstall=""
	no_xvfb=""
	;;
    -h)
	echo "usage: $0 <param>"
	echo "params:"
	echo "    --winetricks"
	echo "    --install"
	echo "    --postinstall"
	echo "    --xvfb"
	;;
    *)
	no_check=""
	no_dl=""
	no_winetricks=""
	no_install=""
	no_postinstall=""
	;;
esac

if [ -z ${no_xvfb} ]; then
    echo "=== Start XVFB ==="
    export DISPLAY=:98
    Xvfb :98 &
    sleep 3
    jwm &
    
    # install handlers only when automating the installation
    # with Xvfb and xdotool
    (handle_rundll)&
    (handle_codemeter)&
    (kill_systray)&
fi
if [ -z ${no_check} ]; then
    echo "=== Checking Prerequisites ==="
    prereq
fi
if [ -z ${no_dl} ]; then
    echo "=== Downloading packets ==="
    get
fi
if [ -z ${no_winetricks} ]; then
    echo "=== Installing Prerequisites w/ winetricks ==="
    winetricks
fi
if [ -z ${no_install} ]; then
    echo "=== Installing CODESYS ==="
    install
fi
if [ -z ${no_postinstall} ]; then
    echo "=== Postinstall Fixups ==="
    post_install
    if [ -z ${no_install} ]; then
	echo "=== Installing CODESYS again ==="
	echo "after one complete run + post install, also all *.exe are copied ;)"
	install
    fi
fi
if [ -z ${no_xvfb} ]; then
    echo "=== Kill XVFB ==="
    killall -9 Xvfb
fi

exit

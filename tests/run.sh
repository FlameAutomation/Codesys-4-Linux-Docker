#!/bin/bash

# exit if one of the commands here fail
set -e

cwd=$(dirname ${0})

(
	# change current working directory to the directory,
	# where this script is located.
	cd ${cwd};

	# execute several commands
	echo "*** Project: Build Bootapplication"
	../codesys-ide/codesys build-bootapp
	echo "*** Project: Save Project Archive"
	../codesys-ide/codesys save-projectarchive
	echo "*** Library: Compile Library"
	../codesys-ide/codesys compile-library
	echo "*** Library: Export Documentation"
	../codesys-ide/codesys export-documentation
	echo "*** Library: Generate package manifest"
	../codesys-ide/codesys gen-package-manifest
	echo "*** Library: Build Package"
	../codesys-ide/codesys build-package

	# unit testing
	# install doesn't work on drone atm.
	#echo "*** Unit Test: install cfunit"
	#../codesys-ide/codesys install 'https://forge.codesys.com/prj/cfunit/code/HEAD/tree/tags/v1.1.0.0/v1.1.0.0.package?format=raw'
	echo "*** Unit Test: build test applications"
	../codesys-ide/codesys build-test
	echo "*** Unit Test: run test w/o cfunit"
	../codesys-ide/codesyscontrol PRG_RUNTEST.library.app output.txt
	[ -f .drone-artifacts/output.txt ]
	echo "*** Unit Test: run test w/ cfunit"
	../codesys-ide/codesyscontrol cfunit-example.library.app C:/cfunit_xunit_testresults.xml
	[ -f .drone-artifacts/C:/cfunit_xunit_testresults.xml ]
)

echo "*** SUCCESS"

# UptimeParser

Simple application to report on SNMP uptime for various devices

* Script reads line separated devices and output number of devices over time limit

# Build (Install requirements)
* Install all libraries in requirements.txt with PIP
* To use PyInstaller to generate EXE, you will need MS Visual C++ 2015 14.0.23918 redistributable

* Run `pyinstaller --clean UptimeParserMain.spec` (build from root dir)

* NOTE: You will need to edit the `UptimeParserMain.spec` file to include where you are building from this is due to an issue with MIB libraries not getting bundled with the complied EXE due to them getting dynamically loaded. Because of this, PyInstaller does not add them to the generated EXE

* TLDR; Dynamically loading libraries do not play well with static analysis :-P

# Testing
* Just run Pytest `pytest --cov -s -v` (from root dir)
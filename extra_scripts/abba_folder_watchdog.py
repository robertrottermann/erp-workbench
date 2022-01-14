"""
@echo off
REM Beispiel Batch fuer Import
REM ---------------------------------------------

REM -------------------------------------------------
REM - Set Parameter for AbaConnect Import
REM -------------------------------------------------

REM ABACUS Pfadangabe f�r abaconnectimportconsole.exe (oder �ltere abajvm.exe)
SET APATH=c:\abac

rem Choose the program for import :
rem ================================
set AC_EXE_PROGRAM=
if EXIST "%APATH%\df\ABAJVM.EXE" (
   rem Set Default as old command line via Abajvm.exe
   set AC_EXE_PROGRAM=%APATH%\df\ABAJVM.EXE -progname ACImport -cmd wait -ownvm -Parameter
)
rem Note : The executable abaconnectimportconsole.exe is available from ABACUS V2010
if EXIST "%APATH%\df\abaconnectimportconsole.exe" (
   rem New for V2010 is with abaconnectimportconsole.exe (not via ABAJVM.EXE)
   set AC_EXE_PROGRAM=%APATH%\df\abaconnectimportconsole.exe
)
if EXIST "%APATH%\df_win64\abaconnectimportconsole.exe" (
   rem New for V2012 is 64 Bit with abaconnectimportconsole.exe
   set AC_EXE_PROGRAM=%APATH%\df_win64\abaconnectimportconsole.exe
)

if "%AC_EXE_PROGRAM%"=="" (
   echo.
   echo *******************************************************
   echo          ERROR : NO ABCONNECT PROGRAM FOUND 
   echo *******************************************************
   echo.
   goto end_of_batch   
)

set CURRENT_DIRECTORY=%CD%

rem ================================
rem Set Benutzer, Password, Mandant
set AC_USERNAME=Administrator
set AC_PASSWORD=eli
set AC_MANDANT=7777

rem ================================
rem Set Schnittstelle Details
set AC_APPLICATION=ADRE
set AC_PROG_ID=625
set AC_IMPORT_FILENAME=%CURRENT_DIRECTORY%\AC_Import_ADRE_Address.xml
set AC_RESPONSE_FILENAME=%CURRENT_DIRECTORY%\Import_Response_File.xml

rem Check the import File exists
if NOT EXIST "%AC_IMPORT_FILENAME%" (
   echo.
   echo *******************************************************
   echo      ERROR : AbaConnect Import File NOT FOUND 
   echo         %AC_IMPORT_FILENAME%
   echo *******************************************************
   echo.
   goto end_of_batch   
)

rem Remove existing Reponse File
if EXIST "%AC_RESPONSE_FILENAME%" del /Q "%AC_RESPONSE_FILENAME%"

set AC_PROG_PARAMS="/USR%AC_USERNAME%" "/PW%AC_PASSWORD%" "-M%AC_MANDANT%" "-responselevelINFO" "-responseYES" "-responsefile%AC_RESPONSE_FILENAME%" "-a%AC_APPLICATION%" "-P%AC_PROG_ID%" -datamodeXML "-importfile%AC_IMPORT_FILENAME%"

rem Execute the command line
%AC_EXE_PROGRAM% %AC_PROG_PARAMS%

REM CHECK RESPONSE FILE EXISTS
if NOT EXIST "%AC_RESPONSE_FILENAME%" (
    echo.
    echo.
    echo ****************************************************
    echo NO RESPONSE FILE CREATED - SOMETHING BAD HAPPENED !
    echo    e.g. an error occurred by abaconnect commandline
    echo         check the exceptions to see the errors
    echo         output by the abaconnect commandline program
    echo ****************************************************
    echo.
    echo.
    goto end_of_batch
)
echo.
echo.

rem OPTIONAL : Read the Response File and to extract the Error and Warning count and echo the Response Messages
rem This Example may be useful for testing phase
if EXIST "%AC_RESPONSE_FILENAME%" (
    if EXIST "read_response_file_test.bat" (
        call read_response_file_test %AC_RESPONSE_FILENAME%
    )
)

:end_of_batch

pause

/opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" /PWeli  -aLOHN  -version2021.00  "-M7777"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefileX:\response.xml"  "-exportfileX:\data.xml"

 290  which abaconnectexportconsole.sh
  291  locate abaconnectexportconsole.sh
  292  /opt/abacus/etc/tools/abaconnectexportconsole.sh
  293  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PWeli"
  294  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PWeli"  "-aLOHN"  "-version2021.00"
  295  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" /PWeli  -aLOHN  -version2021.00
  296  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" /PWeli  -aLOHN  -version2021.00 -M 1
  297  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" /PWeli  -aLOHN  -version2021.00 -M=0
  298  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" /PWeli  -aLOHN  -version2021.00  "-M7777"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefileX:\response.xml"  "-exportfileX:\data.xml"
  301  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PAbacus$99"  -aLOHN  -version2021.00  "-M7777"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefileX:\response.xml"  "-exportfileX:\data.xml"
  303  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PAbacus$99"  -aLOHN  -version2021.00  "-M7777"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefileX:\response.xml"  "-exportfileX:/root/data.xml"
  304  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PAbacus$99"  -aLOHN  -version2021.00  "-M7777"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefileX:\response.xml"  "-exportfile/root/data.xml"
  307  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PAbacus$99"  -aLOHN  -version2021.00  "-M7777"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefile/root/response.xml"  "-exportfile/root/data.xml"
  308  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PAbacus$99"  -aLOHN  -version2021.00  "-M3900"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefile/root/response.xml"  "-exportfile/root/data.xml"
  309  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PAbacus\$99"  -aLOHN  -version2021.00  "-M3900"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefile/root/response.xml"  "-exportfile/root/data.xml"
  310  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PAbacus\$99XXX"  -aLOHN  -version2021.00  "-M3900"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefile/root/response.xml"  "-exportfile/root/data.xml"
  311  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/Pwilli"  -aLOHN  -version2021.00  "-M3900"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefile/root/response.xml"  "-exportfile/root/data.xml"
  312  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PAbacus\$99XXX"  -aLOHN  -version2021.00  "-M3900"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefile/root/response.xml"  "-exportfile/root/data.xml"
  313  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRAdministrator" "/PAbacus"  -aLOHN  -version2021.00  "-M3900"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"  "-responsefile/root/response.xml"  "-exportfile/root/data.xml"
  323  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRacInterface" "/PWsUnFun8!"  -aLOHN  -version2021.00  "-M3900"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-P625" "-VGB100" "-responseYES"  "-responsefile/root/abaConnect/response.xml"  "-exportfile/root/abaConnect/data.xml"
  339  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRacInterface" "/PWSieheSeparaterKanal"  -aLOHN  -version2021.00  "-M3900"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-P625" "-VGB100" "-responseYES"  "-responsefile/root/abaConnect/response.xml"  "-exportfile/root/abaConnect/data.xml“
  341  ll /opt/abacus/etc/tools/abaconnectexportconsole.sh
  342  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRacInterface" "/PWSieheSeparaterKanal"  -aLOHN  -version2021.00  "-M3900"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-P625" "-VGB100" "-responseYES"  "-responsefile/root/abaConnect/response.xml"  "-exportfile/root/abaConnect/data.xml“
  344  /opt/abacus/etc/tools/abaconnectexportconsole.sh "/USRacInterface" "/PWsUnFun8!"  -aLOHN  -version2021.00  "-M3900"  "-acidHierarchyEmployee"  "-mapidAbaDefault"  "-datamodeXML"  "-P625" "-VGB100" "-responseYES"  "-responsefile/root/abaConnect/response.xml"  "-exportfile/root/abaConnect/data.xml"
  351  /opt/abacus/etc/tools/abaconnectexportconsole.sh  "/USacInterface" "/PWsUnFun8!"  "-aLOHN"  "-version2020.00"  "-M3900"      "-acidPeriodPreentry"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"      "-responsefile/root/abaConnect/period/response.xml"  "-exportfile/root/abaConnect/period/data.xml"
  353  /opt/abacus/etc/tools/abaconnectexportconsole.sh  "/USRacInterface" "/PWsUnFun8!"  "-aLOHN"  "-version2020.00"  "-M3900"      "-acidPeriodPreentry"  "-mapidAbaDefault"  "-datamodeXML"  "-responseYES"      "-responsefile/root/abaConnect/period/response.xml"  "-exportfile/root/abaConnect/period/data.xml"
  491  history | grep abaconnectexportconsole

********************************
#!/bin/sh
#
# NAME:
#       abaconnectexportconsole.sh -- export abaconnect definitions
#
# SYNOPSIS:
#       abaconnectexportconsole.sh [arguments]
#
# DESCRIPTION:
#       This is a wrapper around the Java program used to export abaconnect
#       definitions.

# Find and source ABACUS environment
. `dirname $0`/../abacus.env
[ "X$ABACUS_ROOT" != X ] || { echo $0: abacus.env not found >&2; exit 1; }

# Prepare the Java environment:
#       The CLASSPATH wildcard must be expanded by Java, not by shell!
export JAVA_HOME=$ABACUS_ROOT/jre
JAVA=$JAVA_HOME/bin/java
ABACUS_JAVA=$ABACUS_ROOT/java
export CLASSPATH="$ABACUS_JAVA/*:$ABACUS_JAVA/ext/*:$ABACUS_JAVA/ulc/*"

# Run the command.
exec $JAVA -Xmx256m --illegal-access=warn --add-opens=java.base/java.lang=ALL-UNNAMED \
        -Djava.library.path=$ABACUS_ROOT/lib \
        -Djava.net.preferIPv4Stack=true \
        ch.abacus.publ.common.prg.sst.cmdline.SSTExport "$@"
/opt/abacus/etc/tools/abaconnectexportconsole.sh (END)

***********************************
#!/bin/sh
#
# NAME:
#       abaconnectimportconsole.sh -- import abaconnect definitions
#
# SYNOPSIS:
#       abaconnectimportconsole.sh [arguments]
#
# DESCRIPTION:
#       This is a wrapper around the Java program used to import abaconnect
#       definitions.

# Find and source ABACUS environment
. `dirname $0`/../abacus.env
[ "X$ABACUS_ROOT" != X ] || { echo $0: abacus.env not found >&2; exit 1; }

# Prepare the Java environment:
#       The CLASSPATH wildcard must be expanded by Java, not by shell!
export JAVA_HOME=$ABACUS_ROOT/jre
JAVA=$JAVA_HOME/bin/java
ABACUS_JAVA=$ABACUS_ROOT/java
export CLASSPATH="$ABACUS_JAVA/*:$ABACUS_JAVA/ext/*:$ABACUS_JAVA/ulc/*"

# Run the command.
exec $JAVA -Xmx256m --illegal-access=warn --add-opens=java.base/java.lang=ALL-UNNAMED \
        -Djava.library.path=$ABACUS_ROOT/lib \
        -Djava.net.preferIPv4Stack=true \
        ch.abacus.publ.common.prg.sst.cmdline.SSTImport "$@"

******************
less /opt/abacus/etc/abacus.env
"""
# https://thepythoncorner.com/posts/2019-01-13-how-to-create-a-watchdog-in-python-to-look-for-filesystem-changes/
# import time
# from watchdog.observers import Observer
# from watchdog.events import PatternMatchingEventHandler


#  1def on_created(event):
#  2    print(f"hey, {event.src_path} has been created!")
#  3
#  4def on_deleted(event):
#  5    print(f"what the f**k! Someone deleted {event.src_path}!")
#  6
#  7def on_modified(event):
#  8    print(f"hey buddy, {event.src_path} has been modified")
#  9
# 10def on_moved(event):
# 11    print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")

# if __name__ == "__main__":
#     patterns = ["*"]
#     ignore_patterns = None
#     ignore_directories = False
#     case_sensitive = True
#     my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)


import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:

    def on_created(self, event):
        print(f"hey, {event.src_path} has been created!")
    
    def on_deleted(self, event):
        print(f"what the f**k! Someone deleted {event.src_path}!")
    
    def on_modified(self, event):
        if event.is_directory:
            print('i do not bother directories')
        else:
            print(f"hey buddy, {event.src_path} has been modified")
    
    def on_moved(self, event):
        print(f"ok ok ok, someone moved {event.src_path} to {event.dest_path}")
        
    def __init__(self, directory=".", handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory
        
        # monkey patch handler
        self.handler.on_created = self.on_created
        self.handler.on_deleted = self.on_deleted
        self.handler.on_modified = self.on_modified
        self.handler.on_moved = self.on_moved
        

    def run(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        print("\nWatcher Running in {}/\n".format(self.directory))
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join() # Wait until the thread terminates.
        print("\nWatcher Terminated\n")


class MyHandler(FileSystemEventHandler):

    def on_any_event(self, event):
        if event.event_type == "deleted":
                    print("Oh no! It's gone!")
        if event.src_path[-5:] == ".xml":
                    print("Microsoft Word documents not supported.")                
        print(event) # Your code here

if __name__=="__main__":
    w = Watcher(".", MyHandler())
    w.run()

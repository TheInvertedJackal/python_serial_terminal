# Python Serial Terminal
_Created by Mac on 5/4/2026_


This is a simple script to open a sudo "terminal" and allow you to interface with serial connections

## Notes
This assumes a default baud rate of 115200, if you need to change this you can edit the number freely in the script.

When launching the Terminal, you can add an optional boot-up script as an argument.

## Launch

`python serial_terminal.py \<script.txt\>`

## Commands
_All commands specific to the terminal and it's state start with a "!"_
 - !QUIT : Quits the program if called in the terminal, if called in a script, it'll quit out of the script.
 - !RUN \<File Script\> : Runs a given text file as a script.
 - !TIME \<True or False\> : Enables or Disables Time Stamps when sending Serial Data. (Defaults to False)
 - !OPEN \<Port\> : Opens a given Serial Port.
 - !SET \<Port\> : Sets and Open port to be the the one to actively send serial data too.
 - !CLOSE \<Port> : Closes a Port (All Ports are closed when the terminal is closed)
 - !ISOPEN \<Port> : Query to see if a given Serial Port is currently open.
 - !SLEEP \<int (ms)> : Sleep the terminal (or more likely script) for n milliseconds.
 - !UPDATE: See what is currently in the receiving buffer, if it has not already been received.
 - !CRNL \<True or False> : Appends a '\r\n' to each line entered that's sent over the serial connection. (Defaults to True)
 - !WAIT : Only available while running scripts, pauses script execution until [Enter] is pressed.
 - !HELP: Help and Descriptions

_The !HELP command also has this information_

If something is entered in that is not one of these commands, it is assumed that it's meant to be sent over the serial line.

## Comments

These are only available in scripts, but they work similar to python, in that all text after a "#" is ignored.

View the examples in the [examples](examples) folder to see the general flow, as well as how to run scripts etc. Running things in scripts is as if you were entering them manually similar to bash. Unlike bash there are no multi lined commands.

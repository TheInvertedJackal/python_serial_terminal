import serial
import time 
from datetime import datetime
import sys
import os

# Command Setup
# Type: TIME, RUN, <AT-COMMAND>, OPEN, SET, CLOSE, QUIT
# Arg1: Any
# Arg2: Any

# Ports Setup
# Port Name (Str like "COM6")
# Port Object

open_ports = []
active_port = None

baud_rate = 115200
startup_script = ""

if len(sys.argv) == 2:
    startup_script = sys.argv[1]

# Type: TIME, RUN, <AT-COMMAND>, OPEN, SET, CLOSE, QUIT, ISOPEN, HELP, SLEEP
cmd_lookup = {
    "!QUIT": {
        "type": "QUIT",
        "argc": 0,
        "exp_arg1": None,
        "exp_arg2": None,
        "desc": "Quits the program if called in the terminal, if called in a script, it'll quit out of the script."
    },
    "!RUN": {
        "type": "RUN",
        "argc": 1,
        "exp_arg1": "File Script",
        "exp_arg2": None,
        "desc": "Runs a given text file as a script."
    },
    "!TIME": {
        "type": "TIME",
        "argc": 1,
        "exp_arg1": "True or False",
        "exp_arg2": None,
        "desc": "Enables or Disables Time Stamps when sending Serial Data. (Defaults to False)"
    },
    "!OPEN": {
        "type": "OPEN",
        "argc": 1,
        "exp_arg1": "Port",
        "exp_arg2": None,
        "desc": "Opens a given Serial Port."
    },
    "!SET": {
        "type": "SET",
        "argc": 1,
        "exp_arg1": "Port",
        "exp_arg2": None,
        "desc": "Sets and Open port to be the the one to actively send serial data too."
    },
    "!CLOSE": {
        "type": "CLOSE",
        "argc": 1,
        "exp_arg1": "Port",
        "exp_arg2": None,
        "desc": "Closes a Port (All Ports are closed when the terminal is closed)"
    },
    "!ISOPEN": {
        "type": "ISOPEN",
        "argc": 1,
        "exp_arg1": "Port",
        "exp_arg2": None,
        "desc": "Query to see if a given Serial Port is currently open."
    },
    "!SLEEP": {
        "type": "SLEEP",
        "argc": 1,
        "exp_arg1": "int (ms)",
        "exp_arg2": None,
        "desc": "Sleep the terminal (or more likely script) for n milliseconds."
    },
    "!UPDATE": {
        "type": "UPDATE",
        "argc": 0,
        "exp_arg1": None,
        "exp_arg2": None,
        "desc": "See what is currently in the receiving buffer, if it has not already been received."
    },
    "!CRNL": {
        "type": "CRNL",
        "argc": 1,
        "exp_arg1": "True or False",
        "exp_arg2": None,
        "desc": "Appends a \'\\r\\n\' to each line entered that's sent over the serial connection. (Defaults to True)"
    },
    "!WAIT": {
        "type": "WAIT",
        "argc": 0,
        "exp_arg1": None,
        "exp_arg2": None,
        "desc": "Only available while running scripts, pauses script execution until [Enter] is pressed."
    },
    "!HELP": {
        "type": "HELP",
        "argc": 0,
        "exp_arg1": None,
        "exp_arg2": None,
        "desc": "Help and Descriptions"
    },
}
time_next_command = False
in_crnl_mode = True
executing_script = 0

input_txt = "> "

if len(sys.argv) == 3:
    if os.path.isfile(sys.argv[2]):
        startup_script = sys.argv[2]
    else:
        print(f"The provided script [{startup_script}] does not exist!")
        exit(-1)

def print_script_command(script_input):
    print(f"{input_txt}{script_input}")

def print_command_info(info_to_print):
    print(f"! {info_to_print}")

# Get the serial Output
def cmd_print_ser_output():
    global active_port
    if active_port == None:
        print_command_info("No active port set, cannot receive Serial Data")
        return 
    ser = active_port["ser"]
    read_lines = ser.readlines()
    for line in read_lines:
        try:
            print(f"] {line.decode('utf-8').strip()}")
        except Exception as e:
            print_command_info("A line could not be decoded.")
# This ends the command on both the terminal, and signals the end of a command
def print_command_complete():
    print(" ---")

def cmd_wait():
    global executing_script
    if executing_script == 0:
        print_command_info("You cannot pause when in non script settings (Why would want to???)")
    else:
        input("[Press Enter to Continue]")

# Run an AT command
def cmd_run_at_command(command):
    global active_port
    global time_next_command
    global in_crnl_mode
    if active_port == None:
        print_command_info("No active port set, cannot send Serial Data")
        return 
    ser = active_port["ser"]
    start_time = 0
    if time_next_command:
        start_time = datetime.now()
    if in_crnl_mode:
        command = command + "\r\n"
    ser.write(command.encode("utf-8"))
    cmd_print_ser_output()
    if time_next_command:
        print_command_info(f"This Command Ran at: {start_time}")

def cmd_pause(sleep_ms):
    try:
        number = int(sleep_ms)
        time.sleep(number / 1000)
    except ValueError:
        print_command_info(f"The value {sleep_ms} is not an integer")

def validate_true_false_input(input, command_name):
    input = input.upper()
    if input == "FALSE":
        return False
    elif input == "TRUE":
        return True
    else:
        print_command_info(f"You need to use TRUE or FALSE as an Arg for {command_name}")
        return None

# State Time that command is run
def cmd_toggle_flag_time(time_cmd):
    global time_next_command
    new_state = validate_true_false_input(time_cmd, "#TIME")
    if new_state == None:
        return
    time_next_command = new_state
    print_command_info(f"Commands Execution time Displayed: {time_next_command}")

def cmd_toggle_crnl(crnl_cmd):
    global in_crnl_mode
    new_state = validate_true_false_input(crnl_cmd, "#CRNL")
    if new_state == None:
        return
    in_crnl_mode = new_state
    print_command_info(f"Will add a \'\\n\\r\' to the end off all serial connections: {time_next_command}")

def cmd_help():
    print("Multi Serial Port Terminal\nUsed for interacting with multiple Ports at once for testing or other data.\nCommands:")
    for cmd in cmd_lookup:
        command_template = cmd_lookup[cmd]
        command_statement = cmd
        for i in range(command_template["argc"]):
            command_statement += f" <{command_template[f"exp_arg{i + 1}"]}>"
        print(f" - {command_statement}\n  * {command_template["desc"]}\n")
    print("All other data sent that does not line up with the terminal commands above is sent over the serial line via")

## PORT MANAGEMENT
def has_port_open(port_str):
    for port in open_ports:
        if port["name"] == port_str:
           return port
    return False

def cmd_is_port_open(port_str):
    port_open = has_port_open(port_str)
    if port_open == False:
        print_command_info(f"The Port {port_str} is Not Open")
    else:
        print_command_info(f"The Port {port_str} is Open")

# Adds a port to the
def cmd_add_port(port_str):
    global open_ports
    if has_port_open(port_str) != False:
        print_command_info(f"Port {port_str} already open.")
        return
    new_port = serial.Serial(port_str, baud_rate, timeout=1)
    time.sleep(1)
    port_to_add = {}
    port_to_add["name"] = port_str
    port_to_add["ser"] = new_port
    open_ports.append(port_to_add)
    print_command_info(f"Successfully Opened Port {port_str}")

def cmd_set_active_port(port_str):
    global active_port
    to_set = has_port_open(port_str)
    if to_set == False:
        print_command_info(f"No Port: {port_str} is Open")
    else:
        active_port = to_set
        print_command_info(f"Active Port is now: {port_str}")

def cmd_close_port(port_str):
    global open_ports
    global active_port
    to_close = has_port_open(port_str)
    if active_port == to_close:
        active_port = None
    if to_close == False:
        print_command_info(f"No Port: {port_str} is Open")
    else:
        open_ports.remove(to_close)
        to_close["ser"].close()
        print_command_info(f"Closed Port: {port_str}")

def port_cleanup():
    global open_ports
    for port in open_ports:
        port["ser"].close()
    open_ports = []


# Type: TIME, RUN, <AT-COMMAND>, OPEN, SET, CLOSE, QUIT, ISOPEN, HELP, SLEEP
def run_cmd(command):
    if command["type"] == "RUN":
        print("[!] Cannot Run scripts from \"run_cmd\" function.")
    elif command["type"] == "QUIT":
        print("[!] Quit must be processed in the main loop.")
    elif command["type"] == "AT":
        cmd_run_at_command(command["arg1"])
    elif command["type"] == "OPEN":
        cmd_add_port(command["arg1"])
    elif command["type"] == "SET":
        cmd_set_active_port(command["arg1"])
    elif command["type"] == "CLOSE":
        cmd_close_port(command["arg1"])
    elif command["type"] == "TIME":
        cmd_toggle_flag_time(command["arg1"])
    elif command["type"] == "ISOPEN":
        cmd_is_port_open(command["arg1"])
    elif command["type"] == "HELP":
        cmd_help()
    elif command["type"] == "SLEEP":
        cmd_pause(command["arg1"])
    elif command["type"] == "UPDATE":
        cmd_print_ser_output()
    elif command["type"] == "CRNL":
        cmd_toggle_crnl(command["arg1"])
    elif command["type"] == "WAIT":
        cmd_wait()
    else:
        print(f"[!] Command Type: {command["type"]} not recognized")

def cmd_warning(cmd, required_type1, required_type2=None):
    if required_type1 == None:
        print_command_info(f"The Command {cmd} requires no additional args")
    elif required_type2 == None:
        print_command_info(f"The Command {cmd} requires an arg of type {required_type1}.") 
    else: 
        print_command_info(f"The Command {cmd} requires an arg of type {required_type1} and {required_type2}.")

def cmd_parse(raw_line):
    raw_line = raw_line.strip()
    raw_line_split = raw_line.split()
    raw_line_split[0] = raw_line_split[0].upper()
    argc = len(raw_line_split)
    command_data = {}
    if raw_line_split[0] in cmd_lookup:
        command_template = cmd_lookup[raw_line_split[0]]
        if argc - 1 != command_template["argc"]:
            cmd_warning(raw_line_split[0], command_template["exp_arg1"], command_template["exp_arg2"])
            return None
        command_data["type"] = command_template["type"]
        for i in range(argc - 1):
            command_data[f"arg{i + 1}"] = raw_line_split[i + 1]
        return command_data
    else:
        command_data["type"] = "AT"
        command_data["arg1"] = raw_line
        return command_data


# Run script
def cmd_run_at_script(file_loc):
    global executing_script
    if not os.path.isfile(file_loc):
        print(f"No such file {file_loc} exists")
        return
    executing_script += 1
    try:
        with open(file_loc, 'r') as file:
            for line in file:
                line = line.strip()
                comment_index = line.find("#")
                if comment_index != -1:
                    line = line[0:comment_index].strip()
                if line == "":
                    continue # Skip blank lines
                print_script_command(line)
                cmd_data = cmd_parse(line)
                if cmd_data == None:
                    continue # If it fails to parse, don't do anything
                elif cmd_data["type"] == "QUIT":
                    print_command_complete()
                    break # End if we quit
                elif cmd_data["type"] == "RUN":
                    cmd_run_at_script(cmd_data["arg1"])
                else:
                    run_cmd(cmd_data)
                    print_command_complete()
    except Exception as e:
        print_command_info(f"Script {file_loc} failed to open.")
    finally:
        executing_script -= 1


## MAIN LOOP ETC.

## Warmup Text
print("Welcome to the Serial Port Terminal, type \"!HELP\" for a list of commands.")

try:
    run_loop = True
    if startup_script != "":
        cmd_run_at_script(startup_script)
    while run_loop:
        raw_input = input(input_txt)
        to_send = cmd_parse(raw_input)
        if to_send != None:
            # print(f"Would send the following Command: {to_send}")
            if to_send["type"] == "QUIT":
                run_loop = False
            elif to_send["type"] == "RUN":
                cmd_run_at_script(to_send["arg1"])
            else:
                run_cmd(to_send)
                print_command_complete()
        else:
            print_command_complete()
            pass
    port_cleanup()
except KeyboardInterrupt:
    port_cleanup()

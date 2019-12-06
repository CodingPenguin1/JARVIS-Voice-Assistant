#!/usr/bin/env python

import json
from random import randint
import re as reee
import socket
import subprocess
import traceback

ALLOW_EXEC = True
DEBUG = True
LOCALHOST = "127.0.0.1"
MESSAGE_END = "\n"
CONFIG_FILE = "commands.json"

# #############################################################################
# #####                         BEGIN BEST MATCH                          #####
# #############################################################################



def getBestMatch(prompt):
    # Find the best match from the list of commands
    bestMatch = "invalid"
    bestWeight = commands["invalid"]["weight"]
    args = []

    if DEBUG: print("Got command '{}', Starting with {}->{}".format(prompt, bestMatch, bestWeight))

    # First search through for exact matches
    for name, data in commands.items():

        if bestWeight >= data["weight"] and data["exact"].search(prompt):
            if DEBUG: print("{} is the new best".format(name))
            bestMatch = name
            bestWeight = data["weight"]
            args = data["exact"].search(prompt).groups()

    # If none were found, search through the fuzzy matches
    if bestMatch == "invalid":
        if DEBUG: print("Could not find an exact match. Looking for a fuzzy match")
        for name, data in commands.items():
            if bestWeight >= data["weight"] and data["fuzzy"].search(prompt):
                if DEBUG: print("{} is the new best".format(name))
                bestMatch = name
                bestWeight = data["weight"]
                args = data["fuzzy"].search(prompt).groups()

    match = commands[bestMatch]

    if DEBUG: print("Best we got was {}".format(bestMatch))

    return match, args



# #############################################################################
# #####                           HANDLE PROMPT                           #####
# #############################################################################



def handlePrompt(prompt, connection, address):
    # Find the best match from the list of commands
    command, args = getBestMatch(prompt)

    # Check to see that the IP hat requested the command is actually allowed to request the command
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    # TODO                THIS IS NOT SECURE! FIX!                TODO #
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #
    if (address[0] != LOCALHOST and not "allowRemote" in command.keys()) or \
            (address[0] != LOCALHOST and "allowRemote" in command.keys() and not command["allowRemote"]):
        print("Whoa doggy, that ain't good! Received {} from {}".format(prompt, address))
        errMessage = info["permissionDeniedMessages"][randint(0, len(info["permissionDeniedMessages"]) - 1)]
        connection.send((errMessage + MESSAGE_END).encode("utf-8"))
    
    # Else the command will be allowed to run
    else:
        runCommand(command, args, connection, address)



# #############################################################################
# #####                            LOAD CONFIG                            #####
# #############################################################################
# hi


def loadConfig():
    global info, commands, configVars
    print("Loading commands")
    with open(CONFIG_FILE, "r") as commandsFile:
        info = json.load(commandsFile)

    commands = info["commands"]

    configVars = {}

    for k, v in info.items():
        if type(v) in [int, str, bool]:
            configVars[k] = str(v)

    print(configVars)

    # Compile all the regular expressions to make things easier later
    for name, data in commands.items():
        data["exact"] = reee.compile(data["exact"], reee.IGNORECASE)
        data["fuzzy"] = reee.compile(data["fuzzy"], reee.IGNORECASE)
        if("returnParse" in data.keys()):
            data["returnParse"] = reee.compile(data["returnParse"], reee.IGNORECASE)

        # TODO Fill missing flags to default values?



# #############################################################################
# #####                           PARSE STRING                            #####
# #############################################################################



def parseString(message, args, returnVals=[""], newText=""):
    global configVars

    filteredArgs = list(filter(lambda x: x != None, args))
    filteredReturnVals = list(filter(lambda x: x != None, args))

    # First replace all arrays et all
    message = message.replace("{args}", " ".join(filteredArgs))
    message = message.replace("{return}", " ".join(filteredReturnVals))
    message = message.replace("{newText}", newText)

    print(message)

    for k, v in configVars.items():
        message = message.replace("{{{}}}".format(k), v)

    # Now do pretty much the most inefficient way of replacing indexes there is
    for i in range(len(args)):
        if args[i] != None:
            message = message.replace("{{args[{}]}}".format(i), args[i])
        else:
            message = message.replace("{{args[{}]}}".format(i), "None")

    for i in range(len(returnVals)):
        if returnVals[i] != None:
            message = message.replace("{{return[{}]}}".format(i), returnVals[i])
        else:
            message = message.replace("{{return[{}]}}".format(i), "None")

    return message



# #############################################################################
# #####                            RUN COMMAND                            #####
# #############################################################################



def runCommand(command, args, connection, address):
    connection.send(parseString(command["pre"] + MESSAGE_END, args).encode("utf-8"))

    subprocessArr = [command["command"]]

    for i in command["arguments"]:
        print(i)
        subprocessArr.append(parseString(i, args))

    print(subprocessArr)

    # If there is code given to be executed and execution is allowed, execute it now
    if ALLOW_EXEC and "exec" in command.keys():
        exec(command["exec"])

    # Check if the command should be detatched
    # Run the command detatched
    if command["detatch"]:
        if DEBUG: print("Running {} in the background".format(command["command"]))
        subprocess.Popen(subprocessArr)

    else:
        if DEBUG: print("Running {} in the foreground".format(command["command"]))
        
        # Run the command and get the results
        results = subprocess.run(subprocessArr, capture_output=True)

        if "returnParse" in commands.keys():
            returnData = commands["returnParse"].search(results.stdout.decode("utf-8")).groups()
        else:
            returnData = []

        # If we got a bad return code
        if results.returncode != 0:
            connection.send(parseString(info["clarificationMessage"] + command["clarification"]["say"] + MESSAGE_END, args, returnData).encode("utf-8"))

            newText = connection.recv(1024).decode("utf-8").rstrip().lstrip()
            reee.sub("[^\w ]", "", newText)

            handlePrompt(parseString(command["clarification"]["newPrompt"] + MESSAGE_END, args, returnData, newText), connection, address)

        # Return the success response
        else:
            connection.send(parseString(command["post"] + MESSAGE_END, args, returnData).encode("utf-8"))



# #############################################################################
# #####                            BEGIN MAIN                             #####
# #############################################################################



if __name__ == '__main__':

    # Load the configuration file
    loadConfig()

    print("Initializing server")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get the first open port after 22222
    port = 22222
    while True:
        try:
            sock.bind(('localhost', port))
            break
        except:
            port += 1

    

    sock.listen(1)

    print("{}! Listening on port {}".format(info["startupQuote"], port))

    subprocess.Popen(["python", "frontend.py", "--ip", LOCALHOST, "--port", str(port), "--config", CONFIG_FILE])

    while True:
        try:
            conn, addr = sock.accept()

            # Get the prompt that the user wants to run from the socket
            prompt = conn.recv(1024).decode("utf-8").rstrip().lstrip()
            reee.sub("[^\w ]", "", prompt)

            handlePrompt(prompt, conn, addr)
            conn.close()

        except Exception as e:
            print(traceback.format_exc())
            try:
                conn.send((info["errorMessage"] + MESSAGE_END).encode("utf-8"))
                conn.close()
            except:
                print("It's worse than that he's dead Jim")

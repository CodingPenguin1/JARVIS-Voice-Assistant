#!/usr/bin/env python

import json
import re as reee
import socket
import subprocess

if __name__ == '__main__':
    print("Loading commands")
    with open("commands.json", "r") as commandsFile:
        info = json.load(commandsFile)

    commands = info["commands"]

    # Compile all the regular expressions to make things easier later
    for name, data in commands.items():
        data["exact"] = reee.compile(data["exact"], reee.IGNORECASE)
        data["fuzzy"] = reee.compile(data["fuzzy"], reee.IGNORECASE)
        data["returnParse"] = reee.compile(data["returnParse"], reee.IGNORECASE)

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

    try:
        while True:
            conn, addr = sock.accept()
            print("This be from {}".format(addr))
            command = conn.recv(1024).decode("utf-8").rstrip().lstrip()

            # Find the best match from the list of commands
            bestMatch = "invalid"
            bestWeight = commands["invalid"]["weight"]
            args = []

            print("Got command '{}', Starting with {}->{}".format(command, bestMatch, bestWeight))

            # First search through for exact matches
            for name, data in commands.items():
                if bestWeight > data["weight"] and data["exact"].search(command):
                    print("{} is the new best".format(name))
                    bestMatch = name
                    bestWeight = data["weight"]
                    args = data["exact"].search(command)

            # If none were found, search through the fuzzy matches
            if bestMatch == "invalid":
                print("Could not find an exact match. Looking for a fuzzy match")
                for name, data in commands.items():
                    if bestWeight > data["weight"] and data["fuzzy"].search(command):
                        print("{} is the new best".format(name))
                        bestMatch = name
                        bestWeight = data["weight"]
                        args = data["fuzzy"].search(command)

            print("At this point we would run the command {} with arguments {}".format(bestMatch, args.groups()))
            subprocess.run(commands[bestMatch]["command"])

            conn.close()
    except Exception as e:
        print("Caught {}".format(e))
        sock.close()
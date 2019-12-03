JARVIS Voice Assistant

# Front end

The purpose of the front end is to listen for any voice commands and to generate vocal responses for those commands. The flow will be

1. Continually scan the microphone, waiting for someone to say the trigger word (`"name"` in the configuration json)
2. Once the trigger word is detected, open a connection to the back end and send the voice command for processing.
3. Wait for the back end to send a response, and convert it to speech.
4. If the connection to the back end is still open at this point, collect another voice command from the user and send it to the back end.
5. Repeat 4. as until the connection to the back end is no longer open.
6. Go back to 1.

# Back end

The purpose of the back end is to process and run any accepted voice commands and send any necessary responses back to the front end. The flow will be

1. Wait for a connection.
2. Once a connection is established, get a block of data from it.
3. Compare the data to the exact match regular expressions to see if there are any commands that match it. If there is more than one matching command, the one with the lowest weight is given priority.
4. If there are no exact matches, compare the data to the fuzzy match regular expressions. The same rules for multiple matches and priority apply.
5. If still no command was found, the command named "invalid" will be run.
6. Send the data associated with the `pre` key in the command dictionary.
7. Execute any code in the `exec` key, if execution is allowed
8. Start the program in `command` as a subprocess.
9. If the subprocess returned an error, get more data from the connection, and run that command.
10. If the command didn't return an error, send the data in `post`.
11. Close the connection
12. Go back to 1.

New rough design plan:
the controller reads from a json file with a number of entries. Each entry has the following fields:
- A unique name for the command
- A regex for the exact match for the command
- A regex for a close match for the command 
- A "weight" for the command, for if two commands both match an input
- An array of possible responses for the command
- The program to be run when the command is invoked
- A secondary clarification command to be run if the program returned failure
- Format for a response to be returned to the speaker before the command is run
- Format for a response to be returned to the speaker after the command is run

Command line arguments will be taken from capture groups in the regex, and the clarification commands should have access to any previous capture groups

Should also be able to read the output of the command it calls and base a response off that. If I ask "What's your IP" it should run `ip a | grep ... ` and respond with "My IP is $IP"
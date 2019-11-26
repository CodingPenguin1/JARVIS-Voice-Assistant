JARVIS Voice Assistant

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

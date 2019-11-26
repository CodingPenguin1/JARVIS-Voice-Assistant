from os import system


class Command:
    def __init__(self, name, keyphrase, executable, response):
        self.name = name
        self.keyphrase = keyphrase
        self.executable = executable
        self.response = response

    def execute(self):
        system(self.executable)

    def __str__(self):
        rtn = 'Name: ' + self.name + '\n'
        rtn += 'Keyphrase: ' + self.keyphrase + '\n'
        rtn += 'Command: ' + self.executable + '\n'
        rtn += 'Response: ' + self.response
        return rtn

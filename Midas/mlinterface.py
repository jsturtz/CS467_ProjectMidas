class Mlinterface():
    
    # if we want to have a constructor
    # def __init__(self):
        
    # any initialization code can go here
    def start(self):
        print("Interface started...")
    
    # any closing statements go here
    def close(self):
        print("Interface closed...")

    # responsible for asking user to choose among options
    # options is a list of strings
    def choose(self, options):
        print(message)

    # responsible for printing message to screen
    # message is a string
    def print_error(self, message):
        print(message)
    
    # responsible for asking user for filename
    # extensions is a list of extensions formatted like ["csv", "pdf" ... ]
    def get_file_name(self, extensions):
        return "someFileName.txt"

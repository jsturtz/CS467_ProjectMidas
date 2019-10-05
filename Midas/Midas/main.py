# main program here

import interface
import mlalgorithms
import preprocessing
import database
import tools

# specify here which commands will be available to the user
# If you want to add a command to the interface options, 
# just add a function below with a corresponding entry in this
# commands dictionary
commands = 
{
    "Execute Model": execute_model, 
    "Train Model": train_model,
    "Quit": lambda: None
}


def main():
    
    # initialize interface
    interface.init_interface()

    while True:
        # prompt user to choose among the commands
        choice = interface.choose(list(commands.keys()))

        # do the action requested by invoking functions below
        result = commands[choice]

        # user has requested to exit
        if result is None: break
    
    # give any farewell messages and such
    interface.close_interface()

main()



"""
Each of these functions corresponds to a single "command" the user of our system might want to perform
"""

def execute_model():
    
    # check that model exists
    model = database.get_model()
    if not model:
        interface.print_error("No model has yet been trained")
        return

    # get filename from customer
    if f = interface.get_file_name([".CSV"]) == None return None
    
    if tools.file_exists(f):

        if tools.raw_data_is_valid(f):

            mlalgorithms.execute(f):

        else:
            interface.print_error("Raw data file {0} not formatted correctly".format(f))
    else:
        interface.print_error("File {0} does not exist".format(f))

def train_model():
    
    # get filename from customer
    if f = interface.get_file_name() == None return None

    # validate date in filename
    raw_data = tools.get_data(f)
    if not tools.raw_data_is_valid(raw_data):
        interface.print_error("Raw data file {0} not formatted correctly".format(f))
        return

    # derive new features, handle missing data, and clean
    clean_data = preprocessing.format_data(raw_data)

    # store new data into database?
    database.store_clean_data(clean_data)

    # run model
    model = mlalgorithms.logistic_regression(new_data)

    # store model in database
    database.store_model(model)

    # display performance?
    interface.display_performance(model)


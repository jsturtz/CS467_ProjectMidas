## Pipeline File Structure

- Midas/
    - controller.py
    - ML_Task/
        - main.py
        - utils/
            - \_\_init\_\_.py
            - ml_task_utils.py
        - data/
            - sample_data.csv
            
## tasks

Machine Learning Pipeline Tasks (referred to generically as "tasks") are contained in subdirectories. The only exception is the `Databases` directory, which contains the `make` script for spinning up the necessary databases.

Each task directory contains as `main.py` starting point, acting as the central intake for the task. Tasks that require access to a local datastore (such as data_import) have a `/data` subdirectory that the container can access, imported as `./data` in the container.

Each task is also self-contained, meaning that the task will only have resources available in the task directory. Any utility methods will need to be contained the task directory.


## controller.py

The controller script serves as a method to interact with the base infrastructure.

By providing the directory name, the task contained in `main.py` can be initiated by the controller. 

Upon completion, the `main` function of `controller.py`  will return status codes:
- 0 to designate completion of task without errors
- 1 to designate error in task
- any other code designates an error with the container

Cmdline Syntax: `python controller.py <dir_name> <args>`
Python syntax: 
1. `from controller import main`
2. `main(dir_name, args)`
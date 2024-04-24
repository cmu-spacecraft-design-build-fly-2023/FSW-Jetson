import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flight.logger import Logger
from flight.message_id import *
from flight.task_map import ID_TASK_MAPPING
from flight.command import Task

import threading

from flight.payload import Payload 



def add_command(payload, command_id, priority=50):
    """
    Add a command based on the command ID
    """
    try:
        task_fct = ID_TASK_MAPPING[command_id]
    except KeyError:
        raise KeyError(f"Command ID {command_id} not found")

    try:
        task = Task(payload, command_id, task_fct, None, priority=priority)
        payload.command_queue.add_task(task)
    except Exception as e:
        raise e



if __name__ == "__main__":

    import threading
    import time 

    payload = Payload()

    # Create a new thread for running the payload
    payload_thread = threading.Thread(target=payload.run)
    payload_thread.daemon = True
    payload_thread.start()

    print("Payload is running in a separate thread. Access the REPL below.")

    # ADD COMMANDS PRIOR TO THE QUEUE HERE IF YOU WANT
    # e.g. add_command(payload, DEBUG_HELLO)
    add_command(payload, DEBUG_HELLO)   
    add_command(payload, REQUEST_PAYLOAD_STATE)
    add_command(payload,CAPTURE_AND_SEND_IMAGE)
    add_command(payload,REQUEST_LAST_IMAGE)
    add_command(payload,TURN_OFF_CAMERAS)
    add_command(payload,TURN_ON_CAMERAS)
    
    # add_command(payload, RUN_ML_PIPELINE)
    # add_command(payload, REQUEST_LANDMARKED_IMAGE)


    start_time = time.time()

    # REPL to execute user commands
    while True:
        try:
            user_input = input(">>> ")
            exec(user_input, globals(), locals())

            # YOUR SPACE

            # If you want to send commands later, use the add_command(command_id) function within an if statement with time 
            # e.g. add_command(payload, DEBUG_HELLO)
            
            


            
        except KeyboardInterrupt:
            print("\nExiting REPL...")
            break
        except Exception as e:
            print(f"Error: {e}")
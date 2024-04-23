


from flight.message_id import *
from flight.task_map import ID_TASK_MAPPING

import threading

from flight.payload import Payload as PAYLOAD



def execute_command(payload, command_id):
    """
    Execute a command based on the command ID
    """
    try:
        task = ID_TASK_MAPPING[command_id]
        payload.execute_task(task)
    except KeyError:
        print(f"Command ID {command_id} not found")





if __name__ == "__main__":

    from flight.task_map import ID_TASK_MAPPING

    import threading

    payload = PAYLOAD.Payload()

    # Create a new thread for running the payload
    payload_thread = threading.Thread(target=payload.run)
    payload_thread.daemon = True
    payload_thread.start()

    print("Payload is running in a separate thread. Access the REPL below.")

    # REPL to execute user commands
    while True:
        try:
            user_input = input(">>> ")
            exec(user_input, globals(), locals())


            










            
        except KeyboardInterrupt:
            print("\nExiting REPL...")
            break
        except Exception as e:
            print(f"Error: {e}")
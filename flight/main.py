"""
Main Entry Point for the flight software

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

import payload as PAYLOAD


if __name__ == "__main__":

    import flight.message_id as msg
    from flight.task_map import ID_TASK_MAPPING

    import threading

    payload = PAYLOAD.Payload()

    # Creating dummy tasks for demonstration
    # self.DEBUG_tasks()

    # Create a new thread for running the payload
    payload_thread = threading.Thread(target=payload.run)
    payload_thread.daemon = True
    payload_thread.start()

    print("Payload is running in a separate thread. Access the REPL below.")

    # REPL to execute user commands
    while True:
        try:
            user_input = input(">>> ")
            # Execute user input in the context of the globals, including 'payload'
            exec(user_input, globals(), locals())
        except KeyboardInterrupt:
            print("\nExiting REPL...")
            break
        except Exception as e:
            print(f"Error: {e}")

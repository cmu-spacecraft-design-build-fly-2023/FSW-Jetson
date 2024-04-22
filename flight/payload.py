"""
Payload Task Manager

Description: TODO

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""
import time
import threading 

from enum import Enum, unique
from command import CommandQueue, Task
import message as msg
from task_map import ID_TASK_MAPPING
from flight.vision.camera.camera import CameraManager


# PAYLOAD STATES
@unique
class PAYLOAD_STATE(Enum):
    STARTUP = 0x00
    NOMINAL = 0x01
    LOW_POWER = 0x02
    SAFE_MODE = 0x03
    CRITICAL = 0x04



class Payload:

    def __init__(self):
        self._state = PAYLOAD_STATE.STARTUP
        self._command_queue = CommandQueue()
        # self._communication = None
        self._camera_manager = None
        self._threads = []


    @property
    def state(self):
        return self._state
    
    @property
    def command_queue(self):
        return self._command_queue
    

    @property
    def communication(self):
        return self._communication


    def run(self, log_level=0):

        # Logger.configure(log_level)
        # print("Logger configured to level: ", log_level)
        print("Starting Payload Task Manager...")


        self.run_startup_health_procedure()
        self.retrieve_internal_states()
        

        self.launch_camera()
        self.launch_command_queue()
        self.launch_UART_communication()



        ## Dummy stuff for test
        import random
        def print_message(p):
            print(p)
            return "Message printed successfully."

        def throw_random_error(payload):
            if random.random() < 0.7:
                raise Exception("Random error occurred!")
            else:
                print("No error occurred.")


        task1 = Task(msg.DEBUG_HELLO, ID_TASK_MAPPING[msg.DEBUG_HELLO], None, 50)
        task2 = Task(msg.DEBUG_RANDOM_ERROR, ID_TASK_MAPPING[msg.DEBUG_RANDOM_ERROR], None, 10)
        task3 = Task(msg.DEBUG_GOODBYE, ID_TASK_MAPPING[msg.DEBUG_GOODBYE], None, 75)



        self.command_queue.add_task(task1)
        self.command_queue.add_task(task2)
        self.command_queue.add_task(task3)

        self.command_queue.print_all_tasks()




        try:
            while True:
                self.process_next_task()
                pass
                # TODO
        except KeyboardInterrupt:
            print("Shutting down Payload Task Manager...")
            self.cleanup()


    def process_next_task(self):
        task = self._command_queue.get_next_task()
        if task:
            # Execute the task
            task.execute()
        else:
            print("No task to process.")
            time.sleep(5)
            pass

        

    def run_startup_health_procedure(self):
        print("Running startup health checks...")
        # Check status, ...

    def retrieve_internal_states(self):
        print("Retrieving internal states...")
        #  Load configurations, last known states


    def launch_camera(self):
        print("Launching camera manager...")
        """camera_thread = threading.Thread(target=self._camera_manager.run)
        camera_thread.start()
        self._threads.append(camera_thread)"""
       

    def launch_command_queue(self):
        pass

    def launch_UART_communication(self):
        # Start UART communication state machne on its own thread
        print("Initializing UART communication...")
        # TODO
        pass


    def cleanup(self):
        for thread in self._threads:
            thread.join()
        print("All components cleanly shutdown.")
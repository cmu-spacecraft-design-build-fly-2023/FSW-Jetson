"""
Payload Task Manager

Description: This module implements the high-level Payload Task Manager, which is responsible for managing tasks and states of the payload system. 
It runs the main control loop for the payload system and is responsible for:
- Initializing the system, running startup health checks, and retrieving internal states
- Managing and switching between different payload states
- Handling the camera management and UART communication components
- Adding and processing tasks from the command queue
- ...

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

import time
import threading

from enum import Enum, unique
from flight.command import CommandQueue, Task
import flight.message_id as msg
from flight.task_map import ID_TASK_MAPPING
from flight.vision.camera.camera import CameraManager



# PAYLOAD STATES
@unique
class PAYLOAD_STATE(Enum):
    STARTUP = 0x00
    NOMINAL = 0x01
    LOW_POWER = 0x02
    SAFE_MODE = 0x03
    CRITICAL = 0x04
    IDLE = 0x05


class Payload:

    def __init__(self):
        self._state = PAYLOAD_STATE.STARTUP
        self._command_queue = CommandQueue()
        # self._communication = None
        self._camera_manager = None
        self._threads = []

        self.current_task_thread = None  # This will hold the current task's thread
        self._idle_count = 0  # Counter before switching to IDLE state

    @property
    def state(self):
        return self._state

    @property
    def command_queue(self):
        return self._command_queue
    
    @property
    def send_queue(self):
        return self._send_queue

    @property
    def communication(self):
        return self._communication

    def run(self, log_level=0):

        # Logger.configure(log_level)
        # print("Logger configured to level: ", log_level)
        print("Starting Payload Task Manager...")

        self.initialize()

        """
        self.launch_camera()
        self.launch_UART_communication()"""

        # Creating dummy tasks for demonstration
        self.DEBUG_tasks()

        try:
            while True:

                print(f"[INFO] Payload State: {self.state.name}")

                if self.state == PAYLOAD_STATE.IDLE:
                    # print("Payload is in IDLE state. Checking for tasks every 10 seconds.")
                    time.sleep(10)

                    if not self.command_queue.is_empty():
                        self._state = PAYLOAD_STATE.NOMINAL
                    else:
                        continue

                if self.state == PAYLOAD_STATE.NOMINAL:
                    self.process_next_task()
                    self.command_queue.print_all_tasks()
                    time.sleep(1)

                # TODO
        except KeyboardInterrupt:
            print("Shutting down Payload Task Manager...")
            self.cleanup()

    def process_next_task(self):
        if self.current_task_thread and self.current_task_thread.is_alive():
            return  # If the current task is still running, return immediately

        task = self._command_queue.get_next_task()

        if task:
            self.current_task_thread = threading.Thread(target=task.execute)
            self.current_task_thread.start()
        else:
            self._idle_count += 1
            if self._idle_count < 1:
                print("No task to process.")
            if self._idle_count >= 5:
                self._state = PAYLOAD_STATE.IDLE
                print("Payload is in IDLE state. Checking for tasks every 10 seconds.")
                self._idle_count = 0

    def DEBUG_tasks(self):
        # For debugging purposes
        task1 = Task(msg.DEBUG_HELLO, ID_TASK_MAPPING[msg.DEBUG_HELLO], None, 50)
        task2 = Task(msg.DEBUG_RANDOM_ERROR, ID_TASK_MAPPING[msg.DEBUG_RANDOM_ERROR], None, 10)
        task3 = Task(msg.DEBUG_GOODBYE, ID_TASK_MAPPING[msg.DEBUG_GOODBYE], None, 75)
        task4 = Task(msg.DEBUG_NUMBER, ID_TASK_MAPPING[msg.DEBUG_NUMBER], 32, 75)

        self.command_queue.add_task(task1)
        self.command_queue.add_task(task2)
        self.command_queue.add_task(task3)
        self.command_queue.add_task(task4)

    def initialize(self):
        self.run_startup_health_procedure()
        self.retrieve_internal_states()

        # Switch to nominal state
        self._state = PAYLOAD_STATE.NOMINAL

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

    def launch_UART_communication(self):
        # Start UART communication state machne on its own thread
        print("Initializing UART communication...")
        # TODO
        pass

    def cleanup(self):
        for thread in self._threads:
            thread.join()
        print("All components cleanly shutdown.")

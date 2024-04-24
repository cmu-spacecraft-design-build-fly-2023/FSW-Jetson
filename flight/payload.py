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
from flight.command import CommandQueue, Task, TX_Queue

import flight.message_id as msg
from flight.task_map import ID_TASK_MAPPING, get_task_from_id, ID_exists
from flight.vision.camera import CameraManager

from flight.communication.uart import UARTComm

from flight.monitoring import JetsonMetrics

from flight.logger import Logger


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
        self._tx_queue = TX_Queue()
        self._communication = UARTComm()
        self.current_task_thread = None
        self._camera_manager = CameraManager([0, 2, 4, 6, 8, 10])
        self._threads = []
        self._idle_count = 0  # Counter before switching to IDLE state

        self._com_event_stop = threading.Event()

    @property
    def state(self):
        return self._state

    @property
    def command_queue(self):
        return self._command_queue

    @property
    def tx_queue(self):
        return self._tx_queue

    @property
    def camera_manager(self):
        return self._camera_manager

    @property
    def communication(self):
        return self._communication

    def run(self, log_level=0):

        # Logger.configure(log_level)
        # print("Logger configured to level: ", log_level)
        Logger.log("INFO", "Starting Payload Task Manager...")

        self.initialize()

        self.launch_camera()
        self.launch_UART_communication()

        try:
            while True:

                Logger.log("INFO", f"Payload State: {self.state.name}")

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
            Logger.log("INFO", "Shutting down Payload Task Manager...")
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
                Logger.log("INFO", "No task to process.")
            if self._idle_count >= 5:
                self._state = PAYLOAD_STATE.IDLE
                Logger.log("INFO", "Payload is in IDLE state. Checking for tasks every 10 seconds.")
                self._idle_count = 0

    def DEBUG_tasks(self):
        # For debugging purposes
        task1 = Task(self, msg.DEBUG_HELLO, ID_TASK_MAPPING[msg.DEBUG_HELLO], None, 50)
        task2 = Task(
            self, msg.DEBUG_RANDOM_ERROR, ID_TASK_MAPPING[msg.DEBUG_RANDOM_ERROR], None, 10
        )
        task3 = Task(self, msg.DEBUG_GOODBYE, ID_TASK_MAPPING[msg.DEBUG_GOODBYE], None, 75)
        task4 = Task(self, msg.DEBUG_NUMBER, ID_TASK_MAPPING[msg.DEBUG_NUMBER], 32, 75)

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
        Logger.log("INFO", "Running startup health checks...")
        # Check status, ...

    def retrieve_internal_states(self):
        Logger.log("INFO", "Retrieving internal states...")
        #  Load configurations, last known states

    def launch_camera(self):
        Logger.log("INFO", "Launching camera manager...")
        camera_thread = threading.Thread(target=self._camera_manager.run_live)
        camera_thread.start()
        self._threads.append(camera_thread)

    def stop_camera_operations(self):
        Logger.log("INFO", "Stopping camera operations...")
        self._camera_manager.stop_live()

    def launch_UART_communication(self):
        # Start UART communication state machne on its own thread
        Logger.log("INFO", "Initializing UART communication...")
        uart_thread = threading.Thread(target=self.run_UART_loop)
        uart_thread.start()
        self._threads.append(uart_thread)

    def run_UART_loop(self, period=10):
        """
        Main loop for the UART communication.
        """
        while not self._com_event_stop.is_set():

            ## TX
            if not self.tx_queue.is_empty():
                msg = self.tx_queue.get_next()
                if msg != None:
                    self.communication.send_message(msg)

            ## RX
            if self.communication.available() > 0:
                msg_type, msg = self.communication.receive_message()

                if ID_exists(msg_type):
                    # Add a command based on the command ID
                    task_fct = get_task_from_id(msg_type)
                    try:
                        task = Task(self, msg_type, task_fct, None)
                        self.command_queue.put(task)
                    except Exception as e:
                        Logger.log("ERROR", f"Failed to create task from message. {e}")
                        raise e

            time.sleep(period)

        self.communication.stop()

    def stop_UART_communication(self):
        Logger.log("INFO", "Stopping UART communication...")
        self._com_event_stop.set()

    def cleanup(self):
        for thread in self._threads:
            thread.join()
        Logger.log("INFO", "All components cleanly shutdown.")

    def monitor(self):
        metrics = None
        Logger.log("INFO", "Retrieving system metrics...")
        with JetsonMetrics() as metrics:
            metrics = metrics.get_all_metrics()
        Logger.log(
            "INFO",
            f"RAM Usage (%): {metrics['RAM Usage (%)']} | Disk Storage Usage (%): {metrics['Disk Storage Usage (%)']} | CPU Temperature (°C): {metrics['CPU Temperature (°C)']} | GPU Temperature (°C): {metrics['GPU Temperature (°C)']}",
        )
        return metrics

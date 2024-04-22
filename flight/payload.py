"""
Payload Task Manager

Description: TODO

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

from enum import Enum, unique

# PAYLOAD STATES
@unique
class PAYLOAD_STATE(Enum):
    STARTUP = 0x00
    NOMINAL = 0x01
    LOW_POWER = 0x02
    SAFE_MODE = 0x03
    CRITICAL = 0x04



class PayloadManager:

    def __init__(self):
        self.mode = PAYLOAD_STATE.STARTUP

    def run_debug(self):
        pass

    def run(self):

        print("Starting Payload Task Manager...")

        self.run_startup_health_procedure()
        self.retrieve_internal_states()

        self.launch_logger()

        self.launch_camera()

        self.launch_command_queue()

        self.launch_UART_communication()

    def run_startup_health_procedure(self):
        pass

    def retrieve_internal_states(self):
        pass

    def launch_logger(self):
        pass

    def launch_camera(self):
        # Start Camera Manager interface on its own thread
        pass

    def launch_command_queue(self):
        pass

    def launch_UART_communication(self):
        # Start UART communication state machne on its own thread
        pass

"""
UART Communication Module

Description: This file defines the UARTComm class, which is responsible for sending and receiving messages over UART.

Author(s): Sachit Goyal, Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

import time
import serial

import threading

from command import Task

import flight.message as mg
from flight.message import Message
from flight.logger import Logger

MAX_RETRIES = 3
TIMEOUT = 100
BAUDRATE = 57600


class UARTComm:

    def __init__(self, port="/dev/ttyTHS0", baudrate=BAUDRATE):
        try:
            self.uart = serial.Serial(port, baudrate=baudrate)
            self.uart.reset_input_buffer()
            self.uart.reset_output_buffer()
        except serial.SerialException as e:
            Logger.log("Error", "Failed to initialize UART communication. {e}")
            raise e  # Temp

        self.port = port
        self.baudrate = baudrate

        self._event_stop = threading.Event()

    def send_message(self, message) -> bool:
        """
        Sends a message over UART.

        Args:
            message: The message to be sent.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        done = False
        current_seq = 0
        total_packets = message.num_packets

        while not done:

            Logger.log("Info", f"Sending packet number {current_seq} of {total_packets}")
            msg = None
            if current_seq == 0:
                msg = message.create_header()
            else:
                msg = message.create_packet(current_seq)

            # self.uart.write(msg)
            Logger.log("Info", f"Sent packet number {current_seq} of {total_packets}")

            time_s = 0
            while self.uart.in_waiting < mg.PKT_METADATA_SIZE:
                if (time_s >= TIMEOUT):
                    return False
                time.sleep(.01)
                time_s += 1
                continue

            #response = self.uart.read(message.PKT_METADATA_SIZE)
            response = bytearray([0x01, 0x02, 0x03, 0x04])
            Logger.log("Info", f"Received response {response}")
            (seq_num, packet_type, _) = Message.parse_packet_meta(response)
            Logger.log("Info", f"Received response {seq_num} {packet_type}")
            if packet_type == mg.PKT_TYPE_ACK:
                current_seq = seq_num + 1
                if current_seq == total_packets + 1:
                    done = True
            elif packet_type == mg.PKT_TYPE_RESET:
                current_seq = 0
            else:
                current_seq = 0

        return True

    def receive_message(self):
        """
        Receives a message over UART.

        Returns:
            list: The received message.
        """
        expected_seq_num = 0
        retries = 0
        reset = False

        time = 0
        while self.uart.in_waiting < message.HEADER_PKT_SIZE:
            if time > TIMEOUT:
                self.uart.reset_input_buffer()
                return False
            time += 0.01
            time.sleep(0.01)
            continue
    
        header = self.uart.read(mg.PACKET_SIZE)
        (seq_num, packet_type, payload_size) = Message.parse_packet_meta(header)
        if packet_type != mg.PKT_TYPE_HEADER:
            # clear uart buffer
            self.uart.reset_input_buffer()
            raise RuntimeError("Invalid header")

        # do something with message type
        (message_type, num_packets) = Message.parse_header_payload(
            header[mg.PKT_METADATA_SIZE :]
        )
        # TODO do something if not correct message type 
        self.uart.write(Message.create_ack(seq_num))

        expected_seq_num = seq_num + 1
        message = []

        while expected_seq_num != num_packets + 1:
            while self.uart.in_waiting < message.PACKET_SIZE:
                continue
            packet = self.uart.read(message.PACKET_SIZE)
            (seq_num, packet_type, payload_size) = Message.parse_packet_meta(packet)
            if packet_type == mg.PKT_TYPE_DATA and seq_num == expected_seq_num:
                expected_seq_num += 1
                retries = 0
            else:
                if retries >= MAX_RETRIES:
                    raise RuntimeError("Unable to receive message")
                # clear uart buffer
                retries += 1
            self.uart.write(Message.create_ack(expected_seq_num - 1))
            message += packet[mg.PKT_METADATA_SIZE :][:payload_size]

            # TODO handle case with no success

        return message

    def run(self, payload_rx_queue, payload_tx_queue, period=10):
        """
        Main loop for the UART communication module.

        Args:
            payload_rx_queue (Queue): The queue to receive messages from to be converted to Tasks
            payload_tx_queue (Queue): The queue to send messages to.
        """
        while not self._event_stop.is_set():

            if not payload_tx_queue.is_empty():
                msg = payload_tx_queue.get()
                self.send_message(msg)

            if self.uart.in_waiting > 0:
                msg = self.receive_message()
                payload_rx_queue.put(msg)
                # TODO find message type       
                # Create corresponding task 
                # Put in the queue 

            time.sleep(period)

        self.uart.close()


    def stop(self):
        """
        Stops the UART communication module.
        """
        self._event_stop.set()
        #self.uart.close()



if __name__ == "__main__":

    from message_id import *
    import struct 
    ff = "<bbbb"

    uart = UARTComm("/dev/ttyACM0")
    # uart.run()
    dd = [0x01, 0x02, 0x03, 0x04]
    msg = Message(TRANSMIT_DIAGNOSTIC_DATA, struct.pack(ff, *dd))
    uart.send_message(msg)


"""
UART Packetization

Description: This file defines the Packet class and related functions for UART packetization.

Author: Sachit Goyal, Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

from struct import pack, unpack
from typing import List, Tuple

# Constants for packet types and sizes
PKT_TYPE_HEADER = 0x00
PKT_TYPE_DATA = 0x01
PKT_TYPE_ACK = 0x02
PKT_TYPE_RESET = 0x03
PACKET_SIZE = 64
PKT_METADATA_SIZE = 4
PAYLOAD_PER_PACKET = PACKET_SIZE - PKT_METADATA_SIZE
HEADER_PAYLOAD_SIZE = 4
HEADER_PKT_SIZE = HEADER_PAYLOAD_SIZE + PKT_METADATA_SIZE
MAX_PACKETS = 0xFFFF


class Packet:
    def __init__(self, message_type, data):
        """
        Initializes a Packet object.

        Args:
            message_type (int): The type of the message.
            data (bytes): The data to be sent in the packet.

        Raises:
            ValueError: If the message type is out of range or the data is too large to send.
        """
        self.message_type: int = message_type
        self.data: bytes = data
        data_len: int = len(self.data)
        if data_len % PAYLOAD_PER_PACKET != 0:
            self.data += bytearray(PAYLOAD_PER_PACKET - (data_len % PAYLOAD_PER_PACKET))
        self.data_len: int = len(self.data)
        self.num_packets: int = self.data_len // PAYLOAD_PER_PACKET
        if self.message_type > 0xFF or self.message_type < 0x00:
            raise ValueError("Message type out of range")
        if self.num_packets > MAX_PACKETS:
            raise ValueError("Data too large to send")
        self.packets: List[bytes] = [
            self.data[i * PAYLOAD_PER_PACKET : (i + 1) * PAYLOAD_PER_PACKET]
            for i in range(self.num_packets)
        ]

    def create_header(self) -> bytes:
        """
        Creates the header packet.

        Returns:
            bytes: The header packet data.
        """
        data: bytes = pack(
            "@HBBBH",
            0,
            PKT_TYPE_HEADER,
            HEADER_PAYLOAD_SIZE,
            self.message_type,
            self.num_packets,
        )
        return data

    def create_packet(self, packet_seq: int) -> bytes:
        """
        Creates a data packet with the given sequence number.

        Args:
            packet_seq (int): The sequence number of the data packet.

        Returns:
            bytes: The data packet data.

        Raises:
            ValueError: If the packet sequence number is out of range.
        """
        if packet_seq > self.num_packets or packet_seq <= 0:
            raise ValueError("Data Packet number out of range")
        if packet_seq == self.num_packets:
            packet_payload_size: int = self.data_len % PAYLOAD_PER_PACKET
            if packet_payload_size == 0:
                packet_payload_size = PAYLOAD_PER_PACKET
        else:
            packet_payload_size = PAYLOAD_PER_PACKET
        metadata: bytes = pack("@HBB", packet_seq, PKT_TYPE_DATA, packet_payload_size)
        current_packet: bytes = self.packets[packet_seq - 1][:packet_payload_size]
        return metadata + current_packet

    @staticmethod
    def create_ack(packet_seq: int) -> bytes:
        """
        Creates an acknowledgment packet with the given sequence number.

        Args:
            packet_seq (int): The sequence number of the packet to acknowledge.

        Returns:
            bytes: The acknowledgment packet data.

        Raises:
            ValueError: If the packet sequence number is out of range.
        """
        if packet_seq > MAX_PACKETS or packet_seq < 0:
            raise ValueError("Packet number out of range")
        return pack("@HBB", packet_seq, PKT_TYPE_ACK, 0x00)

    @staticmethod
    def create_reset() -> bytes:
        """
        Creates a reset packet.

        Returns:
            bytes: The reset packet data.
        """
        return pack("@HBB", 0x00, PKT_TYPE_RESET, 0x00)

    @staticmethod
    def parse_packet_meta(packet: bytes) -> Tuple[int, int, int]:
        """
        Parses the metadata of a packet.

        Args:
            packet (bytes): The packet data.

        Returns:
            tuple: A tuple containing the sequence number, packet type, and payload size.

        Raises:
            ValueError: If the packet format is invalid.
        """
        metadata: bytes = packet[:PKT_METADATA_SIZE]
        try:
            seq_num, packet_type, payload_size = unpack("@HBB", metadata)
        except:
            raise ValueError("Invalid packet format")
        return seq_num, packet_type, payload_size

    @staticmethod
    def parse_header_payload(header_payload: bytes) -> Tuple[int, int]:
        """
        Parses the header payload.

        Args:
            header_payload (bytes): The header payload data.

        Returns:
            tuple: A tuple containing the message type and number of packets.

        Raises:
            ValueError: If the packet format is invalid.
        """
        try:
            message_type, num_packets = unpack("@BH", header_payload)
        except:
            raise ValueError("Invalid packet format")
        return message_type, num_packets

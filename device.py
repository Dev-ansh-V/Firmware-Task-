import threading
import time
from utils import build_packet, extract_packets, TYPE_DATA, TYPE_ACK, TYPE_NACK

class Device:
    
    def __init__(self, name: str, channel, direction_send: str):
        self.name          = name
        self.channel       = channel
        self.dir_send      = direction_send            # 'A→B' or 'B→A'
        self.dir_recv      = 'B→A' if direction_send == 'A→B' else 'A→B'
        self.send_seq      = 0     # Outgoing sequence number (0-255, wraps)
        self.recv_expected = 0     # Next expected incoming sequence number
        self.recv_buffer   = b''   # Raw bytes accumulator
        self.inbox         = []    # Delivered messages

    def send(self, message: str):
        
        payload = message.encode('utf-8')
        pkt = build_packet(self.send_seq, TYPE_DATA, payload)
        print(f"[{self.name}] Sending seq={self.send_seq}: '{message}'")
        self.channel.send(pkt, self.dir_send)
        self.send_seq = (self.send_seq + 1) % 256
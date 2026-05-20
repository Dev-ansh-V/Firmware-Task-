import threading
import time
import queue
from utils import build_packet, extract_packets, TYPE_DATA, TYPE_ACK, TYPE_NACK

class Device:
   
    def __init__(self, name: str, channel, direction_send: str):
        self.name          = name
        self.channel       = channel
        self.dir_send      = direction_send
        self.dir_recv      = 'B→A' if direction_send == 'A→B' else 'A→B'
        self.send_seq      = 0
        self.recv_expected = 0
        self.recv_buffer   = b''
        self.inbox         = []
        self._lock         = threading.Lock()
        self._running      = True
        # Start background receiver thread
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def send(self, message: str):
       
        payload = message.encode('utf-8')
        pkt = build_packet(self.send_seq, TYPE_DATA, payload)
        print(f"[{self.name}] Sending seq={self.send_seq}: '{message}'")
        self.channel.send(pkt, self.dir_send)
        self.send_seq = (self.send_seq + 1) % 256

    def _receive_loop(self):
       
        recv_queue = self.channel.a_to_b if self.dir_recv == 'A→B' else self.channel.b_to_a
        while self._running:
            try:
                chunk = recv_queue.get(timeout=0.1)
                with self._lock:
                    self.recv_buffer += chunk
                    packets, self.recv_buffer = extract_packets(self.recv_buffer)
                    for pkt in packets:
                        self._handle_packet(pkt)
            except queue.Empty:
                continue

    def _handle_packet(self, pkt: dict):
       
        seq   = pkt['seq']
        ptype = pkt['type']

        if ptype == TYPE_DATA:
            if seq == self.recv_expected:
                msg = pkt['payload'].decode('utf-8', errors='replace')
                print(f"[{self.name}] Received seq={seq}: '{msg}'")
                self.inbox.append(msg)
                self.recv_expected = (self.recv_expected + 1) % 256
                ack_pkt = build_packet(seq, TYPE_ACK, b'')
                self.channel.send(ack_pkt, self.dir_recv)
            else:
                print(f"[{self.name}] Duplicate/OOO seq={seq}, expected={self.recv_expected}")
                ack_pkt = build_packet(seq, TYPE_ACK, b'')
                self.channel.send(ack_pkt, self.dir_recv)

        elif ptype == TYPE_ACK:
            self._last_ack = seq

        elif ptype == TYPE_NACK:
            self._last_nack = seq
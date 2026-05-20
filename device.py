import threading
import time
import queue
from utils import build_packet, extract_packets, TYPE_DATA, TYPE_ACK, TYPE_NACK

class Device:
    
    TIMEOUT   = 1.5   
    MAX_RETRY = 5     

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
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def send(self, message: str):
        
        payload = message.encode('utf-8')
        retries = 0
        acked   = False

        while not acked and retries < self.MAX_RETRY:
            pkt = build_packet(self.send_seq, TYPE_DATA, payload)
            print(f"[{self.name}] Sending seq={self.send_seq}: '{message}' (attempt {retries+1})")
            self.channel.send(pkt, self.dir_send)

            deadline = time.time() + self.TIMEOUT
            while time.time() < deadline:
                ack = self._check_ack(self.send_seq)
                if ack == 'ACK':
                    acked = True
                    break
                elif ack == 'NACK':
                    break  
                time.sleep(0.05)

            retries += 1

        if acked:
            print(f"[{self.name}] ACK received for seq={self.send_seq}")
            self.send_seq = (self.send_seq + 1) % 256
        else:
            print(f"[{self.name}] FAILED to deliver '{message}' after {self.MAX_RETRY} retries")

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
                print(f"[{self.name}] Received new msg seq={seq}: '{msg}'")
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

    def _check_ack(self, seq: int):
        """Poll for ACK/NACK stored by _handle_packet."""
        if hasattr(self, '_last_ack') and self._last_ack == seq:
            del self._last_ack
            return 'ACK'
        if hasattr(self, '_last_nack') and self._last_nack == seq:
            del self._last_nack
            return 'NACK'
        return None
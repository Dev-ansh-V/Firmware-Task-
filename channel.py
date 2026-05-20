import queue
import random

class NoisyChannel:
    
    def __init__(self, drop_rate=0.1):
        self.a_to_b   = queue.Queue()   
        self.b_to_a   = queue.Queue()   
        self.drop_rate = drop_rate

    def send(self, data: bytes, direction: str):
       
        if random.random() < self.drop_rate:
            print(f"  [CHANNEL] Packet DROPPED ({direction})")
            return   

        target = self.a_to_b if direction == 'A→B' else self.b_to_a
        target.put(data)
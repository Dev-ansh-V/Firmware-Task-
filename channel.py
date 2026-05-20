
import queue
import random

class NoisyChannel:
   
    def __init__(self, corrupt_rate=0.1, drop_rate=0.1, dup_rate=0.05):
        self.a_to_b       = queue.Queue()
        self.b_to_a       = queue.Queue()
        self.corrupt_rate = corrupt_rate
        self.drop_rate    = drop_rate
        self.dup_rate     = dup_rate

    def send(self, data: bytes, direction: str):
        

        # 1. Drop the packet entirely
        if random.random() < self.drop_rate:
            print(f"  [CHANNEL] Packet DROPPED ({direction})")
            return

        # 2. Corrupt random bytes (XOR flips bits)
        data = bytearray(data)
        for i in range(len(data)):
            if random.random() < self.corrupt_rate:
                data[i] ^= random.randint(1, 255)
                print(f"  [CHANNEL] Byte {i} CORRUPTED ({direction})")
        data = bytes(data)

        # 3. Put packet in the correct queue
        target = self.a_to_b if direction == 'A→B' else self.b_to_a
        target.put(data)

        # 4. Optionally duplicate
        if random.random() < self.dup_rate:
            print(f"  [CHANNEL] Packet DUPLICATED ({direction})")
            target.put(data)
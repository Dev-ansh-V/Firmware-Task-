# test_demo with example
import threading
import time
from channel import NoisyChannel
from device  import Device

def run_demo():
    print("=" * 55)
    print("  Reliable Comm Protocol — End-to-End Demo")
    print("  corrupt=15%  drop=15%  duplicate=10%")
    print("=" * 55)

    channel = NoisyChannel(corrupt_rate=0.15, drop_rate=0.15, dup_rate=0.1)
    arushi  = Device("Arushi", channel, 'A→B')
    abhik   = Device("Abhik",  channel, 'B→A')

    def arushi_sends():
        for msg in ["Battery at 20%", "Temperature: 34C", "Motion detected"]:
            arushi.send(msg)
            time.sleep(0.5)

    def abhik_sends():
        for msg in ["ACK: signal received", "Rebooting sensor 2"]:
            abhik.send(msg)
            time.sleep(0.7)

    t1 = threading.Thread(target=arushi_sends)
    t2 = threading.Thread(target=abhik_sends)
    t1.start(); t2.start()
    t1.join();  t2.join()

    time.sleep(1)
    print("\n" + "=" * 55)
    print("=== Arushi's Inbox ===", arushi.inbox)
    print("=== Abhik's Inbox  ===", abhik.inbox)
    print("=" * 55)

if __name__ == '__main__':
    run_demo()
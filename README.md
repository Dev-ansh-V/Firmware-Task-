# Firmware-Task-
Submission of Devansh Verma (250331) for Electronics Club Secratory Reqruitement task

- Overview
A simulation of a reliable communication protocol 
built from scratch in Python, designed to work over an unreliable 
channel that can corrupt, drop, duplicate, and merge packets.

- The Problem
Two autonomous wildlife monitoring stations must exchange data 
reliably over a noisy radio channel. The channel:
- Corrupts random bytes
- Drops packets entirely
- Duplicates transmissions
- Merges multiple packets together (no clean boundaries)
- Inserts garbage bytes

- My Solution
I implement a custom framed packet protocol with:
- CRC-16 checksum for error detection
- START/END byte framing to find packet boundaries in a raw byte stream
- Sequence numbers to detect and discard duplicates
- Stop-and-Wait ARQ for guaranteed delivery with retransmission
- Threading for simultaneous bidirectional communication

-Core Concepts Used

1. CRC-16 (Error Detection)
Each packet includes a 2-byte CRC checksum calculated from its contents. The receiver recalculates the CRC and discards the packet if the values do not match, allowing detection of corrupted data.

2. START/END Byte Framing
Every packet begins with 0xAA and ends with 0x55. These markers allow the receiver to extract complete packets from a continuous byte stream, even when packets are merged or split.

3. Sequence Numbers
Each packet carries a sequence number (0–255). The receiver tracks the expected sequence and ignores duplicate packets while still acknowledging them.

4. Stop-and-Wait ARQ
After sending a packet, the sender waits for an ACK. If no ACK is received within a timeout, the packet is retransmitted. This ensures reliable delivery over a lossy channel.

5. Threading
Each device runs a background receiver thread so it can process incoming packets while the main thread handles sending and waiting for acknowledgements.

- Project Structure

`utils.py`  CRC-16, packet building, stream parsing 
`channel.py`  Noisy channel simulation 
`device.py`  Main device logic (send/receive/ARQ) 
`test_demo.py`  End-to-end demo and tests 



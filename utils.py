
import struct

def crc16(data: bytes) -> int:

    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

START_BYTE  = 0xAA
END_BYTE    = 0x55
TYPE_DATA   = 0x01
TYPE_ACK    = 0x02
TYPE_NACK   = 0x03
MAX_PAYLOAD = 28

def build_packet(seq: int, ptype: int, payload: bytes) -> bytes:
    """
    Assemble a framed, checksummed packet.
    [ START | seq | type | len | payload | CRC(2B) | END ]
    """
    payload = payload[:MAX_PAYLOAD]
    length  = len(payload)
    header  = bytes([seq, ptype, length])
    body    = header + payload
    chk     = crc16(body)
    return bytes([START_BYTE]) + body + struct.pack('>H', chk) + bytes([END_BYTE])

def extract_packets(stream: bytes):
    packets  = []
    leftover = stream

    while True:
        start = leftover.find(START_BYTE)
        if start == -1:
            leftover = b''
            break

        leftover = leftover[start:]  

        if len(leftover) < 7:
            break

        length_field = leftover[3]
        packet_size  = 1 + 3 + length_field + 2 + 1

        if len(leftover) < packet_size:
            break  

        candidate = leftover[:packet_size]

        if candidate[-1] != END_BYTE:
            leftover = leftover[1:]  
            continue

      
        body     = candidate[1:-3]
        chk_recv = struct.unpack('>H', candidate[-3:-1])[0]
        chk_calc = crc16(body)

        if chk_recv == chk_calc:
            packets.append({
                'seq':     candidate[1],
                'type':    candidate[2],
                'length':  candidate[3],
                'payload': candidate[4:4 + length_field]
            })
        
        leftover = leftover[packet_size:]

    return packets, leftover
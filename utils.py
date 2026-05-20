import struct

#CRC-16 Checksum -- for corrupted packets
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

#  Packet Constants 
START_BYTE = 0xAA  
END_BYTE   = 0x55  
TYPE_DATA  = 0x01   
TYPE_ACK   = 0x02   
TYPE_NACK  = 0x03  

MAX_PAYLOAD = 28    

# Build a Packet
def build_packet(seq: int, ptype: int, payload: bytes) -> bytes:
    """
    Assemble a framed, checksummed packet.
    
    Final structure:
    [ START_BYTE | seq | type | length | payload | CRC_high | CRC_low | END_BYTE ]
      1 byte       1B    1B     1B       0-28B      2 bytes              1 byte
    """
    payload = payload[:MAX_PAYLOAD]   
    length  = len(payload)
    header  = bytes([seq, ptype, length])
    body    = header + payload        
    chk     = crc16(body)
    return bytes([START_BYTE]) + body + struct.pack('>H', chk) + bytes([END_BYTE])
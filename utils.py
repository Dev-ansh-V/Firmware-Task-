
import struct

# CRC-16 Checksum -- used for corrupted files
def crc16(data: bytes) -> int:
    """
    CRC-16/CCITT checksum.
    Why CRC and not just sum? CRC detects burst errors (multiple
    consecutive flipped bits) that simple checksums miss.
    """
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
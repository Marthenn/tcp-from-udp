"""
crc16.py is a CRC-16 implementation according to CCITT standards (CRC-16/CCITT-FALSE).
0x1021 is the CRC-16 polynomial.
x16 + x12 + x5 + 1

The CRC-16/CCITT-FALSE algorithm is checked against the following online calculator:
https://crccalc.com/
"""
from lib.constants import CRC_INIT, CRC_POLYNOM

def crc16(data: bytes) -> int:
    """Calculate the CRC-16 of a byte string."""
    crc = CRC_INIT
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ CRC_POLYNOM
            else:
                crc <<= 1
    return crc & 0xFFFF


if __name__ == "__main__":
    TEST_DATA = b"hello world bang capek banget nubes wbd"
    print(hex(crc16(TEST_DATA)))

"""Constants used throughout the app"""
# Addresses
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_BROADCAST_PORT = 9999

# Checksum
CRC_POLYNOM = 0x1021
CRC_INIT = 0xFFFF

# Connection
TIMEOUT = 5
SEGMENT_SIZE = 32768

# Sizes
SEGMENT_SIZE = 32768
PAYLOAD_SIZE = SEGMENT_SIZE - 12
WINDOW_SIZE = 3

# Flags
SYN_FLAG = 0b000000010  # 2
ACK_FLAG = 0b000010000  # 16
FIN_FLAG = 0b000000001  # 1
SYN_ACK_FLAG = SYN_FLAG | ACK_FLAG
FIN_ACK_FLAG = FIN_FLAG | ACK_FLAG
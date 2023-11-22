import struct
from constants import ACK_FLAG, FIN_FLAG, SYN_FLAG


class SegmentFlag:
    def __init__(self, flag: bytes):
        # Init flag variable from flag byte
        self.syn = flag & SYN_FLAG
        self.ack = flag & ACK_FLAG
        self.fin = flag & FIN_FLAG

    def get_flag_bytes(self) -> bytes:
        # Convert this object to flag in byte form
        return struct.pack("B", self.syn | self.ack | self.fin)

    def get_flag(self) -> int:
        return self.syn | self.ack | self.fin

    @classmethod
    def from_flag_list(cls, flag_list: list):
        new_flag = 0b0
        for flag in flag_list:
            if flag == "SYN":
                new_flag |= SYN_FLAG
            elif flag == "ACK":
                new_flag |= ACK_FLAG
            elif flag == "FIN":
                new_flag |= FIN_FLAG
        return SegmentFlag(new_flag)

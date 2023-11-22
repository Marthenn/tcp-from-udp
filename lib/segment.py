import struct

from segment_flag import SegmentFlag
from crc16 import crc16

class Segment:
    # -- Private functions --
    def __init__(self):
        # Construct segment
        self.flag = SegmentFlag(0b0)
        self.seq = 0
        self.ack = 0
        self.checksum = 0
        self.data = ""

    def __str__(self):
        # Enable better printout of segments
        output = ""
        output += f"{'SeqNum':12}\t\t| {self.seq}\n"
        output += f"{'AckNum':12}\t\t| {self.ack}\n"
        output += f"{'FlagSYN':12}\t\t| {self.flag.syn >> 1}\n"
        output += f"{'FlagACK':12}\t\t| {self.flag.ack >> 4}\n"
        output += f"{'FlagFIN':12}\t\t| {self.flag.fin}\n"
        output += f"{'Checksum':24}| {self.checksum}\n"
        output += f"{'MsgSize':24}| {len(self.data)}\n"
        return output

    def __calculate_checksum(self) -> int:
        return crc16(self.data)

    # -- Setters --
    def set_header(self, header: dict):
        self.seq = header["seq"]
        self.ack = header["ack"]

    def set_payload(self, payload: bytes):
        self.data = payload

    def set_flag(self, flag_list: list):
        self.flag = SegmentFlag.from_flag_list(flag_list)

    def set_checksum(self, checksum: int):
        self.checksum = checksum

    # -- Getter --
    def get_payload(self) -> bytes:
        return self.data
    
    def get_flag(self) -> SegmentFlag:
        return self.flag.get_flag()

    def get_header(self) -> dict:
        return {"seq": self.seq, "ack": self.ack}
    
    # -- Byte operations --
    @classmethod
    def from_bytes(cls, src: bytes):
        # Convert the src byte into a Segment object
        segment = Segment()
        segment.seq = struct.unpack("I", src[0:4])[0]
        segment.ack = struct.unpack("I", src[4:8])[0]
        segment.flag = SegmentFlag(struct.unpack("B", src[8:9])[0])
        segment.checksum = struct.unpack("H", src[10:12])[0]
        segment.data = src[12:]
        return segment

    def to_bytes(self) -> bytes:
        # Convert the Segment object to pure bytes
        self.checksum = self.__calculate_checksum()
        result = b""
        result += struct.pack("II", self.seq, self.ack)
        result += self.flag.get_flag_bytes()
        result += struct.pack("x")
        result += struct.pack("H", self.checksum)
        result += self.data
        return result

    # -- Checksum --
    def is_valid(self) -> bool:
        # Check whether the Segment object checksum is correct
        return self.__calculate_checksum() == self.checksum
import struct
import io
from typing import List, Dict, Any


def decode_binary(content: bytes) -> List[Dict[str, Any]]:
    records = []
    with io.BytesIO(content) as file:
        while True:
            header_bytes = file.read(4)
            if not header_bytes or len(header_bytes) < 4:
                # Break the loop if there are no more bytes to read
                break

            header = header_bytes[:3].decode("ascii")
            if header == "MIR":
                records.append(_decode_mir(file, header_bytes))
            elif header == "PRR":
                records.append(_decode_prr(file, header_bytes))
            elif header == "PTR":
                records.append(_decode_ptr(file, header_bytes))
    return records


def _decode_mir(file, header_bytes) -> Dict[str, Any]:
    return {
        "type": "MIR",
        "header": header_bytes,
        "temperature": round(struct.unpack("<f", file.read(4))[0], 2),
        "operator": file.read(20).decode("ascii", errors="replace").rstrip("\x00").strip(),
    }


def _decode_prr(file, header_bytes) -> Dict[str, Any]:
    return {
        "type": "PRR",
        "header": header_bytes,
        "part_number": struct.unpack("<i", file.read(4))[0],
        "pass_fail": struct.unpack("<B", file.read(1))[0],
    }


def _decode_ptr(file, header_bytes) -> Dict[str, Any]:
    return {
        "type": "PTR",
        "header": header_bytes,
        "test_name": file.read(20).decode("ascii").rstrip("\x00").strip(),
        "test_value": round(struct.unpack("<f", file.read(4))[0], 2),
        "low_limit": round(struct.unpack("<f", file.read(4))[0], 2),
        "high_limit": round(struct.unpack("<f", file.read(4))[0], 2),
        "pass_fail": struct.unpack("B", file.read(1))[0],
    }


def encode_binary(records: List[Dict[str, Any]]) -> bytes:
    binary_data = bytearray()
    for record in records:
        binary_data += record["header"]

        if record["type"] == "MIR":
            binary_data += struct.pack("<f", record["temperature"])
            binary_data += record["operator"].encode("ascii").ljust(20, b"\x00")[:20]
        elif record["type"] == "PRR":
            binary_data += struct.pack("<i", record["part_number"])
            binary_data += struct.pack("B", record["pass_fail"])
        elif record["type"] == "PTR":
            binary_data += record["test_name"].encode("ascii").ljust(20, b"\x00")[:20]
            binary_data += struct.pack("<f", record["test_value"])
            binary_data += struct.pack("<f", record["low_limit"])
            binary_data += struct.pack("<f", record["high_limit"])
            binary_data += struct.pack("B", record["pass_fail"])
    return bytes(binary_data)

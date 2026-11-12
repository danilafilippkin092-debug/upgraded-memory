#!/usr/bin/env python3
"""Validate nested LZMA EFI FV and AArch64 modules; compile-only, NEVER flash."""
import argparse
import hashlib
import json
import lzma
import struct
import uuid
from pathlib import Path

FFS2 = "8c8ce578-8a3d-4f1c-9935-896185c32dd3"
LZMA_GUID = "ee4e5898-3914-4259-9d6e-dc7bd79403cf"

def scan_fv(b):
    if len(b) < 72 or b[40:44] != b"_FVH":
        raise ValueError("Missing FVH")
    length = struct.unpack_from("<Q", b, 32)[0]
    hdr = struct.unpack_from("<H", b, 48)[0]
    if length != len(b) or hdr < 56 or hdr > 4096 or hdr % 2:
        raise ValueError("FV length/header invalid")
    if str(uuid.UUID(bytes_le=b[16:32])) != FFS2:
        raise ValueError("Unexpected file system GUID")
    if sum(struct.unpack_from("<" + str(hdr // 2) + "H", b)) % 65536:
        raise ValueError("FV header checksum invalid")
    out = []
    p = (hdr + 7) & ~7
    while p + 24 <= len(b):
        h = b[p:p + 24]
        if h in (b"\xff" * 24, b"\0" * 24):
            break
        size = int.from_bytes(h[20:23], "little")
        kind = h[18]
        if size < 24 or size == 0xffffff or p + size > len(b):
            raise ValueError(f"Invalid FFS size at {p:x}")
        name = ""
        sections = []
        if kind != 0xf0:  # FFS pad, not an EFI module
            q = p + 24
            while q + 4 <= p + size:
                sh = b[q:q + 4]
                slen = int.from_bytes(sh[:3], "little")
                if slen < 4 or q + slen > p + size:
                    break
                typ = sh[3]
                data = b[q + 4:q + slen]
                if typ == 0x15:
                    name = data.decode("utf-16-le", "replace").rstrip("\0")
                sections.append((typ, data))
                q = (q + slen + 3) & ~3
        out.append({"guid": str(uuid.UUID(bytes_le=h[:16])),
                    "kind": kind, "name": name, "sections": sections})
        p = (p + size + 7) & ~7
    return out

def arm64_pe(payload):
    if len(payload) < 256 or payload[:2] != b"MZ":
        return False
    at = struct.unpack_from("<I", payload, 60)[0]
    return at + 24 <= len(payload) and payload[at:at + 4] == b"PE\0\0" \
        and struct.unpack_from("<H", payload, at + 4)[0] == 0xaa64

def analyze(blob):
    outer = scan_fv(blob)
    if len(outer) != 3:
        raise ValueError("Unexpected outer FFS count")
    inner_candidates = []
    for f in outer:
        if f["kind"] != 0x0b:  # FV_IMAGE, not a generic DXE driver
            continue
        for typ, data in f["sections"]:
            if typ != 2 or len(data) < 20:
                continue
            if str(uuid.UUID(bytes_le=data[:16])) != LZMA_GUID:
                continue
            offset, attrs = struct.unpack_from("<HH", data, 16)
            if not (24 <= offset < 64 and attrs & 1):
                raise ValueError("LZMA GUID-defined section metadata invalid")
            decoded = lzma.decompress(data[offset - 4:])
            if len(decoded) > 64 * 1024 * 1024:
                raise ValueError("Unexpectedly large decompressed FV")
            if decoded[:4] != b"\x04\x00\x00\x19" or decoded[7] != 0x17:
                raise ValueError("Unexpected nested FV section envelope")
            if int.from_bytes(decoded[4:7], "little") != len(decoded) - 4:
                raise ValueError("Nested FV image length invalid")
            inner_candidates.append(decoded[8:])
    if len(inner_candidates) != 1:
        raise ValueError(f"Expected one nested FV, found {len(inner_candidates)}")
    inner = inner_candidates[0]
    modules = scan_fv(inner)
    pe32 = []
    for f in modules:
        for typ, data in f["sections"]:
            if typ == 0x10:
                if not arm64_pe(data):
                    raise ValueError(f"Non-AARCH64 or invalid PE: {f['name']}")
                pe32.append(f)
    shells = [f for f in modules if f["name"] == "EdkShell" and f["kind"] == 9]
    drivers = [f for f in modules if f["kind"] == 7]
    if len(modules) < 100 or len(pe32) < 100 or len(drivers) < 80 or len(shells) != 1:
        raise ValueError("Incomplete nested firmware structure or missing UEFI Shell")
    return {
        "device": "DBY-W09, variant DBY_W09_VD",
        "fd_sha256": hashlib.sha256(blob).hexdigest(),
        "outer_ffs_count": len(outer),
        "inner_fv_size": len(inner),
        "inner_sha256": hashlib.sha256(inner).hexdigest(),
        "inner_ffs_count": len(modules),
        "inner_dxe_driver_ffs_count": len(drivers),
        "inner_aarch64_pe_count": len(pe32),
        "uefi_shell_present": True,
        "inner_fv_checksum": "PASS",
        "hardware_compatible": False,
        "boot_tested": False,
        "flashable": False,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("firmware", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = analyze(args.firmware.read_bytes())
    s = json.dumps(result, indent=2) + "\n"
    print(s)
    if args.output:
        args.output.write_text(s)

if __name__ == "__main__":
    main()

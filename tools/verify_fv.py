#!/usr/bin/env python3
"""Inspect a compiled UEFI Firmware Volume and its *embedded* uefiplat.cfg.

This is an offline structural audit, not a hardware boot test, verifier of
proprietary DXE compatibility, or permission to flash the file.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
import uuid
from pathlib import Path
from tools.patch_uefiplat import check as check_uefiplat_cfg

FS2_GUID="8c8ce578-8a3d-4f1c-9935-896185c32dd3"
FV_SIGNATURE=b"_FVH"
MIN_SIZE=0x10000
MAX_SIZE=0x4000000

def inspect_fv(blob: bytes, expected_cfg: str|None=None):
    if len(blob)<MIN_SIZE or len(blob)>MAX_SIZE:
        raise ValueError(f"Implausible firmware volume size: {len(blob)}")
    if blob.startswith(b"ANDROID!") or blob[-64:].startswith(b"AVBf"):
        raise ValueError("Unexpected Android boot image metadata")
    if blob[40:44]!=FV_SIGNATURE:
        raise ValueError("Missing FVH signature")
    length=struct.unpack_from("<Q",blob,32)[0]
    if length!=len(blob):
        raise ValueError(f"FVH length mismatch: {length} != {len(blob)}")
    fs_guid=str(uuid.UUID(bytes_le=blob[16:32]))
    if fs_guid!=FS2_GUID:
        raise ValueError(f"Unexpected EFI FFS2 GUID: {fs_guid}")
    header_len=struct.unpack_from("<H",blob,48)[0]
    if header_len<56 or header_len>4096 or header_len%2:
        raise ValueError(f"Invalid FVH header length: {header_len}")
    total=sum(struct.unpack_from("<"+str(header_len//2)+"H",blob,0))&0xffff
    if total!=0:
        raise ValueError(f"Bad FV header checksum: 0x{total:04x}")
    files=[]
    position=(header_len+7)&~7
    cfg=None
    for index in range(4096):
        if position+24>len(blob):break
        header=blob[position:position+24]
        if header==b"\xff"*24:break
        if header==b"\x00"*24:break
        guid=str(uuid.UUID(bytes_le=header[:16]))
        ffs_type=header[18]
        size=int.from_bytes(header[20:23],"little")
        if size in (0,0xffffff) or size<24 or position+size>len(blob):
            raise ValueError(f"Truncated FFS file at 0x{position:x}")
        end=position+size
        secs=[]
        cursor=position+24
        ui_name=None
        raw_sections=[]
        while cursor+4<=end:
            sh=blob[cursor:cursor+4]
            sec_size=int.from_bytes(sh[:3],"little")
            sec_type=sh[3]
            if sec_size<4 or cursor+sec_size>end:
                break
            payload=blob[cursor+4:cursor+sec_size]
            secs.append(sec_type)
            if sec_type==0x15:
                ui_name=payload.decode("utf-16-le","replace").rstrip("\0")
            elif sec_type==0x19:
                raw_sections.append(payload)
            cursor=(cursor+sec_size+3)&~3
        if ui_name=="uefiplat.cfg":
            if cfg is not None or not raw_sections:
                raise ValueError("Duplicate or missing raw uefiplat.cfg section")
            cfg=raw_sections[0].decode("utf-8")
        files.append({"guid":guid,"file_type":ffs_type,"bytes":size,
                      "ui_name":ui_name,"section_types":[hex(s) for s in secs]})
        position=(end+7)&~7
    if len(files)<3:
        raise ValueError(f"Unexpectedly few FFS entries: {len(files)}")
    if cfg is None:
        raise ValueError("Missing embedded uefiplat.cfg")
    cfg_rows=check_uefiplat_cfg(cfg)
    if expected_cfg is not None and cfg!=expected_cfg:
        raise ValueError("Embedded uefiplat.cfg differs from board-specific build input")
    if not any(f["file_type"]==0x0b for f in files):
        raise ValueError("Missing compressed DXE/driver firmware file")
    return {
      "target":"Huawei MatePad 11 DBY-W09 (VD)",
      "kind":"UEFI_FV_NOT_A_BOOT_IMAGE",
      "fw_volume_bytes":len(blob),
      "sha256":hashlib.sha256(blob).hexdigest(),
      "firmware_files":files,
      "ffs2_guid":fs_guid,
      "header_checksum":"PASS",
      "embedded_uefiplat_cfg_sha256":hashlib.sha256(cfg.encode()).hexdigest(),
      "embedded_memory_and_register_regions":len(cfg_rows),
      "embedded_cfg_validated":"PASS_STATIC_ONLY",
      "contains_unvalidated_donor_dxe_drivers":True,
      "hardware_compatible":False,
      "verified_bootable":False,
      "safe_to_flash":False,
      "disclaimer":"Structural validation is not boot testing; do not flash"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("fv",type=Path)
    p.add_argument("--expected-cfg",type=Path)
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    expected=args.expected_cfg.read_text(encoding="utf-8") if args.expected_cfg else None
    result=inspect_fv(args.fv.read_bytes(),expected)
    text=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    print(text)
    if args.out:args.out.write_text(text,encoding="utf-8")

if __name__=="__main__":
    main()

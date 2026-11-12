#!/usr/bin/env python3
"""Statically verify an AArch64 EFI application; NEVER execute it on tablet."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

def inspect(path: Path):
    data=path.read_bytes()
    if len(data)<0x100 or data[:2]!=b'MZ':
        raise ValueError('Missing DOS MZ header')
    peoff=struct.unpack_from('<I',data,0x3c)[0]
    if peoff+24+70>len(data) or data[peoff:peoff+4]!=b'PE\x00\x00':
        raise ValueError('Invalid PE header')
    machine=struct.unpack_from('<H',data,peoff+4)[0]
    if machine!=0xAA64:
        raise ValueError(f'Wrong machine: 0x{machine:04x}')
    optoff=peoff+24
    magic=struct.unpack_from('<H',data,optoff)[0]
    if magic!=0x20B: raise ValueError(f'Wrong PE32+ magic 0x{magic:04x}')
    subsystem=struct.unpack_from('<H',data,optoff+68)[0]
    if subsystem!=10: raise ValueError(f'Wrong subsystem {subsystem}')
    return {
        'device':'DBY-W09','kind':'AARCH64_UEFI_APPLICATION_NOT_FIRMWARE',
        'bytes':len(data),'machine':'0xAA64','subsystem':subsystem,
        'sha256':hashlib.sha256(data).hexdigest(),
        'bootable_on_tablet':False,'flashable':False,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('efi',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    metadata=inspect(args.efi)
    print(json.dumps(metadata,ensure_ascii=False,indent=2))
    if args.out: args.out.write_text(json.dumps(metadata,indent=2)+'\n')

if __name__=='__main__': main()

#!/usr/bin/env python3
"""Fail-closed, device-specific patch for a donor Project Aloha uefiplat.cfg.

Reconciles the *build-time embedded firmware configuration* with the
DBY-W09 (VD) candidate PlatformMemoryMapLib. This does not validate
hardware execution and deliberately does not produce Android boot images.
"""
from __future__ import annotations
import argparse
import re
from pathlib import Path

EXPECTED = {
  "BOOT INFO": (0x80700000, 0x00100000, "Reserv"),
  "XBL Log Buffer": (0x80884000, 0x00010000, "Reserv"),
  "HW Reserved": (0xB0000000, 0x00401000, "Reserv"),
}
RANGE = re.compile(r'^\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*"([^"]+)"\s*,\s*'
                   r'([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,\r\n]+)', re.M)

def lines_for(text: str):
    return [(int(m.group(1),16),int(m.group(2),16),m.group(3).strip(),
             m.group(7).strip(),m.group(4).strip()) for m in RANGE.finditer(text)]

def check(text: str):
    rows=lines_for(text)
    for name,(base,size,typ) in EXPECTED.items():
        matched=[r for r in rows if r[2]==name]
        if len(matched)!=1 or matched[0][:2]!=(base,size) or matched[0][3]!=typ:
            raise ValueError(f"Invalid {name}: expected {hex(base)}, {hex(size)}, {typ}; got {matched}")
    for base,size,name,typ,_ in rows:
        if name=="IPC SHM" and base==0x805D0000:
            raise ValueError("Legacy IPC SHM overlaps reserved 0x80000000..0x80600000")
        if name=="MLVM":
            raise ValueError("Foreign-device MLVM reservation remains in UEFI config")
        if base==0x805F0000 and name=="BOOT INFO":
            raise ValueError("Wrong donor boot-info address")
        # BOOT HYP region is not conventional/boot-services/runtime memory
        if typ in ("Conv","BsData","RtData") and base<0x80600000 and base+size>0x80000000:
            raise ValueError(f"Memory allocation overlaps protected HYP: {name}")
    if text.count("[MemoryMap]")!=1 or text.count("[RegisterMap]")!=1:
        raise ValueError("Unexpected or malformed Qualcomm uefiplat.cfg structure")
    if not text.endswith("\n"):
        raise ValueError("Qualcomm firmware config must end with newline")
    return rows

def patch(original: str):
    # Must match the specific expected donor version; refuse unknown upstream data.
    targets={
       '0x805D0000, 0x00020000, "IPC SHM",           AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK_XN':
       '# DBY-W09 VD: omitted legacy donor IPC SHM (overlaps reserved HYP)',
       '0x805F0000, 0x00010000, "BOOT INFO",         AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK_XN':
       '0x80700000, 0x00100000, "BOOT INFO",         AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN',
       '0xB0400000, 0x09000000, "MLVM",              AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN':
       '0xB0000000, 0x00401000, "HW Reserved",       AddMem, MEM_RES, UNCACHEABLE, Reserv, UNCACHED_UNBUFFERED_XN',
    }
    updated=original
    for before,after in targets.items():
        if updated.count(before)!=1:
            raise ValueError(f"Refusing unrecognized donor uefiplat.cfg; missing or duplicate: {before[:72]}")
        updated=updated.replace(before,after,1)
    anchors={
       '0x80860000, 0x00020000, "AOP CMD DB",':
       '0x80884000, 0x00010000, "XBL Log Buffer",    AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN',
       '0x08800000, 0x00200000, "PERIPH_SS",':
       '0x090BA000, 0x00006000, "MCCC_MCCC_MSTR",     AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE'
    }
    for anchor,addition in anchors.items():
        rows=updated.splitlines(keepends=True)
        where=[i for i,line in enumerate(rows) if line.lstrip().startswith(anchor)]
        if len(where)!=1:raise ValueError(f"Missing unique anchor: {anchor}")
        if any(addition in row for row in rows):
            raise ValueError(f"Unexpected duplicate: {addition[:60]}")
        rows.insert(where[0]+1,addition+"\n")
        updated=''.join(rows)
    check(updated)
    return updated

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cfg",type=Path)
    parser.add_argument("--check",action="store_true",help="Validate only, never modify")
    args=parser.parse_args()
    original=args.cfg.read_text(encoding="utf-8")
    if args.check:
        check(original);print("PASS: DBY-W09 VD UEFI config (embedded-cfg candidate)")
        return
    patched=patch(original)
    args.cfg.write_text(patched,encoding="utf-8")
    print("PASS: replaced incompatible MTP8250 memory/register entries with DBY-W09 VD candidates")
    print("NOTE: Compilation-only; no claim of runtime compatibility or flash safety")

if __name__=="__main__":
    main()

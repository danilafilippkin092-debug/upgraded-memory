#!/usr/bin/env python3
"""Read-only OEM EFI module inventory for the owner's private XBL extraction.

No binary material is uploaded, patched, repacked, flashed or exported.
Input is an existing local archive made from the OWNER'S own XBL extraction,
e.g. DBY_W09_UEFI_Bringup_v2_OEM.zip. Only metadata gets exported.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from zipfile import ZipFile

EFI_RE=re.compile(r"^OEM_FV/PE32/([^/]+)__([a-fA-F0-9-]{36})\.efi$")
GUID_RE=re.compile(r"(?im)^\s*FILE_GUID\s*=\s*([0-9a-fA-F-]{36})")
PRIORITY=("UFSDxe","DisplayDxe","ClockDxe","PmicDxe","UsbfnDwc3Dxe",
          "UsbConfigDxe","XhciDxe","TzDxe","RpmhDxe","SdccDxe",
          "HALIOMMU","SmemDxe","EnvDxe")

def pe_machine(data:bytes):
    if len(data)<0x100 or data[:2]!=b"MZ":return None
    at=struct.unpack_from("<I",data,0x3c)[0]
    if at+96>=len(data) or data[at:at+4]!=b"PE\0\0":return None
    machine=struct.unpack_from("<H",data,at+4)[0]
    subsystem=struct.unpack_from("<H",data,at+24+68)[0]
    return machine,subsystem

def donor_guid_index(root:Path):
    if not root or not root.is_dir():return {}
    mapped={}
    for path in sorted(root.rglob("*.inf")):
        try: data=path.read_text(errors="replace")
        except OSError:continue
        m=GUID_RE.search(data)
        if not m:continue
        guid=m.group(1).lower()
        mapped.setdefault(guid,[]).append(str(path.relative_to(root)))
    return mapped

def inventory(oem:Path,donor:Path|None=None):
    index=donor_guid_index(donor) if donor else {}
    entries=[]
    with ZipFile(oem) as z:
        for n in sorted(z.namelist()):
            m=EFI_RE.match(n)
            if not m: continue
            name,guid=m.groups()
            blob=z.read(n)
            meta=pe_machine(blob)
            if meta is None or meta[0]!=0xaa64:
                raise ValueError(f"OEM module {name} is not PE AARCH64")
            entries.append({
                "name":name,"file_guid":guid.lower(),
                "size":len(blob),"machine":"AARCH64",
                "efi_subsystem":meta[1],
                "sha256":hashlib.sha256(blob).hexdigest(),
                "donor_inf_guid_matches":index.get(guid.lower(),[]),
                "priority_review":name in PRIORITY,
            })
    if not entries:raise ValueError("No extracted OEM_FV/PE32/*.efi modules found")
    matches=sum(bool(e["donor_inf_guid_matches"]) for e in entries)
    return {
        "owner_device":"Huawei MatePad 11 DBY-W09",
        "board_variant":"DBY_W09_VD",
        "source":"Private locally extracted OEM XBL",
        "module_count":len(entries),
        "aarch64_verified":len(entries),
        "donor_guid_matches":matches,
        "note":"Metadata-only. Binary modules have not been injected or validated. Do not flash.",
        "modules":entries,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("oem_archive",type=Path)
    p.add_argument("--donor",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    obj=inventory(args.oem_archive,args.donor)
    report=json.dumps(obj,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(report)
        print(f"Saved local metadata to {args.output}")
    print(f"OEM EFI: {obj['module_count']} / {obj['aarch64_verified']} AARCH64")
    print(f"Exact donor INF GUID matches: {obj['donor_guid_matches']}")
    print("Priority:",", ".join(x["name"] for x in obj["modules"] if x["priority_review"]))
    print("NOT flashable. No binaries copied. No device operations.")

if __name__=="__main__":main()

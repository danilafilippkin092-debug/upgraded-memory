#!/usr/bin/env python3
"""Offline cross-check: DBY-W09 VD candidate UEFI memory against stock DTB/iomem.

The data includes only hardware address ranges, no personal firmware dumps.
A passing audit is NOT proof that booting this firmware is safe.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"port/Platforms/KonaPkg/Device/huawei-dby-w09"
MAP=SRC/"Library/PlatformMemoryMapLib/PlatformMemoryMapLib.c"
HEADER=SRC/"Library/PlatformMemoryMapLib/MemoryMap.h"
PROFILE=ROOT/"profiles/dby-w09-vd-reserved.json"
MAP_ENTRY=re.compile(
    r'\{\s*"([^"]+)"\s*,\s*(0x[0-9a-f]+)ULL\s*,\s*(0x[0-9a-f]+)ULL\s*,\s*'
    r'(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*,\s*(\w+)\s*\}', re.I)
RAM_ENTRY=re.compile(
    r'\bX\s*\(\s*"([^"]+)"\s*,\s*(0x[0-9a-f]+)ULL\s*,\s*(0x[0-9a-f]+)ULL\s*\)',re.I)
AVAILABLE={'Conv','BsData','RtData'}
NO_MAPPING_TYPES={'Reserv'}

def overlap(a,b):
    return max(a[0],b[0])<min(a[1],b[1])

def rows():
    found=[]
    for m in MAP_ENTRY.finditer(MAP.read_text()):
        name,base,size,hob,resource,attr,typ,cache=m.groups()
        start=int(base,16);length=int(size,16)
        found.append(dict(name=name,start=start,end=start+length,hob=hob,
                          resource=resource,attr=attr,typ=typ,cache=cache))
    for m in RAM_ENTRY.finditer(HEADER.read_text()):
        name,base,size=m.groups()
        start=int(base,16);length=int(size,16)
        found.append(dict(name=name,start=start,end=start+length,hob='AddMem',
                          resource='SYS_MEM',attr='SYS_MEM_CAP',typ='Conv',cache='WRITE_BACK_XN'))
    if not found: raise AssertionError("Did not parse memory entries")
    return found

def validate(rows_in=None,profile=None):
    rr=rows_in if rows_in is not None else rows()
    p=profile if profile is not None else json.loads(PROFILE.read_text())
    if p['device']!='DBY-W09' or p['board_variant']!='DBY_W09_VD':
        raise AssertionError("Unexpected target or board variant")
    if len(rr)<25:raise AssertionError(f"Too few memory descriptors: {len(rr)}")
    for r in rr:
        if not (0<r['start']<r['end']):raise AssertionError(f"Bad range: {r}")
        if r['start']%0x1000 or r['end']%0x1000:
            raise AssertionError(f"Unaligned region: {r['name']}")
    # Compare distinct regions introduced to firmware; nested /reserved-memory entries are fine.
    sysmem=[x for x in rr if x['resource']=='SYS_MEM']
    for i,a in enumerate(sysmem):
        for b in sysmem[i+1:]:
            if overlap((a['start'],a['end']),(b['start'],b['end'])):
                raise AssertionError(f"Overlapping SYS_MEM: {a['name']} and {b['name']}")
    source_ranges=[]
    for source in ('fdt_reserved','iomem_reserved'):
        for start,end,label in p[source]:
            source_ranges.append((int(start,16),int(end,16),f'{source}/{label}'))
    for a in sysmem:
        if a['typ'] not in AVAILABLE:continue
        for start,end,label in source_ranges:
            if overlap((a['start'],a['end']),(start,end)):
                raise AssertionError(
                    f"Unsafe {a['typ']} {a['name']} overlaps {label}: "
                    f"{a['start']:#x}..{a['end']:#x} and {start:#x}..{end:#x}"
                )
    # EDK2 Kona.fdf defines FD [0x9FC41000,0x9FF00000), not whole OEM 3 MiB.
    volume=[a for a in rr if a['name'].strip()=='UEFI FD']
    if len(volume)!=1 or (volume[0]['start'],volume[0]['end'])!=(0x9fc41000,0x9ff00000):
        raise AssertionError("UEFI FD must match Kona.fdf base/size")
    # XBL boot-info range overlaps stock no-map xbl_aop: protect it.
    boot=[a for a in rr if a['name'].strip()=='BOOT INFO']
    if len(boot)!=1 or boot[0]['typ']!='Reserv':
        raise AssertionError("XBL BOOT INFO must stay reserved")
    return {'device':p['device'],'board_variant':p['board_variant'],
            'total_regions':len(rr),'system_memory_regions':len(sysmem),
            'stock_protected_ranges':len(source_ranges),
            'firmware_volume':'0x9fc41000..0x9ff00000',
            'status':'PASS_STATIC_ONLY_NOT_FLASHABLE'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--json',action='store_true')
    args=parser.parse_args()
    result=validate()
    if args.json: print(json.dumps(result,indent=2))
    else:
        for k,v in result.items():print(f'{k}: {v}')

if __name__=='__main__': main()

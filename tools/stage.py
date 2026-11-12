#!/usr/bin/env python3
"""Copy only candidate SOURCE files into a local Project Aloha checkout."""
import argparse
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PORT=ROOT/'port/Platforms/KonaPkg/Device/huawei-dby-w09'
DEVICE_REL=Path('Platforms/KonaPkg/Device/huawei-dby-w09')
ALLOWED={'.c','.h','.inf','.inc','.dsl','.dtso'}

def stage(upstream: Path,apply=False):
    upstream=upstream.resolve()
    for required in ('Platforms/KonaPkg/Kona.dsc','Platforms/KonaPkg/Kona.fdf','build_uefi.py'):
        if not (upstream/required).is_file():
            raise SystemExit(f'Not a Project Aloha checkout: missing {required}')
    files=sorted(x for x in PORT.rglob('*') if x.is_file())
    if not files: raise SystemExit('No source files')
    for f in files:
        if f.suffix not in ALLOWED: raise SystemExit(f'Unexpected file: {f}')
        target=upstream/DEVICE_REL/f.relative_to(PORT)
        if target.exists(): raise SystemExit(f'Refusing overwrite: {target}')
    print(f'{"APPLY" if apply else "DRY RUN"}: {len(files)} source files')
    for f in files:
        target=upstream/DEVICE_REL/f.relative_to(PORT)
        print(f'  {f.relative_to(ROOT)} -> {target.relative_to(upstream)}')
        if apply:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(f,target)
    print('No ABL changes, no FDF patch, no firmware image, no device operations.')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--upstream',type=Path,required=True)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--apply',action='store_true')
    mode.add_argument('--dry-run',action='store_true')
    a=parser.parse_args()
    stage(a.upstream,a.apply)

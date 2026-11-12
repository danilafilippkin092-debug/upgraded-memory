#!/usr/bin/env python3
"""Read-only audit of UNVERIFIED Huawei DBY-W09 EDK2 candidate sources."""
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEVICE=ROOT/'port/Platforms/KonaPkg/Device/huawei-dby-w09'
REQUIRED={
  'PcdsFixedAtBuild.dsc.inc',
  'Library/PlatformMemoryMapLib/PlatformMemoryMapLib.c',
  'Library/PlatformMemoryMapLib/PlatformMemoryMapLib.inf',
  'Library/PlatformMemoryMapLib/MemoryMap.h',
  'Library/PlatformConfigurationMapLib/PlatformConfigurationMapLib.c',
  'Library/PlatformConfigurationMapLib/PlatformConfigurationMapLib.inf',
}
MISSING_FOR_BOOT={
  'APRIORI.inc','DXE.inc','DXE.dsc.inc',
  'Binaries/RawFiles/uefiplat.cfg',
  'DeviceTreeBlob/Android/dby-w09.dtb',
  'ACPI/DSDT.aml',
}

def audit():
    p=json.loads((ROOT/'profiles/dby-w09.json').read_text(encoding='utf-8'))
    d=p['device']
    assert d['board']=='DBY'
    assert d['platform']=='kona'
    assert d['dtbo_active_index']==3
    assert d['model_confirmed_by_owner']=='DBY-W09'
    assert d['dtbo_active_board_name']=='DBY_W09_VD'
    assert d['dtbo_active_boardid_cells']==[8,2,0,6]
    u=p['uefi_addresses']
    o_base=int(u['oem_fd_base'],16); o_size=int(u['oem_fd_size'],16)
    a_base=int(u['aloha_sm8250_default_base'],16)
    a_size=int(u['aloha_sm8250_default_size'],16)
    assert o_base <= a_base and a_base+a_size <= o_base+o_size
    missing=sorted(x for x in REQUIRED if not (DEVICE/x).is_file())
    assert not missing,f'Missing candidate files: {missing}'
    memorymap=(DEVICE/'Library/PlatformMemoryMapLib/PlatformMemoryMapLib.c').read_text()
    assert 'DBY_CONVENTIONAL_REGION_LIST' in memorymap
    assert 'IPC SHM' in memorymap
    for script in (ROOT/'tools').glob('*.py'):
        if script.name=='audit.py': continue
        code=script.read_text()
        for forbidden in ('fastboot flash','dd if=','dd of='):
            assert forbidden not in code,f'Forbidden command in {script}'
    print('PASS: board DBY-W09; active DTBO 3; OEM/Aloha FD bounds')
    print('PASS: candidate memory / configuration source files present')
    todo=sorted(x for x in MISSING_FOR_BOOT if not (DEVICE/x).is_file())
    print('INCOMPLETE: full device-specific firmware integration is not available')
    for item in todo: print('  TODO:',item)
    return 0

if __name__=='__main__':
    try: sys.exit(audit())
    except (AssertionError,ValueError,OSError,KeyError) as e:
        print('AUDIT FAILED:',e,file=sys.stderr)
        sys.exit(1)

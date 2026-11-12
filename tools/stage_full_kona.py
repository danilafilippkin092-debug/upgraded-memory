#!/usr/bin/env python3
"""Stage a FULL KonaPkg build tree for DBY-W09 on GitHub Actions.

This is an EXPERIMENTAL compile harness, not a validated Huawei firmware port.
It inherits qcom-mtp8250 proprietary firmware drivers / DXE lists and generic
SM8250 ACPI tables only to resolve dependencies. They are NOT known to work
on Huawei DBY-W09. Device-specific DSDT and DTBO are compiled from VD-specific
candidate sources; donor Android DTB is excluded. Boot image packing disabled.
"""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BOARD=Path("Platforms/KonaPkg/Device/huawei-dby-w09")
DONOR=Path("Platforms/KonaPkg/Device/qcom-mtp8250")
CANDIDATES=ROOT/"port"/BOARD
REQUIRED_CANDIDATE=[
    "PcdsFixedAtBuild.dsc.inc",
    "Library/PlatformMemoryMapLib/MemoryMap.h",
    "Library/PlatformMemoryMapLib/PlatformMemoryMapLib.c",
    "Library/PlatformMemoryMapLib/PlatformMemoryMapLib.inf",
    "Library/PlatformConfigurationMapLib/PlatformConfigurationMapLib.c",
    "Library/PlatformConfigurationMapLib/PlatformConfigurationMapLib.inf",
    "DeviceTreeBlob/Android/dby-w09-vd-rootparam.dtso",
    "ACPI/DSDT.dsl",
]
# No postbuild packaging (Android boot image) and no flashable artifacts.
def disable_boot_pack(upstream: Path):
    for py in ("PlatformBuildNoSb.py",):
        path=upstream/"Platforms"/"KonaPkg"/py
        txt=path.read_text()
        start=txt.find("    def PlatformPostBuild(self):")
        end=txt.find("    def FlashRomImage(self):",start)
        if start<0 or end<0 or end<=start:
            raise RuntimeError("Unexpected upstream PlatformBuild version, refusing to patch")
        replacement=(
            "    def PlatformPostBuild(self):\n"
            "        # DBY-W09 CI: compile firmware FD, NEVER package Android boot.\n"
            "        return 0\n\n"
        )
        path.write_text(txt[:start]+replacement+txt[end:])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream",type=Path,required=True)
    args=p.parse_args()
    upstream=args.upstream.resolve()
    template=upstream/DONOR
    target=upstream/BOARD
    if not template.is_dir():
        raise SystemExit(f"Missing Project Aloha donor directory: {template}")
    if target.exists():
        raise SystemExit(f"Refusing to overwrite existing device directory: {target}")
    for name in REQUIRED_CANDIDATE:
        if not (CANDIDATES/name).is_file():
            raise SystemExit(f"Missing DBY-W09 source: {name}")
    if not (upstream/"Platforms/KonaPkg/Kona.dsc").is_file():
        raise SystemExit("Project Aloha Kona.dsc missing")
    shutil.copytree(template,target)
    # Hardware customization: copy OWN DBY-W09 config & memory code over donor.
    copied=[]
    for name in REQUIRED_CANDIDATE:
        src=CANDIDATES/name
        dst=target/name
        dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,dst)
        copied.append(name)
    # Remove Qualcomm MTP8250 device-specific hardware blobs from target.
    # The compile-stage will generate a VD-specific DSDT. Do not retain donor AML.
    donor_aml=target/"ACPI/DSDT.aml"
    if not donor_aml.exists(): raise SystemExit("Expected donor DSDT.aml missing")
    donor_aml.unlink()
    for donor_dtb in (target/"DeviceTreeBlob/Android").glob("*.dtb"):
        donor_dtb.unlink()
    for donor_dtbo in (target/"DeviceTreeBlob/Android").glob("*.dtbo"):
        donor_dtbo.unlink()
    # No Android DTB packing: PostBuild image generation is disabled.
    disable_boot_pack(upstream)
    print("STAGED",BOARD)
    print("DBY-W09 candidate sources:",", ".join(copied))
    print("INHERITED FROM qcom-mtp8250: vendor DXE binaries/lists, shared SM8250 ACPI, assets")
    print("REMOVED donor ACPI/DSDT.aml and donor Android *.dtb, *.dtbo")
    print("TO BE COMPILED: DBY-W09 VD diagnostic DSDT + rootparam-only DTBO")
    print("NOT HARDWARE VALIDATED, NOT FLASHABLE, POSTBUILD ANDROID IMAGE PACKAGING DISABLED")

if __name__=="__main__":
    main()

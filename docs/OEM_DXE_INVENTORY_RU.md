# OEM DXE inventory: original Huawei DBY-W09

The owner's stock XBL extraction previously produced a local archive `DBY_W09_UEFI_Bringup_v2_OEM.zip`.

Read-only analysis of that **private local archive** found **89 AARCH64 PE/COFF EFI modules**; all 89 PE headers report machine `0xAA64`.

Particularly relevant to board bring-up: `UFSDxe`, `DisplayDxe`, `ClockDxe`, `PmicDxe`, `UsbfnDwc3Dxe`, `UsbConfigDxe`, `XhciDxe`, `TzDxe`, `RpmhDxe`, `SdccDxe`, `HALIOMMU`, `SmemDxe`, `EnvDxe`.

These are **original OEM code**, not evidence of compatibility with another rebuilt EDK2 runtime. Firmware version, protocol GUIDs, image dependencies, relocations and TrustZone interactions must be verified before any driver replacement.

## Reproduce on your own machine, without publishing the firmware

```bash
python3 tools/oem_dxe_inventory.py /path/to/DBY_W09_UEFI_Bringup_v2_OEM.zip \
  --donor /path/to/mu_aloha_platforms/Platforms/KonaPkg/Device/qcom-mtp8250 \
  --output /path/to/private-local/oem-dxe-metadata.json
```

This script **never copies, uploads, patches or flashes EFI modules**. If the donor folder is supplied, it reports module GUID matches with donor `.inf` files, which is a first filter only, not a compatibility guarantee.

This public repository contains only source tools and non-private board-address metadata; OEM binaries remain local.

## Full KonaPkg CI with new diagnostic DSDT and VD rootparam

Build: https://github.com/danilafilippkin092-debug/upgraded-memory/actions/runs/43282797748

Result: **Success**. `SM8250_EFI.fd` produced; 2,879,488 bytes. SHA-256:

```
32192426b534ae6003e8fe65934efbb00158fa5eedccfe724ae5114fc0aaca49
```

However this firmware volume still depends on donor DXE binaries from qcom-mtp8250 and other generic ACPI tables. It is **NOT FLASHABLE OR BOOTABLE ON DBY-W09 AS PROVIDED**.

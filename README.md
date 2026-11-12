# Huawei MatePad 11 DBY-W09 — EDK2 research

This repository is a temporary public workspace for the DBY-W09 EDK2 AArch64 compile probe.

**Status:** source-only experimental bring-up. It is NOT flashable firmware, a working UEFI Shell, or a Windows-on-ARM port. No stock firmware dumps or device serial numbers are included.

The complete source archive is stored in `DBY_W09_EDK2_GitHubActions_v2.tar.xz`. GitHub Actions extracts this archive to run source tests and compile a standalone AArch64 EFI diagnostic application. **Never flash the `.efi` artifact to any device.**

Device model: **DBY-W09 (without S)**, board `DBY`, Snapdragon 865 `kona`.

Source projects: [Project Aloha](https://github.com/Project-Aloha/mu_aloha_platforms), [TianoCore EDK2](https://github.com/tianocore/edk2).

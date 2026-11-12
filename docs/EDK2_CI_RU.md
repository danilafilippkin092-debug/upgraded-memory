# EDK2 AArch64 compile / DBY-W09

Workflow на Ubuntu 24.04 использует TianoCore EDK2 tag edk2-stable202508, компилятор gcc-aarch64-linux-gnu / EDK2 GCC5, вывод UEFI_APPLICATION в формате PE/COFF.

Выпускной артефакт: DBY-W09-EDK2-Probe-NOT-FLASHABLE.efi. Это диагностическая сборка, НЕ BootShim, UEFI firmware volume, Android boot image или загрузчик.

Успешный workflow доказывает лишь исправность инструментария сборки. Для настоящего KonaPkg необходимо подготовить ACPI, DXE, APRIORI, DTB, драйверы, карту памяти и подтвердить безопасный путь восстановления устройства.

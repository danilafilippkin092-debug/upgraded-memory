# DBY-W09 экспериментальная сборка — техническая проверка и граница готовности

**Устройство:** Huawei MatePad 11 (2021) DBY-W09, Snapdragon 865/Kona.
**Аппаратный вариант из собственного DTBO:** `DBY_W09_VD` (запись №3).

## Где находятся сборки

- Исходная успешная полная сборка: https://github.com/danilafilippkin092-debug/upgraded-memory/actions/runs/43284723193
- Сборка исправленного `uefiplat.cfg` с проверкой в финальном `.fd`: GitHub Actions → `FULL KonaPkg compile (DBY-W09 experimental, NOT FLASHABLE)`.
- Артефакт: `DBY-W09-FULL-KonaPkg-FD-NOT-FLASHABLE`; внутри `DBY-W09-COMPILE-ONLY-NOT-FLASHABLE.fd` и `manifest.json`.

## Что проверено

- ZIP старой сборки распаковывается без ошибок CRC.
- FVH: `_FVH` на 0x28, FFS2 GUID, длина 0x2BF000 (2 879 488 байт), сумма 16-битных слов заголовка modulo 65536 = 0.
- Структура FFS: firmware DXE, текстовый `uefiplat.cfg` и сжатый контейнер драйверов.
- Оригинальный `uefi_dump.zip` содержит Android Boot v2 с AVB footer; `.fd` не является `boot.img` и не подходит для `fastboot flash boot`.
- Из оригинального `dtbo.img` проверены index=3, `qcom,board-id = <0x200e 0>`, `rootparam boardid <8 2 0 6>`, `DBY_W09_VD`.
- 20 тестов исходников и статическая проверка RAM/DTBO/DSDT в GitHub Actions прошли.

## Ошибка, найденная в успешной старой сборке

При анализе **содержимого** старого FD выяснилось, что запакованный в него `uefiplat.cfg` был от MTP8250 и расходился с исходниками `PlatformMemoryMapLib` и сведениями OEM XBL.

| Поле | Старый донор MTP8250 | Новая кандидатная конфигурация VD |
|---|---|---|
| BOOT INFO | 0x805F0000, 0x10000, BsData | 0x80700000, 0x100000, Reserv |
| IPC SHM | 0x805D0000, 0x20000, BsData (в диапазоне HYP) | Исключена из общего пула |
| XBL Log Buffer | Отсутствует | 0x80884000, 0x10000, Reserv |
| MLVM | 0xB0400000, 0x9000000 | Удалён донорский диапазон |
| HW Reserved | Отсутствует | 0xB0000000, 0x401000, Reserv |
| MCCC MMIO | Отсутствует | 0x090BA000, 0x6000, MmIO |

Новый `tools/patch_uefiplat.py` прекращает сборку при неизвестном формате донорского файла, а `tools/verify_fv.py` проверяет **готовый** бинарник: checksum заголовка, размер, FFS, содержимое секции `uefiplat.cfg` и идентичность исходному скорректированному файлу.

Это устранение конкретного несоответствия данных, **не доказательство запуска или безопасности памяти**.

## Почему не прошивать

1. Несовместимость проприетарных DXE драйверов от `qcom-mtp8250` с настоящей платой не исключена.
2. Диагностическая `DSDT` не содержит устройств Huawei (UFS/USB/display/PMIC).
3. Компилируемый DTBO содержит только `rootparam`, а не полный оригинальный overlay.
4. Не установлен проверенный для DBY-W09 механизм перехода из Huawei ABL в EDK2; прежняя попытка `fastboot boot` отклонена ABL.
5. Отсутствует тест раннего UEFI boot/console на железе и безотказный подтверждённый откат.

**`.fd` — экспериментальный Firmware Volume, не `boot.img`, не `abl.img`, не `xbl.img`, и его нельзя прошивать в разделы планшета.**

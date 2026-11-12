# Аппаратная проверка Huawei MatePad 11 DBY-W09 — вариант VD

В присланном владельцем исходном `dtbo.img` активная по `androidboot.dtbo_idx=3` запись:

| Параметр | Из оригинального DTBO №3 |
|---|---|
| модель | DBY-W09 |
| board name | DBY_W09_VD |
| root overlay board id cells | 08 02 00 06 |
| selector qcom,board-id | 0x200e 0 |
| product | DBY-W09 |
| firmware hardware_version | SH1DBSLM |
| SoC | Kona / SM8250 |

В публичном Linux-проекте `svesnav/linux-dby-w09` приведён другой вариант: `DBY_W09_VG`, board id `0x206a`, rootparam <08 02 09 08>. **Нельзя считать его взаимозаменяемым с VD**, хотя процессор совпадает.

Собственный минимальный исходник: `port/Platforms/KonaPkg/Device/huawei-dby-w09/DeviceTreeBlob/Android/dby-w09-vd-rootparam.dtso`. Он компилируется `dtc`, но **это не готовый dtbo.img**: отсутствуют 136 OEM фрагментов и нет теста через ABL.

Также добавлен **диагностический пустой DSDT** `.../ACPI/DSDT.dsl`. Он заменяет в компиляционном CI неподходящую ACPI-таблицу MTP8250 и специально **не объявляет настоящие устройства**. Для загрузки Windows нужен отдельный полноценно написанный ACPI и совместимые драйверы.

Проверка `tools/check_vd_memory.py` сопоставляет кандидатную EDK2 карту памяти с зарезервированными диапазонами исходного DTB + `/proc/iomem`. Отчётная память не заменяет аппаратное тестирование: неизвестные TrustZone carveouts и MMIO всё ещё возможны.

**Ни образ `.fd`, ни `.dtbo`, ни `.aml` из этого проекта нельзя прошивать на планшет.**

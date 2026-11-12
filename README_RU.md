# Huawei MatePad 11 DBY-W09 — EDK2 / Snapdragon 865 (Kona)

**Аппаратная модель: DBY-W09, без S.** В системной cmdline встречается `devmodel=DBY-W09S`: это только строка прошивки.

Этот репозиторий содержит исходники и средства тестирования EDK2 для изучения возможности портирования UEFI/Windows ARM64 на Huawei MatePad 11. **Готового UEFI, Windows ARM64 и прошиваемого Android boot.img здесь нет.**

## Состояние

- Подтверждено: `ro.product.board=DBY`, `ro.board.platform=kona`, `ro.boot.hardware=qcom`.
- Root/Android работает; `verifiedbootstate=orange`; ABL отклонял прежний `fastboot boot` с `Load Error`.
- Активный DTBO index = 3, профиль `DBY_W09_VD`; не путать с публичным примером `DBY_W09_VG`.
- OEM XBL UEFI FV: `0x9FC00000 + 0x00300000`; дефолт Project Aloha sm8250: `0x9FC41000 + 0x002BF000`. Адреса НЕ подтверждены для загрузки пересобранной прошивки.
- Порт `port/Platforms/KonaPkg/Device/huawei-dby-w09` — **непроверенная заготовка**; отсутствуют `APRIORI.inc`, `DXE.inc`, `DXE.dsc.inc`, OEM-контрольные файлы, корректные ACPI/DTB, подтвержденный способ загрузки.

## GitHub Actions

Вкладка **Actions** → **EDK2 AArch64 compile (Huawei DBY-W09 probe)** → **Run workflow**.

Workflow использует `edk2-stable202508` (TianoCore), `gcc-aarch64-linux-gnu`, архитектуру `AARCH64` и конфигурацию `edk2-probe/DBY_W09_ProbePkg`.

Артефакт `DBY-W09-EDK2-Probe-NOT-FLASHABLE.efi` — только исполняемый UEFI_APPLICATION для проверки компилятора, linker и PE/COFF. **Не прошивать, не запускать через fastboot, не использовать вместо boot.img.**

Для проверки исходников:

```bash
python3 tools/audit.py
python3 -m unittest discover -s tests -v
```

## Интеграция с Project Aloha

На Linux:

```bash
git clone https://github.com/Project-Aloha/mu_aloha_platforms.git
python3 tools/stage.py --upstream ./mu_aloha_platforms --dry-run
python3 tools/stage.py --upstream ./mu_aloha_platforms --apply
```

`stage.py` переносит только кандидатные исходники, не генерирует boot image, не запускает команды записи на планшет.

**Подробности:** `docs/EDK2_CI_RU.md`, `docs/BUILD_STATUS_RU.md`, `docs/UPSTREAM_INTEGRATION_RU.md`, `docs/SAFETY_RU.md`.

## Исходные проекты

- https://github.com/Project-Aloha/mu_aloha_platforms
- https://github.com/tianocore/edk2
- https://github.com/svesnav/linux-dby-w09

Личные дампы `boot.img`, `xbl.img`, `abl.img`, серийные номера и иные идентификаторы не публикуются.

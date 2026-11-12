# Статус DBY-W09 EDK2

Подтверждено пользователем: **Huawei MatePad 11 DBY-W09**, плата DBY, платформа kona, Qualcomm qcom, Linux 4.19.81+.

Прошивка сообщает `devmodel=DBY-W09S`, но это не корректировка заявленной модели.

- Active DTBO index = 3; name DBY_W09_VD.
- Stock XBL OEM FV 0x9FC00000 + 0x300000.
- Project Aloha upstream SM8250 default 0x9FC41000 + 0x2BF000.
- Память, ACPI, DTB, DXE и аппаратная инициализация не проверены.
- GitHub Actions собирает исключительно пробное AArch64 EFI-приложение.
- Полный KonaPkg EDK2 для DBY-W09 НЕ собран.
- UEFI Shell и Windows ARM64 НЕ запущены.
- Любой сгенерированный из этих исходников образ нельзя считать безопасным для прошивки.

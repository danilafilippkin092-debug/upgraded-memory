# Интеграция с Project Aloha

Исследовательская папка: port/Platforms/KonaPkg/Device/huawei-dby-w09

Общий Kona.dsc требует: DXE.dsc.inc, PcdsFixedAtBuild.dsc.inc, PlatformMemoryMapLib.inf, PlatformConfigurationMapLib.inf.

Общий Kona.fdf требует: APRIORI.inc, DXE.inc, Binaries/RawFiles/uefiplat.cfg.

Эти аппаратно-специфичные файлы не включены, поэтому полный EDK2 KonaPkg для DBY-W09 НЕ СКОМПИЛИРОВАН.

Не использовать файлы от чужих Snapdragon 865 устройств, пока не доказано аппаратное соответствие.

Активный DTBO index = 3, board = DBY_W09_VD; firmware cmdline devmodel=DBY-W09S не меняет аппаратную модель DBY-W09 по уточнению владельца.

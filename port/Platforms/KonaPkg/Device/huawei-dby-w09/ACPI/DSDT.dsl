// SPDX-License-Identifier: BSD-2-Clause-Patent
// DBY-W09 diagnostic-only DSDT: does NOT describe working Huawei peripherals.
// Replaces a wrong-device Qualcomm MTP8250 DSDT during compile checking.
// Do not boot a device or OS using this table.
DefinitionBlock ("", "DSDT", 2, "HUAWEI", "DBYW09", 0x00000001)
{
    Scope (\_SB)
    {
        Device (DBY0)
        {
            Name (_HID, "HUA0001")
            Name (_UID, Zero)
            Name (_STA, Zero)
        }
    }
}

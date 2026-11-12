import json
import unittest
from pathlib import Path

from tools.check_vd_memory import ROOT, rows, validate

DEVICE=ROOT/"port/Platforms/KonaPkg/Device/huawei-dby-w09"

class VdHardwareTests(unittest.TestCase):
    def test_valid_stock_memory_reserved(self):
        report=validate()
        self.assertEqual(report["board_variant"],"DBY_W09_VD")
        self.assertGreater(report["stock_protected_ranges"],25)
    def test_reject_bad_boot_info_allocator(self):
        data=rows()
        for entry in data:
            if entry["name"].strip()=="BOOT INFO":
                entry["typ"]="BsData"
                break
        with self.assertRaises(AssertionError):
            validate(rows_in=data)
    def test_reject_overlap_with_dtb_reserved(self):
        data=rows()
        for entry in data:
            if entry["name"].strip()=="DXE Heap":
                entry["start"]=0x9c000000
                break
        with self.assertRaises(AssertionError):
            validate(rows_in=data)
    def test_reject_wrong_variant(self):
        profile=json.loads((ROOT/"profiles/dby-w09-vd-reserved.json").read_text())
        profile["board_variant"]="DBY_W09_VG"
        with self.assertRaises(AssertionError):
            validate(profile=profile)
    def test_rootparam_matches_stock_overlay_index3(self):
        s=(DEVICE/"DeviceTreeBlob/Android/dby-w09-vd-rootparam.dtso").read_text()
        for required in (
            "qcom,board-id = <0x200e 0>",
            "qcom,boardid = <0x08 0x02 0x00 0x06>",
            'qcom,board_name = "DBY_W09_VD"',
            'qcom,product_name = "DBY-W09"'
        ):
            self.assertIn(required,s)
        self.assertNotIn("DBY_W09_VG",s)
    def test_diagnostic_dsdt_does_not_fake_peripherals(self):
        s=(DEVICE/"ACPI/DSDT.dsl").read_text()
        self.assertIn('DefinitionBlock ("", "DSDT"',s)
        self.assertIn("Name (_STA, Zero)",s)
        self.assertNotIn("OperationRegion",s)
    def test_map_matches_fd_size(self):
        volume=[x for x in rows() if x["name"].strip()=="UEFI FD"]
        self.assertEqual((volume[0]["start"],volume[0]["end"]),(0x9fc41000,0x9ff00000))

if __name__=="__main__":
    unittest.main()

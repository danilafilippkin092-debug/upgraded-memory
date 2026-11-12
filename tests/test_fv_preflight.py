import unittest
from tools.patch_uefiplat import check,patch
from tools.verify_fv import inspect_fv

DONOR="""[Config]
Version = 3
MaxMemoryRegions = 74
[MemoryMap]
0x805D0000, 0x00020000, "IPC SHM",           AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK_XN
0x805F0000, 0x00010000, "BOOT INFO",         AddMem, SYS_MEM, SYS_MEM_CAP, BsData, WRITE_BACK_XN
0x80600000, 0x00100000, "MPSS EFS",          AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN
0x80860000, 0x00020000, "AOP CMD DB",        AddMem, MEM_RES, UNCACHEABLE, Reserv, UNCACHED_UNBUFFERED_XN
0xB0400000, 0x09000000, "MLVM",              AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN
[RegisterMap]
0x08800000, 0x00200000, "PERIPH_SS",         AddDev, MMAP_IO, UNCACHEABLE, MmIO,   NS_DEVICE
"""

class FirmwarePreflightTests(unittest.TestCase):
    def test_donor_cfg_rejected(self):
        with self.assertRaises(ValueError):
            check(DONOR)
    def test_donor_patch_and_check(self):
        final=patch(DONOR)
        rows=check(final)
        self.assertEqual(len(rows),7)
        self.assertIn("0x80700000",final)
        self.assertLess(final.index('"MPSS EFS"'),final.index('"BOOT INFO"'))
        self.assertIn("0x80884000",final)
        self.assertIn("0x090BA000",final)
        self.assertNotIn('0x805F0000',final)
        self.assertNotIn('"MLVM"',final)
    def test_reject_unsorted_ddr_map(self):
        final=patch(DONOR)
        good='0x80600000, 0x00100000, "MPSS EFS",          AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN'
        next='0x80700000, 0x00100000, "BOOT INFO",         AddMem, SYS_MEM, SYS_MEM_CAP, Reserv, WRITE_BACK_XN'
        bad=final.replace(good+'\n'+next,next+'\n'+good)
        self.assertNotEqual(bad,final)
        with self.assertRaises(ValueError):
            check(bad)
    def test_reject_overlapping_ddr_regions(self):
        final=patch(DONOR)
        overlapping=final.replace('0x80700000, 0x00100000, "BOOT INFO"',
                                  '0x80680000, 0x00100000, "BOOT INFO"')
        with self.assertRaises(ValueError):
            check(overlapping)
    def test_refuse_silent_repeat(self):
        with self.assertRaises(ValueError):
            patch(patch(DONOR))
    def test_reject_bad_firmware(self):
        with self.assertRaises(ValueError):
            inspect_fv(b"ANDROID!"+bytes(128))
    def test_fv_checksum_must_be_checked(self):
        with self.assertRaises(ValueError):
            inspect_fv(bytes(0x2bf000))

if __name__=="__main__":
    unittest.main()

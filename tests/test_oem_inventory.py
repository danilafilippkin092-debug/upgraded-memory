import struct
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from tools.oem_dxe_inventory import pe_machine, inventory

class OemInventoryTests(unittest.TestCase):
    def test_pe_aarch64_header(self):
        blob=bytearray(256)
        blob[:2]=b"MZ"
        struct.pack_into("<I",blob,0x3c,0x80)
        blob[0x80:0x84]=b"PE\0\0"
        struct.pack_into("<H",blob,0x84,0xaa64)
        struct.pack_into("<H",blob,0x80+24+68,11)
        self.assertEqual(pe_machine(bytes(blob)),(0xaa64,11))
    def test_metadata_only_inventory(self):
        blob=bytearray(256)
        blob[:2]=b"MZ"
        struct.pack_into("<I",blob,0x3c,0x80)
        blob[0x80:0x84]=b"PE\0\0"
        struct.pack_into("<H",blob,0x84,0xaa64)
        struct.pack_into("<H",blob,0x80+24+68,11)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"test-private.zip"
            with ZipFile(p,"w") as z:
                z.writestr("OEM_FV/PE32/UFSDxe__11111111-2222-3333-4444-555555555555.efi",bytes(blob))
            report=inventory(p)
            self.assertEqual(report["module_count"],1)
            self.assertEqual(report["aarch64_verified"],1)
            self.assertTrue(report["modules"][0]["priority_review"])
            self.assertNotIn("bytes_blob",report["modules"][0])
    def test_non_pe_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"bad.zip"
            with ZipFile(p,"w") as z:
                z.writestr("OEM_FV/PE32/UFSDxe__11111111-2222-3333-4444-555555555555.efi",b"not pe")
            with self.assertRaises(ValueError):
                inventory(p)

if __name__=="__main__":unittest.main()

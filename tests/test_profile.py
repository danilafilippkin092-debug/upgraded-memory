import json
import tempfile
import unittest
from pathlib import Path
from tools.audit import ROOT,audit
from tools.stage import stage

class PortTests(unittest.TestCase):
    def test_profile(self):
        p=json.loads((ROOT/'profiles/dby-w09.json').read_text())
        d=p['device']
        self.assertEqual(d['model_confirmed_by_owner'],'DBY-W09')
        self.assertEqual(d['firmware_cmdline_devmodel'],'DBY-W09S')
        self.assertEqual(d['dtbo_active_index'],3)
        self.assertFalse(p['status']['flashable_image_ready'])
    def test_ci_compilation_assets(self):
        self.assertTrue((ROOT/'edk2-probe/DBY_W09_ProbePkg/DBY_W09_ProbePkg.dsc').is_file())
        self.assertTrue((ROOT/'.github/workflows/edk2-aarch64-compile.yml').is_file())
        self.assertFalse((ROOT/'local-assets').exists())
    def test_fd_bounds(self):
        u=json.loads((ROOT/'profiles/dby-w09.json').read_text())['uefi_addresses']
        a=int(u['aloha_sm8250_default_base'],16)
        size=int(u['aloha_sm8250_default_size'],16)
        self.assertLessEqual(a+size,int(u['oem_fd_base'],16)+int(u['oem_fd_size'],16))
    def test_staging_no_device_actions(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            (p/'Platforms/KonaPkg').mkdir(parents=True)
            (p/'Platforms/KonaPkg/Kona.dsc').touch()
            (p/'Platforms/KonaPkg/Kona.fdf').touch()
            (p/'build_uefi.py').touch()
            stage(p,apply=False)
            self.assertFalse((p/'Platforms/KonaPkg/Device/huawei-dby-w09').exists())
    def test_audit(self):
        self.assertEqual(audit(),0)

if __name__=='__main__': unittest.main()

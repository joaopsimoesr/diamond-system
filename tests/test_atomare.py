"""Testes do gerador de IDs Atomare.

Roda com: python3 -m unittest discover -s tests -v
Usa apenas a biblioteca padrão e dados fictícios.
"""

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ["atomare_core.py", "atomare_zid_generator.py"]

CLUSTER_RE = re.compile(r"^[A-Z]\.\d{3}\.\d{6}\.\d{6}\.\d{3}$")
NODE_ID_RE = r"[A-Z]+-[0-9A-Z]+"


def load(script):
    spec = importlib.util.spec_from_file_location(Path(script).stem, ROOT / script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(script, *args, stdin=None):
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class TestFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load("atomare_core.py")

    def test_to_base36(self):
        self.assertEqual(self.mod.to_base36(0), "0")
        self.assertEqual(self.mod.to_base36(35), "Z")
        self.assertEqual(self.mod.to_base36(36), "10")
        self.assertEqual(int(self.mod.to_base36(123456789), 36), 123456789)

    def test_cluster_id_format(self):
        cid = self.mod.generate_cluster_id(state="222", type_char="P")
        self.assertRegex(cid, CLUSTER_RE)
        self.assertTrue(cid.startswith("P.222."))

    def test_node_block_without_content(self):
        block = self.mod.generate_nod_id_block(prefix="abc")
        self.assertRegex(
            block,
            rf'^<span id="(ABC-[0-9A-Z]+)" class="nod-start"></span> \^\1$',
        )

    def test_node_block_wraps_content(self):
        block = self.mod.generate_nod_id_block(prefix="NOD", content="  Texto fictício.  \n")
        lines = block.split("\n")
        self.assertEqual(len(lines), 3)
        self.assertRegex(lines[0], rf'^<span id="{NODE_ID_RE}" class="nod-start"></span>$')
        self.assertEqual(lines[1], "Texto fictício.")
        self.assertRegex(lines[2], rf'^<span class="nod-end"></span> \^{NODE_ID_RE}$')

    def test_safe_backup_creates_bak(self):
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "nota-ficticia.md"
            note.write_text("conteúdo fictício", encoding="utf-8")
            self.mod.safe_backup(str(note))
            bak = Path(str(note) + ".bak")
            self.assertTrue(bak.exists())
            self.assertEqual(bak.read_text(encoding="utf-8"), "conteúdo fictício")


class TestCLI(unittest.TestCase):
    def test_cluster_command(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                out = run(script, "cluster", "--state", "111", "--type", "N")
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertRegex(out.stdout, CLUSTER_RE)

    def test_node_command_with_pipe(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                out = run(script, "node", "--prefix", "IDEIA", stdin="Ação de exemplo")
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertIn("Ação de exemplo", out.stdout)
                self.assertRegex(out.stdout, r'id="IDEIA-[0-9A-Z]+"')

    def test_node_command_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            note = os.path.join(tmp, "nota.md")
            Path(note).write_text("x", encoding="utf-8")
            out = run("atomare_core.py", "node", "--filepath", note, stdin="")
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertTrue(os.path.exists(note + ".bak"))

    def test_missing_command_fails(self):
        out = run("atomare_core.py")
        self.assertNotEqual(out.returncode, 0)


if __name__ == "__main__":
    unittest.main()

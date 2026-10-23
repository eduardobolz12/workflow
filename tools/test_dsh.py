#!/usr/bin/env python3
"""Autoteste do DSH v0 — roda contra um projeto-fixture com git de verdade."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DSH = Path(__file__).resolve().with_name("dsh.py")
PY = sys.executable

SPEC = """# 001 - exportar CSV

| CA | Dado | Quando | Entao |
|---|---|---|---|
| CA-1 | pedido pago | exporta | uma linha |
| CA-2 | pedido pendente | exporta | uma linha |
"""

TESTS = """def test_CA1():
    assert False, "nao implementado"


def test_CA2():
    assert False, "nao implementado"
"""

STUB = r'''
import json
import sys
import xml.etree.ElementTree as ET

state = json.load(open("src/stub_state.json", encoding="utf-8"))
failed, passed = state["failed"], state["passed"]
suite = ET.Element("testsuite", tests=str(failed + passed),
                   failures=str(failed), errors="0", skipped="0")
n = 1
for _ in range(failed):
    tc = ET.SubElement(suite, "testcase", classname="acc", name=f"test_CA{n}")
    ET.SubElement(tc, "failure", message="ainda nao")
    n += 1
for _ in range(passed):
    ET.SubElement(suite, "testcase", classname="acc", name=f"test_CA{n}")
    n += 1
ET.ElementTree(suite).write(sys.argv[1])
sys.exit(1 if failed else 0)
'''


def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


class Fixture:
    def __init__(self, root: Path):
        self.root = root
        (root / "docs" / "SPECS").mkdir(parents=True)
        (root / "tests" / "acceptance" / "001").mkdir(parents=True)
        (root / "src").mkdir()
        (root / "docs" / "SPECS" / "001.md").write_text(SPEC, encoding="utf-8")
        (root / "tests" / "acceptance" / "001" / "test_001.py").write_text(TESTS, encoding="utf-8")
        (root / "stub.py").write_text(STUB, encoding="utf-8")
        (root / "src" / "stub_state.json").write_text('{"failed": 2, "passed": 0}', encoding="utf-8")
        (root / ".gitignore").write_text(".dsh/\ndocs/manifesto/\n", encoding="utf-8")
        cfg = {
            "repo": ".",
            "base_branch": "main",
            "acceptance_cmd": [PY, "stub.py", "{report}"],
            "report_path": ".dsh/report-{nnn}.xml",
            "report_format": "junit",
            "runner_configs": ["package.json"],
            "allowed_paths": ["src/", "docs/QA/"],
        }
        (root / "dsh.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        self.git("init", "-b", "main")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        self.git("add", "-A")
        self.git("commit", "-m", "base")

    def git(self, *args):
        r = sh(["git", *args], self.root)
        assert r.returncode == 0, r.stdout + r.stderr
        return r.stdout.strip()

    def dsh(self, *args):
        return sh([PY, str(DSH), "--config", str(self.root / "dsh.json"), *args], self.root)

    def deliver(self, commit_files: dict[str, str], declared_result="verde"):
        self.git("checkout", "-b", "feat/001")
        for name, content in commit_files.items():
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-m", "entrega")
        sha = self.git("rev-parse", "HEAD")
        qa = self.root / "docs" / "QA" / "001.md"
        qa.parent.mkdir(parents=True, exist_ok=True)
        qa.write_text(f"commit: {sha}\nresultado: {declared_result}\n", encoding="utf-8")
        return sha


class DshTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_gate_approves_all_red(self):
        r = self.fx.dsh("gate", "001", "--yes")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.fx.root / "docs" / "manifesto" / "001.sha256").exists())
        qa = (self.fx.root / "docs" / "QA" / "001.md").read_text(encoding="utf-8")
        self.assertIn("Vermelho no gate", qa)

    def test_gate_ignores_runner_cache(self):
        cache = self.fx.root / "tests" / "acceptance" / "001" / "__pycache__"
        cache.mkdir()
        (cache / "test_001.cpython-312-pytest.pyc").write_bytes(b"\x00fake")
        r = self.fx.dsh("gate", "001", "--yes")
        self.assertEqual(r.returncode, 0, r.stderr)
        man = json.loads((self.fx.root / "docs" / "manifesto" / "001.sha256")
                         .read_text(encoding="utf-8"))
        self.assertFalse(any("__pycache__" in k for k in man["files"]))

    def test_gate_accepts_trx_report(self):
        stub = (
            "import json, sys\n"
            "import xml.etree.ElementTree as ET\n"
            'state = json.load(open("src/stub_state.json", encoding="utf-8"))\n'
            'run = ET.Element("TestRun")\n'
            'res = ET.SubElement(run, "Results")\n'
            'for i in range(state["failed"]):\n'
            '    ET.SubElement(res, "UnitTestResult", testName=f"CA{i+1}", outcome="Failed")\n'
            'for i in range(state["passed"]):\n'
            '    ET.SubElement(res, "UnitTestResult", testName=f"CA{i+1}", outcome="Passed")\n'
            "ET.ElementTree(run).write(sys.argv[1])\n"
            'sys.exit(1 if state["failed"] else 0)\n'
        )
        (self.fx.root / "stub_trx.py").write_text(stub, encoding="utf-8")
        cfgp = self.fx.root / "dsh.json"
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        cfg["acceptance_cmd"] = [PY, "stub_trx.py", "{report}"]
        cfg["report_path"] = ".dsh/report-{nnn}.trx"
        cfg["report_format"] = "trx"
        cfgp.write_text(json.dumps(cfg), encoding="utf-8")
        r = self.fx.dsh("gate", "001", "--yes")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("2 testes, 2 falhas", r.stdout)

    def test_gate_rejects_partial_green(self):
        (self.fx.root / "src" / "stub_state.json").write_text('{"failed": 1, "passed": 1}',
                                                             encoding="utf-8")
        r = self.fx.dsh("gate", "001", "--yes")
        self.assertEqual(r.returncode, 2)
        self.assertIn("passam antes do build", r.stderr)
        # gate rejeitado nao pode deixar manifesto que legitime a entrega
        self.assertFalse((self.fx.root / "docs" / "manifesto" / "001.sha256").exists())

    def test_gate_rejects_traceability_gap(self):
        spec = self.fx.root / "docs" / "SPECS" / "001.md"
        spec.write_text(SPEC + "| CA-3 | sem teste | x | y |\n", encoding="utf-8")
        r = self.fx.dsh("gate", "001", "--yes")
        self.assertEqual(r.returncode, 2)
        self.assertIn("rastreabilidade", r.stderr)

    def test_verify_confirms_delivery(self):
        self.assertEqual(self.fx.dsh("gate", "001", "--yes").returncode, 0)
        self.fx.deliver({
            "src/app.py": "print('ok')\n",
            "src/stub_state.json": '{"failed": 0, "passed": 2}',
        })
        r = self.fx.dsh("verify", "001")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        qa = (self.fx.root / "docs" / "QA" / "001.md").read_text(encoding="utf-8")
        self.assertIn("entrega confirmada", qa)

    def test_verify_detects_tampered_test(self):
        self.assertEqual(self.fx.dsh("gate", "001", "--yes").returncode, 0)
        self.fx.deliver({"src/stub_state.json": '{"failed": 0, "passed": 2}'})
        test = self.fx.root / "tests" / "acceptance" / "001" / "test_001.py"
        test.write_text(TESTS + "\ndef test_CA1_extra():\n    assert True\n", encoding="utf-8")
        r = self.fx.dsh("verify", "001")
        self.assertEqual(r.returncode, 2)
        self.assertIn("adulterado", r.stderr)

    def test_verify_detects_commit_mismatch(self):
        self.assertEqual(self.fx.dsh("gate", "001", "--yes").returncode, 0)
        sha = self.fx.deliver({"src/stub_state.json": '{"failed": 0, "passed": 2}'})
        qa = self.fx.root / "docs" / "QA" / "001.md"
        qa.write_text("commit: 0000000\nresultado: verde\n", encoding="utf-8")
        r = self.fx.dsh("verify", "001")
        self.assertEqual(r.returncode, 2)
        self.assertIn("commit divergente", r.stderr)

    def test_verify_flags_out_of_scope_diff(self):
        self.assertEqual(self.fx.dsh("gate", "001", "--yes").returncode, 0)
        self.fx.deliver({
            "src/stub_state.json": '{"failed": 0, "passed": 2}',
            "outro.txt": "arquivo alheio\n",
        })
        r = self.fx.dsh("verify", "001")
        self.assertEqual(r.returncode, 1)
        qa = (self.fx.root / "docs" / "QA" / "001.md").read_text(encoding="utf-8")
        self.assertIn("escopo estourado", qa)

    def test_verify_fails_when_regression_breaks(self):
        cfgp = self.fx.root / "dsh.json"
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        cfg["regression_cmd"] = [PY, "-c", "import sys; sys.exit(1)"]
        cfgp.write_text(json.dumps(cfg), encoding="utf-8")
        self.assertEqual(self.fx.dsh("gate", "001", "--yes").returncode, 0)
        self.fx.deliver({"src/stub_state.json": '{"failed": 0, "passed": 2}'})
        r = self.fx.dsh("verify", "001")
        self.assertEqual(r.returncode, 2)
        self.assertIn("regressao", r.stderr)

    def test_verify_uses_files_declared_in_spec(self):
        spec = self.fx.root / "docs" / "SPECS" / "001.md"
        spec.write_text(SPEC + "\n## Arquivos que serao tocados\n- `src/app.py`\n", encoding="utf-8")
        self.fx.git("add", "-A")
        self.fx.git("commit", "-m", "spec declara arquivos")
        self.assertEqual(self.fx.dsh("gate", "001", "--yes").returncode, 0)
        self.fx.deliver({
            "src/app.py": "print('ok')\n",
            "src/stub_state.json": '{"failed": 0, "passed": 2}',
        })
        r = self.fx.dsh("verify", "001")
        self.assertEqual(r.returncode, 1)
        qa = (self.fx.root / "docs" / "QA" / "001.md").read_text(encoding="utf-8")
        self.assertIn("escopo estourado", qa)

    def test_metrics_and_note(self):
        r = self.fx.dsh("metrics", "001", "--rota", "normal", "--cas", "2", "--voltas", "0",
                        "--tempo", "45", "--gatilhos", "", "--obs", "primeira")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = self.fx.dsh("note", "atrito: stub lento")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        lines = (self.fx.root / "docs" / "metricas.csv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("fatia", lines[0])
        self.assertIn("atrito: stub lento", lines[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)

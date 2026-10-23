#!/usr/bin/env python3
"""DSH v0 — gate, verify, metrics.

Implementa o manual de operacao v0 (congelado). Somente biblioteca padrao:
o shell desta maquina nao tem HTTPS, entao `pip install` nao e uma opcao.

Uso:
    python tools/dsh.py gate 001
    python tools/dsh.py verify 001
    python tools/dsh.py metrics 001 --rota normal --cas 2 ...
    python tools/dsh.py note "atrito: pytest 6min lento"

Toda configuracao vem de dsh.json (ver README na funcao build_default_config).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

CONFIG_NAME = "dsh.json"
DEFAULT_CONFIG = {
    "repo": ".",
    "base_branch": "main",
    "spec": "docs/SPECS/{nnn}.md",
    "acceptance_dir": "tests/acceptance/{nnn}",
    "runner_configs": ["pytest.ini", "pyproject.toml", "package.json", "vitest.config.ts"],
    "acceptance_cmd": ["python", "-m", "pytest", "-q", "--junitxml={report}"],
    "report_path": ".dsh/report-{nnn}.xml",
    "report_format": "junit",
    "start_cmd": None,
    "base_url": None,
    "ready_timeout_s": 30,
    "regression_cmd": None,
    "allowed_paths": ["src/", "app/", "lib/", "tests/unit/", "docs/QA/"],
    "manifest_dir": "docs/manifesto",
    "qa_file": "docs/QA/{nnn}.md",
    "metrics_file": "docs/metricas.csv",
}

METRICS_COLUMNS = [
    "fatia", "rota", "CAs", "voltas", "tempo_min", "gatilhos", "contestacoes",
    "contestacoes_procedentes", "defeitos_escapados", "burla_detectada", "observacao",
]

QA_BEGIN = "<!-- dsh:begin {nnn} -->"
QA_END = "<!-- dsh:end {nnn} -->"

# ruido que nao faz parte do oraculo: cache de runner, bytecode e dependencias
NOISE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
              "node_modules", ".git", ".venv"}
NOISE_SUFFIX = {".pyc", ".pyo", ".pyd"}


def is_noise(path: Path) -> bool:
    """Exclui cache/bytecode: eles mudam sozinhos e fariam o manifesto mentir."""
    return path.suffix.lower() in NOISE_SUFFIX or any(part in NOISE_DIRS for part in path.parts)


class DshError(Exception):
    pass


# ----------------------------------------------------------------- utilidades

def load_config(path: str | None) -> dict:
    cfg = dict(DEFAULT_CONFIG)
    p = Path(path or CONFIG_NAME)
    if p.exists():
        cfg.update(json.loads(p.read_text(encoding="utf-8-sig")))
    return cfg


def repo_root(cfg: dict) -> Path:
    return Path(cfg["repo"]).resolve()


def expand(value: str, nnn: str, report: str) -> str:
    return value.replace("{nnn}", nnn).replace("{report}", report)


def sha256_file(path: Path) -> str:
    """Hash estavel: normaliza CRLF, senao o autocrlf do git reprova todo worktree."""
    data = path.read_bytes()
    try:
        data = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    except UnicodeDecodeError:
        pass
    return hashlib.sha256(data).hexdigest()


def run(cmd: list[str], cwd: Path, timeout: int = 1800) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                          timeout=timeout, errors="replace")
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def git(cfg: dict, *args: str) -> str:
    rc, out = run(["git", *args], repo_root(cfg), timeout=120)
    if rc != 0:
        raise DshError(f"git {' '.join(args)} falhou:\n{out}")
    return out.strip()


# ------------------------------------------------------------------- manifesto

def manifest_for(root: Path, cfg: dict, nnn: str) -> dict[str, str]:
    """Hash dos arquivos protegidos, relativo a `root` (repo ou worktree)."""
    acc = root / expand(cfg["acceptance_dir"], nnn, "")
    if not acc.exists():
        raise DshError(f"pasta de aceitacao nao existe: {acc}")
    spec = root / expand(cfg["spec"], nnn, "")
    if not spec.exists():
        raise DshError(f"spec nao existe: {spec}")
    paths = [p for p in acc.rglob("*") if p.is_file() and not is_noise(p)] + [spec]
    for name in cfg.get("runner_configs") or []:
        f = root / name
        if f.is_file():
            paths.append(f)
    report = (root / expand(cfg["report_path"], nnn, "")).resolve()
    files: dict[str, str] = {}
    for p in paths:
        if p.resolve() == report:
            continue
        files[str(p.resolve().relative_to(root)).replace("\\", "/")] = sha256_file(p)
    return files


def build_manifest(cfg: dict, nnn: str) -> dict:
    root = repo_root(cfg)
    return {"slice": nnn, "created": datetime.now(timezone.utc).isoformat(),
            "files": manifest_for(root, cfg, nnn)}


def manifest_path(cfg: dict, nnn: str) -> Path:
    return repo_root(cfg) / cfg["manifest_dir"] / f"{nnn}.sha256"


def write_manifest(cfg: dict, nnn: str, man: dict) -> Path:
    path = manifest_path(cfg, nnn)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(man, indent=2), encoding="utf-8")
    return path


def _diff_manifests(old: dict, new: dict) -> tuple[dict, dict, list[str]]:
    changed = {k: (old[k], new[k]) for k in old if k in new and old[k] != new[k]}
    added = {k: new[k] for k in new if k not in old}
    removed = [k for k in old if k not in new]
    return changed, added, removed


def _stored_manifest(cfg: dict, nnn: str) -> dict:
    path = manifest_path(cfg, nnn)
    if not path.exists():
        raise DshError(f"manifesto ausente: {path} (rode o gate antes)")
    return json.loads(path.read_text(encoding="utf-8-sig"))["files"]


def compare_manifest(cfg: dict, nnn: str) -> tuple[dict, dict, list[str]]:
    old = _stored_manifest(cfg, nnn)
    new = build_manifest(cfg, nnn)["files"]
    return _diff_manifests(old, new)


def compare_manifest_at(root: Path, cfg: dict, nnn: str) -> tuple[dict, dict, list[str]]:
    old = _stored_manifest(cfg, nnn)
    new = manifest_for(root, cfg, nnn)
    return _diff_manifests(old, new)


# ---------------------------------------------------------------- rastreabilidade

CA_RE = re.compile(r"CA[-_ ]?(\d+)", re.IGNORECASE)


def ca_ids_in_text(text: str) -> set[int]:
    return {int(m.group(1)) for m in CA_RE.finditer(text)}


def parse_spec_cas(spec: Path) -> dict[int, str]:
    rows: dict[int, str] = {}
    for line in spec.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        ids = ca_ids_in_text(cells[0])
        if ids:
            rows[next(iter(ids))] = s
    return rows


def parse_test_cas(acc: Path) -> dict[int, str]:
    found: dict[int, str] = {}
    for p in sorted(acc.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in {".py", ".ts", ".js", ".tsx", ".jsx", ".mjs"}:
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
            for ca in ca_ids_in_text(line):
                found.setdefault(ca, f"{p.name}:{n}: {line.strip()[:160]}")
    return found


# --------------------------------------------------------------------- relatorio

def parse_report(cfg: dict, report: Path) -> dict:
    if not report.exists():
        raise DshError(f"relatorio de testes ausente: {report}\n"
                       "a suite de aceitacao precisa gerar relatorio "
                       "(ex.: pytest --junitxml, vitest --reporter=json --outputFile)")
    fmt = (cfg.get("report_format") or "junit").lower()
    if fmt == "junit":
        root = ET.parse(report).getroot()
        suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
        tests = sum(int(s.get("tests", 0)) for s in suites)
        failed = sum(int(s.get("failures", 0)) + int(s.get("errors", 0)) for s in suites)
        skipped = sum(int(s.get("skipped", 0)) for s in suites)
        return {"tests": tests, "failed": failed, "skipped": skipped,
                "passed": tests - failed - skipped}
    if fmt == "vitest":
        data = json.loads(report.read_text(encoding="utf-8"))
        if "numTotalTests" in data:
            tests = int(data.get("numTotalTests", 0))
            failed = int(data.get("numFailedTests", 0))
            passed = int(data.get("numPassedTests", 0))
            return {"tests": tests, "failed": failed, "skipped": tests - passed - failed,
                    "passed": passed}
        results = [a for tr in data.get("testResults", [])
                   for a in tr.get("assertionResults", [])]
        failed = sum(1 for a in results if a.get("status") == "failed")
        passed = sum(1 for a in results if a.get("status") == "passed")
        return {"tests": len(results), "failed": failed,
                "skipped": len(results) - failed - passed, "passed": passed}
    raise DshError(f"report_format desconhecido: {fmt}")


def run_acceptance(cfg: dict, cwd: Path, nnn: str) -> tuple[int, str, dict]:
    report = cwd / expand(cfg["report_path"], nnn, "")
    report.parent.mkdir(parents=True, exist_ok=True)
    if report.exists():
        report.unlink()
    cmd = [expand(part, nnn, str(report.relative_to(cwd)).replace("\\", "/"))
           for part in cfg["acceptance_cmd"]]
    rc, out = run(cmd, cwd)
    if not report.exists():
        raise DshError(
            f"o comando nao gerou relatorio em {report}\n"
            f"comando: {' '.join(cmd)}\n"
            f"saida:\n{out.strip()[-3000:]}")
    counts = parse_report(cfg, report)
    return rc, out, counts


# ------------------------------------------------------------------- arquivo QA

def qa_path(cfg: dict, nnn: str) -> Path:
    return repo_root(cfg) / expand(cfg["qa_file"], nnn, "")


def upsert_block(cfg: dict, nnn: str, title: str, body: str) -> None:
    path = qa_path(cfg, nnn)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    begin, end = QA_BEGIN.format(nnn=nnn), QA_END.format(nnn=nnn)
    block = f"{begin}\n## {title}\n\n{body.rstrip()}\n\n{end}"
    if begin in text and end in text:
        pre = text.split(begin)[0]
        post = text.split(end, 1)[1]
        text = pre + block + post
    else:
        text = (text.rstrip() + "\n\n" if text.strip() else "") + block + "\n"
    path.write_text(text, encoding="utf-8")


def read_qa_field(cfg: dict, nnn: str, field: str) -> str | None:
    path = qa_path(cfg, nnn)
    if not path.exists():
        return None
    m = re.search(rf"^{re.escape(field)}\s*:\s*(\S+)", path.read_text(encoding="utf-8-sig"),
                  re.IGNORECASE | re.MULTILINE)
    return m.group(1) if m else None


# ----------------------------------------------------------------------- gate

def cmd_gate(a: argparse.Namespace) -> int:
    cfg = load_config(a.config)
    repo = repo_root(cfg)
    nnn = a.slice
    spec_ids = parse_spec_cas(repo / expand(cfg["spec"], nnn, ""))
    test_ids = parse_test_cas(repo / expand(cfg["acceptance_dir"], nnn, ""))
    if not spec_ids:
        raise DshError("nenhum CA encontrado na tabela da spec (formato: | CA-1 | dado | ... |)")
    missing = sorted(set(spec_ids) - set(test_ids))
    orphan = sorted(set(test_ids) - set(spec_ids))
    if missing or orphan:
        raise DshError("rastreabilidade falhou\n"
                       f"  CA na spec sem teste: {missing or '-'}\n"
                       f"  teste sem CA na spec: {orphan or '-'}")

    man = build_manifest(cfg, nnn)

    rc, out, counts = run_acceptance(cfg, repo, nnn)
    print(f"[gate] aceitacao: {counts['tests']} testes, {counts['failed']} falhas, "
          f"{counts['passed']} verdes")
    problems = []
    if counts["tests"] == 0:
        problems.append("a suite nao coletou nenhum teste")
    if counts["passed"] > 0:
        problems.append(f"{counts['passed']} teste(s) ja passam antes do build")
    if rc == 0:
        problems.append("a suite saiu com codigo 0 (esperado: vermelho)")
    if problems:
        raise DshError("vermelho nao provado:\n  - " + "\n  - ".join(problems))

    upsert_block(cfg, nnn, "Vermelho no gate",
                 f"commit: {git(cfg, 'rev-parse', 'HEAD')}\n"
                 f"resultado: {counts['failed']}/{counts['tests']} falhas\n\n"
                 f"```\n{out.strip()[-8000:]}\n```")

    show_approval_markdown(spec_ids, test_ids, repo / expand(cfg["acceptance_dir"], nnn, ""))
    if not a.yes:
        if not sys.stdin.isatty():
            raise DshError("gate nao aprovado: rode interativamente ou use --yes")
        if input("Aprova? [s/n] ").strip().lower() != "s":
            raise DshError("gate reprovado pelo humano; nada avanca")

    # so grava o manifesto depois do vermelho provado e da aprovacao humana:
    # gate rejeitado nao pode deixar manifesto que legitime a entrega.
    mpath = write_manifest(cfg, nnn, man)
    print(f"[gate] manifesto: {mpath.relative_to(repo)} ({len(man['files'])} arquivos)")

    state = {"slice": nnn, "gate": "approved", "commit": git(cfg, "rev-parse", "HEAD"),
             "at": datetime.now(timezone.utc).isoformat()}
    manifest_path(cfg, nnn).with_suffix(".state.json").write_text(
        json.dumps(state, indent=2), encoding="utf-8")
    print("[gate] aprovado e registrado")
    return 0


def test_block(acc: Path, ca: int) -> str | None:
    """Imprime o bloco de teste inteiro que contem o CA (para a tela do gate)."""
    pat = re.compile(rf"CA[-_ ]?{ca}\b", re.IGNORECASE)
    for p in sorted(acc.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in {".py", ".ts", ".js", ".tsx", ".jsx", ".mjs"}:
            continue
        lines = p.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        hit = next((i for i, line in enumerate(lines) if pat.search(line)), None)
        if hit is None:
            continue
        start = hit
        while start > 0:
            s = lines[start].lstrip()
            if s.startswith(("def ", "async def ", "it(", "test(", "it.only(", "test.only(")):
                break
            start -= 1
        end = hit + 1
        while end < len(lines) and (not lines[end].strip() or lines[end][:1] in (" ", "\t")):
            end += 1
        return f"{p.name}:{start + 1}\n" + "\n".join(lines[start:end][:30])
    return None


def show_approval_markdown(spec_ids: dict[int, str], test_ids: dict[int, str], acc: Path) -> None:
    print("\n=== APROVACAO DO GATE ===")
    for ca in sorted(spec_ids):
        print(f"\nCA-{ca}")
        print(f"  spec:  {spec_ids[ca][:200]}")
        block = test_block(acc, ca)
        if block:
            print("  teste:\n" + "\n".join("    " + ln for ln in block.splitlines()))
        else:
            print(f"  teste: {test_ids[ca]}")
    print()


# --------------------------------------------------------------------- verify

def cmd_verify(a: argparse.Namespace) -> int:
    cfg = load_config(a.config)
    repo = repo_root(cfg)
    nnn = a.slice

    declared = read_qa_field(cfg, nnn, "commit")
    head = git(cfg, "rev-parse", "HEAD")
    if not declared:
        raise DshError("docs/QA nao declara 'commit:' — entrega invalida")
    if not (head.startswith(declared) or declared.startswith(head)):
        raise DshError(f"commit divergente: QA declara {declared[:12]}, HEAD e {head[:12]}")
    commit = head

    changed, added, removed = compare_manifest(cfg, nnn)
    if changed or added or removed:
        detail = [f"  alterado: {k}" for k in changed] + \
                 [f"  novo: {k}" for k in added] + [f"  removido: {k}" for k in removed]
        upsert_block(cfg, nnn, "Prova do DSH",
                     "resultado: FALHA\nmotivo: oraculo adulterado\n\n" + "\n".join(detail))
        raise DshError("oraculo adulterado (manifesto divergente)\n" + "\n".join(detail))

    tmp = Path(tempfile.mkdtemp(prefix="dsh-verify-"))
    work = tmp / "worktree"
    started = None
    try:
        git(cfg, "worktree", "add", "--detach", str(work), commit)
        changed_w, added_w, removed_w = compare_manifest_at(work, cfg, nnn)
        if changed_w or added_w or removed_w:
            detail = [f"  alterado: {k}" for k in changed_w] + \
                     [f"  novo: {k}" for k in added_w] + [f"  removido: {k}" for k in removed_w]
            upsert_block(cfg, nnn, "Prova do DSH",
                         "resultado: FALHA\nmotivo: oraculo adulterado no commit\n\n"
                         + "\n".join(detail))
            raise DshError("oraculo adulterado no commit verificado\n" + "\n".join(detail))

        if cfg.get("start_cmd"):
            started = start_app(cfg, work)
        rc, out, counts = run_acceptance(cfg, work, nnn)
        reg = run_regression(cfg, work)
        if reg is not None and reg[0] != 0:
            upsert_block(cfg, nnn, "Prova do DSH",
                         f"commit: {commit}\nresultado: FALHA\nmotivo: regressao quebrada\n\n"
                         f"```\n{reg[1].strip()[-8000:]}\n```")
            raise DshError("suite de regressao falhou (teste antigo quebrou)")

        declared_result = (read_qa_field(cfg, nnn, "resultado") or "").lower()
        if rc == 0 and counts["failed"] == 0:
            mine = "verde"
        else:
            mine = "vermelho"
        if declared_result and declared_result != mine:
            verdict = f"divergencia de ambiente ({declared_result} local x {mine} DSH)"
            note = "nao conta como volta"
        elif mine == "vermelho":
            verdict, note = "falha real", "conta como volta"
        else:
            verdict, note = "entrega confirmada", ""

        diff_check = check_diff(cfg, commit,
                                declared_files(repo / expand(cfg["spec"], nnn, "")))

        body = [
            f"commit: {commit}",
            f"resultado: {mine}",
            f"testes: {counts['tests']} ({counts['failed']} falhas, {counts['passed']} verdes)",
            f"veredito: {verdict}" + (f" — {note}" if note else ""),
            f"manifesto: integro",
            f"diff: {diff_check}",
            "",
            "```",
            out.strip()[-8000:],
            "```",
        ]
        upsert_block(cfg, nnn, "Prova do DSH", "\n".join(body))
        print(f"[verify] {verdict}")
        return 0 if mine == "verde" and diff_check == "confinado" else 1
    finally:
        if started is not None:
            stop_app(started)
        subprocess.run(["git", "worktree", "remove", "--force", str(work)],
                       cwd=str(repo), capture_output=True, text=True)
        shutil.rmtree(tmp, ignore_errors=True)


def check_diff(cfg: dict, commit: str, declared: list[str] | None = None) -> str:
    base = cfg.get("base_branch") or "main"
    rc, out = run(["git", "diff", "--name-only", f"{base}...{commit}"], repo_root(cfg))
    if rc != 0:
        return "indeterminado (base ausente)"
    allowed = declared or list(cfg.get("allowed_paths") or [])
    qa_prefix = cfg["qa_file"].split("{")[0]
    bad = []
    for name in [n for n in out.splitlines() if n.strip()]:
        if name.startswith(qa_prefix):
            continue
        if not any(name == p or name.startswith(p) for p in allowed):
            bad.append(name)
    return "confinado" if not bad else "escopo estourado: " + ", ".join(bad)


def declared_files(spec: Path) -> list[str]:
    """Le a lista de arquivos declarados na secao 'Arquivos ...' da spec."""
    if not spec.exists():
        return []
    lines = spec.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    out: list[str] = []
    grab = False
    for line in lines:
        s = line.strip()
        low = s.lower()
        if re.match(r"^#+\s*arquivos", low) or low.startswith("arquivos que ser"):
            grab = True
            continue
        if not grab:
            continue
        if s.startswith("#"):
            break
        if not s:
            if out:
                break
            continue
        for token in re.findall(r"`([^`]+)`", s):
            out.append(token.strip())
    return [p for p in out if p and not p.endswith("/")]


def run_regression(cfg: dict, cwd: Path) -> tuple[int, str] | None:
    cmd = cfg.get("regression_cmd")
    if not cmd:
        return None
    return run([expand(c, "", "") for c in cmd], cwd, timeout=3600)


def stop_app(proc) -> None:
    if proc is None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    else:
        proc.terminate()


def start_app(cfg: dict, cwd: Path):
    cmd = [expand(c, "", "") for c in cfg["start_cmd"]]
    proc = subprocess.Popen(cmd, cwd=str(cwd), stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    url = cfg.get("base_url") or ""
    deadline = time.time() + int(cfg.get("ready_timeout_s", 30))
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return proc
        except urllib.error.URLError:
            time.sleep(0.5)
        except Exception:
            time.sleep(0.5)
    return proc


# -------------------------------------------------------------------- metricas

def cmd_metrics(a: argparse.Namespace) -> int:
    cfg = load_config(a.config)
    path = repo_root(cfg) / cfg["metrics_file"]
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(METRICS_COLUMNS)
        w.writerow([a.slice, a.rota, a.cas, a.voltas, a.tempo, a.gatilhos or "",
                    a.contestacoes, a.procedentes, a.escapados, a.burla, a.obs or ""])
    print(f"[metrics] linha anexada em {path.name}")
    return 0


def cmd_note(a: argparse.Namespace) -> int:
    cfg = load_config(a.config)
    path = repo_root(cfg) / cfg["metrics_file"]
    if not path.exists():
        raise DshError("metricas.csv ainda nao existe")
    rows = list(csv.DictReader(path.open(encoding="utf-8", newline="")))
    if not rows:
        raise DshError("metricas.csv vazio")
    rows[-1]["observacao"] = (rows[-1].get("observacao") or "") + f"; nota: {a.text}"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=METRICS_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print("[metrics] nota registrada")
    return 0


# ------------------------------------------------------------------------ cli

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="dsh", description="DSH v0 (gate/verify/metrics)")
    ap.add_argument("--config", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gate", help="valida oraculo e prova o vermelho")
    g.add_argument("slice")
    g.add_argument("--yes", action="store_true", help="aprova sem perguntar")
    g.set_defaults(func=cmd_gate)

    v = sub.add_parser("verify", help="verifica a entrega em worktree limpo")
    v.add_argument("slice")
    v.set_defaults(func=cmd_verify)

    m = sub.add_parser("metrics", help="anexa linha em metricas.csv")
    for name in ("slice", "rota", "cas", "voltas", "tempo"):
        m.add_argument(f"--{name}" if name != "slice" else "slice")
    for name in ("gatilhos", "obs"):
        m.add_argument(f"--{name}")
    for name in ("contestacoes", "procedentes", "escapados"):
        m.add_argument(f"--{name}", default=0, type=int)
    m.add_argument("--burla", default="nao")
    m.set_defaults(func=cmd_metrics)

    n = sub.add_parser("note", help="anexa observacao a ultima linha")
    n.add_argument("text")
    n.set_defaults(func=cmd_note)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except DshError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())





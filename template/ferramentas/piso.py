import json, sys
import xml.etree.ElementTree as ET

estado = json.load(open("ferramentas/piso_estado.json", encoding="utf-8"))
failed, passed = estado["failed"], estado["passed"]
suite = ET.Element("testsuite", tests=str(failed + passed),
                   failures=str(failed), errors="0", skipped="0")
n = 1
for _ in range(failed):
    tc = ET.SubElement(suite, "testcase", classname="piso", name=f"test_CA{n}")
    ET.SubElement(tc, "failure", message="piso falhando de proposito")
    n += 1
for _ in range(passed):
    ET.SubElement(suite, "testcase", classname="piso", name=f"test_CA{n}")
    n += 1
ET.ElementTree(suite).write(sys.argv[1])
sys.exit(1 if failed else 0)

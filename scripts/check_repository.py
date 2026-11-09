"""Check Python syntax and the shipped example schema without running models.

Uses only the standard library; does not import the workflow scripts or load
pickle models. Passing does not certify numerical correctness or reproducibility.
"""

import ast
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ["BGA", "PGA", "Geology", "Elevation", "Slope", "Curvature", "Aspect"]
EXPECTED += [f"LS8-Band {i}" for i in range(1, 8)] + ["Mmax"]


def main():
    for name in ["1. Training_Mmax.py", "2. Mmax_export_maps.py", "mmax_prediction.py",
                 "tests/test_prediction.py",
                 "scripts/make_synthetic_mapping_example.py", "scripts/check_repository.py"]:
        path = ROOT / name
        ast.parse(path.read_text(encoding="utf-8-sig"), filename=name)
        print(f"Syntax OK: {name}")
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(ROOT / "Example data" / "EQ_sample_Mmax.xlsx") as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            tree = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = ["".join(node.itertext()) for node in tree.findall("m:si", ns)]
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        first_row = sheet.find("m:sheetData", ns)[0]
        header = []
        for cell in first_row:
            value = cell.find("m:v", ns)
            if cell.get("t") == "s":
                header.append(strings[int(value.text)])
            elif cell.get("t") == "inlineStr":
                header.append("".join(cell.find("m:is", ns).itertext()))
            else:
                header.append(value.text if value is not None else "")
        if header != EXPECTED:
            raise ValueError(f"Training example schema differs from documentation: {header}")
    print("Training example header OK (14 predictors and Mmax)")
    print("Checks passed. Full training, mapping and scientific validation were not run.")


if __name__ == "__main__":
    main()

"""Create a deterministic 20-by-20 synthetic mapping input (standard library only).

Values are illustrative, not observations or scientifically validated predictors.
The output does not overwrite the original Sample_area.txt file.
"""

import csv
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "Example data" / "Sample_area_synthetic.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    columns = ["OBJECTID", "X", "Y", "BGA", "PGA", "Geology", "Elevation",
               "Slope", "Curvature", "Aspect"]
    columns += [f"LS8_Band_{i}" for i in range(1, 8)]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        for row in range(20):
            for col in range(20):
                writer.writerow([
                    row * 20 + col + 1, 500000 + 30 * col, 1700000 - 30 * row,
                    -25 + col / 10, 75 + row / 10, 1 + (row + col) % 9,
                    100 + row * 5 + col, 5 + col / 2, (row - 10) / 20,
                    (row * 18 + col) % 360,
                    *[7000 + band * 500 + row * 20 + col * 10 for band in range(1, 8)],
                ])
    print(f"Created {output} (400 synthetic cells; not study data)")


if __name__ == "__main__":
    main()

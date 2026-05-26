from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from internal.domain.models import CTGMetadata, ExtractedSeries
from pkg.ctg.reconstructor import read_metadata
from pkg.timeseries.exporter import save_ctg_csv, to_dataframe


class CtgCsvTests(unittest.TestCase):
    def test_csv_contains_metadata_header(self) -> None:
        series = ExtractedSeries(
            time_min=np.array([0.0, 0.2, 0.4], dtype=np.float32),
            fhr_bpm=np.array([140.0, 141.0, 139.5], dtype=np.float32),
            toco_units=np.array([5.0, 5.5, 5.2], dtype=np.float32),
        )
        metadata = CTGMetadata(
            px_per_minute=47.3,
            px_per_unit_fhr=2.1,
            px_per_unit_toco=1.8,
            fhr_y_min=300,
            fhr_y_max=30,
            toco_y_min=520,
            toco_y_max=360,
            separator_y_top=330,
            separator_y_bottom=352,
            time_start="09:00",
            duration_minutes=20.0,
            paper_speed_cm_per_min=1.0,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "test.csv"
            save_ctg_csv(
                path=csv_path,
                dataframe=to_dataframe(series),
                metadata=metadata,
                source_image=Path("sample.png"),
            )

            text = csv_path.read_text(encoding="utf-8")
            self.assertIn("# type: CTG", text)
            self.assertIn("time_min,fhr_bpm,toco_units", text)

            parsed = read_metadata(csv_path)
            self.assertEqual(parsed.get("source"), "sample.png")
            self.assertEqual(parsed.get("time_start"), "09:00")


if __name__ == "__main__":
    unittest.main()

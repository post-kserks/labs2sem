from __future__ import annotations

import unittest

import numpy as np

from internal.domain.models import AxisSpec, TimeSpec
from pkg.timeseries.series_builder import build_extracted_series


class SeriesBuilderTests(unittest.TestCase):
    def test_build_extracted_series_returns_expected_length(self) -> None:
        width = 200
        upper_pixels = np.linspace(10, 90, width, dtype=np.float32)
        lower_pixels = np.linspace(80, 20, width, dtype=np.float32)

        upper_axis = AxisSpec(name="upper", unit="u", min_value=0.0, max_value=100.0)
        lower_axis = AxisSpec(name="lower", unit="u", min_value=0.0, max_value=50.0)
        time_spec = TimeSpec(duration_minutes=10.0, start_timestamp=None, sampling_step_seconds=1.0)

        series = build_extracted_series(
            upper_y_pixels=upper_pixels,
            lower_y_pixels=lower_pixels,
            upper_panel_height=100,
            lower_panel_height=100,
            upper_axis=upper_axis,
            lower_axis=lower_axis,
            time_spec=time_spec,
        )

        self.assertEqual(len(series.time_seconds), 601)
        self.assertEqual(len(series.upper_values), 601)
        self.assertEqual(len(series.lower_values), 601)
        self.assertAlmostEqual(series.time_seconds[-1], 600.0, places=3)


if __name__ == "__main__":
    unittest.main()

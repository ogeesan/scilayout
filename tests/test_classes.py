import unittest
from collections.abc import Generator

import pytest

from scilayout.classes import PanelAxes, SciFigure


@pytest.fixture
def fig() -> Generator[SciFigure, None, None]:
    scifig = SciFigure()
    yield scifig
    scifig.close()


class TestAddPanel:
    def test_add_panel_returns_panelaxes(self, fig):
        panel = fig.add_panel((1, 2, 5, 6), method="extent")
        assert isinstance(panel, PanelAxes)

    def test_panel_location_bbox(self, fig):
        panel = fig.add_panel((1, 2, 5, 6), method="extent")
        loc = panel.get_location()
        assert loc[0] == pytest.approx(1)
        assert loc[1] == pytest.approx(2)
        assert loc[2] == pytest.approx(5)
        assert loc[3] == pytest.approx(6)

    def test_panel_location_size_method(self, fig):
        panel = fig.add_panel((1, 2, 4, 4), method="bounds")
        loc = panel.get_location()
        assert loc[0] == pytest.approx(1)
        assert loc[1] == pytest.approx(2)
        assert loc[2] == pytest.approx(5)
        assert loc[3] == pytest.approx(6)

    def test_multiple_panels(self, fig):
        panel1 = fig.add_panel((1, 2, 5, 6), method="extent")
        panel2 = fig.add_panel((2, 3, 6, 7), method="extent")
        assert isinstance(panel1, PanelAxes)
        assert isinstance(panel2, PanelAxes)
        assert panel1 != panel2

    def test_kwargs_passed(self, fig):
        panel = fig.add_panel((1, 2, 5, 6), panellabel="a", method="extent")
        assert panel.panellabel is not None
        assert panel.panellabel.text.get_text() == "a"


if __name__ == "__main__":
    unittest.main()

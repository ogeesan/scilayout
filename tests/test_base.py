import matplotlib.image as mpimg
import numpy as np
import pytest
from matplotlib.collections import PathCollection

from scilayout import base


class TestSetFigureSizeCm:
    def test_sets_size_in_inches(self, scifig):
        base.set_figure_size_cm(scifig, 12.7, 5.08)
        assert tuple(scifig.get_size_inches()) == pytest.approx((5, 2))

    def test_scifigure_method(self, scifig):
        scifig.set_size_cm(8, 6)
        assert tuple(scifig.get_size_inches()) == pytest.approx((8 / 2.54, 6 / 2.54))


class TestCreatePanelLocations:
    def test_shape(self):
        result = base.create_panel_locations(0, 0, 10, 10, (2, 3))
        assert result.shape == (2, 3, 4)

    def test_single_panel_fills_the_area(self):
        result = base.create_panel_locations(1, 2, 11, 12, (1, 1))
        assert result[0, 0] == pytest.approx([1, 2, 11, 12])

    def test_panels_are_separated_by_padding(self):
        result = base.create_panel_locations(0, 0, 10.5, 4, (1, 2), pad=0.5)
        left, right = result[0, 0], result[0, 1]
        assert left == pytest.approx([0, 0, 5, 4])
        assert right == pytest.approx([5.5, 0, 10.5, 4])

    def test_rows_are_stacked_downwards(self):
        result = base.create_panel_locations(0, 0, 4, 10.5, (2, 1), pad=0.5)
        assert result[0, 0] == pytest.approx([0, 0, 4, 5])
        assert result[1, 0] == pytest.approx([0, 5.5, 4, 10.5])

    @pytest.mark.parametrize("npanels", [(0, 1), (1, 0), (-1, 2)])
    def test_non_positive_panel_count_raises(self, npanels):
        with pytest.raises(ValueError, match="positive"):
            base.create_panel_locations(0, 0, 10, 10, npanels)


class TestAddCmOverlayGrid:
    def test_returns_axes_and_three_collections(self, scifig):
        ax, one, half, five = base.add_cm_overlay_grid(scifig)
        assert ax in scifig.axes
        for collection in (one, half, five):
            assert isinstance(collection, PathCollection)

    def test_limits_match_figure_size_in_cm_with_inverted_y(self, scifig):
        ax, *_ = base.add_cm_overlay_grid(scifig)
        assert ax.get_xlim() == pytest.approx((0, 13))
        assert ax.get_ylim() == pytest.approx((10, 0))

    def test_explicit_size(self, scifig):
        ax, *_ = base.add_cm_overlay_grid(scifig, width_cm=20, height_cm=4)
        assert ax.get_xlim() == pytest.approx((0, 20))
        assert ax.get_ylim() == pytest.approx((4, 0))

    def test_five_cm_markers_are_sparser(self, scifig):
        _, one, _, five = base.add_cm_overlay_grid(scifig)
        assert len(np.asarray(five.get_offsets())) < len(np.asarray(one.get_offsets()))
        assert np.all(np.asarray(five.get_offsets()) % 5 == 0)


class TestSaveFigure:
    @pytest.mark.parametrize("suffix", [".png", ".svg", ".pdf", ".eps"])
    def test_writes_each_format(self, scifig, tmp_path, suffix):
        scifig.add_panel((1, 1, 5, 4), method="bounds")
        path = tmp_path / f"figure{suffix}"
        base.savefigure(scifig, path)
        assert path.exists()
        assert path.stat().st_size > 0

    def test_accepts_string_path(self, scifig, tmp_path):
        path = tmp_path / "figure.png"
        base.savefigure(scifig, str(path))
        assert path.exists()

    def test_png_has_expected_pixel_size_without_tight_crop(self, scifig, tmp_path):
        path = tmp_path / "figure.png"
        base.savefigure(scifig, path, dpi=100, bbox=None)
        height, width = mpimg.imread(path).shape[:2]
        assert width == pytest.approx(13 / 2.54 * 100, abs=1)
        assert height == pytest.approx(10 / 2.54 * 100, abs=1)

    def test_png_is_transparent_by_default(self, scifig, tmp_path):
        path = tmp_path / "figure.png"
        base.savefigure(scifig, path, dpi=50, bbox=None)
        assert mpimg.imread(path)[0, 0, 3] == 0

    def test_png_can_be_opaque(self, scifig, tmp_path):
        path = tmp_path / "figure.png"
        base.savefigure(scifig, path, dpi=50, bbox=None, transparent_png=False)
        assert mpimg.imread(path)[0, 0, 3] == 1

    def test_svg_keeps_text_as_text(self, scifig, tmp_path):
        ax = scifig.add_panel((1, 1, 5, 4), method="bounds")
        ax.set_title("findable-title")
        path = tmp_path / "figure.svg"
        base.savefigure(scifig, path)
        assert "findable-title" in path.read_text()

    def test_pdf_metadata_is_scrubbed_for_version_control(self, scifig, tmp_path):
        path = tmp_path / "figure.pdf"
        base.savefigure(scifig, path)
        assert b"CreationDate" not in path.read_bytes()

    def test_overwrites_by_default(self, scifig, tmp_path):
        path = tmp_path / "figure.png"
        path.write_bytes(b"old")
        base.savefigure(scifig, path)
        assert path.read_bytes() != b"old"

    def test_overwriting_is_logged_not_printed(self, scifig, tmp_path, caplog, capsys):
        path = tmp_path / "figure.png"
        path.write_bytes(b"old")
        with caplog.at_level("INFO", logger="scilayout.base"):
            base.savefigure(scifig, path)
        assert "Overwriting" in caplog.text
        assert capsys.readouterr().out == ""

    def test_can_forbid_overwriting(self, scifig, tmp_path):
        path = tmp_path / "figure.png"
        path.write_bytes(b"old")
        with pytest.raises(FileExistsError):
            base.savefigure(scifig, path, allow_overwrite=False)
        assert path.read_bytes() == b"old"

    def test_unknown_format_raises(self, scifig, tmp_path):
        with pytest.raises(ValueError, match="not recognised"):
            base.savefigure(scifig, tmp_path / "figure.jpg")

    def test_export_method(self, scifig, tmp_path):
        path = tmp_path / "figure.svg"
        scifig.export(path)
        assert path.exists()

    def test_export_passes_options_through(self, scifig, tmp_path):
        path = tmp_path / "figure.png"
        path.write_bytes(b"old")
        with pytest.raises(FileExistsError):
            scifig.export(path, allow_overwrite=False)

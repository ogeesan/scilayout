from types import SimpleNamespace

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

import scilayout
from scilayout import style
from scilayout.classes import FigureText, PanelAxes, PanelLabel, SciFigure


class TestSciFigure:
    def test_is_a_matplotlib_figure(self, scifig):
        assert isinstance(scifig, Figure)

    def test_figure_function_forwards_arguments(self):
        fig = scilayout.figure(figsize=(3, 2))
        try:
            assert tuple(fig.get_size_inches()) == (3, 2)
        finally:
            plt.close(fig)

    def test_figure_function_rejects_figureclass(self):
        with pytest.raises(ValueError, match="FigureClass"):
            scilayout.figure(FigureClass=Figure)

    def test_set_size_cm(self, scifig):
        scifig.set_size_cm(10, 5)
        assert tuple(scifig.get_size_inches()) == pytest.approx((10 / 2.54, 5 / 2.54))

    def test_resizing_keeps_panels_at_their_location_in_cm(self, scifig):
        ax = scifig.add_panel((2, 3, 4, 2), method="bounds", panellabel="a")
        scifig.set_size_cm(20, 15)
        assert ax.get_location() == pytest.approx((2, 3, 6, 5))
        scifig.set_size_cm(8, 6)
        assert ax.get_location() == pytest.approx((2, 3, 6, 5))

    def test_resizing_moves_panel_labels_with_the_panel(self, scifig):
        ax = scifig.add_panel((2, 3, 4, 2), method="bounds", panellabel="a")
        assert ax.panellabel is not None
        before = ax.panellabel.get_location()
        scifig.set_size_cm(20, 15)
        assert ax.panellabel.get_location() == pytest.approx(before)

    def test_resizing_with_no_panels_works(self, scifig):
        scifig.set_size_cm(20, 15)
        assert tuple(scifig.get_size_inches()) == pytest.approx((20 / 2.54, 15 / 2.54))

    def test_panels_are_added_to_the_figure(self, scifig):
        ax = scifig.add_panel((1, 1, 3, 3), method="bounds")
        assert ax in scifig.axes

    def test_clear_removes_panels(self, scifig):
        scifig.add_panel((1, 1, 3, 3), method="bounds")
        scifig.clear()
        assert scifig.axes == []

    def test_clf_removes_panels(self, scifig):
        scifig.add_panel((1, 1, 3, 3), method="bounds")
        scifig.clf()
        assert scifig.axes == []

    def test_close_closes_the_window(self):
        fig = scilayout.figure()
        number = fig.number
        fig.close()
        assert number not in plt.get_fignums()

    def test_cm_transform_matches_figure_size(self, scifig):
        # 13 x 10 cm: the upper right corner is (13, 0) cm
        assert tuple(scifig.transCM.transform((13, 0))) == pytest.approx((1, 1))


class TestWindowLocation:
    def test_only_pixels_supported(self, scifig):
        with pytest.raises(NotImplementedError, match="px"):
            scifig.set_location(1, 1, method="cm")

    def test_non_qt_backend_not_implemented(self, scifig):
        with pytest.raises(NotImplementedError, match="not implemented"):
            scifig.set_location(10, 20)

    def test_qt_backend_without_window_manager_raises(self, scifig, monkeypatch):
        monkeypatch.setattr("scilayout.classes.mpl.get_backend", lambda: "QtAgg")
        monkeypatch.setattr(scifig.canvas, "manager", None)
        with pytest.raises(RuntimeError, match="window manager"):
            scifig.set_location(10, 20)

    def test_qt_backend_moves_window_keeping_its_size(self, scifig, monkeypatch):
        calls = []
        window = SimpleNamespace(
            geometry=lambda: SimpleNamespace(getRect=lambda: (0, 0, 640, 480)),
            setGeometry=lambda *args: calls.append(args),
        )
        monkeypatch.setattr("scilayout.classes.mpl.get_backend", lambda: "QtAgg")
        monkeypatch.setattr(scifig.canvas, "manager", SimpleNamespace(window=window))
        scifig.set_location(10, 20)
        assert calls == [(10, 20, 640, 480)]


class TestPanelAxes:
    def test_panel_without_label(self, scifig):
        ax = scifig.add_panel((1, 1, 3, 3), method="bounds")
        assert ax.panellabel is None

    def test_add_label_creates_then_updates(self, scifig):
        ax = scifig.add_panel((1, 1, 3, 3), method="bounds")
        ax.add_label("a")
        first = ax.panellabel
        assert isinstance(first, PanelLabel)
        ax.add_label("b")
        assert ax.panellabel is first
        assert first.text.get_text() == "b"

    def test_add_label_right_alignment_shifts_offset(self, scifig):
        ax = scifig.add_panel((1, 1, 3, 3), method="bounds")
        ax.add_label("a", ha="right")
        assert ax.panellabel is not None
        assert ax.panellabel.xoffset == -1

    def test_clear_removes_label(self, scifig):
        ax = scifig.add_panel((1, 1, 3, 3), method="bounds", panellabel="a")
        assert ax.panellabel is not None
        label_text = ax.panellabel.text
        ax.clear()
        assert ax.panellabel is None
        assert label_text not in ax.texts

    def test_label_follows_panel_when_moved(self, scifig):
        ax = scifig.add_panel((1, 1, 3, 3), method="bounds", panellabel="a")
        assert ax.panellabel is not None
        before = ax.panellabel.get_location()
        ax.set_location((4, 3, 3, 3), method="bounds")
        after = ax.panellabel.get_location()
        assert after[0] - before[0] == pytest.approx(3)
        assert after[1] - before[1] == pytest.approx(2)

    def test_panellabel_anchor_is_the_panel_upper_left(self, scifig):
        ax = scifig.add_panel((2, 3, 3, 3), method="bounds", panellabel="a")
        assert ax.panellabel is not None
        assert tuple(ax.panellabel.anchorlocation) == pytest.approx((2, 3))

    def test_set_offset(self, scifig):
        ax = scifig.add_panel((2, 3, 3, 3), method="bounds", panellabel="a")
        assert ax.panellabel is not None
        ax.panellabel.set_offset(x=-1, y=-0.5)
        assert ax.panellabel.get_location() == pytest.approx((1, 2.5))

    def test_is_panelaxes_instance(self, scifig):
        assert isinstance(scifig.add_panel((1, 1, 3, 3), method="bounds"), PanelAxes)

    def test_wrong_figure_type_not_required(self):
        # PanelAxes works on any matplotlib figure, not just SciFigure
        fig = plt.figure(figsize=(5, 4))
        try:
            ax = PanelAxes(fig, (1, 1, 3, 3), method="bounds")
            assert ax.get_location() == pytest.approx((1, 1, 4, 4))
        finally:
            plt.close(fig)


class TestFigureText:
    def test_positions_text_in_cm_from_upper_left(self, scifig):
        text = FigureText(2, 3, "hello", scifig)
        x, y = text.text.get_position()
        assert x == pytest.approx(2 / 13)
        assert y == pytest.approx(1 - 3 / 10)
        assert text.text.get_text() == "hello"

    def test_set_position(self, scifig):
        text = FigureText(2, 3, "hello", scifig)
        text.set_position(6.5, 5)
        x, y = text.text.get_position()
        assert x == pytest.approx(0.5)
        assert y == pytest.approx(0.5)

    def test_default_font_comes_from_the_style(self, scifig):
        text = FigureText(2, 3, "hello", scifig)
        assert text.text.get_fontsize() == style.params["figuretext.fontsize"]
        assert text.text.get_fontstyle() == style.params["figuretext.fontstyle"]
        assert text.text.get_fontweight() == style.params["figuretext.fontweight"]

    def test_style_changes_apply_to_new_text(self, scifig):
        style.params["figuretext.fontsize"] = 14
        style.params["figuretext.fontstyle"] = "italic"
        style.params["figuretext.fontweight"] = "bold"
        text = FigureText(2, 3, "hello", scifig)
        assert text.text.get_fontsize() == 14
        assert text.text.get_fontstyle() == "italic"
        assert text.text.get_fontweight() == "bold"

    @pytest.mark.parametrize(
        ("kwargs", "getter", "expected"),
        [
            ({"fontsize": 20}, "get_fontsize", 20),
            ({"size": 20}, "get_fontsize", 20),
            ({"fontstyle": "italic"}, "get_fontstyle", "italic"),
            ({"style": "italic"}, "get_fontstyle", "italic"),
            ({"fontweight": "bold"}, "get_fontweight", "bold"),
            ({"weight": "bold"}, "get_fontweight", "bold"),
        ],
    )
    def test_explicit_font_options_beat_the_style(
        self, scifig, kwargs, getter, expected
    ):
        text = FigureText(2, 3, "hello", scifig, **kwargs)
        assert getattr(text.text, getter)() == expected

    def test_kwargs_go_to_text(self, scifig):
        text = FigureText(2, 3, "hello", scifig, fontsize=15)
        assert text.text.get_fontsize() == 15

    def test_remove(self, scifig):
        text = FigureText(2, 3, "hello", scifig)
        text.remove()
        assert text.text not in scifig.texts


def test_scifigure_type_exported():
    assert scilayout.classes.SciFigure is SciFigure

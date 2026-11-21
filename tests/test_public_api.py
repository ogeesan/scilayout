"""Lock in which names are public.

A name is public if it is in ``__all__``. Adding a public class or function to a public
module without exporting it (or deliberately listing it as internal below) fails here,
so the API only grows on purpose.
"""

import importlib
import inspect

import pytest

import scilayout

PUBLIC_MODULES = ["classes", "locations", "scalebars", "stats", "style", "types"]
INTERNAL_MODULES = ["base", "grid"]

# Public-looking names in public modules that are deliberately not exported.
NOT_EXPORTED = {
    "locations": {"resolve_method", "to_extent"},  # method handling, see locations
}

TOP_LEVEL = {
    "FigureText": "classes",
    "LinkedScaleBar": "scalebars",
    "PanelAxes": "classes",
    "PanelLabel": "classes",
    "ScaleBar": "scalebars",
    "SciFigure": "classes",
    "StatsLine": "stats",
}


def module(name: str):
    return importlib.import_module(f"scilayout.{name}")


class TestTopLevel:
    def test_all_names_exist(self):
        for name in scilayout.__all__:
            assert hasattr(scilayout, name), name

    def test_all_is_sorted_and_unique(self):
        assert scilayout.__all__ == sorted(scilayout.__all__)
        assert len(set(scilayout.__all__)) == len(scilayout.__all__)

    def test_exports(self):
        assert set(scilayout.__all__) == {
            *TOP_LEVEL,
            "__version__",
            "figure",
            *PUBLIC_MODULES,
        }

    @pytest.mark.parametrize(("name", "home"), TOP_LEVEL.items())
    def test_classes_are_the_same_objects_as_in_their_modules(self, name, home):
        assert getattr(scilayout, name) is getattr(module(home), name)

    def test_star_import_gives_all(self):
        namespace: dict[str, object] = {}
        exec("from scilayout import *", namespace)
        assert set(namespace) - {"__builtins__"} == set(scilayout.__all__)

    def test_figure_is_the_entry_point(self):
        assert callable(scilayout.figure)
        assert "figure" in scilayout.__all__

    def test_version_is_a_string(self):
        assert isinstance(scilayout.__version__, str)


class TestPublicModules:
    @pytest.mark.parametrize("name", PUBLIC_MODULES)
    def test_all_is_defined_and_valid(self, name):
        mod = module(name)
        assert hasattr(mod, "__all__"), f"scilayout.{name} needs an __all__"
        assert len(set(mod.__all__)) == len(mod.__all__)
        for exported in mod.__all__:
            assert hasattr(mod, exported), exported
            assert not exported.startswith("_"), exported

    @pytest.mark.parametrize("name", PUBLIC_MODULES)
    def test_all_is_sorted(self, name):
        assert module(name).__all__ == sorted(module(name).__all__)

    @pytest.mark.parametrize("name", PUBLIC_MODULES)
    def test_public_definitions_are_exported(self, name):
        mod = module(name)
        defined_here = {
            attr
            for attr, obj in vars(mod).items()
            if not attr.startswith("_")
            and (inspect.isfunction(obj) or inspect.isclass(obj))
            and getattr(obj, "__module__", None) == mod.__name__
        }
        missing = defined_here - set(mod.__all__) - NOT_EXPORTED.get(name, set())
        assert not missing, f"{missing} defined in scilayout.{name} but not in __all__"

    @pytest.mark.parametrize("name", PUBLIC_MODULES)
    def test_exported_classes_and_functions_are_documented(self, name):
        mod = module(name)
        for exported in mod.__all__:
            obj = getattr(mod, exported)
            if (inspect.isfunction(obj) or inspect.isclass(obj)) and (
                obj.__module__ == mod.__name__
            ):
                assert inspect.getdoc(obj), f"{name}.{exported} has no docstring"

    def test_not_exported_names_exist(self):
        for name, names in NOT_EXPORTED.items():
            for attr in names:
                assert hasattr(module(name), attr), f"{name}.{attr}"

    def test_expected_exports(self):
        expected = {
            "classes": {
                "FigureText",
                "LocationCM",
                "PanelAxes",
                "PanelLabel",
                "SciFigure",
            },
            "scalebars": {"LinkedScaleBar", "ScaleBar"},
            "stats": {"StatsLine"},
            "style": {"StyleDictionary", "defaultstyles", "params", "reset", "use"},
            "locations": {
                "CMTransform",
                "LocationMethod",
                "cm_to_fraction",
                "cm_to_inch",
                "fraction_to_cm",
                "inch_to_cm",
                "locationcm_to_position",
            },
            "types": {
                "Bound",
                "BoundCM",
                "BoundFraction",
                "BoundInches",
                "Extent",
                "ExtentCM",
                "ExtentFraction",
                "ExtentInches",
                "centimetres",
                "fraction",
                "inches",
            },
        }
        for name, names in expected.items():
            assert set(module(name).__all__) == names, name


class TestInternalModules:
    @pytest.mark.parametrize("name", INTERNAL_MODULES)
    def test_still_importable(self, name):
        assert module(name) is getattr(scilayout, name)

    @pytest.mark.parametrize("name", INTERNAL_MODULES)
    def test_not_in_public_all(self, name):
        assert name not in scilayout.__all__

    @pytest.mark.parametrize("name", INTERNAL_MODULES)
    def test_documented_as_internal(self, name):
        assert "Internal" in (module(name).__doc__ or "")

    def test_savefigure_still_reachable_for_existing_users(self):
        assert callable(scilayout.base.savefigure)

import json

import pytest

from scilayout import style


class TestParams:
    def test_defaults_match_defaultstyles(self):
        assert dict(style.params) == style.defaultstyles

    def test_set_existing_key(self):
        style.params["panellabel.fontsize"] = 20
        assert style.params["panellabel.fontsize"] == 20

    def test_unknown_key_raises(self):
        with pytest.raises(ValueError, match="Invalid key"):
            style.params["not.a.key"] = 1

    def test_attribute_access_for_simple_keys(self):
        style.params._setitem_bypass("simple", 3)
        assert style.params.simple == 3  # pyright: ignore[reportAttributeAccessIssue]

    def test_missing_attribute_raises_attribute_error(self):
        with pytest.raises(AttributeError, match="nope"):
            style.params.nope  # noqa: B018  # pyright: ignore[reportAttributeAccessIssue]

    def test_hasattr_and_getattr_default_work(self):
        # these rely on AttributeError, not KeyError
        assert not hasattr(style.params, "nope")
        assert getattr(style.params, "nope", "default") == "default"

    def test_can_be_copied_and_pickled(self):
        import copy
        import pickle

        copied = copy.deepcopy(style.params)
        assert dict(copied) == dict(style.params)
        assert dict(pickle.loads(pickle.dumps(style.params))) == dict(style.params)

    def test_bypass_allows_new_keys(self):
        style.params._setitem_bypass("new.key", 1)
        assert style.params["new.key"] == 1

    def test_instances_do_not_share_state(self):
        other = style.StyleDictionary()
        other["panellabel.fontsize"] = 99
        assert style.params["panellabel.fontsize"] != 99

    def test_defaultstyles_not_mutated_by_set(self):
        original = style.defaultstyles["panellabel.fontsize"]
        style.params["panellabel.fontsize"] = original + 5
        assert style.defaultstyles["panellabel.fontsize"] == original


class TestUse:
    def write(self, tmp_path, content):
        path = tmp_path / "style.json"
        path.write_text(json.dumps(content))
        return path

    def test_use_sets_params(self, tmp_path):
        path = self.write(tmp_path, {"panellabel.fontsize": 18, "stats.linewidth": 2})
        style.use(path)
        assert style.params["panellabel.fontsize"] == 18
        assert style.params["stats.linewidth"] == 2

    def test_use_accepts_string_path(self, tmp_path):
        path = self.write(tmp_path, {"panellabel.fontsize": 18})
        style.use(str(path))
        assert style.params["panellabel.fontsize"] == 18

    def test_use_leaves_other_params_alone(self, tmp_path):
        path = self.write(tmp_path, {"panellabel.fontsize": 18})
        style.use(path)
        assert (
            style.params["scalebars.fontsize"]
            == style.defaultstyles["scalebars.fontsize"]
        )

    def test_invalid_keys_raise_and_change_nothing(self, tmp_path):
        path = self.write(tmp_path, {"panellabel.fontsize": 18, "bogus": 1})
        with pytest.raises(ValueError, match="bogus"):
            style.use(path)
        assert (
            style.params["panellabel.fontsize"]
            == style.defaultstyles["panellabel.fontsize"]
        )

    def test_invalid_keys_ignored_when_not_strict(self, tmp_path):
        path = self.write(tmp_path, {"panellabel.fontsize": 18, "bogus": 1})
        style.use(path, allow_only_valid_keys=False)
        assert style.params["panellabel.fontsize"] == 18
        assert "bogus" not in style.params

    def test_custom_params_dictionary(self, tmp_path):
        path = self.write(tmp_path, {"panellabel.fontsize": 18})
        custom = style.StyleDictionary()
        style.use(path, params=custom)
        assert custom["panellabel.fontsize"] == 18
        assert (
            style.params["panellabel.fontsize"]
            == style.defaultstyles["panellabel.fontsize"]
        )

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            style.use(tmp_path / "missing.json")

    def test_malformed_json_raises(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{not json")
        with pytest.raises(json.JSONDecodeError):
            style.use(path)


class TestReset:
    def test_reset_removes_added_keys(self):
        style.params._setitem_bypass("new.key", 1)
        style.reset()
        assert "new.key" not in style.params
        assert dict(style.params) == style.defaultstyles

    def test_reset_restores_defaults(self):
        style.params["panellabel.fontsize"] = 40
        style.params["stats.linecolor"] = "red"
        style.reset()
        assert dict(style.params) == style.defaultstyles


class TestStyleAffectsElements:
    def test_panellabel_case(self, panel):
        style.params["panellabel.case"] = "upper"
        panel.add_label("a")
        assert panel.panellabel is not None
        assert panel.panellabel.text.get_text() == "A"

    def test_panellabel_case_lower(self, panel):
        style.params["panellabel.case"] = "lower"
        panel.add_label("B")
        assert panel.panellabel is not None
        assert panel.panellabel.text.get_text() == "b"

    def test_panellabel_case_none_keeps_text(self, panel):
        panel.add_label("Ab")
        assert panel.panellabel is not None
        assert panel.panellabel.text.get_text() == "Ab"

    def test_panellabel_fontsize(self, panel):
        style.params["panellabel.fontsize"] = 17
        panel.add_label("a")
        assert panel.panellabel is not None
        assert panel.panellabel.text.get_fontsize() == 17

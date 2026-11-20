"""Tests that write figures for viewing are marked ``visual`` automatically."""

import pytest


@pytest.fixture
def picture_dir(output_dir):
    """A fixture that reaches output_dir indirectly, as the layout fixtures do."""
    return output_dir / "somewhere"


def test_a_test_using_output_dir_is_marked_visual(request, output_dir):
    assert request.node.get_closest_marker("visual") is not None


def test_a_test_using_a_fixture_that_uses_output_dir_is_marked_visual(
    request, picture_dir
):
    assert request.node.get_closest_marker("visual") is not None


def test_other_tests_are_not_marked(request):
    assert request.node.get_closest_marker("visual") is None

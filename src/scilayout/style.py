"""Style parameters for the elements scilayout draws.

``scilayout.style.params`` holds the defaults for things like panel labels and
scalebars. Change a parameter directly, or load several from a JSON file with
[`use`][scilayout.style.use]; both affect elements created afterwards. Setting an option when creating an
element (for example ``fontsize`` on a ``ScaleBar``) overrides the parameter for that
element only. [`reset`][scilayout.style.reset] restores the defaults.

Examples
--------
>>> import scilayout
>>> scilayout.style.params["panellabel.fontsize"] = 10
>>> scilayout.style.params["panellabel.fontsize"]
10
>>> scilayout.style.reset()

Notes
-----
All parameters:

| Parameter | Used for |
| --- | --- |
| `panellabel.case` | None keeps the text, "upper" or "lower" changes it |
| `panellabel.font` | font family of panel labels |
| `panellabel.fontsize` | font size of panel labels (pt) |
| `panellabel.fontweight` | font weight of panel labels |
| `panellabel.fontstyle` | font style of panel labels |
| `panellabel.xoffset` | label offset to the right of the panel corner (cm) |
| `panellabel.yoffset` | label offset below the panel corner (cm) |
| `scalebars.fontsize` | default font size of scalebar text (pt) |
| `scalebars.linewidth` | default linewidth of scalebars |
| `scalebars.pad` | default gap between a scalebar's line and its text (cm) |
| `figuretext.fontsize` | default font size of `FigureText` (pt) |
| `figuretext.fontstyle` | default font style of `FigureText` |
| `figuretext.fontweight` | default font weight of `FigureText` |
| `stats.linecolor` | color of `StatsLine` |
| `stats.linewidth` | linewidth of `StatsLine` |
| `stats.drop_amount` | length of a `StatsLine`'s drops, as a fraction of the axes height |
"""

import json
from pathlib import Path
from typing import Any

__all__ = ["StyleDictionary", "defaultstyles", "params", "reset", "use"]

# --- Handle styling of scilayout elements
# This dictionary defines the default styles used across scilayout.
# These can be overridden by the user by using a configuration file using scilayout.style.use(path/to/json) or by modifying the dictionary directly.
# The user can also set the parameters directly in the plotting functions/classes, which will override the stylesheet.
defaultstyles = {
    # classes.py
    # i.e. special cases of text/label styling
    # 'figuretext.font': 'sans-serif',
    "figuretext.fontsize": 8,
    "figuretext.fontstyle": "normal",
    "figuretext.fontweight": "normal",
    "panellabel.case": None,
    "panellabel.font": "sans-serif",
    "panellabel.fontsize": 12,
    "panellabel.fontstyle": "normal",
    "panellabel.fontweight": "bold",
    "panellabel.xoffset": -0.5,
    "panellabel.yoffset": -0.3,
    "scalebars.fontsize": 8,
    "scalebars.linewidth": 1,
    "scalebars.pad": 0.1,
    "stats.linecolor": "black",
    "stats.linewidth": 1,
    "stats.drop_amount": 0.025,
}
"""The default value of every style parameter. Not changed by :func:`use` or by setting a parameter, so it is what :func:`reset` restores."""


class StyleDictionary(dict):
    """A dictionary of style parameters that only accepts the keys it already has.

    Keys are strings like ``"panellabel.fontsize"``. Reading works like a normal
    dictionary, and ``params.key`` also works for keys that are valid Python names.
    Setting an unknown key raises an error, which catches typos.

    """

    # This is like matplotlib.rcParams but not so complicated (and validated) that it does your head in

    def __init__(self) -> None:
        super().__init__(defaultstyles.copy())

    def __setitem__(self, name: str, value: Any) -> None:
        """Set an existing parameter, rejecting unknown keys.

        Parameters
        ----------
        name : str
            The parameter to set.
        value : Any
            Its new value.

        Raises
        ------
        ValueError
            If ``name`` is not an existing parameter.

        """
        # Validate the key
        if name not in self.keys():
            raise ValueError(f"Invalid key: {name}. Can only set existing keys.")
        super().__setitem__(name, value)

    def __reduce__(self) -> tuple[Any, tuple[dict[str, Any]]]:
        """Support ``copy`` and ``pickle``, which can't rebuild the usual way.

        The default rebuilds a dictionary by setting each key on an empty one, which
        this class rejects because it only accepts keys it already has.
        """
        return _restore_style_dictionary, (dict(self),)

    def _setitem_bypass(self, name: str, value: Any) -> None:
        """Set a parameter without checking that the key exists.

        Parameters
        ----------
        name : str
            The parameter to set.
        value : Any
            Its value.

        """
        super().__setitem__(name, value)

    def __getattr__(self, key: str) -> Any:
        """Read a parameter as an attribute.

        Parameters
        ----------
        key : str
            The parameter to read.

        Returns
        -------
        Any
            Its value.

        Raises
        ------
        AttributeError
            If ``key`` is not a parameter. (Not a ``KeyError``: Python's
            ``hasattr``, ``getattr`` with a default, ``copy`` and ``inspect`` rely on
            attribute errors.)

        """
        try:
            return self[key]
        except KeyError:
            msg = f"{type(self).__name__!r} object has no parameter {key!r}"
            raise AttributeError(msg) from None


def _restore_style_dictionary(items: dict[str, Any]) -> StyleDictionary:
    """Rebuild a StyleDictionary with exactly ``items`` (used by copy and pickle)."""
    restored = StyleDictionary()
    dict.clear(restored)
    dict.update(restored, items)
    return restored


params = StyleDictionary()
"""The current style parameters. Read or set them like a dictionary, for example ``params["panellabel.fontsize"] = 10``."""

# --- Config file handling ---


def _load_config(filepath: str | Path) -> dict[str, Any]:
    """Load a configuration file to set parameters.

    Parameters
    ----------
    filepath : str or pathlib.Path
        Path to the JSON configuration file.

    Returns
    -------
    dict
        The parameters in the file.

    """
    # Why JSON and not the same format as matplotlib? Because their implementation is too complicated to replicate here.
    # Fight me.
    with Path(filepath).open() as f:
        config = json.load(f)
    return config


def use(
    filepath: str | Path,
    params: dict[str, Any] = params,
    allow_only_valid_keys: bool = True,
) -> None:
    """Use a configuration file to set parameters.

    Parameters
    ----------
    filepath : str or pathlib.Path
        Path to the JSON configuration file.
    params : dict, optional
        The dictionary to set the parameters in. Defaults to ``scilayout.style.params``.
    allow_only_valid_keys : bool, optional
        If True (default) raise an error when the file has keys that are not already in
        ``params``. If False those keys are ignored.

    Raises
    ------
    ValueError
        If ``allow_only_valid_keys`` is True and the file has unknown keys.

    """
    config = _load_config(filepath)

    if allow_only_valid_keys:
        config_keys = config.keys()
        valid_keys = params.keys()
        failing_keys = []
        for key in config_keys:
            if key not in valid_keys:
                failing_keys.append(key)
        if len(failing_keys) > 0:
            # This error will occur if your configuration file has other options
            # If you're patching in something fresh, you might want to consider setting up some default values using params._setitem() first.
            # For example, if you're adding a new parameter called 'newparam', you could do:
            # params._setitem('newparam', 'defaultvalue')
            raise ValueError(f"Invalid keys in configuration file: {failing_keys}")

    for key in config:
        if key in params:
            # If allow_only_valid_keys is False, this would allow you to have other non-scilayout parameters in the config file
            params[key] = config[key]


def reset() -> None:
    """Reset the parameters to the default values.

    Parameters added with ``params._setitem_bypass`` are removed.
    """
    params.clear()
    for key, value in defaultstyles.items():
        params._setitem_bypass(key, value)

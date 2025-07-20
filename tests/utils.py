import os
import sys
def add_parent_dir_to_sys_path():
    """Add the project root directory to sys.path."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

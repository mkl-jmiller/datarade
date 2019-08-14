from pathlib import Path
import sys

PACKAGE_ROOT = Path(__file__).parent
PROJECT_ROOT = PACKAGE_ROOT.parent
STATIC_FILES_DIR = PACKAGE_ROOT / Path('static_files')

sys.path.insert(0, str(PROJECT_ROOT.absolute()))

from query_tools import endpoints, querysets, datasets

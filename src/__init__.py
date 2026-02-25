"""

"""


from .app import parse_config
from .app.ui import MazeApp
from .mazegen import MazeGenerator, MazeError


__version__ = "1.0.0"
__author__ = "Anaïs and Mario"

__all__ = ["parse_config", "MazeApp", "MazeGenerator", "MazeError"]

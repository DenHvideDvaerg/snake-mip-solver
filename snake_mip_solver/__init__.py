"""
Snake MIP Solver -  Mixed Integer Programming approach to solving Snake logic puzzles.
"""

from .puzzle import SnakePuzzle
from .solver import SnakeSolver
from .generator import SnakePuzzleGenerator

__version__ = "0.3.0"
__all__ = ["SnakePuzzle", "SnakeSolver", "SnakePuzzleGenerator"]

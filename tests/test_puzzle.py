import pytest
from snake_mip_solver import SnakePuzzle


class TestSnakePuzzle:
    """Test cases for SnakePuzzle class."""

    def test_basic_puzzle_creation(self):
        """Test creating a basic puzzle."""
        # Test basic 3x3 puzzle with some constraints
        row_sums = [2, None, 1]  # Row 0 needs 2 cells, row 1 unconstrained, row 2 needs 1 cell
        col_sums = [1, 2, None]  # Col 0 needs 1 cell, col 1 needs 2 cells, col 2 unconstrained
        start_cell = (0, 0)
        end_cell = (2, 2)
        
        puzzle = SnakePuzzle(row_sums=row_sums, col_sums=col_sums, 
                           start_cell=start_cell, end_cell=end_cell)
        assert puzzle is not None
        
        # Test basic properties
        assert puzzle.rows == 3
        assert puzzle.cols == 3
        assert puzzle.row_sums == [2, None, 1]
        assert puzzle.col_sums == [1, 2, None]
        assert puzzle.get_grid_size() == (3, 3)
        assert puzzle.get_start_cell() == (0, 0)
        assert puzzle.get_end_cell() == (2, 2)
        
    def test_puzzle_validation(self):
        """Test puzzle input validation."""
        start_cell = (0, 0)
        end_cell = (2, 2)
        
        # Test invalid dimensions (empty lists)
        with pytest.raises(ValueError, match="Number of rows must be positive"):
            SnakePuzzle([], [1, 2, 3], start_cell, end_cell)
            
        with pytest.raises(ValueError, match="Number of columns must be positive"):
            SnakePuzzle([1, 2, 3], [], start_cell, end_cell)
            
        # Test invalid sum values
        with pytest.raises(ValueError, match="Row 0 sum 5 must be between 0 and 3"):
            SnakePuzzle([5, 1, 1], [1, 1, 1], start_cell, end_cell)
            
        with pytest.raises(ValueError, match="Column 1 sum -1 must be between 0 and 3"):
            SnakePuzzle([1, 1, 1], [1, -1, 1], start_cell, end_cell)
            
        # Test invalid start/end cells
        with pytest.raises(ValueError, match="Start cell .* is out of bounds"):
            SnakePuzzle([1, 1, 1], [1, 1, 1], (3, 0), end_cell)
            
        with pytest.raises(ValueError, match="End cell .* is out of bounds"):
            SnakePuzzle([1, 1, 1], [1, 1, 1], start_cell, (0, 3))
            
        with pytest.raises(ValueError, match="Start cell and end cell cannot be the same"):
            SnakePuzzle([1, 1, 1], [1, 1, 1], (0, 0), (0, 0))
            
    def test_solution_validation(self):
        """Test solution validation."""
        puzzle = SnakePuzzle([2, 1, 2], [1, 3, 1], start_cell=(0, 0), end_cell=(2, 2))
        
        # Actual solution is (0,0), (0,1), (1,1), (2,1), (2,2)

        # Test empty solution
        assert not puzzle.is_valid_solution(set())
        
        # Test solution missing start or end cell
        assert not puzzle.is_valid_solution({(0, 1), (1, 1), (2, 1)})  # Missing start (0,0) and end (2,2)
        
        # Test out of bounds solution
        assert not puzzle.is_valid_solution({(0, 0), (3, 0), (2, 2)})  # row 3 is out of bounds
        assert not puzzle.is_valid_solution({(0, 0), (0, 3), (2, 2)})  # col 3 is out of bounds
        
        # Test the actual valid solution
        valid_solution = {(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)}
        assert puzzle.is_valid_solution(valid_solution)
        
        # Test solution that violates row constraints
        invalid_row_solution = {(0, 0), (1, 1), (2, 2)}  # Row 0 has only 1 cell but needs 2
        assert not puzzle.is_valid_solution(invalid_row_solution)
        
        # Test solution that violates column constraints  
        invalid_col_solution = {(0, 0), (0, 1), (0, 2), (2, 2)}  # Col 1 has only 1 cell but needs 3
        assert not puzzle.is_valid_solution(invalid_col_solution)
        
        # Test disconnected path
        disconnected_solution = {(0, 0), (0, 1), (2, 1), (2, 2)}  # Missing (1,1) - creates gap
        assert not puzzle.is_valid_solution(disconnected_solution)
        
    def test_utility_methods(self):
        """Test utility methods."""
        puzzle = SnakePuzzle([2, None, 1], [1, 2, None], start_cell=(0, 0), end_cell=(2, 2))
        
        # Test get_row_sum
        assert puzzle.get_row_sum(0) == 2
        assert puzzle.get_row_sum(1) is None
        assert puzzle.get_row_sum(2) == 1
        
        with pytest.raises(IndexError):
            puzzle.get_row_sum(3)
            
        # Test get_col_sum
        assert puzzle.get_col_sum(0) == 1
        assert puzzle.get_col_sum(1) == 2
        assert puzzle.get_col_sum(2) is None
        
        with pytest.raises(IndexError):
            puzzle.get_col_sum(3)
            
        # Test start/end cell getters
        assert puzzle.get_start_cell() == (0, 0)
        assert puzzle.get_end_cell() == (2, 2)
        
        # Test helper methods
        assert puzzle.is_within_bounds(0, 0)
        assert puzzle.is_within_bounds(2, 2)
        assert not puzzle.is_within_bounds(-1, 0)
        assert not puzzle.is_within_bounds(3, 0)
        assert not puzzle.is_within_bounds(0, 3)
        
        # Test get_tile_by_offset
        assert puzzle.get_tile_by_offset((1, 1), (-1, 0)) == (0, 1)
        assert puzzle.get_tile_by_offset((0, 0), (-1, 0)) is None  # out of bounds
        
        # Test get_tiles_by_offsets
        adjacent_tiles = puzzle.get_tiles_by_offsets((1, 1), puzzle._orthogonal_offsets)
        expected_adjacent = {(0, 1), (2, 1), (1, 0), (1, 2)}
        assert adjacent_tiles == expected_adjacent
            
    def test_repr(self):
        """Test string representation."""
        puzzle = SnakePuzzle([1, None], [2, 1, None], start_cell=(0, 0), end_cell=(1, 2))
        repr_str = repr(puzzle)
        assert "SnakePuzzle" in repr_str
        assert "rows=2" in repr_str
        assert "cols=3" in repr_str
        assert "start=(0, 0)" in repr_str
        assert "end=(1, 2)" in repr_str
        
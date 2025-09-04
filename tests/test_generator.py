import pytest
from typing import Set, Tuple
from snake_mip_solver import SnakePuzzleGenerator
from snake_mip_solver.puzzle import SnakePuzzle


class TestSnakePuzzleGenerator:
    """Test suite for SnakePuzzleGenerator class."""

    def test_init_without_seed(self):
        """Test generator initialization without seed."""
        generator = SnakePuzzleGenerator()
        assert generator.seed is None

    def test_init_with_seed(self):
        """Test generator initialization with seed."""
        generator = SnakePuzzleGenerator(seed=42)
        assert generator.seed == 42

    def test_generate_basic_valid_puzzle(self):
        """Test basic puzzle generation with valid parameters."""
        generator = SnakePuzzleGenerator(seed=42)
        puzzle, path = generator.generate(rows=6, cols=6, fill_percentage=0.3)

        # Check return types
        assert isinstance(puzzle, SnakePuzzle)
        assert isinstance(path, set)

        # Check path contains tuples
        assert all(isinstance(cell, tuple) and len(cell) == 2 for cell in path)

        # Check minimum path length
        assert len(path) >= 2

        # Check path meets target length
        expected_length = int(6 * 6 * 0.3)
        assert len(path) >= expected_length

    def test_generate_deterministic_with_seed(self):
        """Test that same seed produces same results."""
        generator1 = SnakePuzzleGenerator(seed=42)
        generator2 = SnakePuzzleGenerator(seed=42)

        puzzle1, path1 = generator1.generate(rows=5, cols=5, fill_percentage=0.4)
        puzzle2, path2 = generator2.generate(rows=5, cols=5, fill_percentage=0.4)

        # Same seed should produce identical results
        assert path1 == path2
        assert puzzle1.start_cell == puzzle2.start_cell
        assert puzzle1.end_cell == puzzle2.end_cell
        assert puzzle1.row_sums == puzzle2.row_sums
        assert puzzle1.col_sums == puzzle2.col_sums

    def test_seed_reset_consistency(self):
        """Test that seed is properly reset for consistent generation."""
        generator = SnakePuzzleGenerator(seed=42)

        # Generate first puzzle
        puzzle1, path1 = generator.generate(rows=5, cols=5, fill_percentage=0.3)

        # Generate second puzzle (should be same due to seed reset)
        puzzle2, path2 = generator.generate(rows=5, cols=5, fill_percentage=0.3)

        # Should be identical due to seed reset
        assert path1 == path2
        assert puzzle1.start_cell == puzzle2.start_cell
        assert puzzle1.end_cell == puzzle2.end_cell

    def test_generate_different_seeds_produce_different_results(self):
        """Test that different seeds produce different results."""
        generator1 = SnakePuzzleGenerator(seed=42)
        generator2 = SnakePuzzleGenerator(seed=999)

        puzzle1, path1 = generator1.generate(rows=6, cols=6, fill_percentage=0.3)
        puzzle2, path2 = generator2.generate(rows=6, cols=6, fill_percentage=0.3)

        # Different seeds should (very likely) produce different results
        assert path1 != path2

    def test_generate_various_grid_sizes(self):
        """Test generation with various grid sizes."""
        generator = SnakePuzzleGenerator(seed=42)

        test_cases = [
            (3, 3, 0.5),
            (4, 6, 0.3),
            (8, 8, 0.25),
            (10, 5, 0.4),
        ]

        for rows, cols, fill_pct in test_cases:
            puzzle, path = generator.generate(rows, cols, fill_pct)

            # Check basic properties
            expected_min_length = int(rows * cols * fill_pct)
            assert len(path) >= expected_min_length

            # Check all cells are within bounds
            for r, c in path:
                assert 0 <= r < rows
                assert 0 <= c < cols

            # Check path is valid solution
            assert puzzle.is_valid_solution(path)


    def test_generate_various_fill_percentages(self):
        """Test generation with various fill percentages."""
        generator = SnakePuzzleGenerator(seed=42)

        fill_percentages = [0.1, 0.2, 0.3, 0.4, 0.5]

        for fill_pct in fill_percentages:
            puzzle, path = generator.generate(rows=8, cols=8, fill_percentage=fill_pct)

            expected_min_length = int(8 * 8 * fill_pct)
            assert len(path) >= expected_min_length

            # Check path is valid solution
            assert puzzle.is_valid_solution(path)

    def test_puzzle_constraints_match_path(self):
        """Test that puzzle constraints correctly reflect the generated path."""
        generator = SnakePuzzleGenerator(seed=42)
        puzzle, path = generator.generate(rows=5, cols=5, fill_percentage=0.4)

        # Calculate expected row and column sums
        expected_row_sums = [0] * 5
        expected_col_sums = [0] * 5

        for r, c in path:
            expected_row_sums[r] += 1
            expected_col_sums[c] += 1

        # Check that puzzle constraints match
        assert puzzle.row_sums == expected_row_sums
        assert puzzle.col_sums == expected_col_sums

    def test_start_and_end_cells_in_path(self):
        """Test that start and end cells are part of the generated path."""
        generator = SnakePuzzleGenerator(seed=42)
        puzzle, path = generator.generate(rows=6, cols=6, fill_percentage=0.3)

        assert puzzle.start_cell in path
        assert puzzle.end_cell in path
        assert puzzle.start_cell != puzzle.end_cell

    # Parameter validation tests
    def test_generate_invalid_rows(self):
        """Test generation with invalid row counts."""
        generator = SnakePuzzleGenerator()

        with pytest.raises(ValueError, match="Rows and columns must be positive"):
            generator.generate(rows=0, cols=5, fill_percentage=0.3)

        with pytest.raises(ValueError, match="Rows and columns must be positive"):
            generator.generate(rows=-1, cols=5, fill_percentage=0.3)

    def test_generate_invalid_cols(self):
        """Test generation with invalid column counts."""
        generator = SnakePuzzleGenerator()

        with pytest.raises(ValueError, match="Rows and columns must be positive"):
            generator.generate(rows=5, cols=0, fill_percentage=0.3)

        with pytest.raises(ValueError, match="Rows and columns must be positive"):
            generator.generate(rows=5, cols=-1, fill_percentage=0.3)

    def test_generate_invalid_fill_percentage(self):
        """Test generation with invalid fill percentages."""
        generator = SnakePuzzleGenerator()

        with pytest.raises(ValueError, match="Fill percentage must be between 0.0 and 1.0"):
            generator.generate(rows=5, cols=5, fill_percentage=0.0)

        with pytest.raises(ValueError, match="Fill percentage must be between 0.0 and 1.0"):
            generator.generate(rows=5, cols=5, fill_percentage=-0.1)

        with pytest.raises(ValueError, match="Fill percentage must be between 0.0 and 1.0"):
            generator.generate(rows=5, cols=5, fill_percentage=1.1)

    def test_generate_minimum_valid_fill_percentage(self):
        """Test generation with minimum valid fill percentage."""
        generator = SnakePuzzleGenerator(seed=42)

        # Should work with very small positive percentage
        puzzle, path = generator.generate(rows=5, cols=5, fill_percentage=0.01)
        # Should generate minimum path (max(2, int(5*5*0.01)) = max(2, 0.25) = 2)
        assert len(path) == 2

    def test_generate_high_valid_fill_percentage(self):
        """Test generation with high but achievable fill percentage."""
        generator = SnakePuzzleGenerator(seed=42)

        # Use a more realistic high fill percentage that's achievable
        puzzle, path = generator.generate(rows=6, cols=6, fill_percentage=0.6)
        expected_length = int(6 * 6 * 0.6)
        assert len(path) >= expected_length

    def test_generate_impossible_fill_percentage_handled(self):
        """Test that impossible fill percentages are handled gracefully."""
        generator = SnakePuzzleGenerator(seed=42)

        # It is impossible to achieve a fill rate of 100%. Should fail and raise RuntimeError after max attempts
        with pytest.raises(RuntimeError, match="Failed to generate any valid puzzle after"):
            generator.generate(rows=4, cols=4, fill_percentage=1.0)

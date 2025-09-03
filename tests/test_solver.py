import pytest
import io
import sys
from snake_mip_solver import SnakePuzzle, SnakeSolver


class TestSnakeSolver:
    """Test cases for SnakeSolver class."""

    def test_solver_creation(self):
        """Test creating a solver with a valid puzzle."""
        puzzle = SnakePuzzle(
            row_sums=[2, 1, 2],
            col_sums=[1, 3, 1],
            start_cell=(0, 0),
            end_cell=(2, 2)
        )
        solver = SnakeSolver(puzzle)
        
        assert solver.puzzle == puzzle
        assert solver.solver is not None
        assert isinstance(solver.variables, dict)
        assert len(solver.variables) == 9  # 3x3 grid
        
        # Check that all grid positions have variables
        for row in range(3):
            for col in range(3):
                assert (row, col) in solver.variables

    def test_solver_with_invalid_puzzle(self):
        """Test that solver creation fails with invalid puzzle type."""
        with pytest.raises(ValueError, match="Puzzle must be a SnakePuzzle instance"):
            SnakeSolver("not a puzzle")  # type: ignore
    
    def test_solver_with_invalid_solver_type(self):
        """Test that solver creation fails with invalid solver type."""
        puzzle = SnakePuzzle([1, 1], [1, 1], (0, 0), (1, 1))
        with pytest.raises(ValueError, match="Could not create solver of type"):
            SnakeSolver(puzzle, solver_type='INVALID_SOLVER')

    def test_simple_solvable_puzzle(self):
        """Test solving a simple 3x3 puzzle."""
        puzzle = SnakePuzzle(
            row_sums=[2, 1, 2],
            col_sums=[1, 3, 1],
            start_cell=(0, 0),
            end_cell=(2, 2)
        )
        solver = SnakeSolver(puzzle)
        solution = solver.solve()
        
        assert solution is not None
        assert len(solution) == 5  # Expected solution size
        assert puzzle.is_valid_solution(solution)
        
        # Check that start and end cells are in solution
        assert (0, 0) in solution
        assert (2, 2) in solution
        
        # Check expected solution path
        expected_solution = {(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)}
        assert solution == expected_solution

    def test_larger_solvable_puzzle(self):
        """Test solving a larger 8x8 puzzle."""
        puzzle = SnakePuzzle(
            row_sums=[4, 2, 2, 3, 1, 3, 2, 6],
            col_sums=[3, 2, 7, 2, 2, 4, 1, 2],
            start_cell=(2, 5),
            end_cell=(6, 7)
        )
        solver = SnakeSolver(puzzle)
        solution = solver.solve()
        
        assert solution is not None
        assert len(solution) == 23  # Expected solution size
        assert puzzle.is_valid_solution(solution)
        
        # Check that start and end cells are in solution
        assert (2, 5) in solution
        assert (6, 7) in solution
        
        # Check expected complete solution
        expected_solution = {
            (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 5), (2, 2), (2, 5), 
            (3, 0), (3, 1), (3, 2), (4, 0), (5, 0), (5, 1), (5, 2), (6, 2), 
            (6, 7), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)
        }
        assert solution == expected_solution

    def test_infeasible_puzzle(self):
        """Test solving an infeasible puzzle."""
        # Create a puzzle with impossible constraints
        puzzle = SnakePuzzle(
            row_sums=[2, 3, 3, 0, 0],
            col_sums=[0, 3, 2, 2, 1],
            start_cell=(0, 2),
            end_cell=(1, 4)
        )
        solver = SnakeSolver(puzzle)
        solution = solver.solve()
        
        assert solution is None

    def test_puzzle_with_none_constraints(self):
        """Test solving a puzzle with None constraints (unlabeled rows/columns)."""
        puzzle = SnakePuzzle(
            row_sums=[11, 2, 7, 4, 4, None, None, None, 3, 2, None, 5],
            col_sums=[9, 7, None, 2, 5, 6, None, None, 5, None, None, None],
            start_cell=(2, 6),
            end_cell=(7, 5)
        )
        solver = SnakeSolver(puzzle)
        solution = solver.solve()
        
        assert solution is not None
        assert len(solution) == 49  # Expected solution size
        assert puzzle.is_valid_solution(solution)
        
        # Check expected complete solution
        expected_solution = {
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), 
            (0, 9), (0, 10), (0, 11), (1, 1), (1, 11), (2, 0), (2, 1), (2, 6), 
            (2, 8), (2, 9), (2, 10), (2, 11), (3, 0), (3, 5), (3, 6), (3, 8), 
            (4, 0), (4, 1), (4, 5), (4, 8), (5, 1), (5, 5), (5, 6), (5, 7), 
            (5, 8), (6, 0), (6, 1), (7, 0), (7, 5), (8, 0), (8, 4), (8, 5), 
            (9, 0), (9, 4), (10, 0), (10, 4), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4)
        }
        assert solution == expected_solution

    def test_get_solver_info(self):
        """Test getting solver information."""
        puzzle = SnakePuzzle(
            row_sums=[2, 1, 2],
            col_sums=[1, 3, 1],
            start_cell=(0, 0),
            end_cell=(2, 2)
        )
        solver = SnakeSolver(puzzle)
        info = solver.get_solver_info()
        
        assert isinstance(info, dict)
        assert "solver_type" in info
        assert "num_variables" in info
        assert "num_constraints" in info
        assert "puzzle_size" in info
        assert "start_cell" in info
        assert "end_cell" in info
        
        assert info["num_variables"] == "9"
        assert info["puzzle_size"] == "3x3"
        assert info["start_cell"] == "(0, 0)"
        assert info["end_cell"] == "(2, 2)"

    def test_verbose_solve(self):
        """Test solving with verbose output."""
        puzzle = SnakePuzzle(
            row_sums=[2, 1, 2],
            col_sums=[1, 3, 1],
            start_cell=(0, 0),
            end_cell=(2, 2)
        )
        solver = SnakeSolver(puzzle)
        
        # Capture output to verify verbose flag works
        captured_output = io.StringIO()
        sys.stdout = captured_output
        solution = solver.solve(verbose=True)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        assert "Solving Snake puzzle..." in output
        assert "solver_type:" in output
        assert "num_variables:" in output
        assert "num_constraints:" in output
        assert "Valid solution found with" in output
        assert solution is not None

    def test_verbose_solve_infeasible(self):
        """Test verbose output for infeasible puzzle."""
        puzzle = SnakePuzzle(
            row_sums=[2, 3, 3, 0, 0],
            col_sums=[0, 3, 2, 2, 1],
            start_cell=(0, 2),
            end_cell=(1, 4)
        )
        solver = SnakeSolver(puzzle)
        
        # Capture output to verify verbose flag works
        captured_output = io.StringIO()
        sys.stdout = captured_output
        solution = solver.solve(verbose=True)
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        assert "Solving Snake puzzle..." in output
        assert "No solution exists for this puzzle" in output
        assert solution is None

    def test_different_solver_types(self):
        """Test creating solvers with different solver types."""
        puzzle = SnakePuzzle(
            row_sums=[2, 1, 2],
            col_sums=[1, 3, 1],
            start_cell=(0, 0),
            end_cell=(2, 2)
        )
        
        # Test SCIP solver (default)
        solver_scip = SnakeSolver(puzzle, solver_type='SCIP')
        solution_scip = solver_scip.solve()
        assert solution_scip is not None
        
        # Test GLOP solver
        solver_glop = SnakeSolver(puzzle, solver_type='GLOP')
        assert solver_glop.solver is not None

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Single row puzzle
        puzzle_single_row = SnakePuzzle(
            row_sums=[2],
            col_sums=[1, 1],
            start_cell=(0, 0),
            end_cell=(0, 1)
        )
        solver = SnakeSolver(puzzle_single_row)
        solution = solver.solve()
        assert solution == {(0,0), (0,1)}

        # Single column puzzle
        puzzle_single_col = SnakePuzzle(
            row_sums=[1, 1],
            col_sums=[2],
            start_cell=(0, 0),
            end_cell=(1, 0)
        )
        solver = SnakeSolver(puzzle_single_col)
        solution = solver.solve()
        assert solution == {(0,0), (1,0)}

    def test_connectivity_cutting_planes_disjoint_infeasible(self):
        """Test that the cutting plane approach correctly identifies disjoint puzzles as infeasible."""
        # This puzzle forces disconnected components and should be infeasible
        puzzle = SnakePuzzle(
            row_sums=[4, 3, 3, 3, 0],
            col_sums=[3, 0, 4, 2, 4],
            start_cell=(0, 0),
            end_cell=(2, 0)
        )
        solver = SnakeSolver(puzzle)
        
        # Should return None (infeasible)
        solution = solver.solve(verbose=False, max_iterations=5)
        assert solution is None
        
        # Check that cutting planes were used
        stats = solver.get_solve_stats()
        assert stats['iterations'] >= 2  # Should take more than 1 iteration
        assert stats['disconnected_solutions_found'] >= 1
        assert stats['cutting_planes_added'] >= 1

    def test_connectivity_cutting_planes_stats_initialization(self):
        """Test that solve statistics are properly initialized."""
        puzzle = SnakePuzzle(
            row_sums=[2, 1, 2],
            col_sums=[1, 3, 1],
            start_cell=(0, 0),
            end_cell=(2, 2)
        )
        solver = SnakeSolver(puzzle)
        
        # Stats should be initialized before solving
        initial_stats = solver.get_solve_stats()
        assert initial_stats['iterations'] == 0
        assert initial_stats['cutting_planes_added'] == 0
        assert initial_stats['disconnected_solutions_found'] == 0
        
        # Solve and check stats are updated
        solution = solver.solve(verbose=False)
        assert solution is not None
        
        final_stats = solver.get_solve_stats()
        assert final_stats['iterations'] >= 1

    def test_connectivity_cutting_planes_stats_reset(self):
        """Test that solve statistics are reset between solve calls."""
        puzzle = SnakePuzzle(
            row_sums=[4, 3, 3, 3, 0],
            col_sums=[3, 0, 4, 2, 4],
            start_cell=(0, 0),
            end_cell=(2, 0)
        )
        solver = SnakeSolver(puzzle)
        
        # First solve attempt
        solution1 = solver.solve(verbose=False, max_iterations=3)
        stats1 = solver.get_solve_stats()
        
        # Second solve attempt (note: cutting planes from first solve persist)
        solution2 = solver.solve(verbose=False, max_iterations=3)
        stats2 = solver.get_solve_stats()
        
        # Both should be None (infeasible)
        assert solution1 is None
        assert solution2 is None
        
        # Stats should be reset, not accumulated
        assert stats1['iterations'] == 2
        assert stats2['iterations'] == 1
        
        # First solve should find disconnected solutions
        assert stats1['disconnected_solutions_found'] == 1
        # Second solve shouldn't find any disconnected solution because cutting planes from first solve persist
        assert stats2['disconnected_solutions_found'] == 0

    def test_connectivity_valid_puzzle_no_cutting_planes(self):
        """Test that valid puzzles don't trigger cutting planes."""
        puzzle = SnakePuzzle(
            row_sums=[1, 1, 1, 3, 2, 5],
            col_sums=[4, 3, 1, 1, 1, 3],
            start_cell=(0, 0),
            end_cell=(3, 5)
        )
        solver = SnakeSolver(puzzle)
        
        solution = solver.solve(verbose=False)
        assert solution is not None
        
        # Should solve in 1 iteration with no cutting planes
        stats = solver.get_solve_stats()
        assert stats['iterations'] == 1
        assert stats['cutting_planes_added'] == 0
        assert stats['disconnected_solutions_found'] == 0

    def test_connectivity_max_iterations_parameter(self):
        """Test that max_iterations parameter is respected."""
        puzzle = SnakePuzzle(
            row_sums=[4, 3, 3, 3, 0],
            col_sums=[3, 0, 4, 2, 4],
            start_cell=(0, 0),
            end_cell=(2, 0)
        )
        solver = SnakeSolver(puzzle)
        
        # Test with limited iterations
        solution0 = solver.solve(verbose=False, max_iterations=0)
        assert solution0 is None
        stats0 = solver.get_solve_stats()
        assert stats0['iterations'] == 0

        solution1 = solver.solve(max_iterations=1)
        assert solution1 is None
        stats1 = solver.get_solve_stats()
        assert stats1['iterations'] == 1

    def test_connectivity_verbose_output(self):
        """Test that verbose output works correctly with cutting planes."""
        puzzle = SnakePuzzle(
            row_sums=[4, 3, 3, 3, 0],
            col_sums=[3, 0, 4, 2, 4],
            start_cell=(0, 0),
            end_cell=(2, 0)
        )
        solver = SnakeSolver(puzzle)
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            solution = solver.solve(verbose=True, max_iterations=3)
            assert solution is None
            
            # Restore stdout and check output
            sys.stdout = sys.__stdout__
            output = captured_output.getvalue()
            
            # Should contain expected verbose messages
            assert "Solving Snake puzzle..." in output
            assert "Found disconnected solution" in output or "No solution exists" in output
            
        finally:
            # Ensure stdout is restored even if test fails
            sys.stdout = sys.__stdout__
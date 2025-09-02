from .puzzle import SnakePuzzle
from ortools.linear_solver import pywraplp
from typing import Dict, Set, Tuple, Optional


class SnakeSolver:
    """
    Mathematical programming solver for Snake puzzles.
    
    Uses Google OR-Tools to model the puzzle as an integer linear programming
    problem.
    """

    def __init__(self, puzzle: SnakePuzzle, solver_type: str = 'SCIP'):
        """
        Initialize the solver with a puzzle.
        
        Args:
            puzzle: The SnakePuzzle instance to solve
            solver_type: The solver type to use (default: 'SCIP')
            
        Raises:
            ValueError: If puzzle is invalid or solver creation fails
        """
        
        if not isinstance(puzzle, SnakePuzzle):
            raise ValueError("Puzzle must be a SnakePuzzle instance")
        
        self.puzzle = puzzle
        self.solver = pywraplp.Solver.CreateSolver(solver_type)
        if not self.solver:
            raise ValueError(f"Could not create solver of type '{solver_type}'")
        
        # Dictionary to store variables - adapt based on your puzzle needs
        # Example: self.variables: Dict[Tuple[int, int], pywraplp.Variable] = {}
        self.variables: Dict[Tuple[int, int], pywraplp.Variable] = {}
        
        # Setup the mathematical model
        self._add_variables()
        self._add_constraints()

    def _add_variables(self) -> None:
        """
        Create variables for the mathematical model.
        
        Creates binary variables x_ij for each cell (i,j) in the grid.
        x_ij = 1 if cell (i,j) is part of the snake, 0 otherwise.
        """
        # Create binary variables for each cell in the grid
        for row in range(self.puzzle.rows):
            for col in range(self.puzzle.cols):
                var_name = f"x_{row}_{col}"
                self.variables[(row, col)] = self.solver.BoolVar(var_name)

    def _add_constraints(self) -> None:
        """
        Add all puzzle constraints to the mathematical model.
        """
        self._add_start_end_constraints()
        self._add_row_sum_constraints()
        self._add_col_sum_constraints()
        self._add_snake_path_constraints()
        self._add_diagonal_touching_constraints()
        self._add_adjacent_touching_constraints()
    
    def _add_start_end_constraints(self) -> None:
        """
        Fix start and end cells: x_ij = 1 for given start and end cells.
        These cells must be included in the solution.
        """
        # Fix start cell
        self.solver.Add(self.variables[self.puzzle.start_cell] == 1)
        
        # Fix end cell
        self.solver.Add(self.variables[self.puzzle.end_cell] == 1)
    
    def _add_snake_path_constraints(self) -> None:
        """
        Snake path constraints: Ensure the activated cells form a single path.
        - Start and end cells: must have exactly 1 adjacent activated neighbor
        - Other cells: when activated, must have exactly 2 adjacent activated neighbors; when not activated, any number
        """
        for row in range(self.puzzle.rows):
            for col in range(self.puzzle.cols):
                position = (row, col)
                
                # Get adjacent cells
                adjacent_positions = self.puzzle.get_tiles_by_offsets(position, self.puzzle._orthogonal_offsets)
                adjacent_vars = [self.variables[adj_pos] for adj_pos in adjacent_positions]
                neighbor_sum = self.solver.Sum(adjacent_vars)
                
                if position == self.puzzle.start_cell or position == self.puzzle.end_cell:
                    # Start and end cells: must have exactly 1 neighbor
                    self.solver.Add(neighbor_sum == 1)
                else:
                    # Other cells: if activated (x_ij = 1), must have exactly 2 neighbors, if not activated (x_ij = 0) then no limit
                    # Enforced using two constraints as follows:
                    self.solver.Add(neighbor_sum >= 2 * self.variables[position])  # type: ignore
                    self.solver.Add(neighbor_sum <= 4 - 2 * self.variables[position])  # type: ignore

                    # Depending on the value of x_ij, these two constraints evaluate to:
                    #   x_ij = 1:
                    #       neighbor_sum >= 2
                    #       neighbor_sum <= 2
                    #   x_ij = 0
                    #       neighbor_sum >= 0
                    #       neighbor_sum <= 4
    
    def _add_row_sum_constraints(self) -> None:
        """
        Add row sum constraints for rows with specified sums.
        """
        for row_idx, required_sum in enumerate(self.puzzle.row_sums):
            if required_sum is not None:
                row_vars = [self.variables[(row_idx, col)] for col in range(self.puzzle.cols)]
                self.solver.Add(sum(row_vars) == required_sum) # type: ignore
    
    def _add_col_sum_constraints(self) -> None:
        """
        Add column sum constraints for columns with specified sums.
        """
        for col_idx, required_sum in enumerate(self.puzzle.col_sums):
            if required_sum is not None:
                col_vars = [self.variables[(row, col_idx)] for row in range(self.puzzle.rows)]
                self.solver.Add(sum(col_vars) == required_sum) # type: ignore
    
    def _add_diagonal_touching_constraints(self) -> None:
        """
        Diagonal touching constraints: x_ij + x_{i-1,j-1} <= x_{i-1,j} + x_{i,j-1} + 1
        Two diagonal cells can only both be activated if there's an orthogonal connection.
        """
        for row in range(self.puzzle.rows):
            for col in range(self.puzzle.cols):
                position = (row, col)
                
                # Check all four diagonal directions
                for diag_offset in self.puzzle._diagonal_offsets:
                    diag_pos = self.puzzle.get_tile_by_offset(position, diag_offset)
                    if diag_pos is not None:
                        # Get the two orthogonal cells that could connect the diagonal pair
                        dr, dc = diag_offset
                        ortho_pos1 = self.puzzle.get_tile_by_offset(position, (dr, 0))  # vertical connection
                        ortho_pos2 = self.puzzle.get_tile_by_offset(position, (0, dc))  # horizontal connection
                        
                        if ortho_pos1 is not None and ortho_pos2 is not None:
                            # x_ij + x_diagonal <= x_ortho1 + x_ortho2 + 1
                            left_vars = [self.variables[position], self.variables[diag_pos]]
                            right_vars = [self.variables[ortho_pos1], self.variables[ortho_pos2]]
                            self.solver.Add(
                                self.solver.Sum(left_vars) <= self.solver.Sum(right_vars) + 1
                            )
    
    def _add_adjacent_touching_constraints(self) -> None:
        """
        Adjacent touching constraints: For all 2x2 sub-grids, at most 3 variables can be activated.
        This prevents forming disconnected 2x2 blocks.
        """
        for row in range(self.puzzle.rows - 1):
            for col in range(self.puzzle.cols - 1):
                # Define the 2x2 sub-grid
                positions = [
                    (row, col),         # top-left
                    (row, col + 1),     # top-right
                    (row + 1, col),     # bottom-left
                    (row + 1, col + 1)  # bottom-right
                ]
                
                # Sum of variables in 2x2 grid <= 3
                grid_vars = [self.variables[pos] for pos in positions]
                self.solver.Add(self.solver.Sum(grid_vars) <= 3)

    def solve(self, verbose: bool = False) -> Optional[set]:
        """
        Solve the puzzle and return the solution.
        
        Args:
            verbose: If True, print solver information
            
        Returns:
            Set of (row, col) tuples representing the snake path, or None if no solution
        """
        if verbose:
            print("Solving Snake puzzle...")
            info = self.get_solver_info()
            for key, value in info.items():
                print(f"  {key}: {value}")
        
        status = self.solver.Solve()
        
        if status == pywraplp.Solver.OPTIMAL:
            # Extract solution: cells where x_ij = 1
            solution = set()
            for position, variable in self.variables.items():
                if variable.solution_value() == 1:
                    solution.add(position)
            
            if verbose:
                print(f"Solution found with {len(solution)} cells")
            
            return solution
        elif status == pywraplp.Solver.FEASIBLE:
             # This should not happen since the problem doesn't have an objective function
            raise RuntimeError("What the... Solver returned FEASIBLE status for a constraint satisfaction problem??")
        elif status == pywraplp.Solver.INFEASIBLE:
            if verbose:
                print("No solution exists for this puzzle")
            return None
        else:
            if verbose:
                print(f"Solver status: {status}")
            return None

    def get_solver_info(self) -> Dict[str, str]:
        """Get information about the solver and problem size."""
        return {
            "solver_type": str(self.solver.SolverVersion()),
            "num_variables": str(self.solver.NumVariables()),
            "num_constraints": str(self.solver.NumConstraints()),
            "puzzle_size": f"{self.puzzle.rows}x{self.puzzle.cols}",
            "start_cell": str(self.puzzle.start_cell),
            "end_cell": str(self.puzzle.end_cell)
        }

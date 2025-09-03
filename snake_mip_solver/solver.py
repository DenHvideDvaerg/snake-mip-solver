from .puzzle import SnakePuzzle
from ortools.linear_solver import pywraplp
from typing import Dict, Tuple, Optional, Set, List


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
        
        self._solve_stats: Dict[str, int] = {
            'iterations': 0,
            'cutting_planes_added': 0,
            'disconnected_solutions_found': 0
        }        
        
        # Setup the mathematical model
        self.variables: Dict[Tuple[int, int], pywraplp.Variable] = {}

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
        self._add_no_2x2_block_constraints()
    
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
                neighbor_sum = sum(adjacent_vars) # type: ignore
                
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
        Diagonal touching constraints: Two diagonal cells can only both be activated 
        if there's an orthogonal connection between them.
        
        Only checks upper diagonals to avoid duplicate constraints.
        """
        for row in range(self.puzzle.rows):
            for col in range(self.puzzle.cols):
                position = (row, col)
                
                # Only check upper-left and upper-right diagonals to avoid duplicates
                # This covers all diagonal pairs exactly once
                for diag_offset in [(-1, -1), (-1, 1)]:
                    diag_pos = self.puzzle.get_tile_by_offset(position, diag_offset)
                    if diag_pos is not None:
                        # Get the two orthogonal cells that could connect the diagonal pair
                        dr, dc = diag_offset
                        ortho_pos1 = self.puzzle.get_tile_by_offset(position, (dr, 0))  # vertical connection
                        ortho_pos2 = self.puzzle.get_tile_by_offset(position, (0, dc))  # horizontal connection
                        
                        if ortho_pos1 is not None and ortho_pos2 is not None:
                            # x_ij + x_diagonal <= x_ortho1 + x_ortho2 + 1
                            self.solver.Add(self.variables[position] + self.variables[diag_pos] <= self.variables[ortho_pos1] + self.variables[ortho_pos2] + 1) # type: ignore

    def _add_no_2x2_block_constraints(self) -> None:
        """
        No 2x2 block constraints: For all 2x2 sub-grids, at most 3 variables can be activated.
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
                self.solver.Add(sum(grid_vars) <= 3) # type: ignore

    def solve(self, verbose: bool = False, max_iterations: int = 10) -> Optional[set]:
        """
        Solve the puzzle using iterative connectivity enforcement.
        
        Args:
            verbose: If True, print solver information
            max_iterations: Maximum number of iterations for cutting plane method
            
        Returns:
            Set of (row, col) tuples representing the snake path, or None if no solution
        """
        if verbose:
            print("Solving Snake puzzle...")
            info = self.get_solver_info()
            for key, value in info.items():
                print(f"  {key}: {value}")
        
        # Reset solve statistics
        self._solve_stats = {
            'iterations': 0,
            'cutting_planes_added': 0,
            'disconnected_solutions_found': 0
        }
        
        for iteration in range(max_iterations):
            self._solve_stats['iterations'] = iteration + 1
            
            if verbose and iteration > 0:
                print(f"Iteration {iteration + 1}")
            
            status = self.solver.Solve()
            
            if status == pywraplp.Solver.OPTIMAL:
                # Extract solution: cells where x_ij = 1
                solution = set()
                for position, variable in self.variables.items():
                    if variable.solution_value() == 1:
                        solution.add(position)
                
                # Check connectivity using puzzle validation
                if self.puzzle.is_valid_solution(solution):
                    if verbose:
                        print(f"Valid solution found with {len(solution)} cells")
                    return solution
                else:
                    # Solution is invalid - check if it's due to disconnected components
                    disconnected_components = self._find_disconnected_components(solution)
                    
                    if len(disconnected_components) > 1:
                        # We have disconnected components - add cutting plane constraints
                        self._solve_stats['disconnected_solutions_found'] += 1
                        
                        if verbose:
                            print(f"Found disconnected solution with {len(disconnected_components)} components, adding cutting plane constraint")
                        
                        constraints_added = self._add_cutting_plane_constraints(disconnected_components)
                        self._solve_stats['cutting_planes_added'] += constraints_added
                    else:
                        # Solution is invalid for other reasons (not disconnected components)
                        if verbose:
                            print("Solution failed validation for reasons other than connectivity")
                        return None
                    
            elif status == pywraplp.Solver.FEASIBLE:
                # This should not happen since the problem doesn't have an objective function.
                raise RuntimeError("Unexpected FEASIBLE status for constraint satisfaction problem")
            elif status == pywraplp.Solver.INFEASIBLE:
                if verbose:
                    print("No solution exists for this puzzle")
                return None
            else:
                if verbose:
                    print(f"Solver status: {status}")
                return None
        
        if verbose:
            print(f"No valid solution found after {max_iterations} iterations")
        return None
    
    def _find_disconnected_components(self, solution: Set[Tuple[int, int]]) -> List[Set[Tuple[int, int]]]:
        """Find all disconnected components in the solution."""
        unvisited = solution.copy()
        components = []
        
        while unvisited:
            # Start DFS from any unvisited node
            start = next(iter(unvisited))
            component = set()
            stack = [start]
            
            while stack:
                current = stack.pop()
                if current in unvisited:
                    unvisited.remove(current)
                    component.add(current)
                    
                    # Add orthogonal neighbors to stack
                    adjacent_positions = self.puzzle.get_tiles_by_offsets(current, self.puzzle._orthogonal_offsets)
                    for neighbor in adjacent_positions:
                        if neighbor in unvisited:
                            stack.append(neighbor)
            
            components.append(component)
        
        return components
    
    def _add_cutting_plane_constraints(self, components: List[Set[Tuple[int, int]]]) -> int:
        """
        Add constraints to prevent the current disconnected solution.
        
        Args:
            components: List of disconnected components found in the solution
            
        Returns:
            Number of cutting plane constraints added
        """
        if len(components) <= 1:
            # No disconnected components, nothing to do
            return 0
        
        # Find the component that contains both start and end (this is the valid component)
        valid_component = None
        for component in components:
            if self.puzzle.start_cell in component and self.puzzle.end_cell in component:
                valid_component = component
                break
        
        # For each invalid component (doesn't contain both start and end),
        # add a constraint that prevents all cells in that component from being activated simultaneously
        constraints_added = 0
        for component in components:
            if component != valid_component and len(component) > 0:
                # Add constraint: sum of variables in this component <= |component| - 1
                component_vars = [self.variables[pos] for pos in component]
                self.solver.Add(sum(component_vars) <= len(component) - 1)  # type: ignore
                constraints_added += 1
        
        if constraints_added == 0:
            raise RuntimeError("Expected to add cutting plane constraints but none were added")
        
        return constraints_added

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
    
    def get_solve_stats(self) -> Dict[str, int]:
        """
        Get statistics from the last solve attempt.
        
        Returns:
            Dictionary with solving statistics including iterations, cutting planes added, etc.
        """
        return self._solve_stats.copy()

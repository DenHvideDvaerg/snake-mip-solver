from typing import Set, Tuple, Optional, List, Union
import random
from .puzzle import SnakePuzzle


class SnakePuzzleGenerator:
    """
    Generator for random Snake puzzles.
    
    This class handles the creation of valid Snake puzzles by generating
    snake paths and deriving constraints from them.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the puzzle generator.
        
        Args:
            seed: Optional random seed for reproducible generation
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
    
    def generate(self, rows: int, cols: int, fill_percentage: float = 0.3) -> Tuple[SnakePuzzle, Set[Tuple[int, int]]]:
        """
        Generate a random Snake puzzle using organic path growth.
        
        Args:
            rows: Number of rows in the puzzle (must be > 0)
            cols: Number of columns in the puzzle (must be > 0) 
            fill_percentage: Target percentage of cells to fill (0.0 to 1.0)
            
        Returns:
            A tuple of (SnakePuzzle instance, solution path as set of coordinates)
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If puzzle generation fails after maximum attempts
        """
        if rows <= 0 or cols <= 0:
            raise ValueError("Rows and columns must be positive")
        if not (0.0 < fill_percentage <= 1.0):
            raise ValueError("Fill percentage must be between 0.0 and 1.0")
        
        # Reset seed for consistent generation if provided
        if self.seed is not None:
            random.seed(self.seed)
        
        # Calculate realistic target length based on snake constraints
        max_realistic_length = self._calculate_max_path_length(rows, cols)
        target_length = max(2, min(int(rows * cols * fill_percentage), max_realistic_length))
        
        # Try multiple starting points for better success rate
        max_attempts = 50
        best_path = None
        best_start = None
        best_end = None
        
        for attempt in range(max_attempts):
            try:
                # Generate path using organic growth strategy
                snake_path, start_cell, end_cell = self._generate_snake_path_organic(
                    rows, cols, target_length
                )
                
                if snake_path and len(snake_path) >= 2:
                    # Keep track of best attempt
                    if best_path is None or len(snake_path) > len(best_path):
                        best_path = snake_path
                        best_start = start_cell
                        best_end = end_cell
                    
                    if len(snake_path) >= target_length: 
                        break
                        
            except Exception:
                # Continue to next attempt if generation fails
                continue
        
        if best_path is None:
            raise RuntimeError(f"Failed to generate any valid puzzle after {max_attempts} attempts")
        
        # These should not be None if best_path is not None
        assert best_start is not None and best_end is not None, "Internal error: missing start/end points"
        
        # Calculate row and column sums from the best path found
        row_sums: List[Union[int, None]] = [0] * rows
        col_sums: List[Union[int, None]] = [0] * cols
        
        for r, c in best_path:
            row_sums[r] += 1  # type: ignore
            col_sums[c] += 1  # type: ignore
        
        # Create puzzle instance
        puzzle = SnakePuzzle(row_sums, col_sums, best_start, best_end)
        
        # Verify the generated path is a valid solution
        if puzzle.is_valid_solution(best_path):
            return puzzle, best_path
        else:
            raise RuntimeError("Generated path is not a valid solution")
    
    def _calculate_max_path_length(self, rows: int, cols: int) -> int:
        """
        Calculate realistic maximum snake path length.
        
        For a snake that cannot touch itself diagonally, the theoretical maximum
        is significantly less than the total grid size. This uses a conservative
        estimate based on checkerboard patterns and connectivity constraints.
        
        Args:
            rows: Grid rows
            cols: Grid columns
            
        Returns:
            Conservative estimate of maximum achievable path length
        """
        total_cells = rows * cols
        
        # Conservative heuristic based on snake constraints:
        # - Checkerboard pattern: ~50% theoretical maximum
        # - Connectivity requirements: reduce further
        # - Path constraints: additional reduction
        # Conservative estimate: 35-40% of grid
        max_theoretical = int(total_cells * 0.35)
        
        # Ensure minimum of 2 (start + end)
        return max(2, max_theoretical)
    
    def _generate_snake_path_organic(self, rows: int, cols: int, 
                                target_length: int) -> Tuple[Set[Tuple[int, int]], Tuple[int, int], Tuple[int, int]]:
        """
        Generate a valid snake path using organic linear growth with randomness.
        
        Creates interesting snake patterns by using random walks that maintain
        proper linear connectivity. Start and end cells have exactly 1 orthogonal neighbor and all other body cells have exactly 2.
        
        Args:
            rows: Grid rows
            cols: Grid columns
            target_length: Desired path length
            
        Returns:
            Tuple of (path_set, start_cell, end_cell)
            
        Raises:
            ValueError: If generation fails completely
        """
        max_attempts = 100
        
        for attempt in range(max_attempts):
            # Start with a random cell
            start_pos = (random.randint(0, rows - 1), random.randint(0, cols - 1))
            path = [start_pos]
            path_set = {start_pos}
            
            # Stack for backtracking
            backtrack_stack = [(start_pos, [])]
            
            while len(path) < target_length:
                current_pos = path[-1]
                r, c = current_pos
                
                # Get all orthogonally adjacent positions
                orthogonal_moves = [
                    (r - 1, c),  # Up
                    (r + 1, c),  # Down  
                    (r, c - 1),  # Left
                    (r, c + 1)   # Right
                ]
                
                # Filter valid moves
                valid_moves = []
                for new_pos in orthogonal_moves:
                    nr, nc = new_pos
                    
                    # Check bounds
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        continue
                        
                    # Can't revisit existing path
                    if new_pos in path_set:
                        continue
                    
                    # **KEY CHECK**: Snake can't be orthogonally adjacent to any existing body part
                    # except the current position it's extending from
                    is_adjacent_to_body = False
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        adjacent_pos = (nr + dr, nc + dc)
                        if adjacent_pos in path_set and adjacent_pos != current_pos:
                            is_adjacent_to_body = True
                            break
                    
                    if is_adjacent_to_body:
                        continue
                    
                    # Check diagonal touching constraint
                    if self._would_create_diagonal_touching(path_set, new_pos):
                        continue
                    
                    valid_moves.append(new_pos)
                
                if valid_moves:
                    # Randomly select from valid moves
                    next_pos = random.choice(valid_moves)
                    path.append(next_pos)
                    path_set.add(next_pos)
                    
                    # Update backtrack stack with remaining moves
                    remaining_moves = [move for move in valid_moves if move != next_pos]
                    backtrack_stack.append((next_pos, remaining_moves))
                    
                else:
                    # No valid moves - backtrack
                    if len(backtrack_stack) <= 1:
                        break
                    
                    # Remove current position from path
                    removed_pos = path.pop()
                    path_set.remove(removed_pos)
                    backtrack_stack.pop()
                    
                    # Try alternative moves from previous position
                    while backtrack_stack:
                        prev_pos, remaining_moves = backtrack_stack[-1]
                        
                        if remaining_moves:
                            # Try next alternative move
                            next_pos = remaining_moves.pop(0)
                            
                            # Re-verify it's still valid (need to check orthogonal adjacency again)
                            nr, nc = next_pos
                            if (0 <= nr < rows and 0 <= nc < cols and 
                                next_pos not in path_set):
                                
                                # Check orthogonal adjacency constraint again
                                is_adjacent_to_body = False
                                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                    adjacent_pos = (nr + dr, nc + dc)
                                    if adjacent_pos in path_set and adjacent_pos != prev_pos:
                                        is_adjacent_to_body = True
                                        break
                                
                                if (not is_adjacent_to_body and 
                                    not self._would_create_diagonal_touching(path_set, next_pos)):
                                    
                                    path.append(next_pos)
                                    path_set.add(next_pos)
                                    backtrack_stack.append((next_pos, []))
                                    break
                        else:
                            # No more alternatives, backtrack further
                            if len(backtrack_stack) <= 1:
                                break
                            removed_pos = path.pop()
                            path_set.remove(removed_pos)
                            backtrack_stack.pop()
                    else:
                        # Exhausted all backtracking options
                        break
            
            # Check if we got a decent path
            if len(path) >= max(2, target_length * 0.7):
                start_cell = path[0]
                end_cell = path[-1]
                return set(path), start_cell, end_cell
        
        raise ValueError(f"Failed to generate snake path after {max_attempts} attempts")

    def _would_create_diagonal_touching(self, existing_path: Set[Tuple[int, int]], 
                                      new_pos: Tuple[int, int]) -> bool:
        """
        Check if adding a new position would create invalid diagonal touching.
        
        Args:
            existing_path: Current path positions
            new_pos: Position to potentially add
            
        Returns:
            True if adding new_pos would create diagonal touching violation
        """
        r, c = new_pos
        diagonal_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        orthogonal_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in diagonal_offsets:
            diag_pos = (r + dr, c + dc)
            if diag_pos in existing_path:
                # Check if there are orthogonal connections between the positions
                pos_orthogonal = {(r + odr, c + odc) for odr, odc in orthogonal_offsets}
                diag_orthogonal = {(diag_pos[0] + odr, diag_pos[1] + odc) 
                                 for odr, odc in orthogonal_offsets}
                
                shared_orthogonal = pos_orthogonal.intersection(diag_orthogonal)
                orthogonal_connections = shared_orthogonal.intersection(existing_path)
                
                # If no orthogonal connection exists, this would be invalid diagonal touching
                if not orthogonal_connections:
                    return True
        
        return False

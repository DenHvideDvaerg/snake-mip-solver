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
        target_length = max(2, int(rows * cols * fill_percentage))
        
        # Try multiple attempts until we get a valid path
        max_attempts = 50
        
        for attempt in range(max_attempts):
            result = self._generate_snake_path(rows, cols, target_length)
            if result is not None:
                snake_path, start_cell, end_cell = result
                break
        else:
            raise RuntimeError(f"Failed to generate any valid puzzle after {max_attempts} attempts")
        
        # Calculate row and column sums from the generated path
        row_sums: List[Union[int, None]] = [0] * rows
        col_sums: List[Union[int, None]] = [0] * cols
        
        for r, c in snake_path:
            row_sums[r] += 1  # type: ignore
            col_sums[c] += 1  # type: ignore
        
        # Create puzzle instance
        puzzle = SnakePuzzle(row_sums, col_sums, start_cell, end_cell)
        
        # Verify the generated path is a valid solution
        if puzzle.is_valid_solution(snake_path):
            return puzzle, snake_path
        else:
            raise RuntimeError("Generated path is not a valid solution")
    
    def _generate_snake_path(self, rows: int, cols: int, 
                                target_length: int) -> Optional[Tuple[Set[Tuple[int, int]], Tuple[int, int], Tuple[int, int]]]:
        """
        Generate a valid snake path using random walk with backtracking.
        
        Balances interesting patterns with reliable completion.
        
        Args:
            rows: Grid rows
            cols: Grid columns
            target_length: Desired path length
            
        Returns:
            Tuple of (path_set, start_cell, end_cell) if successful, None if failed
        """
        max_attempts = 30  # Moderate number of attempts
        
        for attempt in range(max_attempts):
            
            # Start with a random cell
            start_pos = (random.randint(0, rows - 1), random.randint(0, cols - 1))
            path = [start_pos]
            path_set = {start_pos}
            
            # Growth with bailout limits
            max_steps = target_length * 4  # Reasonable step limit
            steps = 0
            stuck_count = 0
            max_stuck = 5  # Give up after being stuck too many times
            
            while len(path) < target_length and steps < max_steps and stuck_count < max_stuck:
                steps += 1
                current_pos = path[-1]
                r, c = current_pos
                
                # Get orthogonally adjacent positions
                possible_moves = [
                    (r - 1, c),  # Up
                    (r + 1, c),  # Down  
                    (r, c - 1),  # Left
                    (r, c + 1)   # Right
                ]
                
                # Filter moves with proper constraints
                valid_moves = []
                for new_pos in possible_moves:
                    nr, nc = new_pos
                    
                    # Basic checks (always apply)
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        continue
                    if new_pos in path_set:
                        continue
                    
                    # Apply orthogonal adjacency constraint
                    is_adjacent_to_body = False
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        adjacent_pos = (nr + dr, nc + dc)
                        if adjacent_pos in path_set and adjacent_pos != current_pos:
                            is_adjacent_to_body = True
                            break
                    if is_adjacent_to_body:
                        continue
                    
                    # Apply diagonal touching constraint
                    if self._would_create_diagonal_touching(path_set, new_pos):
                        continue
                    
                    valid_moves.append(new_pos)
                
                if valid_moves:
                    # Grow the path
                    next_pos = random.choice(valid_moves)
                    path.append(next_pos)
                    path_set.add(next_pos)
                    stuck_count = 0  # Reset stuck counter
                else:
                    # Backtrack
                    if len(path) <= 1:
                        break
                    
                    # Remove 1-2 recent cells
                    backtrack_amount = min(random.randint(1, 2), len(path) - 1)
                    for _ in range(backtrack_amount):
                        if len(path) > 1:
                            removed = path.pop()
                            path_set.remove(removed)
                    
                    stuck_count += 1
            
            if len(path) >= target_length:
                start_cell = path[0]
                end_cell = path[-1]
                return set(path), start_cell, end_cell
        
        return None  # Failed to generate valid path

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

from typing import List, Set, Tuple, Optional, Union


class SnakePuzzle:
    """
    Represents a Snake puzzle.
    
    Rules of Snake:
    - The snake's body can be filled in horizontally and vertically and must connect the given start and end cells
    - The body must never touch itself, not even diagonally
    - The numbers outside the playing grid tell you how many cells must be filled in for a row or column (may be blank)
    """
    
    def __init__(self, 
                 row_sums: List[Union[int, None]],
                 col_sums: List[Union[int, None]],
                 start_cell: Tuple[int, int],
                 end_cell: Tuple[int, int]):
        """
        Initialize a Snake puzzle.
        
        Args:
            row_sums: List of required sums for each row (None for unlabelled rows)
            col_sums: List of required sums for each column (None for unlabelled columns)
            start_cell: (row, col) position where the snake starts
            end_cell: (row, col) position where the snake ends
                
        Raises:
            ValueError: If puzzle configuration is invalid
        """
        # Deduce grid dimensions from constraint lists
        rows = len(row_sums)
        cols = len(col_sums)
        
        # Validate inputs
        if rows <= 0:
            raise ValueError("Number of rows must be positive")
        if cols <= 0:
            raise ValueError("Number of columns must be positive")
        
        # Validate start and end cells
        if not (0 <= start_cell[0] < rows and 0 <= start_cell[1] < cols):
            raise ValueError(f"Start cell {start_cell} is out of bounds")
        if not (0 <= end_cell[0] < rows and 0 <= end_cell[1] < cols):
            raise ValueError(f"End cell {end_cell} is out of bounds")
        if start_cell == end_cell:
            raise ValueError("Start cell and end cell cannot be the same")
        
        # Store puzzle configuration
        self.rows = rows
        self.cols = cols
        self.row_sums = row_sums.copy()
        self.col_sums = col_sums.copy()
        self.start_cell = start_cell
        self.end_cell = end_cell
        
        # Offset patterns for different types of tile relationships
        self._orthogonal_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self._diagonal_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        # Validate puzzle configuration
        self._validate_puzzle()
    
    def is_valid_solution(self, solution: Set[Tuple[int, int]]) -> bool:
        """
        Check if the given solution satisfies all puzzle constraints.

        Args:
            solution: Set of positions (row, col) representing the filled cells of the snake

        Returns:
            True if the solution is valid, False otherwise
        """
        if not solution:
            return False
            
        # Check that start and end cells are included
        if self.start_cell not in solution:
            return False
        if self.end_cell not in solution:
            return False
            
        # Check that all positions are within bounds
        for row, col in solution:
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                return False
        
        # Check row sums
        for row_idx, expected_sum in enumerate(self.row_sums):
            if expected_sum is not None:
                actual_sum = sum(1 for r, c in solution if r == row_idx)
                if actual_sum != expected_sum:
                    return False
        
        # Check column sums
        for col_idx, expected_sum in enumerate(self.col_sums):
            if expected_sum is not None:
                actual_sum = sum(1 for r, c in solution if c == col_idx)
                if actual_sum != expected_sum:
                    return False
        
        # Check that snake doesn't touch itself diagonally
        if not self._check_no_diagonal_touching(solution):
            return False
            
        # Check that snake forms a connected path from start to end
        if not self._check_snake_path(solution):
            return False
            
        return True
    
    def __repr__(self) -> str:
        return f"SnakePuzzle(rows={self.rows}, cols={self.cols}, start={self.start_cell}, end={self.end_cell})"
        
    def _validate_puzzle(self) -> None:
        """Validate that the puzzle configuration is valid."""
        # Check that row sums are reasonable
        for i, row_sum in enumerate(self.row_sums):
            if row_sum is not None and (row_sum < 0 or row_sum > self.cols):
                raise ValueError(f"Row {i} sum {row_sum} must be between 0 and {self.cols}")
        
        # Check that column sums are reasonable
        for i, col_sum in enumerate(self.col_sums):
            if col_sum is not None and (col_sum < 0 or col_sum > self.rows):
                raise ValueError(f"Column {i} sum {col_sum} must be between 0 and {self.rows}")
    
    def is_within_bounds(self, row: int, col: int) -> bool:
        """Check if the given position is within puzzle boundaries."""
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def get_tile_by_offset(self, position: Tuple[int, int], offset: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Get the tile at the specified offset from the given position.
        
        Args:
            position: Starting (row, col) position
            offset: (row_delta, col_delta) offset
            
        Returns:
            (row, col) tuple if valid position, None otherwise
        """
        row, col = position
        new_row, new_col = row + offset[0], col + offset[1]
        return (new_row, new_col) if self.is_within_bounds(new_row, new_col) else None
    
    def get_tiles_by_offsets(self, position: Tuple[int, int], offsets: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """
        Get all valid tiles at the specified offsets from the given position.
        
        Args:
            position: Starting (row, col) position
            offsets: List of (row_delta, col_delta) offsets
            
        Returns:
            Set of valid (row, col) tuples (excludes None values)
        """
        tiles = set()
        for offset in offsets:
            tile = self.get_tile_by_offset(position, offset)
            if tile is not None:
                tiles.add(tile)
        return tiles
    
    def _check_no_diagonal_touching(self, solution: Set[Tuple[int, int]]) -> bool:
        """
        Check that no two cells in the solution touch diagonally.
        
        Args:
            solution: Set of filled positions
            
        Returns:
            True if no diagonal touching, False otherwise
        """
        for position in solution:
            row, col = position
            # Check all 4 diagonal neighbors using the offset pattern
            diagonal_neighbors = self.get_tiles_by_offsets(position, self._diagonal_offsets)
            
            for diagonal_pos in diagonal_neighbors:
                if diagonal_pos in solution:
                    # Check if they are connected by orthogonal cells
                    # If there are orthogonal connections, diagonal touching is allowed
                    orthogonal_neighbors = self.get_tiles_by_offsets(position, self._orthogonal_offsets)
                    diagonal_orthogonal_neighbors = self.get_tiles_by_offsets(diagonal_pos, self._orthogonal_offsets)
                    
                    # Check if there's an orthogonal path connecting the two diagonal cells
                    shared_orthogonal = orthogonal_neighbors.intersection(diagonal_orthogonal_neighbors)
                    orthogonal_connections = shared_orthogonal.intersection(solution)
                    
                    # If diagonal cells touch but no orthogonal connection exists, it's invalid
                    if not orthogonal_connections:
                        return False
        
        return True
    
    def _check_snake_path(self, solution: Set[Tuple[int, int]]) -> bool:
        """
        Check that the solution forms a valid snake path from start to end.
        A valid snake path means:
        1. All cells are connected orthogonally
        2. The path forms a single continuous line (no branches)
        3. Start and end cells have exactly 1 neighbor each
        4. All other cells have exactly 2 neighbors each
        
        Args:
            solution: Set of filled positions
            
        Returns:
            True if valid snake path, False otherwise
        """
        if not solution:
            return False
            
        # Count neighbors for each cell
        neighbor_count = {}
        for position in solution:
            orthogonal_neighbors = self.get_tiles_by_offsets(position, self._orthogonal_offsets)
            count = len(orthogonal_neighbors.intersection(solution))
            neighbor_count[position] = count
        
        # Check start and end cells have exactly 1 neighbor
        if neighbor_count.get(self.start_cell, 0) != 1:
            return False
        if neighbor_count.get(self.end_cell, 0) != 1:
            return False
            
        # Check all other cells have exactly 2 neighbors (forming a path)
        for cell, count in neighbor_count.items():
            if cell not in (self.start_cell, self.end_cell):
                if count != 2:
                    return False
        
        # Check connectivity from start to end using DFS
        visited = set()
        
        def dfs(current):
            if current in visited:
                return
            visited.add(current)
            
            orthogonal_neighbors = self.get_tiles_by_offsets(current, self._orthogonal_offsets)
            for neighbor in orthogonal_neighbors:
                if neighbor in solution and neighbor not in visited:
                    dfs(neighbor)
        
        # Start DFS from start_cell
        dfs(self.start_cell)
        
        # All cells should be reachable from start
        return len(visited) == len(solution) and self.end_cell in visited
    
    def get_grid_size(self) -> Tuple[int, int]:
        """Get the grid dimensions."""
        return (self.rows, self.cols)
    
    def get_row_sum(self, row: int) -> Optional[int]:
        """Get the required sum for a specific row."""
        if 0 <= row < self.rows:
            return self.row_sums[row]
        raise IndexError(f"Row {row} out of bounds")
    
    def get_col_sum(self, col: int) -> Optional[int]:
        """Get the required sum for a specific column."""
        if 0 <= col < self.cols:
            return self.col_sums[col]
        raise IndexError(f"Column {col} out of bounds")
    
    def get_start_cell(self) -> Tuple[int, int]:
        """Get the start cell position."""
        return self.start_cell
    
    def get_end_cell(self) -> Tuple[int, int]:
        """Get the end cell position."""
        return self.end_cell
    
    def get_board_visualization(self, snake_positions: Optional[Set[Tuple[int, int]]] = None, 
                     show_indices: bool = False) -> str:
        """
        Create a string representation of the puzzle.
        
        Args:
            snake_positions: Optional set of snake body positions to display
            show_indices: Whether to show row/column indices
            
        Returns:
            String representation of the puzzle
        """
        snake_positions = snake_positions or set()
        lines = []
        
        # Header with column indices and sums
        if show_indices:
            header = "    " + " ".join(str(i) for i in range(self.cols))
            lines.append(header)
            col_sums_line = "    " + " ".join(str(s) if s is not None else "?" for s in self.col_sums)
        else:
            col_sums_line = "  " + " ".join(str(s) if s is not None else "?" for s in self.col_sums)
        
        lines.append(col_sums_line)
        
        # Board rows
        for row in range(self.rows):
            row_parts = []
            
            if show_indices:
                row_parts.append(str(row))
            
            row_sum_str = str(self.row_sums[row]) if self.row_sums[row] is not None else "?"
            row_parts.append(row_sum_str)
            
            for col in range(self.cols):
                pos = (row, col)
                if pos == self.start_cell:
                    row_parts.append('S')
                elif pos == self.end_cell:
                    row_parts.append('E')
                elif pos in snake_positions:
                    row_parts.append('x') # █
                else:
                    row_parts.append('_')
            
            lines.append(' '.join(row_parts))
        
        return '\n'.join(lines)
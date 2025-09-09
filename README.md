# Snake MIP Solver

[![CI](https://github.com/DenHvideDvaerg/snake-mip-solver/actions/workflows/ci.yml/badge.svg)](https://github.com/DenHvideDvaerg/snake-mip-solver/actions/workflows/ci.yml)
[![Code Coverage](https://img.shields.io/codecov/c/github/DenHvideDvaerg/snake-mip-solver?color=blue)](https://codecov.io/gh/DenHvideDvaerg/snake-mip-solver)
[![PyPI version](https://img.shields.io/pypi/v/snake-mip-solver?color=green)](https://pypi.org/project/snake-mip-solver/)
[![Python](https://img.shields.io/pypi/pyversions/snake-mip-solver?color=blue)](https://pypi.org/project/snake-mip-solver/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Snake puzzle solver using mathematical programming.

## Overview

Snake is a logic puzzle where you must create a single connected path on a grid according to these rules:

- **Single connected path** - the snake forms one continuous line from start to end cell
- **No self-touching** - the snake body never touches itself, neither orthogonally nor diagonally
- **Row and column constraints** - each row/column must have a specific number of filled cells
  - **Missing constraints variant** - supports puzzles where some row/column constraints are unknown (specified as `None`)

This package provides:
- **SnakeSolver** - models puzzles as Mixed Integer Programming (MIP) problems to find solutions
- **SnakePuzzleGenerator** - creates random valid puzzles using random walk and backtracking

## Try It Online

🚀 **[Interactive Dashboard](https://snake-dashboard.streamlit.app/)** - Try the solver in your browser with a user-friendly interface built with Streamlit!


## Installation

```bash
pip install snake-mip-solver
```

## Requirements

- Python 3.9+
- Google OR-Tools
- pytest (for testing)

## Example Puzzles

### 6x6 Easy Puzzle

This 6x6 puzzle demonstrates a straightforward Snake puzzle:

| Puzzle | Solution |
|--------|----------|
| <img src="https://github.com/DenHvideDvaerg/snake-mip-solver/raw/main/images/6x6_Easy.png" width="400"> | <img src="https://github.com/DenHvideDvaerg/snake-mip-solver/raw/main/images/6x6_Easy_solution.png" width="400"> |

```python
def example_6x6_easy():
    """6x6 easy example"""
    puzzle = SnakePuzzle(
        row_sums=[1, 1, 1, 3, 2, 5],
        col_sums=[4, 3, 1, 1, 1, 3],
        start_cell=(0, 0),
        end_cell=(3, 5)
    )
    return puzzle
```

### 12x12 Evil Puzzle with Missing Constraints

This 12x12 puzzle demonstrates a challenging large-scale puzzle with missing row/column constraints:

| Puzzle | Solution |
|--------|----------|
| <img src="https://github.com/DenHvideDvaerg/snake-mip-solver/raw/main/images/12x12_Evil.png" width="400"> | <img src="https://github.com/DenHvideDvaerg/snake-mip-solver/raw/main/images/12x12_Evil_solution.png" width="400"> |

```python
def example_12x12_evil():
    """12x12 'Evil' puzzle from https://gridpuzzle.com/snake/evil-12"""
    puzzle = SnakePuzzle(
        row_sums=[11, 2, 7, 4, 4, None, None, None, 3, 2, None, 5],
        col_sums=[9, 7, None, 2, 5, 6, None, None, 5, None, None, None],
        start_cell=(2, 6),
        end_cell=(7, 5)
    )
    return puzzle
```

## Usage

```python
from snake_mip_solver import SnakePuzzle, SnakeSolver, SnakePuzzleGenerator
import time

def solve_puzzle(puzzle, name):
    """Solve a snake puzzle and display results"""
    print(f"\n" + "="*60)
    print(f"SOLVING {name.upper()}")
    print("="*60)
    
    # Create and use the solver
    solver = SnakeSolver(puzzle)
    
    print("Solver information:")
    info = solver.get_solver_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\nSolving...")
    start_time = time.time()
    solution = solver.solve(verbose=False)
    solve_time = time.time() - start_time
    
    if solution:
        print(f"\nSolution found in {solve_time:.3f} seconds!")
        print(f"Solution has {len(solution)} filled cells")
        print(f"Solution: {sorted(list(solution))}")
        
        # Display the board with solution
        print("\nPuzzle with solution:")
        print(puzzle.get_board_visualization(solution, show_indices=False))
        
        # Validate solution
        if puzzle.is_valid_solution(solution):
            print("✅ Solution is valid!")
        else:
            print("❌ Solution validation failed!")
    else:
        print(f"\nNo solution found (took {solve_time:.3f} seconds)")

# Load and solve example puzzles
puzzle_6x6 = example_6x6_easy()
solve_puzzle(puzzle_6x6, "6x6 Easy")

puzzle_12x12 = example_12x12_evil()
solve_puzzle(puzzle_12x12, "12x12 Evil")
```

### Output

```
============================================================
SOLVING 6X6 EASY
============================================================
Solver information:
  solver_type: SCIP 9.2.2 [LP solver: SoPlex 7.1.3]
  num_variables: 36
  num_constraints: 159
  puzzle_size: 6x6
  start_cell: (0, 0)
  end_cell: (3, 5)

Solving...

Solution found in 0.002 seconds!
Solution has 13 filled cells
Solution: [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1), (3, 5), (4, 1), (4, 5), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5)]

Puzzle with solution:
  4 3 1 1 1 3
1 S _ _ _ _ _
1 x _ _ _ _ _
1 x _ _ _ _ _
3 x x _ _ _ E
2 _ x _ _ _ x
5 _ x x x x x
✅ Solution is valid!

============================================================
SOLVING 12X12 EVIL
============================================================
Solver information:
  solver_type: SCIP 9.2.2 [LP solver: SoPlex 7.1.3]
  num_variables: 144
  num_constraints: 665
  puzzle_size: 12x12
  start_cell: (2, 6)
  end_cell: (7, 5)

Solving...

Solution found in 0.255 seconds!
Solution has 49 filled cells
Solution: [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (1, 1), (1, 11), (2, 0), (2, 1), (2, 6), (2, 8), (2, 9), (2, 10), (2, 11), (3, 0), (3, 5), (3, 6), (3, 8), (4, 0), (4, 1), (4, 5), (4, 8), (5, 1), (5, 5), (5, 6), (5, 7), (5, 8), (6, 0), (6, 1), (7, 0), (7, 5), (8, 0), (8, 4), (8, 5), (9, 0), (9, 4), (10, 0), (10, 4), (11, 0), (11, 1), (11, 2), (11, 3), (11, 4)]

Puzzle with solution:
   9 7 ? 2 5 6 ? ? 5 ? ? ?
11 _ x x x x x x x x x x x
 2 _ x _ _ _ _ _ _ _ _ _ x
 7 x x _ _ _ _ S _ x x x x
 4 x _ _ _ _ x x _ x _ _ _
 4 x x _ _ _ x _ _ x _ _ _
 ? _ x _ _ _ x x x x _ _ _
 ? x x _ _ _ _ _ _ _ _ _ _
 ? x _ _ _ _ E _ _ _ _ _ _
 3 x _ _ _ x x _ _ _ _ _ _
 2 x _ _ _ x _ _ _ _ _ _ _
 ? x _ _ _ x _ _ _ _ _ _ _
 5 x x x x x _ _ _ _ _ _ _
✅ Solution is valid!
```

### Running the example

The repository includes a complete example in `main.py`:

```bash
python main.py
```

## Generating Random Puzzles

The `SnakePuzzleGenerator` class allows you to create random Snake puzzles with valid solutions. Puzzles are created using random walk with backtracking to create interesting, non-trivial snake patterns that adhere to all puzzle rules. 

### Parameters and Features

- **`rows`, `cols`** (int): Grid dimensions (must be > 0)
- **`fill_percentage`** (float): Target percentage of cells to fill (0.0 < value ≤ 1.0)
  - Generator will achieve this target or fail completely - choose sensible values (~50% max works well)
- **`seed`** (int, optional): Random seed for reproducible generation

### Usage

```python
from snake_mip_solver import SnakePuzzleGenerator, SnakeSolver

# Generate random puzzle
generator = SnakePuzzleGenerator(seed=42)
random_puzzle, solution_path = generator.generate(
    rows=12, 
    cols=12, 
    fill_percentage=0.5  # Target 50% of cells filled
)

# Display the generated puzzle with its solution
print(random_puzzle.get_board_visualization(solution_path))

# Verify the solver returns the same solution
calculated_solution = SnakeSolver(random_puzzle).solve()
print(f'Calculated solution matches: {solution_path == calculated_solution}')
```

### Output
```
  7 5 9 5 4 6 6 3 8 5 8 6
8 x x x _ _ _ x x x x x _
4 x _ x _ _ _ x _ _ _ x _
7 x _ x _ x x x _ _ x x _
5 x _ x _ x _ _ _ x x _ _
7 x _ x x x _ S _ x _ _ E
6 x _ _ _ _ _ x x x _ x x
5 x x x x _ _ _ _ _ _ x _
6 _ _ _ x _ x x x x _ x _
6 _ _ x x _ x _ _ x _ x x
5 _ x x _ _ x _ _ x _ _ x
5 _ x _ _ _ x _ _ x x _ x
8 _ x x x x x _ _ _ x x x
Calculated solution matches: True
```

## Testing

The project uses pytest for testing:

```bash
pytest
pytest --cov=snake_mip_solver # Run with coverage
```

## Mathematical Model

The solver uses **Mixed Integer Programming (MIP)** to model the puzzle constraints. Google OR-Tools provides the optimization framework, with SCIP as the default solver.

The mathematical formulation includes six types of constraints:
1. **Start and End Cell Constraints** - fixing the path endpoints
2. **Row Sum Constraints** - ensuring correct number of cells per row
3. **Column Sum Constraints** - ensuring correct number of cells per column  
4. **Snake Path Connectivity Constraints** - forming a single connected path
5. **Diagonal Non-Touching Constraints** - preventing diagonal self-contact
6. **No 2×2 Block Constraints** - preventing disconnected filled blocks

**Connectivity Enforcement:** Even with these constraints it is still theoretically possible to have disconnected components in a solution. Therefore, the solver uses an **iterative cutting planes approach** to ensure true connectivity.

See the complete formulation in **[Complete Mathematical Model Documentation](https://github.com/DenHvideDvaerg/snake-mip-solver/blob/main/model.md)**

## License

This project is open source and available under the [MIT License](LICENSE).

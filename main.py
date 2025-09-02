from snake_mip_solver import SnakePuzzle, SnakeSolver
import time


def example_3x3():
    """Simple 3x3 example for testing"""
    puzzle = SnakePuzzle(
        row_sums=[2, 1, 2],
        col_sums=[1, 3, 1],
        start_cell=(0, 0),
        end_cell=(2, 2)
    )
    return puzzle


def example_diagonal_touching():
    """Diagonal touching example (infeasible)"""
    puzzle = SnakePuzzle(
        row_sums=[2, 3, 3, 0, 0],
        col_sums=[0, 3, 2, 2, 1],
        start_cell=(0, 2),
        end_cell=(1, 4)
    )
    return puzzle

def example_adjacent_touching():
    """Adjacent touching example (infeasible)"""
    puzzle = SnakePuzzle(
        row_sums=[1, 4, 3, 0],
        col_sums=[3, 2, 1, 2],
        start_cell=(0, 0),
        end_cell=(3, 3)
    )
    return puzzle

def example_6x6_easy():
    """6x6 easy example"""
    puzzle = SnakePuzzle(
        row_sums=[1, 1, 1, 3, 2, 5],
        col_sums=[4, 3, 1, 1, 1, 3],
        start_cell=(0, 0),
        end_cell=(3, 5)
    )
    return puzzle

def example_12x12_evil():
    """12x12 'Evil' puzzle from https://gridpuzzle.com/snake/evil-12"""
    puzzle = SnakePuzzle(
        row_sums=[11, 2, 7, 4, 4, None, None, None, 3, 2, None, 5],
        col_sums=[9, 7, None, 2, 5, 6, None, None, 5, None, None, None],
        start_cell=(2, 6),
        end_cell=(7, 5)
    )
    return puzzle

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


def main():
    # Solve different puzzle examples
    puzzle_6x6 = example_6x6_easy()
    solve_puzzle(puzzle_6x6, "6x6 Easy")

    puzzle_12x12 = example_12x12_evil()
    solve_puzzle(puzzle_12x12, "12x12 Evil")

if __name__ == "__main__":
    main()
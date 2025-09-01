from snake_mip_solver import SnakePuzzle, SnakeSolver
import time


def example_8x8():
    """8x8 example from https://puzzlegenius.org/snake/"""
    puzzle = SnakePuzzle(
        row_sums=[4, 2, 2, 3, 1, 3, 2, 6],
        col_sums=[3, 2, 7, 2, 2, 4, 1, 2],
        start_cell=(2, 5),
        end_cell=(6, 7)
    )
    return puzzle


def main():
    """
    Example usage of the Snake solver.
    
    """
    print("Snake MIP Solver - Example Usage")
    print("=" * 50)
    

    try:
        puzzle = example_8x8()
        print(f"Created puzzle: {puzzle}")
        
        # Create solver
        solver = SnakeSolver(puzzle)
        print("Solver initialized successfully")
        
        # Solve the puzzle
        print("\nSolving puzzle...")
        start_time = time.time()
        solution = solver.solve(verbose=True)
        solve_time = time.time() - start_time
        
        # Display results
        if solution is not None:
            print(f"\n✅ Solution found in {solve_time:.3f} seconds!")
            print(f"Solution: {solution}")
            print(puzzle.get_board_visualization())
            
            manual_solution = set()
            manual_solution.add((2, 5))
            manual_solution.add((1, 5))
            manual_solution.add((0, 5))
            manual_solution.add((0, 4))
            manual_solution.add((0, 3))
            manual_solution.add((0, 2))
            manual_solution.add((1, 2))
            manual_solution.add((2, 2))
            manual_solution.add((3, 2))
            manual_solution.add((3, 1))
            manual_solution.add((3, 0))
            manual_solution.add((4, 0))
            manual_solution.add((5, 0))
            manual_solution.add((5, 1))
            manual_solution.add((5, 2))
            manual_solution.add((6, 2))
            manual_solution.add((7, 2))
            manual_solution.add((7, 3))
            manual_solution.add((7, 4))
            manual_solution.add((7, 5))
            manual_solution.add((7, 6))
            manual_solution.add((7, 7))
            manual_solution.add((6, 7))
            print(puzzle.get_board_visualization(manual_solution, show_indices=True))
            print(f"Manual solution valid? {puzzle.is_valid_solution(manual_solution)}")
            # TODO: Add solution visualization or validation
            # Example:
            # if puzzle.is_valid_solution(solution):
            #     print("Solution is valid!")
            #     display_solution(puzzle, solution)
            # else:
            #     print("Solution validation failed!")
        else:
            print(f"\nNo solution found (took {solve_time:.3f} seconds)")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to implement your puzzle class and solver logic!")


if __name__ == "__main__":
    main()
from snake_mip_solver import SnakePuzzle, SnakeSolver
import time


def main():
    """
    Example usage of the Snake solver.
    
    TODO: Replace with your specific puzzle parameters and usage.
    """
    print("Snake MIP Solver - Example Usage")
    print("=" * 50)
    
    # TODO: Create your puzzle instance
    # Example:
    # puzzle = SnakePuzzle(
    #     size=5,
    #     constraints=[1, 2, 3, 2, 1]
    # )
    
    try:
        # For now, create a basic puzzle (replace with your parameters)
        puzzle = SnakePuzzle()
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
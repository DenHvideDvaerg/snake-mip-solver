<!--
## Development Checklist

Complete these tasks to fully implement Snake solver:

**Note:** Complete phases in order to ensure badges and links work correctly!

### Phase 1: Core Implementation
- [ ] **Implement puzzle logic** in `snake_mip_solver/puzzle.py`
  - [ ] Define puzzle parameters and constraints
  - [ ] Add validation methods (ensure puzzle is well-formed)
  - [ ] Implement solution verification
- [ ] **Implement MIP solver** in `snake_mip_solver/solver.py`
  - [ ] Add decision variables and constraints
  - [ ] Implement solution extraction
- [ ] **Update tests** in `tests/`
  - [ ] Add test cases for puzzle validation
  - [ ] Add solver test cases with known solutions
  - [ ] Ensure good test coverage

### Phase 2: Documentation & Examples  
- [ ] **Update main.py** with working example
- [ ] **Update README.md** with proper usage examples
- [ ] **Test locally** - ensure `python main.py` and `pytest` work
- [ ] **Complete mathematical model** in `model.md`
  - [ ] Define sets, variables, and constraints and write full model
  - [ ] Add illustrations/examples if required

### Phase 3: Repository Setup
- [ ] **Create GitHub repository** (public)
- [ ] **Push initial code** and verify CI passes
- [ ] **Set up Codecov**
  - [ ] Add repository to Codecov
  - [ ] Configure coverage reporting
  - [ ] Verify coverage badge works

### Phase 4: Publishing
- [ ] **Test package building** with `python build_package.py`
- [ ] **Publish to PyPI** with `python -m twine upload dist/*`
- [ ] **Verify PyPI page** and badges in README
- [ ] **Test installation** from PyPI: `pip install snake-mip-solver`

### Phase 5: Final Polish
- [ ] **Remove this checklist** from README
- [ ] **Add project-specific documentation**
- [ ] **Update version** and create release tag
-->

# Snake MIP Solver

[![CI](https://github.com/DenHvideDvaerg/snake-mip-solver/actions/workflows/ci.yml/badge.svg)](https://github.com/DenHvideDvaerg/snake-mip-solver/actions/workflows/ci.yml)
[![Code Coverage](https://img.shields.io/codecov/c/github/DenHvideDvaerg/snake-mip-solver?color=blue)](https://codecov.io/gh/DenHvideDvaerg/snake-mip-solver)
[![PyPI version](https://img.shields.io/pypi/v/snake-mip-solver?color=green)](https://pypi.org/project/snake-mip-solver/)
[![Python](https://img.shields.io/pypi/pyversions/snake-mip-solver?color=blue)](https://pypi.org/project/snake-mip-solver/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Snake puzzle solver using mathematical programming.

## Overview

Snake is a logic puzzle where ...

This solver models the puzzle as a **Mixed Integer Programming (MIP)** problem to find solutions.

## Installation

```bash
pip install snake-mip-solver
```

## Requirements

- Python >=3.9
- Google OR-Tools
- pytest (for testing)

## Usage

```python
from snake_mip_solver import SnakePuzzle, SnakeSolver

# TODO: Make example either a direct copy of or very similar to main.py 
```

### Running the example

The repository includes a complete example in `main.py`:

```bash
python main.py
```

## Testing

The project uses pytest for testing:

```bash
pytest
pytest --cov=snake_mip_solver # Run with coverage
```

## Mathematical Model

The solver uses **Mixed Integer Programming (MIP)** to model the puzzle constraints. Google OR-Tools provides the optimization framework, with SCIP as the default solver.

See the complete formulation in **[Complete Mathematical Model Documentation](https://github.com/DenHvideDvaerg/snake-mip-solver/blob/main/model.md)**


## License

This project is open source and available under the [MIT License](LICENSE).
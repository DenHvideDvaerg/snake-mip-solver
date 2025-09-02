# Mathematical Model Documentation

This document provides a formal mathematical programming formulation of the Snake puzzle as a Mixed Integer Programming (MIP) problem.

## Problem Definition

Given:
- An **m × n** grid representing the puzzle board
- **Row sum requirements** R = {r₁, r₂, ..., rₘ} where rᵢ is the required number of snake cells in row i, or undefined if no requirement is given
- **Column sum requirements** C = {c₁, c₂, ..., cₙ} where cⱼ is the required number of snake cells in column j, or undefined if no requirement is given
- **Start cell** (s₁, s₂) where the snake path must begin
- **End cell** (e₁, e₂) where the snake path must terminate

**Objective:** Find which cells to fill to create a valid snake path that satisfies all Snake puzzle rules:
- The snake forms a single connected path from start to end
- The snake body never touches itself, neither orthogonally nor diagonally  
- Row and column sum requirements are satisfied

## Sets and Indices

| Symbol | Definition |
|--------|------------|
| **I** | Set of row indices: I = {0, 1, ..., m-1} |
| **J** | Set of column indices: J = {0, 1, ..., n-1} |
| **N(i,j)** | Set of orthogonally adjacent cells to (i,j): N(i,j) = {(i',j') : \|i-i'\| + \|j-j'\| = 1, (i',j') ∈ I×J} |
| **D(i,j)** | Set of diagonally adjacent cells to (i,j): D(i,j) = {(i',j') : \|i-i'\| = 1, \|j-j'\| = 1, (i',j') ∈ I×J} |

## Decision Variables

| Variable | Domain | Definition |
|----------|--------|------------|
| **x_{i,j}** | {0, 1} | 1 if cell (i,j) is part of the snake path, 0 otherwise |

## Objective Function

This is a constraint satisfaction problem where the goal is to find a feasible solution that satisfies all constraints without optimizing any particular objective. Therefore, we define the objective function as:

```
minimize 0
```

## Constraints

### 1. Start and End Cell Constraints

The start and end cells must be part of the snake path:

```
x_{s₁,s₂} = 1
x_{e₁,e₂} = 1
```

### 2. Row Sum Constraints

For each row i with a defined requirement rᵢ:

```
∑_{j∈J} x_{i,j} = rᵢ    ∀i ∈ I : rᵢ is defined
```

### 3. Column Sum Constraints

For each column j with a defined requirement cⱼ:

```
∑_{i∈I} x_{i,j} = cⱼ    ∀j ∈ J : cⱼ is defined
```

### 4. Snake Path Connectivity Constraints

The snake must form a single connected linear path from start to end with no self-touching:

**Start and end cells must have exactly one neighbor:**
```
∑_{(i',j') ∈ N(s₁,s₂)} x_{i',j'} = 1
∑_{(i',j') ∈ N(e₁,e₂)} x_{i',j'} = 1
```

**Other cells must have exactly 2 neighbors if activated, or no limit if not activated:**
```
∑_{(i',j') ∈ N(i,j)} x_{i',j'} ≥ 2 · x_{i,j}                  ∀(i,j) ∈ I×J : (i,j) ≠ (s₁,s₂), (i,j) ≠ (e₁,e₂)
∑_{(i',j') ∈ N(i,j)} x_{i',j'} ≤ 4 - 2 · x_{i,j}              ∀(i,j) ∈ I×J : (i,j) ≠ (s₁,s₂), (i,j) ≠ (e₁,e₂)
```

These two inequalities create conditional constraints. 
- When x_{i,j} = 1 (cell is activated), they become "∑x_{i',j'} x_{i',j'} ≥ 2" and "∑x_{i',j'} x_{i',j'} ≤ 2", enforcing exactly 2 neighbors. 
- When x_{i,j} = 0 (cell is not activated), they become "∑x_{i',j'} x_{i',j'} ≥ 0" and "∑x_{i',j'} x_{i',j'} ≤ 4", which impose no meaningful restriction. 

This ensures that only activated cells contribute to the snake path structure, while non-activated cells are free to have any number of activated neighbors.

### 5. Diagonal Non-Touching Constraints

The snake body cannot touch itself diagonally. Two diagonally adjacent cells can only both be part of the snake if there is an orthogonal connection between them (i.e., they are connected through the snake path, not just touching):

```
x_{i,j} + x_{i',j'} ≤ x_{i,j'} + x_{i',j} + 1    ∀(i,j) ∈ I×J, ∀(i',j') ∈ D(i,j) such that (i,j'), (i',j) ∈ I×J
```

This constraint allows diagonal adjacency only when there's an orthogonal path connection, preventing the snake from "touching itself" diagonally. The constraint requires that if two diagonally adjacent cells `(i,j)` and `(i',j')` are both filled, then at least one of the two orthogonal "bridge" cells `(i,j')` or `(i',j)` must also be filled. The domain restriction ensures these bridge cells are within the grid bounds.

### 6. No 2×2 Block Constraints

The snake cannot form solid 2×2 blocks. For every 2×2 sub-grid, at most 3 cells can be part of the snake:

```
x_{i,j} + x_{i,j+1} + x_{i+1,j} + x_{i+1,j+1} ≤ 3    ∀i ∈ {0,1,...,m-2}, ∀j ∈ {0,1,...,n-2}
```

This constraint is essential to prevent disconnected filled 2×2 blocks, which would otherwise satisfy both the snake path connectivity constraints (constraint 4) and diagonal non-touching constraints (constraint 5) but violate the fundamental snake rule that the path must be a single connected line. A filled 2×2 block has each cell with exactly 2 orthogonal neighbors (satisfying constraint 4) and all diagonal pairs connected through orthogonal bridges (satisfying constraint 5), but forms an illegal disconnected component that is not part of a linear snake path.

#### Example: 12×12 'Evil' Puzzle

The necessity of this constraint is demonstrated by the 12×12 'Evil' puzzle used as an example elsewhere. Without the 2×2 block constraint, the solver produces an invalid solution containing a disconnected 2×2 block:

```
**Invalid solution (without 2×2 constraint):**
   9 7 ? 2 5 6 ? ? 5 ? ? ?
11 _ x x x x x x x x x x x
 2 _ x _ _ _ _ _ _ _ _ _ x
 7 x x _ _ _ x S _ _ x x x
 4 x _ _ _ _ x _ _ x x _ _
 4 x _ _ _ _ x _ x x _ _ _
 ? x _ _ _ _ x x x _ _ _ _
 ? x x _ _ _ _ _ _ _ _ _ _
 ? _ x _ _ x E _ _ _ _ _ _
 3 x x _ _ x _ _ _ _ _ _ _
 2 x _ _ _ x _ _ _ _ _ _ _
 ? x _ x x x _ _ _ x x _ _  ← 2x2 block
 5 x x x _ _ _ _ _ x x _ _

**Correct solution (with 2×2 constraint):**
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
```

## Complete MIP Formulation

**Variables:**
```
x_{i,j} ∈ {0,1}    ∀(i,j) ∈ I×J
```

**Objective:**
```
minimize 0
```

**Subject to:**
```
x_{s₁,s₂} = 1
x_{e₁,e₂} = 1

∑_{j∈J} x_{i,j} = rᵢ                                           ∀i ∈ I : rᵢ is defined

∑_{i∈I} x_{i,j} = cⱼ                                           ∀j ∈ J : cⱼ is defined

∑_{(i',j') ∈ N(s₁,s₂)} x_{i',j'} = 1

∑_{(i',j') ∈ N(e₁,e₂)} x_{i',j'} = 1

∑_{(i',j') ∈ N(i,j)} x_{i',j'} ≥ 2 · x_{i,j}                  ∀(i,j) ∈ I×J \ {(s₁,s₂), (e₁,e₂)}

∑_{(i',j') ∈ N(i,j)} x_{i',j'} ≤ 4 - 2 · x_{i,j}              ∀(i,j) ∈ I×J \ {(s₁,s₂), (e₁,e₂)}

x_{i,j} + x_{i',j'} ≤ x_{i,j'} + x_{i',j} + 1                 ∀(i,j) ∈ I×J, ∀(i',j') ∈ D(i,j) : (i,j'), (i',j) ∈ I×J

x_{i,j} + x_{i,j+1} + x_{i+1,j} + x_{i+1,j+1} ≤ 3             ∀i ∈ {0,...,m-2}, ∀j ∈ {0,...,n-2}

x_{i,j} ∈ {0,1}                                                ∀(i,j) ∈ I×J
```
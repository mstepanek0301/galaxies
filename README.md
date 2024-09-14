This is a program for generating and solving [Galaxies](https://www.puzzle-galaxies.com) puzzles. If you don't know what these puzzles are, check out the link, which explains the rules and you can also try to solve the puzzles there.

# The puzzle

There is a rectangular grid which contains some _galaxy centers_. A center can be in the middle of a cell, or on the boundary between two or four cells. A cell can only touch one center.

The goal is to assign every cell to one of the galaxy centers. The set of cells assigned to that center is called a _galaxy_. Every galaxy must be connected (cells are considered neighbours if they share an edge) and it must also be 180-degree rotationally symmetrical. This assignment is a solution to the puzzle.

It is possible for a grid and a set of centers to have no solutions or more than one solution, but for it to be a valid puzzle, it should have exactly one solution (similar to Sudoku etc.).

# Usage

**Solver:** This script finds a solution to a given puzzle, if there is any. Run `solve.py` and input the puzzle (using the standard input). The format is as follows:

- The first line should contain the dimensions of the grid (width x height) separated by whitespace.
- The remaining lines should contain the coordinates of the galaxy centers.
  - The first coordinate is the row (from the top) and the second is the column (from the left).
  - Both are the number of half-cells from the edge, starting at 0. That means galaxies inside cells will have even coordinates while galaxies on edges (between cells) will have odd coordinates.
- Any other whitespace (including blank lines) is ignored.

The output is a description of the resulting grid. Each cell contains the number of the galaxy it belongs to (numbered in the order they appear in the input, starting from 0).

**Generator:** This script generates a random puzzle given the dimensions of the grid. Run `generate.py` and input the width and height, separated by whitespace. The output contains the generated puzzle in the same format as the input of the solver. The generated puzzle is guaranteed to have a unique solution.

**Batch:** The generator generates a random puzzle, not giving you any control over the dificulty. This script generates many puzzles and sorts them based on their estimated difficulty.

Run `batch.py` and input the width, height and number of puzzles you want to generate. These will be sorted into buckets based on their difficulty, as estimated by the solver. The difficulty is represented by two numbers, the _branch count_ and the _force count_ (see the _How it works_ section for more details on what these mean). The output is as follows:

- First, there is an index of the generated puzzles -- for every bucket, there is the number of puzzles in it.
- Then, there is a list of all the puzzles, sorted by their difficulty, in the order they appear in the index. For every puzzle, there is a line with a hashtag and the difficulty, then the puzzle itself (in the format used by the generator and solver), and finally a blank line.

Generally, with a constant density, bigger puzzles are harder to solve (and not just proportionally to their size). **If you want to generate a very big puzzle (bigger than roughly 25x25), consider using a higher density than the default.** With a high density, it is possible to generate much bigger puzzles, as can be seen in the example.

# Examples

The `examples` folder contains some puzzles that you can input to the solver. All of them except `external.in` and `impossible.in` are generated using this generator. The puzzle `external.in` is puzzle #5,280,963 (10x10 Hard) from puzzle-galaxies.com. All of the puzzles except for `impossible.in` have a unique solution.

All of the generated examples were made with the default density (0.14), except for `huge.in`, which had density 0.3.

# Code organization

The galaxies are referred to by their indexes (order in which they appear in the input). The grid (both in the generator and solver) is represented as a dictionary mapping cells (coordinate tuples) to their assigned galaxy IDs. A not-yet-assigned cell is not in the dictionary.

The code is split up into the following files:

- `common.py`: This contains functions used by both the solver and the generator.
- `generate.py`: This implements the function `generate` which generates a puzzle. It is a wrapper for constructing the class `Generate` with the chosen parameters and calling its method `Generate.generate`, which does the work.
- `solver.py`: This implements the function `solve` which finds the solution to a given puzzle and computes some other data along the way. It is a wrapper that constructs the class `Solve` and calls its method `Solve.solve`. This method returns any one solution of the puzzle (or `None` if there is none), and also computes the properties `solution_count`, `branch_count`, and `force_count`.
- `batch.py`: The function `batch` generates many puzzles and returns a dictionary mapping their estimated difficulty (see _How it works_) to the puzzle statements.
- `i_o.py`: This contains functions that read/write the input/output of the functions in other files from/to the standard input/output.

For more information on specific methods, see their docstrings.

# How it works

**Solver:** Every cell has to be assigned to some galaxy, so that all the galaxies are symmetrical. For every galaxy, the cells that touch its center belong to it, the others start as empty. Then, the solver tries to figure out where an empty cell could be assigned.

Then, for every galaxy, its maximum area (all the cells that could potentially belong to it) are computed (similarly to a DFS, but "mirrored", so the galaxies are always symmetrical). If there is any cell that cannot belong to any galaxy (including ones that were already assigned, meaning the galaxy is not connected), then there is no solution. If there are any cells that can only belong to one galaxy, then these are assigned to their respective galaxies -- this is called a _force_. If there is no such cell, then a random cell is picked, and the solver tries to recursively solve the puzzle with this cell assigned to every possible galaxy -- each of these recursive calls is called a _branch_.

The solver counts these forces and branches and uses them to estimate the difficulty of the puzzle (which is used by the batch generator). A puzzle with a small branch count but a high force count is difficult in the sense that it requires more steps to solve, but can be solved using the standard methods. A puzzle with a high branch count is difficult in the sense that it requires some more advanced reasoning (or guesswork).

If the puzzle has more than one solutions, the solver finds any one of them, but internally, the solver actually finds all of them and counts them. This way, the solver can also be used to determine whether the puzzle has a unique solution.

**Generator:** First, the starting number of galaxies is determined based on the *density* (1 / the average size of a galaxy), which is an optional parameter (when running the script, it is set to a reasonable default value). These galaxies are randomly placed into the grid and then grown at random: in each step, a cell next to a galaxy is picked and if possible, the galaxy is expanded into that cell. This is repeated until no more expansions are possible.

Then, the generator finds the remaining connected components. For each component, the generator tests all the possible galaxy centers in it, and finds out which cells could potentially belong to a galaxy with that center. Out of all these potential galaxies, the largest one is added to the grid. This is repeated until there are no more empty cells.

A puzzle generated this way can have more than one solution. To generate a puzzle with a unique solution, puzzles are generated and then solved using the solver, until one with a unique solution is found.

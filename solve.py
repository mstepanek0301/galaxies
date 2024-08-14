from common import *
from random import choice

class Solve:
    def __init__(self, width: int, height: int, galaxies: list[Point]):
        self.width = width
        self.height = height
        self.area = width * height
        self.galaxies = galaxies
        self.centers: dict[int, Point] = {}
        self.grid: dict[Point, int] = {}
        self.force_count = 0
        self.branch_count = 0
        self.solution_count = 0
        self.setup()

    def setup(self):
        '''Assign the centers of all galaxies'''
        for i, galaxy in enumerate(self.galaxies):
            for cell in center_cells(galaxy):
                if self.inside(cell):
                    self.grid[cell] = i
                    self.centers[i] = cell

    def solve(self) -> dict[Point, int] | None:
        '''Count the total number of solutions and return any one of them'''
        if len(self.grid) == self.area:
            # found solution
            self.solution_count += 1
            return self.grid.copy()
        possible = self.possible()
        if possible is None:
            return None
        solved = None
        if len(possible[0][1]) == 1:
            self.force_count += 1
            stop = self.assign_forced(possible)
            if stop is None:
                # if there is no contradiction, we can continue
                solution = self.solve()
                if solution:
                    solved = solution
            # if there was a contradiction, only revert up to that point
            self.revert_forced(possible, stop)
        else:
            cell, options = choice(possible)
            for galaxy in options:
                self.branch_count += 1
                self.assign(cell, galaxy)
                solution = self.solve()
                if solution:
                    solved = solution
                self.revert(cell, galaxy)
        return solved

    def assign_forced(self, possible: list[tuple[Point, list[int]]]):
        '''Assign all cells with only one possible galaxy. If there is a contradiction, stop and return that cell'''
        for cell, (galaxy, *others) in possible:
            if others: return
            if not self.free(cell, galaxy):
                return cell
            self.assign(cell, galaxy)

    def revert_forced(
        self, possible: list[tuple[Point, list[int]]],
        stop: Point | None = None
    ):
        for cell, (galaxy, *others) in possible:
            if others or cell == stop: return
            if cell in self.grid:
                self.revert(cell, galaxy)

    def possible(self):
        '''For each empty cell, find a list of all possible galaxies it can belong to. If there is a cell which cannot belong to any galaxy (including an assigned one, which means the galaxy is disconnected), return None'''
        possible: dict[Point, list[int]] = {
            (row, column): []
            for row in range(self.height)
            for column in range(self.width)
        }
        for galaxy in range(len(self.galaxies)):
            seen = set()
            self.floodfill(self.centers[galaxy], galaxy, seen)
            for cell in seen:
                possible[cell].append(galaxy)
        possible_list = sorted(possible.items(), key = lambda p: len(p[1]))
        if len(possible_list[0][1]) == 0:
            return None
        return [
            (cell, galaxies) for cell, galaxies in possible_list
            if not cell in self.grid
        ]

    def floodfill(self, cell: Point, galaxy: int, seen: set[Point]):
        '''Find the potential area of a galaxy with a "mirrored" DFS'''
        if cell in seen: return
        seen.add(cell)
        row, column = cell
        for neighbour in (
            (row - 1, column), (row, column - 1),
            (row, column + 1), (row + 1, column)
        ):
            if self.free(neighbour, galaxy):
                self.floodfill(neighbour, galaxy, seen)

    def inside(self, cell: Point):
        '''Check if a cell is inside the grid'''
        return 0 <= cell[0] < self.height and 0 <= cell[1] < self.width

    @mirror
    def free(self, cell: Point, galaxy: int):
        '''Check if a cell can belong to a galaxy, including its reflection'''
        return self.inside(cell) and (
            not cell in self.grid
            or self.grid[cell] == galaxy
        )

    @mirror
    def assign(self, cell: Point, galaxy: int):
        '''Assign a cell to a galaxy, including its reflection'''
        self.grid[cell] = galaxy

    @mirror
    def revert(self, cell: Point, galaxy: int):
        '''Undo the assignment of a cell, including its reflection'''
        del self.grid[cell]

def solve(width: int, height: int, galaxies: list[Point]):
    solver = Solve(width, height, galaxies)
    solution = solver.solve()
    return (
        solution, solver.solution_count,
        solver.branch_count, solver.force_count
    )

if __name__ == '__main__':
    from i_o import read_puzzle, print_solution
    width, height, galaxies = read_puzzle()
    solution, *_ = solve(width, height, galaxies)
    print_solution(width, height, solution)

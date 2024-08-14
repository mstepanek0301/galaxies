from collections import defaultdict
from common import *
from random import randrange, choice
from solve import solve

def choice_index(it: list):
    '''Pick a random item from a sequence and return it along with the index'''
    index = randrange(len(it))
    return index, it[index]

def remove(it: list, index: int):
    '''Remove an item from a list, not preserving order'''
    it[index], it[-1] = it[-1], it[index]
    it.pop()

def pick_border(
        borders: list[tuple[int, list[Point]]]
) -> tuple[int, Point, list[Point] | None]:
    '''Pick a border of a galaxy and remove it'''
    i, (galaxy, border) = choice_index(borders)
    j, cell = choice_index(border)
    remove(border, j)
    if not border:
        # if it's the last border, also remove the galaxy
        remove(borders, i)
        return galaxy, cell, None
    return galaxy, cell, border

def update_borders(
    cell: Point, galaxy: int, border: list[Point] | None,
    borders: list[tuple[int, list[Point]]]
):
    '''Add neighbours of a cell as borders'''
    new_border = list(neighbours(cell))
    if border is None:
        # if the last border was removed before
        borders.append((galaxy, new_border))
    else:
        border.extend(new_border)

def empty_cells(grid: dict[Point, int], width: int, height: int):
    '''Find the empty cells of a grid'''
    return set((
        (row, column)
        for row in range(height)
        for column in range(width)
        if not (row, column) in grid
    ))

def find_components(cells: set[Point]):
    '''Sort cells into connected components'''
    components: list[set[Point]] = []
    seen: set[Point] = set()
    for start in cells:
        if start in seen: continue
        components.append(set())
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in seen: continue
            seen.add(cell)
            components[-1].add(cell)
            for neighbour in neighbours(cell):
                if neighbour in cells:
                    stack.append(neighbour)
    return components

def best_center(component: set[Point]):
    '''Find the center with the biggest potential galaxy in a set of empty cells'''
    scores = defaultdict(list)
    for row, column in component:
        for center in (
            (2 * row, 2 * column), (2 * row + 1, 2 * column + 1),
            (2 * row, 2 * column + 1), (2 * row + 1, 2 * column)
        ):
            if not all((cell in component for cell in center_cells(center))):
                continue
            score = len(fill(component, center))
            scores[score].append(center)
    best = max(scores.keys())
    return choice(scores[best])

def fill(component: set[Point], center: Point):
    '''Find all the potential cells of a galaxy in a set of cells'''
    seen: set[Point] = set()
    stack = [(center[0] // 2, center[1] // 2)]
    while stack:
        cell = stack.pop()
        reflection = reflect(cell, center)
        if cell in seen: continue
        seen.update((cell, reflection))
        for neighbour in neighbours(cell):
            other = reflect(neighbour, center)
            if neighbour in component and other in component:
                stack.extend((neighbour, other))
    return seen

class Generate:
    def __init__(self, width: int, height: int, density: float):
        self.width = width
        self.height = height
        self.density = density
        self.area = width * height
        self.galaxies: list[Point] = []
        self.grid: dict[Point, int] = {}

    def generate(self):
        '''Generate a random puzzle (solution not necessarily unique)'''
        self.setup(int(self.area * self.density))
        self.fill()
        # fill in the remaining spaces
        while len(self.grid) < self.area:
            empty = empty_cells(self.grid, self.width, self.height)
            components = find_components(empty)
            for component in components:
                center = best_center(component)
                galaxy = len(self.galaxies)
                self.galaxies.append(center)
                for cell in fill(component, center):
                    self.grid[cell] = galaxy
        return sorted(self.galaxies)

    def setup(self, n: int):
        '''Generate n random galaxy centers'''
        fails = 0
        # if there are too many galaxies,
        # many random centers will be occupied already,
        # we don't want to waste time on those
        while len(self.galaxies) < n and fails < 2 * n:
            galaxy = (
                randrange(self.height * 2 - 1),
                randrange(self.width * 2 - 1)
            )
            if any((
                cell in self.grid
                for cell in center_cells(galaxy)
            )):
                fails += 1
                continue
            i = len(self.galaxies)
            self.galaxies.append(galaxy)
            for cell in center_cells(galaxy):
                self.grid[cell] = i

    def fill(self):
        '''Randomly expand the galaxies until no longer possible'''
        iterations = 0
        borders = self.borders()
        while borders:
            galaxy, cell, border = pick_border(borders)
            if not self.free(cell, galaxy) or (
                cell in self.grid and self.grid[cell] == galaxy
            ):
                continue
            self.assign(cell, galaxy)
            update_borders(cell, galaxy, border, borders)
            reflection = reflect(cell, self.galaxies[galaxy])
            update_borders(reflection, galaxy, border, borders)

    def borders(self):
        '''Find the initial borders for all galaxies'''
        borders: defaultdict[int, list[Point]] = defaultdict(list)
        for row in range(self.height):
            for column in range(self.width):
                cell = row, column
                if cell in self.grid: continue
                for neighbour in neighbours(cell):
                    if not (
                        self.inside(neighbour)
                        and neighbour in self.grid
                    ):
                        continue
                    borders[self.grid[neighbour]].append(cell)
        return list(borders.items())

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

def generate(width: int, height: int, density = 0.14):
    attempt = 1
    while True:
        generator = Generate(width, height, density)
        galaxies = generator.generate()
        solution, solcount, *_ = solve(width, height, galaxies)
        if solcount == 1:
            return galaxies, attempt
        attempt += 1

if __name__ == '__main__':
    from i_o import print_puzzle
    width, height = map(int, input().split())
    galaxies, _ = generate(width, height)
    print_puzzle(width, height, galaxies)

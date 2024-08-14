Point = tuple[int, int]

def center_range(point: int):
    '''Range of coordinates touching a galaxy's center'''
    return range(point // 2, (point + 1) // 2 + 1)

def center_cells(galaxy: Point):
    '''Cells touching a galaxy's center'''
    return (
        (row, column)
        for row in center_range(galaxy[0])
        for column in center_range(galaxy[1])
    )

def reflect(point: Point, center: Point):
    return center[0] - point[0], center[1] - point[1]

def mirror(fn):
    '''Decorator for functions which take in a cell and a galaxy'''
    def inner(self, cell: Point, galaxy: int):
        a = fn(self, cell, galaxy)
        b = fn(self, reflect(cell, self.galaxies[galaxy]), galaxy)
        return a and b
    return inner

def neighbours(cell: Point):
    row, column = cell
    return (
        (row - 1, column), (row, column - 1),
        (row, column + 1), (row + 1, column)
    )

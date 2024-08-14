from sys import stdin
from common import Point

def read_puzzle():
    w, h = map(int, input().split())
    galaxies: list[Point] = []
    for line in stdin.readlines():
        line = line.strip()
        if not line: continue
        row, column = map(int, line.split())
        galaxies.append((row, column))
    return w, h, galaxies

def print_solution(width: int, height: int, solution: dict[Point, int] | None):
    if solution is None: return print('no solution :(')
    cellsize = len(str(max(solution.values())))
    for row in range(height):
        for column in range(width):
            cell = solution.get((row, column))
            print(str(cell).rjust(cellsize), end = '  ')
        print()

def print_puzzle(width: int, height: int, galaxies: list[Point]):
    print(width, height)
    for galaxy in galaxies:
        print(*galaxy)

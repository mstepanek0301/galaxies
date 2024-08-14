from collections import defaultdict
from common import Point
from generate import generate
from solve import solve

def batch(width: int, height: int, batch_size: int):
    puzzles: defaultdict[tuple[int, int], list[list[Point]]] = defaultdict(list)
    for _ in range(batch_size):
        puzzle, _ = generate(width, height)
        _, _, branch, force = solve(width, height, puzzle)
        puzzles[branch, force].append(puzzle)
    return puzzles

if __name__ == '__main__':
    from i_o import print_puzzle
    width, height, batch_size = map(int, input().split())
    puzzles = sorted(batch(width, height, batch_size).items())
    for (branch, force), bucket in puzzles:
        print(f'{branch}/{force}: {len(bucket)}')
    print()
    for (branch, force), bucket in puzzles:
        for puzzle in bucket:
            print('#', f'{branch}/{force}')
            print_puzzle(width, height, puzzle)
            print()

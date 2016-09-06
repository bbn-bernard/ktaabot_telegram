
# coding: utf-8

import pandas as pd
import random

NCOLS, NROWS = 4, 4
DICT = pd.read_csv(r'data/words.txt', header=None)
DICT.columns = ['word']
DICT['word'] = DICT['word'].astype(str)
ALPHABET = [chr(c) for c in range(ord('a'), ord('z')+1)]

def get_random_pos():
    x = random.randint(0, NROWS-1)
    y = random.randint(0, NCOLS-1)
    
    return (x,y)

def neighbors((x, y)):
    for nx in range(max(0, x-1), min(x+2, NCOLS)):
        for ny in range(max(0, y-1), min(y+2, NROWS)):
            yield (nx, ny)

def find_path_(grid=[], pos=(), wlen=7):
    path = []
    if not pos:
        pos = get_random_pos()
    path.append(pos)
    for i in range(wlen-1):
#         print path, ns
        ns_ = [p for p in neighbors(pos) if p not in path]
        ns = [p for p in ns_ if grid[p[0]][p[1]] == '*']
        # doesn't found neighbors
        if not ns:
            return False
        next_pos = random.choice(ns)
        path.append(next_pos)
        pos = next_pos
        
    return path

def find_path(grid=[], pos=(), wlen=7):
    import time
    
    path = []
    counter = 0
    while not path:
        path = find_path_(grid, pos, wlen)
        counter += 1
        if counter > 10:
            path = []
            break
        time.sleep(1)
        
    return path

def update_grid(grid, path, keyword):
    for i,pos in enumerate(path):
        grid[pos[0]][pos[1]] = keyword[i]

    return grid

def get_solution(grid):
    import kata2
    g = [''.join(x) for x in grid]
    solutions = kata2.get_solutions(g)
    
    return solutions

def make_game():
    grid = [['*' for i in range(NCOLS)] for k in range(NROWS)]
    k1 = random.choice(DICT[DICT['word'].str.len() == 7].values)[0]
    path1 = find_path(grid, (), wlen=7)
    assert(path1)    
    grid = update_grid(grid, path1, k1)
    
    pos2 = random.choice(path1)
    k2 = random.choice(DICT[(DICT['word'].str.len() == 5) & 
                            (DICT['word'].str.startswith(grid[pos2[0]][pos2[1]]))].values)[0]
    path2 = find_path(grid, pos2, wlen=5)
    assert(path2)
    grid = update_grid(grid, path2, k2)
    
    pos3 = random.choice(path2)
    k3 = random.choice(DICT[(DICT['word'].str.len() == 4) & 
                            (DICT['word'].str.startswith(grid[pos3[0]][pos3[1]]))].values)[0]
    path3 = find_path(grid, pos3, wlen=4)
    assert(path3)
    grid = update_grid(grid, path3, k3)

    for x in range(NROWS):
        for y in range(NCOLS):
            if grid[x][y] == '*':
                grid[x][y] = random.choice(ALPHABET)

    solutions = get_solution(grid)
    game = {'keywords': ','.join([k1, k2, k3]),
            'grid': ' '.join([''.join(x) for x in grid]),
            'solutions': ','.join(solutions)}
    
    return game





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

def find_path(grid=[], pos=(), wlen=7):
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

def update_grid(grid, path, keyword):
    for i,pos in enumerate(path):
        grid[pos[0]][pos[1]] = keyword[i]

    return grid

def get_solution(grid):
    import kata2
    g = [''.join(x) for x in grid]
    solutions = kata2.get_solutions(g)
    
    return solutions

# NOTES: grid type based on keyword length
# tuple (nk1, nk2, nk3) with nk1+nk2+nk3-1 < NROWS*NCOLS
# nk1, nk2, nk3 >= 3
GRID_TYPE = [(7, 5, 4),
             (9, 5, 4),
             (10, 5, 0),
             (11, 5, 0),
             (12, 5, 0),
             (14, 3, 0),
             (15, 0, 0)]
def create_grid(grid_type=False):
    if grid_type:
        type_idx = grid_type
        assert type_idx < len(GRID_TYPE), 'wrong grid type'
    else:
        type_idx = random.randint(0, len(GRID_TYPE)-1)
    nk1, nk2, nk3 = GRID_TYPE[type_idx]
    k1, k2, k3 = ('',)*3
    npath_max = NROWS * NCOLS
    nretry = 100
    while nretry > 0:
        grid = [['*' for i in range(NCOLS)] for k in range(NROWS)]
        k1 = random.choice(DICT[DICT['word'].str.len() == nk1].values)[0]
        available_pos = [(x,y) for x in range(NROWS) for y in range(NCOLS) if grid[x][y] == '*']
        random.shuffle(available_pos)
        for pos in available_pos:
            path1 = find_path(grid, pos, wlen=nk1)
            if path1:
                break

        if not path1:
            nretry -= 1
            continue
        
        grid = update_grid(grid, path1, k1)

        if (npath_max-(nk1-1) < 3) or (nk1 >= npath_max):
            path3 = path1
            break
            
        available_pos = path1
        random.shuffle(available_pos)
        path2 = []
        for pos2 in available_pos:
            k2_candidate = DICT[(DICT['word'].str.len() == nk2) & 
                                    (DICT['word'].str.startswith(grid[pos2[0]][pos2[1]]))]
            if k2_candidate.empty:
                continue
            k2 = random.choice(k2_candidate.values)[0]
            path2 = find_path(grid, pos2, wlen=nk2)
            if path2:
                break
                
        if not path2:
            nretry -= 1
            continue

        grid = update_grid(grid, path2, k2)
        if (npath_max - (nk1+nk2-1) < 3) or (nk1+nk2-1) >= npath_max:
            path3 = path2
            break
            
        available_pos = path1 + path2
        random.shuffle(available_pos)
        path3 = []
        for pos3 in available_pos:
            k3_candidate = DICT[(DICT['word'].str.len() == nk3) & 
                                    (DICT['word'].str.startswith(grid[pos3[0]][pos3[1]]))]
            if k3_candidate.empty:
                continue
            k3 = random.choice(k3_candidate.values)[0]                                    
            path3 = find_path(grid, pos3, wlen=nk3)
            if path3:
                break
                
        if path3:
            grid = update_grid(grid, path3, k3)
            break
        nretry -= 1

    result = {}
    if path3:
        for x in range(NROWS):
            for y in range(NCOLS):
                if grid[x][y] == '*':
                    grid[x][y] = random.choice(ALPHABET)

        solutions = get_solution(grid)
        result = {'keywords': ','.join([k1, k2, k3]),
                  'grid': ' '.join([''.join(x) for x in grid]),
                  'solutions': ','.join(solutions),
                  'type': type_idx}
    
    return result

if __name__ == '__main__':
    # TESTING
    # print create_grid()
    


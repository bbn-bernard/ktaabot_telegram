def solve():
    global grid
    for y, row in enumerate(grid):
        for x, letter in enumerate(row):
            for result in extending(letter, ((x, y),)):
                yield result

def extending(prefix, path):
    global grid, words, prefixes
    if prefix in words:
        yield (prefix, path)
    for (nx, ny) in neighbors(path[-1]):
        if (nx, ny) not in path:
            prefix1 = prefix + grid[ny][nx]
            if prefix1 in prefixes:
                for result in extending(prefix1, path + ((nx, ny),)):
                    yield result

def neighbors((x, y)):
    for nx in range(max(0, x-1), min(x+2, ncols)):
        for ny in range(max(0, y-1), min(y+2, nrows)):
            yield (nx, ny)
            
def get_solutions(grid_):
    '''ex: 
grid = 'rbor koeu irek akis'.split()'''
    global grid, nrows, ncols, words, prefixes
    
    grid = grid_
    nrows, ncols = len(grid), len(grid[0])

    # A dictionary word that could be a solution must use only the grid's
    # letters and have length >= 3. (With a case-insensitive match.)

    import re
    alphabet = ''.join(set(''.join(grid)))
    bogglable = re.compile('[' + alphabet + ']{3,}$', re.I).match

    words = set(word.rstrip('\n') for word in ALLWORDS if bogglable(word))
    prefixes = set(word[:i] for word in words
                   for i in range(2, len(word)+1))

    result = sorted(set(word for (word, path) in solve()))
    
    return result

with open(r'data/words.txt') as f:
    ALLWORDS = f.readlines()
    
if __name__ == '__main__':
    pass
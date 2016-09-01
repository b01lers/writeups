# Trend Micro : Maze

#### Author: GSAir & Wh1t3Fox

**Description**:
> We were given 1001 mazes with one starting and one ending point.
> We started with 13000 energy and each time you crossed the same spot you lost energy.
> There were also some checkpoint and energy drink in the maze. You could only use energy drink once.
>
> We had to solve each maze without running out of energy and submit our solution in the format:
> LLL
> RR

Reading the description, we figured out that it was difficult to take care of every constrains at the same time. For example the energy constrain seemed to difficult to solve by only using a greedy algorithm, so let's start with something simple we will optimize if needed:

 1. Parse the maze, and keep record of Starting, Ending, Checkpoint, EnergyDrink
 2. Compute the distance between S and every checkpoint
 3. Pick the closest one, and extract the path.
 4. Remove the checkpoint from the list
 5. Put starting point to be the checkpoint and go back to 2 if there are still Checkpoint
 6. Find shortest path to E

And it worked!!! No optimizations needed :)

We polished the code a little bit afterward in order to print the path when printing the maze:

    #!/usr/bin/env python2

    import sys

    WALL = '#'
    END = 'G'
    START = 'S'
    ENERGY = 'E'
    CHECK = 'C'
    PATH = '.'

    # Auxilary functions

    def copy_list(maze):
    	cop = []
    	for l in maze:
    		cop.append([x for x in l])

    	return cop

    def find_closet_checkpoint(maze, C):
    	m = 1 << 31
    	for (x, y) in C:
    		if maze[x][y] < m:
    			m = maze[x][y]
    			c = (x, y)

    	return c

    def find_path(maze, w, h, S, E):
    	(ex, ey) = E
    	(sx, sy) = S
    	n = int(maze[ex][ey])
    	p = ""
    	while (ex, ey) != (sx, sy):
    		if ex + 1 < h and maze[ex + 1][ey] == n - 1:
    			(ex, ey) = (ex + 1, ey)
    			p = "U" + p
    		elif ey + 1 < w and maze[ex][ey + 1] == n - 1:
    			(ex, ey) = (ex, ey + 1)
    			p = "L" + p
    		elif ex - 1 >= 0 and maze[ex - 1][ey] == n - 1:
    			(ex, ey) = (ex - 1, ey)
    			p = "D" + p
    		elif ey - 1 >= 0 and maze[ex][ey - 1] == n - 1:
    			(ex, ey) = (ex, ey - 1)
    			p = "R" + p
    		else:
    			print "No path found ", n
    			sys.exit()
    		n = n - 1

    	return p

    def rec_solve(maze, x, y, w, h, n):
    	if (maze[x][y] == WALL or str(maze[x][y]).isdigit() and int(maze[x][y]) <= n):
    		return

    	maze[x][y] = n
    	if x - 1 >= 0:
    		rec_solve(maze, x - 1, y, w, h, n+ 1)
    	if x + 1 < h:
    		rec_solve(maze, x + 1, y, w, h, n+ 1)
    	if y - 1 >= 0:
    		rec_solve(maze, x, y - 1, w, h, n+ 1)
    	if y +  1 < w:
    		rec_solve(maze, x, y + 1, w, h, n+ 1)

    def write_path(maze, path, S):
    	(sx, sy) = S
    	for d in path:
    		if maze[sx][sy] == '.':
    			maze[sx][sy] = '@'
    		if d == 'L':
    			sy = sy - 1
    		elif d == 'R':
    			sy = sy + 1
    		elif d == 'U':
    			sx = sx - 1
    		else:
    			sx = sx + 1

    # solving function
    def solve_maze(maze, w, h):
    	nrj = []
    	C = []
    	for x in xrange(h):
    		for y in xrange(w):
    			if maze[x][y] == START:
    				S = (x, y)
    			elif maze[x][y] == ENERGY:
    				nrj.append((x,y))
    			elif maze[x][y] == END:
    				E = (x,y)
    			elif maze[x][y] == CHECK:
    				C.append((x,y))

    	(sx, sy) = S
    	path = ""
    	while C:
    		cur = copy_list(maze)
    		rec_solve(cur, sx, sy, w, h, 0)
    		(ex, ey) = find_closet_checkpoint(cur, C)
    		C.remove((ex, ey))
    		path += find_path(cur, w, h, (sx, sy), (ex, ey))
    		(sx, sy) = (ex, ey)

    	cur = copy_list(maze)
    	rec_solve(cur, sx, sy, w, h, 0)
    	(ex, ey) = E
    	path += find_path(cur, w, h, (sx, sy), (ex, ey))

    	write_path(maze, path, S)
    	print
    	for l in maze:
    		print l
    	print path
    	return path

    def main():
    	solution = []
    	curr_maze = []
    	with open('maze.txt', 'r') as fr:
    		i = 0
    		while True:
    			curr_maze = []
    			try:
    				width, height, checkpoints = map(int, fr.readline().split())
    			except ValueError:
    				break

    			for x in range(height):
    				curr_maze.append(list(fr.readline().replace('\n','')))

    			solution.append(solve_maze(curr_maze, width, height))
    	with open("solution.txt", "wb") as f:
    		f.write('\n'.join(solution))


    if __name__ == '__main__':
    	main()

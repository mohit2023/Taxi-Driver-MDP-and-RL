import random

# list = [a,b] => list[0]=a=x-cordinate, list[1]=b=y-coordinate

class Cell:
  def __init__(self):
    self.depot = False
    # set walls
    self.walls = {'North': False, 'South': False, 'East': False, 'West': False}

class Grid:
  
  __reverse = {'North': 'South', 'South': 'North', 'East': 'West', 'West': 'East'}

  def __init__(self, n, m):
    self.grid = {}
    self.n = n
    self.m = m
    self.pick = [-1,-1]
    self.drop = [-1,-1]
    self.depots = []
    for x in range(n):
      for y in range(m):
        self.grid[(x,y)] = Cell()
    
    # set boundary walls
    for y in range(m):
      self.grid[(0,y)].walls['West'] = True
      self.grid[(n-1,y)].walls['East'] = True
    for x in range(n):
      self.grid[(x,0)].walls['South'] = True
      self.grid[(x,m-1)].walls['North'] = True

  def addWalls(self, walls):
    for wall in walls:
      self.addWall(wall)
  
  def addWall(self, wall):
    self.check(wall[0])
    self.check(wall[1])
    dir = self.__relativeDirection(wall[0],wall[1])
    if dir == 'none' :
      return
    revdir = self.__reverse[dir]
    self.grid[wall[0]].walls[dir] = True
    self.grid[wall[1]].walls[revdir] = True

  def addDepots(self, depots):
    for depo in depots:
      self.addDepo(depo)

  def addDepo(self, depo):
    self.check(depo)
    if self.grid[depo].depot == False:
      self.depots.append(depo)
      self.grid[depo].depot = True

  def updatePick(self, location):
    self.check(location)
    if self.grid[location].depot == True:
      self.pick = location
  
  def updateDrop(self, location):
    self.check(location)
    if self.grid[location].depot == True:
      self.drop = location

  def __relativeDirection(self, p1, p2):
    if p1[1]+1 == p2[1] :
      return 'North'
    elif p1[1]-1 == p2[1] :
      return 'South'
    elif p1[0]+1 == p2[0] :
      return 'East'
    elif p1[0]-1 == p2[0] :
      return 'West'
    else :
      return 'none'

  def check(self, location):
    if location[0] >= self.n or location[1] >= self.m or location[0] < 0 or location[1] < 0:
      raise Exception('Location not in grid')  
    
class Taxi:
  def __init__(self, location):
    self.location = location
    self.active = False
  
  def move(self, dir):
    if dir == 'North':
      self.location[1] = self.location[1]+1
    elif dir == 'South':
      self.location[1] = self.location[1]-1
    elif dir == 'East':
      self.location[0] = self.location[0]+1
    elif dir == 'West':
      self.location[0] = self.location[0]-1

  def __str__(self):
    return str(self.__class__) + ": " + str(self.__dict__)


class MDP:

  actionList = ['North', 'South', 'East', 'West', 'Pickup', 'Drop']
  directions = ['North', 'South', 'East', 'West']

  def __init__(self, layout, taxi):
    layout.check(taxi.location)
    self.env = layout
    self.state = taxi

  def applyAction(self, action):
    if action not in self.actionList:
      raise Exception('Invalid action')

    if action == 'Pickup':
      return self.pickup()
    elif action == 'Drop':
      return self.drop()
    else:
      return self.actdir(action)

  def actdir(self, dir):
    sample = random.random()
    if sample < 0.85:
      self.move(dir)
    else:
      posdir = [d for d in self.directions if d != dir]
      fdir = random.choice(posdir)
      self.move(fdir)
    return -1

  def move(self, dir):
    if self.env.grid[tuple(self.state.location)].walls[dir] == False:
      self.state.move(dir)
      if self.state.active:
        self.env.updatePick(self.state.location)

  def pickup(self):
    if self.env.pick != self.state.location:
      return -10
    else:
      self.state.active = True
      return -1

  def drop(self):
    if self.env.pick != self.state.location:
      return -10
    else:
      self.state.active = False
      if self.env.drop == self.state.location:
        return 20
      else:
        return -1

  def __str__(self):
    return str(self.__class__) + ": " + str(self.__dict__)
    
  
def problem_layout():
  grid = Grid(5,5)
  depots = [(0,4),(4,4),(0,0),(3,0)]
  grid.addDepots(depots)
  walls = [
    [(1,4),(2,4)],
    [(1,3),(2,3)],
    [(0,1),(1,1)],
    [(0,0),(1,0)],
    [(2,1),(3,1)],
    [(2,0),(3,0)]
  ]
  grid.addWalls(walls)
  return grid

def partA():
  grid = problem_layout()
  posDepots = grid.depots
  print(posDepots)
  startDepo = random.choice(posDepots)
  posDepots = [d for d in posDepots if d != startDepo]
  endDepo = random.choice(posDepots)
  grid.updatePick(startDepo)
  grid.updateDrop(endDepo)

  x = random.randint(0,grid.n-1)
  y= random.randint(0,grid.m-1)
  taxi = Taxi([x,y])

  simulator = MDP(grid,taxi)

  # test run
  print(simulator.state)
  act = random.choice(simulator.actionList)
  print(act)
  simulator.applyAction(act)
  print(simulator.state)

partA()
import random
import copy # TODO: check if allowed

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
    if self.grid[tuple(location)].depot == True:
      self.pick = location
  
  def updateDrop(self, location):
    self.check(location)
    if self.grid[tuple(location)].depot == True:
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

    self.all_states = [(x,y,status,a,b) for x in range(self.env.n) for y in range(self.env.m) for status in [False, True] for a in range(self.env.n) for b in range(self.env.m) if status!=True or (a==x and b==y)]

    self.transition = {}
    self.reward = {}

    for state in self.all_states:
      dict_state_t = {}
      dict_state_r = {}
      for action in self.actionList:
        dict_action_t = {}
        dict_action_r = {}
        if action == 'Pickup':
          if state[3]==state[0] and state[4]==state[1]:
            dict_action_t[(state[0],state[1],True,state[3],state[4])] = 1.0
            dict_action_r[(state[0],state[1],True,state[3],state[4])] = -1
          else:
            dict_action_t[state] = 1.0
            dict_action_r[state] = -10
        elif action == 'Drop':
          if state[2]==True:
            dict_action_t[(state[0],state[1],False,state[3],state[4])] = 1.0
            if [state[0],state[1]] == self.env.drop:
              dict_action_r[(state[0],state[1],False,state[3],state[4])] = 20
            else:
              dict_action_r[(state[0],state[1],False,state[3],state[4])] = -1
          else:
            dict_action_t[state] = 1.0
            if state[3]==state[0] and state[4]==state[1]:
              dict_action_r[state] = -1
            else:
              dict_action_r[state] = -10
        else:
          for dir in self.directions:
            if self.env.grid[(state[0],state[1])].walls[dir] == True:
              result = state
            else:
              location = [state[0],state[1]]
              if dir == 'North':
                location[1] = location[1]+1
              elif dir == 'South':
                location[1] = location[1]-1
              elif dir == 'East':
                location[0] = location[0]+1
              elif dir == 'West':
                location[0] = location[0]-1

              if state[2]==True:
                result = (location[0],location[1],True,location[0],location[1])
              else:
                result = (location[0],location[1],False,state[3],state[4])

            if dir == action:
              dict_action_t[result] = 0.85
            else:
              dict_action_t[result] = 0.15/3
            dict_action_r[result] = -1

        dict_state_t[action] = dict_action_t
        dict_state_r[action] = dict_action_r

      self.transition[state] = dict_state_t
      self.reward[state] = dict_state_r
    

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
  
  def updateState(self, loc, status):
    self.state.location = loc
    self.state.active = status


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

def instance(grid):
  posDepots = grid.depots
  startDepo = random.choice(posDepots)
  posDepots = [d for d in posDepots if d != startDepo]
  endDepo = random.choice(posDepots)
  grid.updatePick(list(startDepo))
  grid.updateDrop(list(endDepo))

  x = random.randint(0,grid.n-1)
  y= random.randint(0,grid.m-1)
  taxi = Taxi([x,y])

  simulator = MDP(grid,taxi)

  return simulator


def normDistance(cvfn, pvfn, all_states):
  normd = 0
  for state in all_states:
    normd = max(normd, abs(cvfn[state]-pvfn[state])) 
  return normd

def value_iteration(simulator, epsilon, gamma):
  pvfn = {}
  cvfn = {}
  all_states = simulator.all_states
  actionList = simulator.actionList
  for state in all_states:
    pvfn[state] = 0

  norm_distance = []
  
  while(True):
    for state in all_states:
      cvfn[state] = max([sum([simulator.transition[state][action][result]*(simulator.reward[state][action][result] + (gamma*pvfn[result])) for result in simulator.transition[state][action]]) for action in actionList])

    normd = normDistance(cvfn, pvfn, all_states)
    norm_distance.append(normd)

    if normd <= epsilon:
      break
    pvfn = copy.deepcopy(cvfn)
  
  return norm_distance,cvfn

def policy_valueIteration(simulator, epsilon, gamma):
  norm_distance,valuefn = value_iteration(simulator, epsilon, gamma)
  policy = {}
  for state in simulator.all_states:
    mxv = float('-inf')
    for action in simulator.actionList:
      val = sum([simulator.transition[state][action][result]*(simulator.reward[state][action][result] + gamma*valuefn[result]) for result in simulator.transition[state][action]])
      if val>mxv:
        res = action
    policy[state] = res
  
  return policy,norm_distance

def partA2a(simulator, epsilon):
  gamma = 0.9
  # epsilon = 0.1
  policy,norm_distance = policy_valueIteration(simulator, epsilon, gamma)

  print("partA - 2 - a")
  print(policy)
  print("choosen epsilon: ", epsilon, " Number of iteration: ", len(norm_distance))


def partA2b(simulator, epsilon):
  # epsilon = 0.1
  discount = [0.01, 0.1, 0.5, 0.8, 0.99]

  print("partA2b: ")
  for gamma in discount:
    norm_distance,valuefn = value_iteration(simulator, epsilon, gamma)
    print(gamma, len(norm_distance))
    # TODO : plot graphs



def partA():
  grid = problem_layout()
  simulator = instance(grid)
  
  epsilon = 0.1
  # partA -> 2 -> a
  partA2a(simulator, epsilon)

  # partA -> 2 -> b
  partA2b(simulator, epsilon)



partA()
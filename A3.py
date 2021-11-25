import random
import copy # TODO: check if allowed
import numpy as np

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
      self.pick = location.copy()
  
  def updateDrop(self, location):
    self.check(location)
    if self.grid[tuple(location)].depot == True:
      self.drop = location.copy()

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
    goal = self.env.drop
    self.goal_state = (goal[0],goal[1],False,goal[0],goal[1])
    self.all_states = [(x,y,status,a,b) for x in range(self.env.n) for y in range(self.env.m) for status in [False, True] for a in range(self.env.n) for b in range(self.env.m) if status!=True or (a==x and b==y)]

    self.transition = {}
    self.reward = {}

    for state in self.all_states:
      if(state == self.goal_state):
        continue
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
        self.updatePassenger(self.state.location)

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
    self.state.location = loc.copy()
    self.state.active = status

  def updatePassenger(self, location):
    self.env.pick = location.copy()

  def getState(self):
    return (self.state.location[0],self.state.location[1],self.state.active,self.env.pick[0],self.env.pick[1])

  def reset(self):
    depots = [depo for depo in self.env.depots if depo!=self.env.drop]
    pick = list(random.choice(depots))
    taxi  = [random.randint(0,self.env.n-1),random.randint(0,self.env.m-1)]
    self.updatePassenger(pick)
    self.updateState(taxi, False)


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
  goal_state = simulator.goal_state
  while(True):
    cvfn[goal_state] = 0
    for state in all_states:
      if state==goal_state:
        continue
      cvfn[state] = max([sum([simulator.transition[state][action][result]*(simulator.reward[state][action][result] + (gamma*pvfn[result])) for result in simulator.transition[state][action]]) for action in actionList])

    normd = normDistance(cvfn, pvfn, all_states)
    norm_distance.append(normd)

    if normd <= epsilon:
      break
    pvfn = copy.deepcopy(cvfn)
  
  return norm_distance,cvfn


def policy_Given_Valuefn(simulator, gamma, valuefn):
  policy = {}
  goal_state = simulator.goal_state
  policy[goal_state] = 'Episode end'
  for state in simulator.all_states:
    if(state == goal_state):
      continue
    mxv = float('-inf')
    for action in simulator.actionList:
      val = sum([simulator.transition[state][action][result]*(simulator.reward[state][action][result] + gamma*valuefn[result]) for result in simulator.transition[state][action]])
      if val>mxv:
        mxv = val
        res = action
    policy[state] = res

  return policy


def policy_valueIteration(simulator, epsilon, gamma):
  norm_distance,valuefn = value_iteration(simulator, epsilon, gamma)
  policy = policy_Given_Valuefn(simulator, gamma, valuefn)
  
  return policy,norm_distance


def partA2a(simulator, epsilon):
  gamma = 0.9
  policy,norm_distance = policy_valueIteration(simulator, epsilon, gamma)

  print("partA - 2 - a: ")
  print(policy)
  print("choosen epsilon: ", epsilon, " Number of iteration: ", len(norm_distance))


def partA2b(simulator, epsilon):
  discount = [0.01, 0.1, 0.5, 0.8, 0.99]

  print("partA - 2 - b: ")
  for gamma in discount:
    norm_distance,valuefn = value_iteration(simulator, epsilon, gamma)
    print(gamma, len(norm_distance))
    # TODO : plot graphs


def simulate(simulator, policy, steps=20):
  for i in range(steps):
    t = simulator.state.location
    p = simulator.env.pick
    a = simulator.state.active
    current_state = (t[0],t[1],a,p[0],p[1])
    actionTotake = policy[current_state]
    print("state: ", current_state, " action prescribed: ", actionTotake)
    if(current_state == simulator.goal_state):
      break
    simulator.applyAction(actionTotake)


def partA2c(simulator, epsilon):
  print("partA - 2 - c: ")

  taxiLocation = simulator.state.location.copy()
  passengerLocation = simulator.env.pick.copy()
  destLocation = simulator.env.drop
  depots = simulator.env.depots
  depots = [list(depo) for depo in depots if list(depo)!=destLocation]

  policy_10,norm_distance_10 = policy_valueIteration(simulator, epsilon, 0.1)
  policy_99,norm_distance_99 = policy_valueIteration(simulator, epsilon, 0.99)

  print("\n Discount factor 0.1, Taxi at: ", taxiLocation, "Passenger at: ", passengerLocation)
  simulate(simulator, policy_10)

  simulator.updateState(taxiLocation, False)
  simulator.env.updatePick(passengerLocation)
  print("\n Discount factor 0.99, Taxi at: ", taxiLocation, "Passenger at: ", passengerLocation)
  simulate(simulator, policy_99)

  # Run by varying taxi location and passenger location, (run num times)
  num = 5
  for i in range(num):
    newTaxiLocation = [random.randint(0,simulator.env.n-1),random.randint(0,simulator.env.m-1)]
    newPassengerLocation = random.choice(depots)

    simulator.updateState(newTaxiLocation, False)
    simulator.env.updatePick(newPassengerLocation)
    print("\n Discount factor 0.1, Taxi at: ", newTaxiLocation, "Passenger at: ", newPassengerLocation)
    simulate(simulator, policy_10)

    simulator.updateState(newTaxiLocation, False)
    simulator.env.updatePick(newPassengerLocation)
    print("\n Discount factor 0.99, Taxi at: ", newTaxiLocation, "Passenger at: ", newPassengerLocation)
    simulate(simulator, policy_99)


def policyEvaluation_iterate(simulator, policy, epsilon, gamma):
  pvfn = {}
  cvfn = {}
  all_states = simulator.all_states
  for state in all_states:
    pvfn[state] = 0

  goal_state = simulator.goal_state
  while(True):
    cvfn[goal_state] = 0
    for state in all_states:
      if(state == goal_state):
        continue
      action = policy[state]
      cvfn[state] = sum([simulator.transition[state][action][result]*(simulator.reward[state][action][result] + (gamma*pvfn[result])) for result in simulator.transition[state][action]])

    normd = normDistance(cvfn, pvfn, all_states)
    if normd <= epsilon:
      break
    pvfn = copy.deepcopy(cvfn)
  
  return cvfn
  

def policyEvaluation_algebra(simulator, policy, gamma):
  stateNum = {}
  i = 0
  for state in simulator.all_states:
    stateNum[state]=i
    i+=1

  lhs = []
  rhs = []

  n = len(simulator.all_states)
  for state in simulator.all_states:
    eqn = [0]*n
    val = 0.0
    eqn[stateNum[state]] = 1.0
    if state != simulator.goal_state:
      action = policy[state]
      for result in simulator.transition[state][action]:
        val+= simulator.transition[state][action][result]*simulator.reward[state][action][result]
        eqn[stateNum[result]] += -gamma*simulator.transition[state][action][result]
    lhs.append(eqn)
    rhs.append(val)
  
  lhs = np.array(lhs)
  rhs = np.array(rhs)
  res = np.linalg.solve(lhs,rhs)

  valuefn = {}
  for state in simulator.all_states:
    valuefn[state] = res[stateNum[state]]

  return valuefn


def policyEvaluation(simulator, policy, epsilon, method, gamma):
  if method == 1:
    return policyEvaluation_iterate(simulator, policy, epsilon, gamma)
  else:
    return policyEvaluation_algebra(simulator, policy, gamma)


def policyImprovement(simulator, gamma, valuefn):
  return policy_Given_Valuefn(simulator, gamma, valuefn)


def policy_policyIteration(simulator, epsilon, gamma, convergedPolicy={}, method=1):
  # make random policy
  policy = {}
  policy[simulator.goal_state] = 'Episode end'
  for state in simulator.all_states:
    if state == simulator.goal_state:
      continue
    policy[state] = random.choice(simulator.actionList)

  policyLoss = []
  
  while(True):
    valuefn = policyEvaluation(simulator, policy, epsilon, method, gamma)
    newPolicy = policyImprovement(simulator, gamma, valuefn)
    converged = True
    
    if convergedPolicy!={}:
      loss = 0
      for state in simulator.all_states:
        if convergedPolicy[state]!=policy[state]:
          loss+=1
      policyLoss.append(loss)

    for state in simulator.all_states:
      if newPolicy[state] != policy[state]:
        converged = False
    if converged:
      break
    policy = copy.deepcopy(newPolicy)

  return policy,policyLoss


def partA3b(simulator, epsilon):
  print("partA - 3 - b: ")

  # TODO: to check if initial policy should be same for policy for the two runs of initially finding policy and then for calculating policy loss

  policy,policyLoss = policy_policyIteration(simulator, epsilon, 0.1) # give parameter method=2, for using policy evaluation by solving linear systems

  temp,policyLoss = policy_policyIteration(simulator, epsilon, 0.1, policy)
  print(policyLoss)

  discount = [0.01, 0.1, 0.5, 0.8, 0.99]
  for gamma in discount:
    policy,policyLoss = policy_policyIteration(simulator, epsilon, gamma)
    temp,policyLoss = policy_policyIteration(simulator, epsilon, gamma, policy)
    print(gamma, policyLoss)
    # TODO: plot graphs
    


def partA():
  grid = problem_layout()
  simulator = instance(grid)
  
  epsilon = 0.01
  # partA -> 2 -> a
  # partA2a(simulator, epsilon)

  # partA -> 2 -> b
  # partA2b(simulator, epsilon)

  # partA -> 2 -> c
  partA2c(simulator, epsilon)

  # partA -> 3 -> b
  # partA3b(simulator, epsilon)


def selectAction(simulator, PRexp, Qval, state):
  if state==simulator.goal_state:
    return 'Episode end'
  exp = random.random()
  if exp<PRexp: # explore
    res = random.choice(simulator.actionList)
  else: # act according to optimal policy
    mxv = float('-inf')
    for action in simulator.actionList:
      if mxv<Qval[state][action]:
        mxv = Qval[state][action]
        res = action
  return res


def initialize_Qval(simulator):
  Qval = {}
  for state in simulator.all_states:
    Qval[state] = {}
    if state==simulator.goal_state:
      Qval[state]['Episode end'] = 0.0
    else:
      for action in simulator.actionList:
        Qval[state][action] = 0.0
  return Qval


def policy_Given_Qval(simulator, Qval):
  policy = {}
  for state in simulator.all_states:
    mxv = float('-inf')
    for action in Qval[state]:
      if mxv<Qval[state][action]:
        mxv = Qval[state][action]
        res = action
    policy[state] = res
  return policy


def evaluatePolicy(simulator, Qval, gamma, steps, analysis):
  policy = policy_Given_Qval(simulator, Qval)
  average_reward = 0
  for i in range(analysis):
    simulator.reset()
    reward = 0
    while simulator.getState()!=simulator.goal_state and steps>0:
      reward = simulator.applyAction(policy[simulator.getState()]) + gamma*reward
      steps-=1
    average_reward+=reward
  average_reward /= analysis
  return average_reward

def Qlearning(simulator, alpha, gamma, epsilon=0.1, episodes=2000, steps=500, analysis=10):
  Qval=initialize_Qval(simulator)
  average_utility = []
  for episode in range(episodes):
    simulator.reset()
    state = simulator.getState()
    iterations=steps
    while state!=simulator.goal_state and iterations>0:
      res = selectAction(simulator, epsilon, Qval, state)
      reward = simulator.applyAction(res)
      resultant_state = simulator.getState()
      sample = reward + gamma*max([Qval[resultant_state][action] for action in Qval[resultant_state]])
      Qval[state][res] = (1-alpha)*Qval[state][res] + alpha*sample
      state = resultant_state
      iterations-=1
    if analysis!=0:
      average_utility.append(evaluatePolicy(simulator, Qval, gamma, steps, analysis))
  return policy_Given_Qval(simulator, Qval),average_utility

def Qlearning_decay(simulator, alpha, gamma, epsilon=0.1, episodes=2000, steps=500, analysis=10):
  Qval=initialize_Qval(simulator)
  average_utility = []
  learn = 1
  for episode in range(episodes):
    simulator.reset()
    state = simulator.getState()
    iterations=steps
    while state!=simulator.goal_state and iterations>0:
      res = selectAction(simulator, epsilon/learn, Qval, state)
      reward = simulator.applyAction(res)
      resultant_state = simulator.getState()
      sample = reward + gamma*max([Qval[resultant_state][action] for action in Qval[resultant_state]])
      Qval[state][res] = (1-alpha)*Qval[state][res] + alpha*sample
      state = resultant_state
      iterations-=1
      learn+=1
    if analysis!=0:
      average_utility.append(evaluatePolicy(simulator, Qval, gamma, steps, analysis))
  return policy_Given_Qval(simulator, Qval),average_utility

def sarsa(simulator, alpha, gamma, epsilon=0.1, episodes=2000, steps=500, analysis=10):
  Qval=initialize_Qval(simulator)
  average_utility = []
  for episode in range(episodes):
    simulator.reset()
    state = simulator.getState()
    action = selectAction(simulator, epsilon, Qval, state)
    iterations=steps
    while state!=simulator.goal_state and iterations>0:
      reward = simulator.applyAction(action)
      resultant_state = simulator.getState()
      resultant_state_action = selectAction(simulator, epsilon, Qval, resultant_state)
      sample = reward + gamma*Qval[resultant_state][resultant_state_action]
      Qval[state][action] = (1-alpha)*Qval[state][action] + alpha*sample
      state = resultant_state
      action = resultant_state_action
      iterations-=1
    if analysis!=0:
      average_utility.append(evaluatePolicy(simulator, Qval, gamma, steps, analysis))
  return policy_Given_Qval(simulator, Qval),average_utility

def sarsa_decay(simulator, alpha, gamma, epsilon=0.1, episodes=2000, steps=500, analysis=10):
  Qval = initialize_Qval(simulator)
  average_utility = []
  learn = 1
  for episode in range(episodes):
    simulator.reset()
    state = simulator.getState()
    action = selectAction(simulator, epsilon/learn, Qval, state)
    iterations=steps
    while state!=simulator.goal_state and iterations>0:
      reward = simulator.applyAction(action)
      resultant_state = simulator.getState()
      resultant_state_action = selectAction(simulator, epsilon/learn, Qval, resultant_state)
      sample = reward + gamma*Qval[resultant_state][resultant_state_action]
      Qval[state][action] = (1-alpha)*Qval[state][action] + alpha*sample
      state = resultant_state
      action = resultant_state_action
      iterations-=1
      learn+=1
    if analysis!=0:
      average_utility.append(evaluatePolicy(simulator, Qval, gamma, steps, analysis))
  return policy_Given_Qval(simulator, Qval),average_utility


def partB2(simulator):
  gamma = 0.99
  alpha = 0.85

  policy1,average_utility_Qlearning = Qlearning(simulator, alpha, gamma)
  policy2,average_utility_Qlearning_decay = Qlearning_decay(simulator, alpha, gamma)
  policy3,average_utility_sarsa = sarsa(simulator, alpha, gamma)
  policy4,average_utility_sarsa_decay = sarsa_decay(simulator, alpha, gamma)

  print("partB -> 2")
  print("Qlearning: ", average_utility_Qlearning[len(average_utility_Qlearning)-1])
  print("Qlearning_decay: ", average_utility_Qlearning_decay[len(average_utility_Qlearning_decay)-1])
  print("sarsa: ", average_utility_sarsa[len(average_utility_sarsa)-1])
  print("sarsa_decay: ", average_utility_sarsa_decay[len(average_utility_sarsa_decay)-1])

  # TODO : plot graphs


def partB():
  grid = problem_layout()
  simulator = instance(grid)

  # partB -> 2
  partB2(simulator)

partA()

# partB()
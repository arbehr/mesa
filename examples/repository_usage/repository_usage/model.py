import mesa

from .agent import UserAgent, LearningObjectAgent
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

def get_total_downloads(model):
    """sum of all agents' downloads"""
    agent_downloads = [a.downloads for a in model.schedule.agents if isinstance(a, LearningObjectAgent)]
    # return the sum of agents' downloads
    return str(np.sum(agent_downloads))

def get_total_views(model):
    """sum of all agents' views"""    
    agent_views = [a.views for a in model.schedule.agents if isinstance(a, LearningObjectAgent)]
    # return the sum of agents' views
    #print(np.sum(agent_views))
    return str(np.sum(agent_views))

def get_total_likes(model):
    """sum of all agents' likes"""
    agent_likes = [a.likes for a in model.schedule.agents if isinstance(a, LearningObjectAgent)]
    # return the sum of agents' likes
    return str(np.sum(agent_likes))

class RepositoryUsageModel(mesa.Model):
    """A model with some number of agents representing the repository users.
        Each grid cell represent one learning object in the repository. 
        The agent color represent the action performed: download, view, rate, or like."""

    def __init__(self, init_users=10, view_weight=2, download_weight=4, rate_weight=8, like_weight=7, 
        view_chance=0.6, download_chance=0.5, rate_chance=0.15, like_chance=0.3,
        max_steps=30, h_size=10, v_size=10, width=10, height=10, mainPageWidth=5, showMainPage=True):
        self.running = True
        self.num_agents = init_users
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.max_steps = max_steps
        self.mainPage = []
        self.oldMainPage = []
        self.view_chance = view_chance
        self.download_chance = download_chance
        self.like_chance = like_chance
        self.rate_chance = rate_chance
        self.view_weight = view_weight
        self.download_weight = download_weight
        self.rate_weight = rate_weight
        self.like_weight = like_weight
        self.showMainPage = showMainPage
        self.currentCycle = 0
        self.weights = []
        self.weightMainPageGain = 0.15 * (self.grid.width * self.grid.height)
        self.weightSocialNetGain = 0.35 * (self.grid.width * self.grid.height)
        self.weightRefactored = 0.7 * (self.grid.width * self.grid.height)
        self.deltaScores = []

        # Create learning object agents, one in each cell, static
        id = 0
        for i in range(self.grid.width):
            for j in range(self.grid.height):
                a = LearningObjectAgent(id, False, self)
                id += 1
                self.grid.place_agent(a, (i, j))
                self.schedule.add(a)
        
        # Weights of each learning object be picked up
        self.weights = np.ones((self.grid.width * self.grid.height))
        
        # Get five random agents to put on main page in first time and update attribute
        pickedIds = 0
        while pickedIds < mainPageWidth:
            random_id = self.random.randrange(id)
            if(random_id not in self.mainPage):
                pickedIds += 1
                self.mainPage.append(random_id)
                a = self.schedule.agents.__getitem__(random_id)
                a.isOnMainPage = True
                a.cyclesOnMainPage.append(self.currentCycle)
                x, y = a.pos
                self.weights[random_id] += self.weightMainPageGain
          
        # Create user agents
        for i in range(self.num_agents):
            a = UserAgent(id, self)
            id += 1
            self.schedule.add(a)

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        # see datacollector functions above
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Views": get_total_views,
                "Downloads": get_total_downloads,
                #"Rates": get_total_rates,
                "Likes": get_total_likes,
            },
        )
        #self.datacollector.collect(self)
        
    def step(self):
        # collect data
        self.datacollector.collect(self)
        # tell all the agents in the model to run their step function
        self.schedule.step()
        if(self.schedule.steps == self.max_steps):
            self.running = False
            
            

    def run_model(self):
        for i in range(self.run_time):
            self.step()

    def isSequential(self, size, list):
        #print(list)
        for i in range(0,size-1):
            #print(list[-size+i] + 1)
            #print(list[-size+i+1])
            if(list[-size+i] + 1 != list[-size+i+1]):
                return False
        return True

    def checkSucessiveTimesOnMainPage(self, max, gain: float, type):
        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            a = self.schedule.agents.__getitem__(cell_content[0].unique_id)
            if((len(a.cyclesOnMainPage) >= max) and 
               (self.isSequential(max, a.cyclesOnMainPage)) and
               (a.cyclesOnMainPage[-1] == self.currentCycle)):
                if(len(a.cyclesOnMainPage) > max and
                (a.cyclesOnMainPage[-max-1] +1 == a.cyclesOnMainPage[-max])):
                    print("LO = " + str(a.unique_id) + " já foi para " + type + ".")
                    print(a.cyclesOnMainPage)
                else:
                    print("Muitas vezes seguidas escaparate! Vai para " + type + ", LO = " + str(a.unique_id))
                    #print("Atratividade antes:")
                    if(a.attractivity <= 0.65):
                        a.attractivity = float(a.attractivity) + float(gain)
                    print(a.attractivity)
                    #print(self.weights[cell_content[0].unique_id])
                    if(type == "redes sociais"):
                        a.isOnSocialNetwork = True
                        self.weights[cell_content[0].unique_id] += self.weightSocialNetGain
                    if(type == "refatoração"):
                        #a.isOnMainPage = False
                        self.weights[cell_content[0].unique_id] += self.weightRefactored


    #updateProbabilities(self):
    #scores = np.zeros((model.grid.width, model.grid.height))

    def updateAttractivity(self):
        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            a = self.schedule.agents.__getitem__(cell_content[0].unique_id)
            if(a.attractivity >= 0.7):
                continue
            if(a.downloads - a.lastCycleDownloads >= 10):
                #print("Antigo ATTR = " + str(a.attractivity))
                a.attractivity = round(float(a.attractivity) + float(0.1),2)
                print("Attractivity updated by download. LO = " + str(a.unique_id) + " with delta = " + str(a.downloads - a.lastCycleDownloads) + " ATTR = " + str(a.attractivity))
            if(a.likes - a.lastCycleLikes >= 5):
                #print("Antigo ATTR = " + str(a.attractivity))
                a.attractivity = round(float(a.attractivity) + float(0.2),2)
                print("Attractivity updated by like. LO = " + str(a.unique_id) + " with delta = " + str(a.likes - a.lastCycleLikes) + " ATTR = " + str(a.attractivity))

    def updateMainPageLikeDownloads(self):
        self.oldMainPage = self.oldMainPage.copy()
        d = {}
        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            a = self.schedule.agents.__getitem__(cell_content[0].unique_id)
            d[cell_content[0].unique_id] = a.score
            a.lastCycleLikes = a.likes
            a.lastCycleDownloads = a.downloads
            if(a.isOnMainPage):
                self.weights[cell_content[0].unique_id] -= self.weightMainPageGain
            #elif(not a.isOnSocialNetwork):
            #    self.weights[cell_content[0].unique_id] = 1
            a.isOnMainPage = False
            #print(d)
        sorted_dict = dict(sorted(d.items(), key=lambda x:x[1]))
        #print(sorted_dict)
        print("Scores:")
        print("First One: " + str(list(sorted_dict.values())[0]) + " LO = " + str(list(sorted_dict.keys())[0]) + " ATTR = " + str(self.schedule.agents.__getitem__(list(sorted_dict.keys())[0]).attractivity))
        print("Last One: " + str(list(sorted_dict.values())[-1]) + " LO = " + str(list(sorted_dict.keys())[-1]) + " ATTR = " + str(self.schedule.agents.__getitem__(list(sorted_dict.keys())[-1]).attractivity))
        print("Delta: " + str(list(sorted_dict.values())[-1] - list(sorted_dict.values())[0]))
        self.deltaScores.append(list(sorted_dict.values())[-1] - list(sorted_dict.values())[0])
        five_first = 0
        self.mainPage = []
        #print(sorted_dict)
        for key in sorted_dict.keys():
            self.mainPage.append(key)
            a = self.schedule.agents.__getitem__(key)
            a.isOnMainPage = True
            #if(len(a.cyclesOnMainPage) == 0 or 
            #   (len(a.cyclesOnMainPage) > 0 and a.cyclesOnMainPage[-1] + 1 != model.currentCycle)):
            #    x, y = a.pos
                #print("X = " + str(x) + " Y = " + str(y))
            self.weights[key] += self.weightMainPageGain
            if(key in self.oldMainPage):
                self.weights[key] += self.weightMainPageGain
                #print(self.probabilities)
            a.cyclesOnMainPage.append(model.currentCycle)
            five_first += 1
            #print(sorted_dict)
            if(five_first == 5):
                break

"""A model with parameters setted in cosntructor and run in cycles for 100 steps"""
cycles = 300
model = RepositoryUsageModel(init_users=10, width=10, height=10)

for j in range(cycles):
    print(">>>>> Starting cycle #" + str(j))
    if (j > 0):
        # Weights of each learning object be picked up
        model.updateMainPageLikeDownloads() 
        print("New main page:")
        
    else:
        print("Old main page:")
        

    print(sorted(model.mainPage))
    #print(model.weights)
    
    for i in range(100):
        model.step()
    

    model.updateAttractivity()
    model.checkSucessiveTimesOnMainPage(4, 0.2, "redes sociais")
    model.checkSucessiveTimesOnMainPage(8, 0.3, "refatoração")
    model.currentCycle += 1
#print(model.weights)    

scores = np.zeros((model.grid.width, model.grid.height))
views = np.zeros((model.grid.width, model.grid.height))
downloads = np.zeros((model.grid.width, model.grid.height))
likes = np.zeros((model.grid.width, model.grid.height))
#rates = np.zeros((model.grid.width, model.grid.height))

for cell in model.grid.coord_iter():
    cell_content, x, y = cell
    a = model.schedule.agents.__getitem__(cell_content[0].unique_id)
    scores[x][y] = a.score
    views[x][y] = a.views
    downloads[x][y] = a.downloads
    likes[x][y] = a.likes
    #rates[x][y] = a.rates

#print(scores)

con = np.concatenate((likes,downloads,views))
name = ['Likes', 'Downloads', 'Views']
#magnitude = np.linalg.norm(con)
#normalized_con = con / magnitude

newarr = np.array_split(con, 3)
min_attr = np.min([np.min(con)])
max_attr = np.max([np.max(con)])

max_score = np.max([np.max(scores)])
min_score = np.min([np.min(scores)])

fig = plt.figure(constrained_layout=True)
(subfig_l, subfig_c1, subfig_c2, subfig_r) = fig.subfigures(nrows=1, ncols=4)

axes_l = subfig_l.subplots(nrows=3, ncols=1, sharex=True, sharey=True)
for i,ax in enumerate(axes_l.flat):
    im = ax.imshow(newarr[i], interpolation='nearest', vmin=min_attr, vmax=max_attr)
    ax.set_title(name[i])

cax,kw = mpl.colorbar.make_axes([ax for ax in axes_l.flat])
subfig_l.colorbar(im, cax=cax, **kw)

axes_c1 = subfig_c1.subplots(nrows=1, ncols=1, sharex=True, sharey=True)
im = axes_c1.imshow(scores, interpolation='nearest', vmin=min_score, vmax=max_score)
axes_c1.set_title("Scores")
subfig_c1.colorbar(im, ax=axes_c1)

axes_c2 = subfig_c2.subplots(nrows=1, ncols=1)

x_axis = [i for i in range(0,cycles-1)]
y_axis = model.deltaScores

axes_c2.plot(x_axis, y_axis)
axes_c2.set_title('Delta scores x Cycles')

axes_r = subfig_r.subplots(nrows=1, ncols=1)
x = model.deltaScores
axes_r.hist(x)
#subfig_r.xlabel('Cycle')
#subfig_r.ylabel('Delta score')

plt.show()

sns.histplot(data=model.deltaScores)
plt.title("Histograma de delta escores")
plt.grid()
plt.show()
print(model.detaScores)

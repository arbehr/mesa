import mesa

from .agent import UserAgent, LearningObjectAgent
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import csv
import time

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
        download_chance=0.5, select_chance=0.7, like_chance=0.5,
        max_steps=30, h_size=10, v_size=10, width=10, height=10, mainPageWidth=5, showMainPage=True):
        self.running = True
        self.num_agents = init_users
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.max_steps = max_steps
        self.mainPage = []
        self.select_chance = select_chance
        self.download_chance = download_chance
        self.like_chance = like_chance
        self.view_weight = view_weight
        self.download_weight = download_weight
        self.rate_weight = rate_weight
        self.like_weight = like_weight
        self.showMainPage = showMainPage
        self.currentCycle = 0
        self.attractivities = []
        self.deltaScores = []
        self.scenario = "HARD" #EASY, MEDIUM, HARD
        self.dataToCSV = []

        # Parameters to analyse
        self.gainOnMainPage = 0.2
        self.gainOnSocialMedia = 0.2

        # Create learning object agents, one in each cell, static
        object_id = 0
        for i in range(self.grid.width):
            for j in range(self.grid.height):
                a = LearningObjectAgent(object_id, False, self)
                object_id += 1
                self.grid.place_agent(a, (i, j))
                self.schedule.add(a)
                self.attractivities.append(a.attractivity)
                       
        # Create user agents
        for i in range(self.num_agents):
            a = UserAgent(object_id, self)
            object_id += 1
            self.schedule.add(a)
           
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            # Then move to a proper learning object with more attractivity
            a.move()

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
               #(self.isSequential(max, a.cyclesOnMainPage)) and
               (a.cyclesOnMainPage[-1] == self.currentCycle)):
                if(len(a.cyclesOnMainPage) > max and
                (a.cyclesOnMainPage[-max-1] +1 == a.cyclesOnMainPage[-max])):
                    print("LO = " + str(a.unique_id) + " já foi para " + type + ".")
                    print(a.cyclesOnMainPage)
                else:
                    print("Muitas vezes seguidas escaparate! Vai para " + type + ", LO = " + str(a.unique_id))
                    #print("Atratividade antes:")
                    #if(a.attractivity <= 0.65):
                    #    a.attractivity = float(a.attractivity) + float(gain)
                    #print(a.attractivity)
                    #print(self.weights[cell_content[0].unique_id])
                    if(type == "redes sociais"):
                        a.socialNetwork += self.gainOnSocialMedia
                        #self.weights[cell_content[0].unique_id] += self.weightSocialNetGain
                    if(type == "refatoração"):
                        #a.mainPage = 0
                        a.cyclesOnMainPage = []
                        #a.refactored = 0.
                        a.refactored = round(self.random.uniform(-0.2, 0.3),3)
                        #print("REFATORADO = " + str(a.refactored))
                        #self.weights[cell_content[0].unique_id] += self.weightRefactored
    
    def updateAttractivities(self):
        self.attractivities = []
        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            a = self.schedule.agents.__getitem__(cell_content[0].unique_id)
            a.attractivity = a.intrinsicValue + a.mainPage + a.socialNetwork + a.refactored
            self.attractivities.append(a.attractivity)  
    
    def updateMainPage(self):
        d = {}
        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            a = self.schedule.agents.__getitem__(cell_content[0].unique_id)
            a.mainPage = 0
            a.gainOnMainPage = 0
            d[cell_content[0].unique_id] = a.score
            
        sorted_dict = dict(sorted(d.items(), key=lambda x:x[1]))
        #print(sorted_dict)
        print("Scores:")
        self.dataToCSV.append(str(list(sorted_dict.values())[0]))
        self.dataToCSV.append(str(list(sorted_dict.values())[-1]))
        self.dataToCSV.append(str(list(sorted_dict.values())[-1] - list(sorted_dict.values())[0]))
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
            a.cyclesOnMainPage.append(model.currentCycle)
            a.mainPage += self.gainOnMainPage
            five_first += 1
            #print(sorted_dict)
            if(five_first == 5):
                break

"""A model with parameters setted in cosntructor and run in cycles for 100 steps (ticks)"""
cycles = 30
ticks = 100
ts = time.time()
model = RepositoryUsageModel(init_users=10, width=10, height=10)

header = ['cycle', 'ticks', 'first_score', 'last_score', 'delta_score',
          'main_page', 'gainMainpage', 'gainSocialNetwork', 'gainRefactored',],

with open('experiments' + str(ts) + '.csv', 'w+', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for j in range(cycles):
        model.dataToCSV = []
        model.dataToCSV.append(str(j))
        model.dataToCSV.append(ticks)

        print(">>>>> Starting cycle #" + str(j))
           
        for i in range(ticks):
            model.step()
        
        #Decisions after cycle
        if (j > 0):
            model.updateMainPage() 
            print("New main page:")
            print(sorted(model.mainPage))
        else:
            model.dataToCSV.append("0")
            model.dataToCSV.append("0")
            model.dataToCSV.append("0")
        
        model.dataToCSV.append(str(sorted(model.mainPage)))
        model.dataToCSV.append(str(model.gainOnMainPage))
        model.dataToCSV.append(str(model.gainOnSocialMedia))
        model.dataToCSV.append("0")
       
        if(model.scenario == "HARD" or model.scenario == "MEDIUM"):
            model.checkSucessiveTimesOnMainPage(4, 0.5, "redes sociais")
        if(model.scenario == "HARD"):
            model.checkSucessiveTimesOnMainPage(8, 0.0, "refatoração")
        model.updateAttractivities()
        model.currentCycle += 1

        
        writer.writerow(model.dataToCSV)
#print(model.attractivities)    

scores = np.zeros((model.grid.width, model.grid.height))
views = np.zeros((model.grid.width, model.grid.height))
downloads = np.zeros((model.grid.width, model.grid.height))
likes = np.zeros((model.grid.width, model.grid.height))

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

import mesa

from .agent import UserAgent, LearningObjectAgent
import numpy as np

def get_total_downloads(model):
    """sum of all agents' downloads"""
    agent_downloads = [a.downloads for a in model.schedule.agents if isinstance(a, LearningObjectAgent)]
    # return the sum of agents' downloads
    return str(np.sum(agent_downloads))

def get_total_views(model):
    """sum of all agents' views"""    
    agent_views = [a.views for a in model.schedule.agents if isinstance(a, LearningObjectAgent)]
    # return the sum of agents' views
    print(np.sum(agent_views))
    return str(np.sum(agent_views))

def get_total_rates(model):
    """sum of all agents' rates"""
    agent_rates = [a.rates for a in model.schedule.agents if isinstance(a, LearningObjectAgent)]
    # return the sum of agents' rates
    return str(np.sum(agent_rates))

def get_total_likes(model):
    """sum of all agents' likes"""
    agent_likes = [a.likes for a in model.schedule.agents if isinstance(a, LearningObjectAgent)]
    # return the sum of agents' likes
    return str(np.sum(agent_likes))

class RepositoryUsageModel(mesa.Model):
    """A model with some number of agents representing the repository users.
        Each grid cell represent one learning object in the repository. 
        The agent color represent the action performed: download, view, rate, or like."""

    def __init__(self, init_users, view_weight=2, download_weight=4, rate_weight=8, like_weight=7, 
        view_chance=0.6, download_chance=0.4, rate_chance=0.15, like_chance=0.2,
        max_steps=30, h_size=10, v_size=10, width=5, height=2, mainPageWidth=5):
        self.running = True
        self.num_agents = init_users
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.max_steps = max_steps
        self.mainPage = " "
        self.view_chance = view_chance
        self.download_chance = download_chance
        self.like_chance = like_chance
        self.rate_chance = rate_chance
        self.view_weight = view_weight
        self.download_weight = download_weight
        self.rate_weight = rate_weight
        self.like_weight = like_weight

        # Create learning object agents, one in each cell, static
        id = 0
        for i in range(self.grid.width):
            for j in range(self.grid.height):
                a = LearningObjectAgent(id, id < 5, self)
                id += 1
                self.grid.place_agent(a, (i, j))
                self.schedule.add(a)
        # Get five random agents to put on main page
        pickedIds = 0
        while pickedIds < mainPageWidth:
            random_id = self.random.randrange(id)
            if((" " + str(random_id) + " ") not in self.mainPage):
                pickedIds += 1
                self.mainPage += str(random_id) + " "
                
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
                "Rates": get_total_rates,
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

"""A model with 10 agents and run it for 10 steps"""
#model = RepositoryUsageModel(10,1,10)
#for i in range(10):
#    model.step()
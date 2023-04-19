import mesa
import numpy as np

class LearningObjectAgent(mesa.Agent):
    """An learning object agent that takes action in repository."""
    def __init__(self, unique_id, on_main_page, model):
        super().__init__(unique_id, model)    
        self.views = 0
        self.downloads = 0
        self.lastCycleDownloads = 0
        self.likes = 0
        self.lastCycleLikes = 0
        self.text = ""
        self.score = 0
        self.cyclesOnMainPage = []
        self.isOnMainPage = on_main_page
        self.showMainPage = model.showMainPage
        self.isOnSocialNetwork = False
        self.attractivity = float(round(self.random.random(),2))
        if(self.attractivity == 1.0):
            self.attractivity = 0.9
        if (self.attractivity < 0.1):
            self.attractivity = 0.1

    def step(self):
        weights_sum = self.model.view_weight + self.model.download_weight + self.model.like_weight #+ self.model.rate_weight 
        self.score = (self.model.view_weight * self.views) + (self.model.download_weight * self.downloads)
        self.score = self.score + (self.model.like_weight * self.likes) #+ (self.model.rate_weight * self.rates)
        self.score = self.score / weights_sum
        self.text = "ID: " + str(self.unique_id) + ". V:" + str(self.views) 
        self.text += " D:" + str(self.downloads) + " L:" + str(self.likes) #+ " R:" + str(self.rates)
        self.text += " SCORE:" + str(float("{:.4f}".format(self.score)))
        self.text += " ATT:" + str(self.attractivity)

class UserAgent(mesa.Agent):
    """An user agent that takes action in repository."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.action = 0
        self.canMove = True
   
    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        if(self.canMove):
            self.move()
        self.do_action()
        
        #x, y = self.pos
        #print("Hi, I am agent " + str(self.unique_id) + ". Position: " + str(self.pos) + 
        #    ". X = " + str(x) + " Y = " + str(y))
    
    def do_action(self):
        #x, y = self.pos
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        self.canMove = False
        if isinstance(cellmates[0], LearningObjectAgent):
            #print("Old action = " + str(self.action))

            prob_user_interest = round(self.random.random(),2)
            
            if self.action == 0 :
                #print("Main page = " + self.model.mainPage)
                main_page_exp = 0
                if((" " + str(cellmates[0].unique_id) + " ") in self.model.mainPage):
                    main_page_exp = 0.3
                    #print("*** LO on main page ***")
                if(float(prob_user_interest + cellmates[0].attractivity + main_page_exp) >= 1.0):
                #if(float(prob_user_interest + main_page_exp) >= cellmates[0].attractivity):
                    #print("User: " + str(self.unique_id) + " - Viewed LO(" + str(cellmates[0].unique_id) + ")! at " + str(cellmates[0].pos))
                    #print(str(cellmates[0].unique_id) + ": " + str(prob_user_interest) + " - " + str(cellmates[0].attractivity))
                    self.action = 1
                    cellmates[0].views += 1
                else:
                    #print("User: " + str(self.unique_id) + " - NOT Viewed LO(" + str(cellmates[0].unique_id) + ")! at " + str(cellmates[0].pos))
                    self.canMove = True
            elif self.action == 1:
                #if(prob_user_interest + (cellmates[0].attractivity * self.model.download_chance) >= 1):
                if(prob_user_interest >= (cellmates[0].attractivity * self.model.download_chance)):
                    #print("User: " + str(self.unique_id) + " - Downloaded LO(" + str(cellmates[0].unique_id) + ")! at " + str(cellmates[0].pos))
                    self.action = 2
                    cellmates[0].downloads += 1
                else:
                    #print("User: " + str(self.unique_id) + " - NOT Downloaded LO(" + str(cellmates[0].unique_id) + ")! at " + str(cellmates[0].pos))
                    self.action = 0
                    self.canMove = True
            elif self.action == 2:
                #if(prob_user_interest + (cellmates[0].attractivity * self.model.like_chance) >= 1):
                if(prob_user_interest >= (cellmates[0].attractivity * self.model.like_chance)):
                    #print("User: " + str(self.unique_id) + " - Liked LO(" + str(cellmates[0].unique_id) + ")! at " + str(cellmates[0].pos))
                    cellmates[0].likes += 1
                    #self.action = 3
                #else:
                    #print("User: " + str(self.unique_id) + " - NOT Liked LO(" + str(cellmates[0].unique_id) + ")!  at " + str(cellmates[0].pos)) #+ " Let's try to rate")
                    #self.action = -3
                self.canMove = True
                self.action = 0
            '''elif self.action == 3 or self.action == -3:
                if(prob_user_interest <= self.model.rate_chance * 100):
                    print(str(self.unique_id) + " - Rated LO!  at " + str(cellmates[0].pos))
                    cellmates[0].rates += 1
                    self.action = 4
                else:
                    print(str(self.unique_id) + " - NOT Rated LO! at " + str(cellmates[0].pos))
                    self.action = 0
                self.canMove = True
                '''

    def move(self):
        #x = self.random.randrange(self.model.grid.width)
        #y = self.random.randrange(self.model.grid.height)
        probabilities = [weight/sum(self.model.weights) for weight in self.model.weights]
        position = np.random.choice(np.arange(0, 100), p = probabilities)
        a = self.model.schedule.agents.__getitem__(position)
        x , y = a.pos
        self.model.grid.move_agent(self, (x, y))

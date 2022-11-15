import mesa

class LearningObjectAgent(mesa.Agent):
    """An learning object agent that takes action in repository."""
    def __init__(self, unique_id, onMainPage, model):
        super().__init__(unique_id, model)    
        self.views = 0
        self.downloads = 0
        self.rates = 0
        self.likes = 0
        self.text = ""
        self.score = 0

    def step(self):
        self.text = "ID: " + str(self.unique_id) + ". V:" + str(self.views) 
        self.text += " D:" + str(self.downloads) + " R:" + str(self.rates) + " L:" + str(self.likes)
        self.score = 0
        # calc score

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
        
        x, y = self.pos
        #print("Hi, I am agent " + str(self.unique_id) + ". Position: " + str(self.pos) + 
        #    ". X = " + str(x) + " Y = " + str(y))
    
    def do_action(self):
        x, y = self.pos
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        self.canMove = False
        if isinstance(cellmates[0], LearningObjectAgent):
            print("Old action = " + str(self.action))

            prob_action = self.random.randrange(0,100)
            if(self.action == 0):
                print("Main page = " + self.model.mainPage)
                mainPageExp = 0
                if((" " + str(self.unique_id) + " ") in self.model.mainPage):
                    mainPageExp = 0.1
                    print("*** LO on main page ***")
                if(prob_action <= (self.model.view_chance + mainPageExp) * 100):
                    print(str(self.unique_id) + " - Viewed LO!")
                    self.action = 1
                    cellmates[0].views += 1
                else:
                    print(str(self.unique_id) + " - NOT Viewed LO!")
                    self.canMove = True
            #cellmates[0].color = self.number_to_string_color(action_number)
            #print(cellmates[0].color)
            elif(self.action == 1):
                if(prob_action <= self.model.download_chance * 100):
                    print(str(self.unique_id) + " - Downloaded LO!")
                    self.action = 2
                    cellmates[0].downloads += 1
                else:
                    print(str(self.unique_id) + " - NOT Downloaded LO!")
                    self.action = 0
                    self.canMove = True
            elif self.action == 2:
                if(prob_action <= self.model.like_chance * 100):
                    print(str(self.unique_id) + " - Liked LO!")
                    cellmates[0].likes += 1
                    self.action = 3
                else:
                    print(str(self.unique_id) + " - NOT Liked LO! Let's try to rate")
                    self.action = -3
            elif self.action == 3 or self.action == -3:
                if(prob_action <= self.model.rate_chance * 100):
                    print(str(self.unique_id) + " - Rated LO!")
                    cellmates[0].rates += 1
                    self.action = 4
                else:
                    print(str(self.unique_id) + " - NOT Rated LO!")
                    self.action = 0
                    self.canMove = True

    def move(self):
        x = self.random.randrange(self.model.grid.width)
        y = self.random.randrange(self.model.grid.height)
        self.model.grid.move_agent(self, (x, y))

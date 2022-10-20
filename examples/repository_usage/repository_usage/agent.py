import mesa

class LearningObjectAgent(mesa.Agent):
    """An learning object agent that takes action in repository."""
    def __init__(self, unique_id, onMainPage, model):
        super().__init__(unique_id, model)    
        self.views = 0
        self.downloads = 0
        self.rates = 0
        self.likes = 0
        self.isOnMainPage = onMainPage
        self.text = ""

    def step(self):
        self.text = "ID: " + str(self.unique_id) + ". V:" + str(self.views) 
        self.text += " D:" + str(self.downloads) + " R:" + str(self.rates) + " L:" + str(self.likes)

class UserAgent(mesa.Agent):
    """An user agent that takes action in repository."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.action = 0
   
    def step(self):
        # The agent's step will go here.
        # For demonstration purposes we will print the agent's unique_id
        self.move()
        self.do_action()
        
        x, y = self.pos
        print("Hi, I am agent " + str(self.unique_id) + ". Position: " + str(self.pos) + 
            ". X = " + str(x) + " Y = " + str(y))
    
    def do_action(self):
        x, y = self.pos
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if isinstance(cellmates[0], LearningObjectAgent):
            self.action = self.random.randrange(0,4)
            #cellmates[0].color = self.number_to_string_color(action_number)
            #print(cellmates[0].color)
            if self.action == 0:
                cellmates[0].views += 1
            elif self.action == 1:
                cellmates[0].downloads += 1
            elif self.action == 2:
                cellmates[0].rates +=1
            elif self.action == 3:
                cellmates[0].likes += 1

    def move(self):
        x = self.random.randrange(self.model.grid.width)
        y = self.random.randrange(self.model.grid.height)
        self.model.grid.move_agent(self, (x, y))

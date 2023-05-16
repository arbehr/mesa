from repository_usage.model import *
import mesa
import matplotlib.pyplot as plt

# The colors here are taken from Matplotlib's tab10 palette
# Gray, action_code = 0
NONE_COLOR = "#868786"
# Green, action_code = 1
VIEW_COLOR = "#2ca02c"
# Red, action_code = 2
DOWNLOAD_COLOR = "#d62728"
# Blue, action_code = 3
LIKE_COLOR = "#1f77b4"
# Gold, action_code = 4
RATE_COLOR = "#b4991f"

NUMBER_OF_CELLS = 10
SIZE_OF_CANVAS_IN_PIXELS_X = 800
SIZE_OF_CANVAS_IN_PIXELS_Y = 800

def get_objects_on_main_page(model):
    """
    Display a text of learning objects on main page.
    """
    return f"Main page: {model.mainPage}"

def agent_portrayal(agent):

    if agent is None:
        return

    portrayal = {}

    if isinstance(agent, UserAgent):
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Layer"] = 0
        portrayal["Filled"] = "true"
        color = NONE_COLOR
        if agent.action == 1:
            color = VIEW_COLOR
        elif agent.action == 2:
            color = DOWNLOAD_COLOR
        elif agent.action == 3:
            color = LIKE_COLOR
        elif agent.action == 4:
            color = RATE_COLOR
        portrayal["Color"] = color
    elif type(agent) is LearningObjectAgent:
        portrayal["Layer"] = 1
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Text"] = agent.text
        if agent.mainPage:
            portrayal["Color"] = ["#84e184", "#adebad", "#d6f5d6"]
            portrayal["Shape"] = "circle"
            portrayal["Filled"] = "true"
            portrayal["Layer"] = 1
            portrayal["r"] = 0.2
        
        
    return portrayal

# dictionary of user settable parameters - these map to the model __init__ parameters
model_params = {
    "showMainPage": mesa.visualization.Checkbox("Showcase Enabled", True),
    "sec_repository": mesa.visualization.StaticText("Repository Parameters:"),
    "max_steps": mesa.visualization.Slider(
        "Lifecycle (max steps)",
        100,
        1,
        1000,
        description="Like weight to be used to rank",
    ),
    "h_size": mesa.visualization.Slider(
        "Horizontal amount of learning objects",
        10,
        1,
        100,
        description="Horizontal size of learning objects",
    ),
    "v_size": mesa.visualization.Slider(
        "Vertical amount of learning objects",
        10,
        1,
        100,
        description="Vertical size of learning objects",
    ),
    "download_chance": mesa.visualization.Slider(
        "Download Chance",
        0.5,
        0.0,
        1.0,
        0.1,
        description="Probability that a learning object will be downloaded",
    ),
    "like_chance": mesa.visualization.Slider(
        "Like Chance",
        0.5,
        0.0,
        1.0,
        0.1,
        description="Probability that a learning object will be liked",
    ),
    "sec_users": mesa.visualization.StaticText("Users Parameters:"),
    "init_users": mesa.visualization.Slider(
        "Amount of users", 2, 1, 200, description="Initial Number of Users"
    ),
    "sec_rank": mesa.visualization.StaticText("Ranking Parameters:"),
    "view_weight": mesa.visualization.Slider(
        "View weight",
        2,
        1,
        100,
        description="View weight to be used to rank",
    ),
    "download_weight": mesa.visualization.Slider(
        "Download weight",
        4,
        1,
        100,
        description="Download weight to be used to rank",
    ),
    "like_weight": mesa.visualization.Slider(
        "Like weight",
        7,
        1,
        100,
        description="Like weight to be used to rank",
    ),
    "width": NUMBER_OF_CELLS,
    "height": NUMBER_OF_CELLS,
}

grid = mesa.visualization.CanvasGrid(agent_portrayal, NUMBER_OF_CELLS, NUMBER_OF_CELLS, SIZE_OF_CANVAS_IN_PIXELS_X, SIZE_OF_CANVAS_IN_PIXELS_Y)

# map data to chart in the ChartModule
line_chart = mesa.visualization.ChartModule(
    [
        {"Label": "Views", "Color": VIEW_COLOR},
        {"Label": "Downloads", "Color": DOWNLOAD_COLOR},
        {"Label": "Rates", "Color": RATE_COLOR},
        {"Label": "Likes", "Color": LIKE_COLOR},
    ]
)

server = mesa.visualization.ModularServer(
    RepositoryUsageModel, [grid, get_objects_on_main_page, line_chart], "Repository Model",  model_params=model_params,
)
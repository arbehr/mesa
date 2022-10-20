from repository_usage.model import *
import mesa

# The colors here are taken from Matplotlib's tab10 palette
# Green, color_code = 0
VIEW_COLOR = "#2ca02c"
# Red, color_code = 1
DOWNLOAD_COLOR = "#d62728"
# Blue, color_code = 2
LIKE_COLOR = "#1f77b4"
# Gold, color_code = 3
RATE_COLOR = "#b4991f"

def agent_portrayal(agent):

    if agent is None:
        return

    portrayal = {}

    if isinstance(agent, UserAgent):
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Layer"] = 0
        portrayal["Filled"] = "true"
        color = "gray"
        if agent.action == 0:
            color = VIEW_COLOR
        elif agent.action == 1:
            color = DOWNLOAD_COLOR
        elif agent.action == 2:
            color = LIKE_COLOR
        elif agent.action == 3:
            color = RATE_COLOR
        portrayal["Color"] = color
    elif type(agent) is LearningObjectAgent:
        if agent.isOnMainPage:
            portrayal["Color"] = ["#84e184", "#adebad", "#d6f5d6"]
            portrayal["Shape"] = "rect"
            portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["Text"] = agent.text
    return portrayal

# dictionary of user settable parameters - these map to the model __init__ parameters
model_params = {
    "sec_users": mesa.visualization.StaticText("Users Parameters:"),
    "init_users": mesa.visualization.Slider(
        "Amount of users", 2, 1, 200, description="Initial Number of Users"
    ),
    "view_chance": mesa.visualization.Slider(
        "View Chance",
        0.6,
        0.0,
        1.0,
        0.1,
        description="Probability that a learning object will be viewed",
    ),
    "download_chance": mesa.visualization.Slider(
        "Download Chance",
        0.4,
        0.0,
        1.0,
        0.1,
        description="Probability that a learning object will be downloaded",
    ),
    "rate_chance": mesa.visualization.Slider(
        "Rate Chance",
        0.15,
        0.0,
        1.0,
        0.1,
        description="Probability that a learning object will be rated",
    ),
    "like_chance": mesa.visualization.Slider(
        "Like Chance",
        0.2,
        0.0,
        1.0,
        0.1,
        description="Probability that a learning object will be liked",
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
    "rate_weight": mesa.visualization.Slider(
        "Rate weight",
        8,
        1,
        100,
        description="Rate weight to be used to rank",
    ),
    "like_weight": mesa.visualization.Slider(
        "Like weight",
        7,
        1,
        100,
        description="Like weight to be used to rank",
    ),
}

grid = mesa.visualization.CanvasGrid(agent_portrayal, 5, 5, 500, 500)

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
    RepositoryUsageModel, [grid, line_chart], "Repository Model",  model_params=model_params,
)
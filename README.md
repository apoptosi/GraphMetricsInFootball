# GraphMetricsInFootball

## Project Motivation
When watching football, it often appears that certain players dominate the game, acting as central points for passes in most of the actions. Therefore, they should be valued as more important than others.
To properly assess this, we need a reliable and quantifiable measure: we aim to examine whether a player’s centrality in a team’s passing network - along with, if necessary, other measures - correlates with match outcome and individual performance.


## Project structure
### Raw Data
In this folder are stored all the .json data in a compress format to run the project locally just run the extractRawData.cmd that will
extract all the zip in .json format inside the data folder

### compile project
The project uses varius external libraries to compile the project locally run:

- python -m pip install networkx
- python -m pip install pandas
- python -m pip install c
- pip install sqlalchemy
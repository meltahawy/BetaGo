# BetaGo
BetaGo is a graphical user interface for the game of Go with a built-in AI. It is built using Python + TkInter. Users can opt to play 2 player with a friend locally. They can also play against BetaGo, an AI that is built with the Monte Carlo Search Tree technique and can run 500 simulations/sec. The GUI is flexible and users can opt to play on any size board they please. The game rules are as follows: no illegal ko moves, no suicides, and area scoring.

# Demo:
5x5 BetaGo against the AI (white)

BetaGo can search/simulate 546 nodes/sec on a 5x5 board.


![BetaGo Demo](https://raw.githubusercontent.com/meltahawy/meltahawy.github.io/master/img/BetaGo.png)

# Documentation

The AI finds the next best move using the Monte Carlo Search Tree technique. The root of the search tree is the current state of the game (normally the black stone player has just played) then for the amount of time decided by the user, the Monte Carlo Search Tree repeats the following 4 phases:

### 1. Selection

The AI picks the most promising leaf node in the tree to begin testing. The term promising is subjective and is decided by a multi-bandit algorithm known as UCB1 (Upper Confidence Bound). Each node in the tree has a UCB1 value and the formula is as follows:

(node.wins / node.noOfSimulations) + sqrt(2 * ln(node.parent.noOfSimulations) / node.noOfSimulations)

There are two caveats. First the algorithm always picks unvisited nodes, if the number of simulations of a node is 0, then it's UCB1 value is INT_MAX. The other caveat is that the leaf node picked cannot correspond to a terminal state (the game is over), to account for that I made it always return the parent of a terminal state.

### 2. Expansion

Once a node (corresponding to a state in the game) is selected, as long as it is not a node in a terminal state, all possible states from that node are generated and added as children to the selected node. Other implementations add 1 node per expansion phase, my implementation adds all possible nodes/states per expansion phase iteration.

### 3. Simulation

Since Go is a very variable game with billions of possibilities, creating a robust AI with random simulations (light playouts) is impractical, at least on my computer. Thus I decided to implement heavy playouts. Heavy playouts means that the simulations are not completely random, they use some information about the game state to make a decision. My heavy playout implementation is that black/white will play the move that yields the highest net score increase and will avoid playing moves that are suicidal or that will cause a future reduction in score (for example fill an eye out of two eyes of a group at risk of capture)

### 4. Backpropogation

The result of simulation/heavy playout are added to the stats of the node simulated and backpropogated all the way to the first ancestor of the simulated node, updating every node encountered along the way.


## Summary:

Black plays at position (0, 0). A MCTS (Monte Carlo Search Tree) node, let's call it black1 is created and a Monte Carlo Search Tree is created. Black1 becomes the root of the tree. Since the root is the only node in the tree, it is selected. Then expansion occurs, all possible white moves considering black played at (0, 0) are added as children to black1. Then one of these children are selected to be simulated from game start to game end (NOT AFFECTING THE NODE), let's say white1 is selected, a copy of white1 is created and a simulated game is played on the copy of white1, the result of the game is recorded and added to the stats of white1. Then that result is backpropogated all the way to the first ancestor of white1, updating every node encountered along the way.

## Logistics: 

The GUI is created using TkInter. Every intersection has an invisible placeholder button that when clicked becomes the image of either a white stone or a black stone.

Users can change the size of the board as they please in the constructor of the GameBoard class

The AI is coded to only play White. 

## TO DO:

- The game score method needs a lot of improvement. It cannot account for dead pieces after a game is over. For example, if white plays in black territory and the game is over, this function will give points to white for having pieces on the board and will not count that territory as black territory.
- Allow AI to play as black/give the player the option of playing whatever color they please against the AI.
- Display stats (stones captured).
- Implement the pass feature for both player and AI. (Easy to make for the AI, as it will pass if no valid moves left).
- Parallelize the code for better performance.
- Clean up code/refactor.
#### Experiment with: 
- Expand node only if simulated at least k times.
- Implement Dynamic Komi
- Integrate other proven successful methods with MCTS such as RAVE.

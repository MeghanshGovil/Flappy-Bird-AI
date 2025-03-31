# Flappy Bird AI

An implementation of Flappy Bird game with an AI agent that learns to play through reinforcement learning (Q-learning).

![Image Alt](https://github.com/MeghanshGovil/Flappy-Bird-AI/blob/main/imgs/Running.png)

## Overview

This project implements a Flappy Bird game clone using Pygame, with an AI agent that learns to play the game through reinforcement learning. The AI uses Q-learning to improve its performance over multiple generations, learning optimal strategies to navigate through pipes and achieve higher scores.

## Features

- **Dual Control Modes**: Toggle between AI and manual control
- **Real-time Learning**: Watch the AI improve with each generation
- **Learning Visualization**: Track the AI's progress through real-time graphs
- **Pause Functionality**: Pause the game to observe the AI's decision-making
- **Interactive UI**: User-friendly interface with keyboard controls

## Learning Progress

The AI agent's performance improves over generations through Q-learning, as demonstrated by the graph below:

![Learning Progress](https://github.com/MeghanshGovil/Flappy-Bird-AI/blob/main/imgs/learning_progress.png)

## Dependencies

- Python 3.6+
- Pygame
- NumPy
- Matplotlib

## Installation

1. Clone this repository:
```bash
git clone https://github.com/MeghanshGovil/flappy-bird-ai.git
cd flappy-bird-ai
```

2. Install the required dependencies:
```bash
pip install pygame numpy matplotlib
```

3. Ensure you have the necessary image files in the `imgs` folder:
   - bird1.png
   - bg.png
   - pipe.png
   - base.png

## How to Run

Run the game with:
```bash
python Updated.py
```

## Controls

- **Space/Up Arrow**: Flap (in manual mode)
- **Q**: Toggle between AI and manual control
- **S**: Pause/Resume the game
- **P**: Show the learning progress plot

## How It Works

### Q-Learning Implementation

The AI agent uses Q-learning, a reinforcement learning algorithm, to learn the optimal policy for playing Flappy Bird. The state space is discretized based on:

1. The horizontal distance to the next pipe
2. The vertical distance between the bird and the pipe opening

The action space consists of two possible actions:
- Flap (jump)
- Do nothing (fall)

The Q-values are updated using the formula:
```
Q(s,a) = (1-α) * Q(s,a) + α * (reward + γ * max(Q(s',a')))
```

Where:
- `s` is the current state
- `a` is the action taken
- `s'` is the next state
- `α` is the learning rate (0.6)
- `γ` is the discount factor (implied)
- `reward` is the immediate reward (15 for surviving, -1000 for collision)

### Performance

The AI typically learns to consistently achieve scores of 50+ within 100-200 generations, with occasional scores exceeding 150. The learning curve shows steady improvement with occasional spikes in performance.

## Future Improvements

- Implement Deep Q-learning for better performance
- Add different difficulty levels
- Optimize the Q-learning parameters
- Implement different AI algorithms for comparison

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original Flappy Bird game by Dong Nguyen
- Pygame community for game development resources

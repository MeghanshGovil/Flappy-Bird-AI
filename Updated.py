import random
import sys
import pygame
from pygame.locals import *
import numpy
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

# Window dimensions - properly set to avoid black bars
SW = 400
SH = 600

BASEY = SH * 0.8
IMAGES = {}
pygame.font.init()

# Initialize window with the proper size to prevent black bars
WINDOW = pygame.display.set_mode((SW, SH))
Font = pygame.font.SysFont("Arial", 30)
SmallFont = pygame.font.SysFont("Arial", 20)
BIRD = 'imgs/bird1.png'
BG = 'imgs/bg.png'
PIPE = 'imgs/pipe.png'
Q = numpy.zeros((7, 21, 2), dtype=float)
FPS = 60
SCORE_HISTORY = []

# Track if AI or manual mode is active
AI_CONTROL = True
# Track if game is paused
PAUSED = False

def draw_text_with_outline(text, font, color, x, y, outline_color=(0, 0, 0)):
    """Draw text with outline for better visibility"""
    outline = font.render(text, True, outline_color)
    text_surface = font.render(text, True, color)
    
    # Draw outline in all directions
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, -1), (-1, 0), (1, 0), (0, 1)]:
        WINDOW.blit(outline, (x + dx, y + dy))
    
    # Draw main text
    WINDOW.blit(text_surface, (x, y))

def draw_progress_graph(x, y):
    """Create a matplotlib graph and convert to pygame surface"""
    fig = Figure(figsize=(4, 3), dpi=100, tight_layout=True)
    ax = fig.add_subplot(111)
    ax.plot(x, y, 'b-', marker='o', markersize=4)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Score")
    ax.set_title("Learning Progress")
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Set background color
    ax.set_facecolor("#e6f2ff")
    fig.patch.set_facecolor("#e6f2ff")
    
    # Create canvas and render to string buffer
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.tostring_rgb()
    
    # Create pygame surface
    size = canvas.get_width_height()
    surf = pygame.image.fromstring(raw_data, size, "RGB")
    
    return surf

def show_plot(x, y):
    """Display the current learning progress plot in a separate window"""
    if len(x) > 1:
        plt.figure(figsize=(10, 6))
        plt.scatter(x, y, c='blue', alpha=0.7)
        plt.plot(x, y, 'r-', alpha=0.5)
        plt.xlabel("GENERATION/Number of Trials")
        plt.ylabel("SCORE")
        plt.title("Flappy Birds: AI Learning Progress")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig("learning_progress_current.png")
        plt.show(block=False)

def static():
    birdxpos = int(SW/5)
    birdypos = int((SH - IMAGES['bird'].get_height())/2)
    basex = 0
    
    # Add some animation for the start screen
    bird_y_change = 1
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
        
        # Fill the entire screen with background color first to prevent black bars
        WINDOW.fill((135, 206, 235))  # Sky blue color
        
        # Animate bird on start screen
        birdypos += bird_y_change
        if birdypos > SH/2 + 20 or birdypos < SH/2 - 20:
            bird_y_change *= -1
            
        # Background parallax effect - ensure it covers the whole screen
        rel_x = basex % IMAGES['background'].get_width()
        WINDOW.blit(IMAGES['background'], (rel_x - IMAGES['background'].get_width(), 0))
        if rel_x < SW:
            WINDOW.blit(IMAGES['background'], (rel_x, 0))
        basex -= 1
        
        # Draw bird and base
        WINDOW.blit(IMAGES['bird'], (birdxpos, birdypos))
        WINDOW.blit(IMAGES['base'], (0, BASEY))
        # Ensure base covers the entire width
        if IMAGES['base'].get_width() < SW:
            WINDOW.blit(IMAGES['base'], (IMAGES['base'].get_width(), BASEY))
        
        # Draw title and instructions with glow effect
        draw_text_with_outline("FLAPPY BIRD AI", Font, (255, 255, 255), SW/2 - 100, SH/2 - 60, (0, 0, 0))
        draw_text_with_outline("Press SPACE to Start", SmallFont, (255, 220, 0), SW/2 - 90, SH/2 - 10, (0, 0, 0))
        draw_text_with_outline("Press Q to toggle AI/Manual", SmallFont, (200, 255, 200), SW/2 - 115, SH/2 + 20, (0, 0, 0))
        draw_text_with_outline("Press S to Pause/Resume", SmallFont, (200, 255, 200), SW/2 - 95, SH/2 + 50, (0, 0, 0))
        draw_text_with_outline("Press P to Show Plot", SmallFont, (200, 255, 200), SW/2 - 85, SH/2 + 80, (0, 0, 0))
                
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def game_start(generation, x, y):
    global AI_CONTROL, PAUSED
    
    score = 0
    birdxpos = int(SW/5)
    birdypos = int(SH/2)
    basex1 = 0
    basex2 = SW

    bgx1 = 0
    bgx2 = IMAGES['background'].get_width()

    newPipe1 = get_new_pipe()
    newPipe2 = get_new_pipe()

    up_pipes = [
        {'x': SW + 200, 'y': newPipe1[0]['y']},
        {'x': SW + 500, 'y': newPipe2[0]['y']}
    ]

    bttm_pipes = [
        {'x': SW + 200, 'y': newPipe1[1]['y']},
        {'x': SW + 500, 'y': newPipe2[1]['y']}
    ]

    pipeVelx = -4

    birdyvel = -9
    birdymaxvel = 10
    birdyvelmin = -8
    birdyacc = 1

    playerFlapAccv = -8
    playerFlapped = False
    
    # For showing the mini graph during gameplay
    if len(x) > 1:
        mini_graph = draw_progress_graph(x, y)
    else:
        mini_graph = None
    
    while True:
        jump = False
        x_prev, y_prev = convert(birdxpos, birdypos, bttm_pipes)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                plt.figure(figsize=(10, 6))
                plt.scatter(x, y, c='blue', alpha=0.7)
                plt.plot(x, y, 'r-', alpha=0.5)
                plt.xlabel("GENERATION/Number of Trials")
                plt.ylabel("SCORE")
                plt.title("Flappy Birds: AI Learning Progress")
                plt.grid(True, linestyle='--', alpha=0.7)
                plt.savefig("learning_progress.png")
                plt.show()
                pygame.quit()
                sys.exit()
            
            elif event.type == KEYDOWN:
                if event.key == K_q:
                    # Toggle between AI and manual control
                    AI_CONTROL = not AI_CONTROL
                
                elif event.key == K_s:
                    # Toggle pause state
                    PAUSED = not PAUSED
                
                elif event.key == K_p:
                    # Show current progress plot
                    show_plot(x, y)
                    
                if not AI_CONTROL and (event.key == K_SPACE or event.key == K_UP):
                    jump = True
                    if birdypos > 0:
                        birdyvel = playerFlapAccv
                        playerFlapped = True
        
        # Skip game update if paused
        if PAUSED:
            # Continue to render the game but don't update game state
            render_game(birdxpos, birdypos, bgx1, bgx2, basex1, basex2, 
                        up_pipes, bttm_pipes, score, generation, mini_graph, birdyvel)
            
            # Draw pause text
            draw_text_with_outline("PAUSED", Font, (255, 50, 50), SW/2 - 50, SH/2 - 20)
            draw_text_with_outline("Press 'S' to Resume", SmallFont, (255, 255, 255), SW/2 - 85, SH/2 + 20)
            
            pygame.display.update()
            FPSCLOCK.tick(FPS)
            continue
        
        # AI control logic
        if AI_CONTROL:
            jump = ai_play(x_prev, y_prev)
            
            if jump:
                if birdypos > 0:
                    birdyvel = playerFlapAccv
                    playerFlapped = True
        
        # Score logic
        playerMidPos = birdxpos + IMAGES['bird'].get_width()/2
        for pipe in up_pipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width()/2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1

        # Bird movement physics
        if birdyvel < birdymaxvel and not playerFlapped:
            birdyvel += birdyacc

        if playerFlapped:
            playerFlapped = False

        playerHeight = IMAGES['bird'].get_height()
        birdypos = birdypos + min(birdyvel, BASEY - birdypos - playerHeight)

        # Pipe movement
        for upperPipe, lowerPipe in zip(up_pipes, bttm_pipes):
            upperPipe['x'] += pipeVelx
            lowerPipe['x'] += pipeVelx

        # Add new pipes
        if 0 < up_pipes[0]['x'] < 5:
            newPipe = get_new_pipe()
            up_pipes.append(newPipe[0])
            bttm_pipes.append(newPipe[1])

        # Remove pipes that are off screen
        if up_pipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            up_pipes.pop(0)
            bttm_pipes.pop(0)

        # Base and background movement (parallax effect)
        basex1 -= 4
        basex2 -= 4
        if basex1 <= -IMAGES['base'].get_width():
            basex1 = basex2
            basex2 = basex1 + IMAGES['base'].get_width()

        bgx1 -= 1
        bgx2 -= 1
        if bgx1 <= -IMAGES['background'].get_width():
            bgx1 = bgx2
            bgx2 = bgx1 + IMAGES['background'].get_width()

        # Collision detection
        crashTest = Collision(birdxpos, birdypos, up_pipes, bttm_pipes)
        x_new, y_new = convert(birdxpos, birdypos, bttm_pipes)
        
        if crashTest:
            if AI_CONTROL:
                reward = -1000
                Q_update(x_prev, y_prev, jump, reward, x_new, y_new)
            return score

        # Update Q values if AI is in control
        if AI_CONTROL:
            reward = 15
            Q_update(x_prev, y_prev, jump, reward, x_new, y_new)

        # Render game (extracted to a function to avoid code duplication)
        render_game(birdxpos, birdypos, bgx1, bgx2, basex1, basex2, 
                    up_pipes, bttm_pipes, score, generation, mini_graph, birdyvel)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def render_game(birdxpos, birdypos, bgx1, bgx2, basex1, basex2, up_pipes, bttm_pipes, score, generation, mini_graph, birdyvel):
    """Render all game elements without updating game state"""
    global AI_CONTROL
    
    # First fill the entire screen with background color to prevent black bars
    WINDOW.fill((135, 206, 235))  # Sky blue color
    
    # Draw background - ensure it covers entire width
    WINDOW.blit(IMAGES['background'], (bgx1, 0))
    WINDOW.blit(IMAGES['background'], (bgx2, 0))
    
    # Draw pipes
    for upperPipe, lowerPipe in zip(up_pipes, bttm_pipes):
        # Draw the pipes
        WINDOW.blit(IMAGES['pipe'][0], (upperPipe['x'], upperPipe['y']))
        WINDOW.blit(IMAGES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))
    
    # Draw base - ensure it covers the entire width
    WINDOW.blit(IMAGES['base'], (basex1, BASEY))
    WINDOW.blit(IMAGES['base'], (basex2, BASEY))
    
    # Draw bird with rotation based on velocity
    bird_angle = max(-90, min(25, -birdyvel * 3))  # Limit rotation angles
    rotated_bird = pygame.transform.rotate(IMAGES['bird'], bird_angle)
    WINDOW.blit(rotated_bird, (birdxpos, birdypos))
    
    # Draw score and generation info with outline for better visibility
    draw_text_with_outline(f"Gen: {generation}", Font, (255, 255, 255), 10, 10)
    draw_text_with_outline(f"Score: {score}", Font, (255, 255, 255), SW - 150, 10)
    
    # Display control mode
    mode_text = "AI Control" if AI_CONTROL else "Manual Control"
    mode_color = (100, 255, 100) if AI_CONTROL else (255, 200, 100)
    draw_text_with_outline(mode_text, SmallFont, mode_color, SW//2 - 50, 10)
    
    # Show key controls
    draw_text_with_outline("S: Pause  P: Plot", SmallFont, (255, 255, 200), SW//2 - 60, SH - 30)
    
    # Show mini graph if available
    if mini_graph and len(x) > 5:
        mini_graph_size = (150, 100)
        resized_graph = pygame.transform.scale(mini_graph, mini_graph_size)
        WINDOW.blit(resized_graph, (10, SH - 120))

def Collision(birdxpos, birdypos, up_pipes, bttm_pipes):
    if birdypos >= BASEY - IMAGES['bird'].get_height() or birdypos < 0:
        return True
        
    for pipe in up_pipes:
        pipeHeight = IMAGES['pipe'][0].get_height()
        if birdypos < pipeHeight + pipe['y'] and abs(birdxpos - pipe['x']) < IMAGES['pipe'][0].get_width():
            return True

    for pipe in bttm_pipes:
        if birdypos + IMAGES['bird'].get_height() > pipe['y'] and abs(birdxpos - pipe['x']) < IMAGES['pipe'][0].get_width():
            return True
            
    return False

def get_new_pipe():
    pipeHeight = IMAGES['pipe'][1].get_height()
    gap = int(SH/4)
    y2 = int(gap + random.randrange(0, int(SH - IMAGES['base'].get_height() - 1.2*gap)))
    pipex = int(SW + 300)
    y1 = int(pipeHeight - y2 + gap)

    pipe = [
        {'x': pipex, 'y': -y1},
        {'x': pipex, 'y': y2}
    ]
    return pipe

def ai_play(x, y):
    max_val = 0
    jump = False
    
    if Q[x][y][1] > Q[x][y][0]:
        max_val = Q[x][y][1]
        jump = True

    return jump

def convert(birdxpos, birdypos, bttm_pipes):
    x = min(280, bttm_pipes[0]['x'])
    y = bttm_pipes[0]['y'] - birdypos
    if y < 0:
        y = abs(y) + 408
    return int(x/40 - 1), int(y/40)

def Q_update(x_prev, y_prev, jump, reward, x_new, y_new):
    if jump:
        Q[x_prev][y_prev][1] = 0.4 * Q[x_prev][y_prev][1] + (0.6) * (reward + max(Q[x_new][y_new][0], Q[x_new][y_new][1]))
    else:
        Q[x_prev][y_prev][0] = 0.4 * Q[x_prev][y_prev][0] + (0.6) * (reward + max(Q[x_new][y_new][0], Q[x_new][y_new][1]))

if __name__ == "__main__":
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption("Flappy Bird AI Project")

    # Set the display mode once and ensure it's the correct size
    WINDOW = pygame.display.set_mode((SW, SH))

    # Load and scale images to ensure proper sizing
    try:
        # Load base images
        base_img = pygame.image.load('imgs/base.png').convert_alpha()
        bg_img = pygame.image.load(BG).convert()
        bird_img = pygame.image.load(BIRD).convert_alpha()
        pipe_img = pygame.image.load(PIPE).convert_alpha()
        
        # Scale background to ensure it covers the width
        if bg_img.get_width() < SW:
            bg_img = pygame.transform.scale(bg_img, (SW, bg_img.get_height()))
        
        # Scale base to ensure it covers the width
        if base_img.get_width() < SW:
            base_img = pygame.transform.scale(base_img, (SW, base_img.get_height()))
        
        # Store processed images
        IMAGES['base'] = base_img
        IMAGES['pipe'] = (pygame.transform.rotate(pipe_img, 180), pipe_img)
        IMAGES['background'] = bg_img
        IMAGES['bird'] = bird_img
        
    except pygame.error as e:
        print(f"Error loading game assets: {e}")
        print("Make sure all image files exist in the imgs folder.")
        pygame.quit()
        sys.exit()
    
    generation = 1
    static()  # Show start screen
    
    x = []  # Generation numbers
    y = []  # Scores for each generation
    
    while True:
        score = game_start(generation, x, y)
        if score == -1:
            break
            
        x.append(generation)
        y.append(score)
        
        # Update mini-graph every 5 generations
        if generation % 5 == 0 and len(x) > 5:
            plt.figure(figsize=(6, 4), facecolor='white')
            plt.plot(x, y, 'b-o')
            plt.xlabel("Generation")
            plt.ylabel("Score")
            plt.title(f"Learning Progress (Gen {generation})")
            plt.grid(True)
            plt.savefig("progress.png", bbox_inches='tight')
            plt.close()
        
        generation += 1
    
    print(f"Final generation: {generation}")
    
    # Save final results
    plt.figure(figsize=(10, 6), facecolor='white')
    plt.plot(x, y, 'b-o')
    plt.xlabel("Generation/Number of Trials")
    plt.ylabel("Score")
    plt.title("Flappy Bird AI: Learning Progress")
    plt.grid(True)
    plt.savefig("final_results.png", bbox_inches='tight')
    plt.show()
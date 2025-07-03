import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
BLUE = (100, 150, 255)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
PURPLE = (200, 100, 255)
PINK = (255, 150, 200)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

BUBBLE_COLORS = [RED, BLUE, GREEN, YELLOW, PURPLE, PINK, ORANGE, CYAN]

class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(20, 40)
        self.color = random.choice(BUBBLE_COLORS)
        self.speed = random.uniform(1, 3)
        self.pop_animation = 0
        self.is_popped = False
        
        # Special bubble types
        rand = random.random()
        if rand < 0.05:  # 5% chance
            self.type = "star"
            self.points = 50
            self.color = YELLOW
        elif rand < 0.15:  # 10% chance
            self.type = "heart"
            self.points = 25
            self.color = PINK
        else:
            self.type = "normal"
            self.points = 10
    
    def update(self):
        if not self.is_popped:
            self.y -= self.speed
            # Add floating effect
            self.x += math.sin(self.y * 0.01) * 0.5
        else:
            self.pop_animation += 1
    
    def draw(self, screen):
        if not self.is_popped:
            # Draw bubble
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
            
            # Draw special bubble indicators
            if self.type == "star":
                # Draw star shape
                star_points = []
                for i in range(5):
                    angle = i * 2 * math.pi / 5 - math.pi / 2
                    star_x = self.x + math.cos(angle) * (self.radius * 0.4)
                    star_y = self.y + math.sin(angle) * (self.radius * 0.4)
                    star_points.append((star_x, star_y))
                pygame.draw.polygon(screen, WHITE, star_points)
            
            elif self.type == "heart":
                # Draw heart shape (simplified)
                heart_size = self.radius // 3
                pygame.draw.circle(screen, WHITE, (int(self.x - heart_size//2), int(self.y - heart_size//2)), heart_size//2)
                pygame.draw.circle(screen, WHITE, (int(self.x + heart_size//2), int(self.y - heart_size//2)), heart_size//2)
                pygame.draw.polygon(screen, WHITE, [(self.x, self.y + heart_size//2), 
                                                  (self.x - heart_size, self.y - heart_size//4),
                                                  (self.x + heart_size, self.y - heart_size//4)])
            
            # Add shine effect
            pygame.draw.circle(screen, WHITE, (int(self.x - self.radius//3), int(self.y - self.radius//3)), self.radius//4)
        
        else:
            # Pop animation
            if self.pop_animation < 20:
                explosion_radius = self.radius + self.pop_animation * 2
                alpha = 255 - (self.pop_animation * 12)
                if alpha > 0:
                    # Create surface for transparency
                    pop_surface = pygame.Surface((explosion_radius * 2, explosion_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(pop_surface, (*self.color, alpha), (explosion_radius, explosion_radius), explosion_radius)
                    screen.blit(pop_surface, (self.x - explosion_radius, self.y - explosion_radius))
    
    def is_clicked(self, pos):
        distance = math.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)
        return distance <= self.radius and not self.is_popped
    
    def pop(self):
        self.is_popped = True
        self.pop_animation = 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🎈 Rainbow Bubble Pop!")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        self.reset_game()
    
    def reset_game(self):
        self.bubbles = []
        self.score = 0
        self.lives = 3
        self.level = 1
        self.spawn_timer = 0
        self.game_over = False
        self.game_started = False
        self.background_offset = 0
    
    def spawn_bubble(self):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = SCREEN_HEIGHT + 50
        bubble = Bubble(x, y)
        self.bubbles.append(bubble)
    
    def update(self):
        if not self.game_started or self.game_over:
            return
        
        # Update background
        self.background_offset += 0.5
        if self.background_offset > 50:
            self.background_offset = 0
        
        # Spawn bubbles
        spawn_rate = max(60 - self.level * 5, 20)  # Faster spawning at higher levels
        self.spawn_timer += 1
        if self.spawn_timer >= spawn_rate:
            self.spawn_bubble()
            self.spawn_timer = 0
        
        # Update bubbles
        for bubble in self.bubbles[:]:
            bubble.update()
            
            # Remove bubbles that went off screen
            if bubble.y < -50:
                if not bubble.is_popped:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                self.bubbles.remove(bubble)
            
            # Remove popped bubbles after animation
            elif bubble.is_popped and bubble.pop_animation > 20:
                self.bubbles.remove(bubble)
        
        # Level up
        if self.score >= self.level * 200:
            self.level += 1
    
    def handle_click(self, pos):
        if not self.game_started:
            self.game_started = True
            return
        
        if self.game_over:
            self.reset_game()
            return
        
        # Check if any bubble was clicked
        for bubble in self.bubbles:
            if bubble.is_clicked(pos):
                bubble.pop()
                self.score += bubble.points
                break
    
    def draw_background(self):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(135 + (70 * color_ratio))
            g = int(206 + (49 * color_ratio))
            b = int(235 + (20 * color_ratio))
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Floating particles
        for i in range(20):
            x = (i * 40 + self.background_offset) % SCREEN_WIDTH
            y = (i * 30 + self.background_offset * 0.5) % SCREEN_HEIGHT
            pygame.draw.circle(self.screen, (255, 255, 255, 100), (int(x), int(y)), 2)
    
    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        # Level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 90))
        
        # Game title
        title_text = self.font.render("🎈 Rainbow Bubble Pop!", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 30))
        self.screen.blit(title_text, title_rect)
    
    def draw_start_screen(self):
        # Title
        title_text = self.big_font.render("🎈 Bubble Pop! 🎈", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        instructions = [
            "Click bubbles to pop them!",
            "⭐ Star bubbles = 50 points",
            "💖 Heart bubbles = 25 points",
            "🟢 Normal bubbles = 10 points",
            "Don't let bubbles escape!",
            "",
            "Click anywhere to start!"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30 + i * 30))
            self.screen.blit(text, text_rect)
    
    def draw_game_over(self):
        # Game over text
        game_over_text = self.big_font.render("Game Over!", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(final_score_text, final_score_rect)
        
        # Restart instruction
        restart_text = self.font.render("Click to play again!", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        self.draw_background()
        
        if not self.game_started:
            self.draw_start_screen()
        elif self.game_over:
            self.draw_game_over()
        else:
            # Draw bubbles
            for bubble in self.bubbles:
                bubble.draw(self.screen)
            
            self.draw_ui()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
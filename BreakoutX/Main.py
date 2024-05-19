import cv2
import mediapipe as mp
import pygame
import random

pygame.init()
screenWidth = 800
screenHeight = 600
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
paddleColour = (50, 50, 255)
ballColour = (255, 255, 255)
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Breakout")
font = pygame.font.Font(pygame.font.get_default_font(), 36)

class Brick(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        self.image = pygame.Surface((brickWidth, brickHeight))
        self.image.fill(color)
        pygame.draw.rect(self.image, black, self.image.get_rect(), 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Ball(pygame.sprite.Sprite):
    def __init__(self, color, radius):
        super().__init__()
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        pygame.draw.circle(self.image, black, (radius, radius), radius, 2)
        self.rect = self.image.get_rect()
        self.radius = radius
        self.reset()

    def reset(self):
        self.rect.x = screenWidth // 2
        self.rect.y = screenHeight // 2
        self.speed_x = random.choice([-4, 4])
        self.speed_y = -4

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left <= 0 or self.rect.right >= screenWidth:
            self.speed_x = -self.speed_x
        if self.rect.top <= 0:
            self.speed_y = -self.speed_y

def create_bricks():
    bricks = pygame.sprite.Group()
    for row in range(4):
        for col in range(10):
            color = blue if (row + col) % 2 == 0 else white
            brick = Brick(color, col * (brickWidth + 2), row * (brickHeight + 2))
            bricks.add(brick)
    return bricks

brickWidth = screenWidth // 10
brickHeight = screenHeight // 20
bricks = create_bricks()
ball = Ball(ballColour, 10)
balls = pygame.sprite.Group()
balls.add(ball)
paddle_width = 100
paddle_height = 10
paddle = pygame.Rect((screenWidth - paddle_width) / 2, screenHeight - paddle_height - 10, paddle_width, paddle_height)

def reset_game():
    global bricks, score
    bricks = create_bricks()
    ball.reset()
    paddle.x = (screenWidth - paddle_width) / 2
    score = 0

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

score = 0
gameWin = font.render("YOU WIN. Restarting......", True, white)
gameEnd = gameWin.get_rect(center=(screenWidth / 2, screenHeight / 2))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Reading the image from camera, flipping the image and converting it's bgr colour scheme to rgb
    #Also calling mediapipe's hand tracking process to see the user's hands
    _, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    hand_detected = False
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
            hand_detected = True

#Moving the paddle based on the hand movements
            paddle.x = int(x * screenWidth) - paddle.width // 2
            paddle.x = max(0, min(screenWidth - paddle.width, paddle.x))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

    #Below the ball movement is upated and collision are detected wether to the wall, blocks or paddle
    ball.update()
    if pygame.sprite.spritecollide(ball, bricks, True):
        ball.speed_y = -ball.speed_y
        score += 1
    if ball.rect.colliderect(paddle):
        ball.speed_y = -ball.speed_y
    if ball.rect.bottom >= screenHeight:
        ball.reset()
    screen.fill(black)
    bricks.draw(screen)

    if len(bricks) <= 0:
        screen.blit(gameWin, gameEnd)
        pygame.display.flip()
        pygame.time.wait(6000)
        reset_game()

    pygame.draw.rect(screen, paddleColour, paddle)
    pygame.draw.rect(screen, black, paddle, 2)
    balls.draw(screen)
    score_text = font.render(f"Score: {score}", True, white)
    score_rect = score_text.get_rect(center=(100, screenHeight // 2))
    screen.blit(score_text, score_rect)
    pygame.display.flip()
cap.release()
cv2.destroyAllWindows()
pygame.quit()

import pygame

BLACK = (0, 0, 0)


class Paddle(pygame.sprite.Sprite):

    def __init__(self, width, height, start_x):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Pass in the color of the paddle, its width and height.
        # Set the background color and set it to be transparent
        self.image = pygame.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        # Draw the paddle (a rectangle!)
        pygame.draw.rect(self.image, (255, 255, 255), [0, 0, width, height])

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()
        self.rect.x = start_x

    def move(self, move_y):
        self.rect.y = move_y

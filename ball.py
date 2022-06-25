import pygame


class Ball(pygame.sprite.Sprite):
    # This class represents a ball. It derives from the "Sprite" class in Pygame.

    def __init__(self, pixel_size, start_x, start_y):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # Pass in the color of the ball, its width and height.
        # Set the background color and set it to be transparent
        self.image = pygame.Surface([pixel_size, pixel_size])
        self.image.fill((0, 0, 0))
        self.image.set_colorkey((0, 0, 0))

        # Draw the ball (a rectangle!)
        pygame.draw.rect(self.image, (255, 255, 255), [0, 0, pixel_size, pixel_size])

        # Fetch the rectangle object that has the dimensions of the image.

        self.rect = self.image.get_rect()
        self.rect.x = start_x * pixel_size
        self.rect.y = start_y * pixel_size

    def move(self, ball_x, ball_y):
        self.rect.x = ball_x
        self.rect.y = ball_y

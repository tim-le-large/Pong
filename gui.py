import random

import numpy as np
import pygame

from ball import Ball
from paddle import Paddle

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PIXEL_SIZE = 20
SIZE_X = 30
SIZE_Y = 26
PADDLE_Y = round(SIZE_Y / 5)
PADDLE_X = 0.5
MAX_STATES = [SIZE_Y, SIZE_X, SIZE_Y, 2, 2]


class GUI:

    def __init__(self):
        pygame.init()
        self.curr_ball_x = SIZE_X / 2
        self.curr_ball_y = SIZE_Y / 2
        self.curr_paddle_one_y = SIZE_Y / 2 - PADDLE_Y
        self.curr_paddle_two_y = SIZE_Y / 2 - PADDLE_Y
        self.curr_vel_x = 1
        self.curr_vel_y = 1
        self.episodes = 0
        self.error = 0
        self.training = False
        self.speed = 20
        self.q = {}
        # init board
        self.screen = pygame.display.set_mode([SIZE_X * PIXEL_SIZE, SIZE_Y * PIXEL_SIZE])
        pygame.display.set_caption("Pong")
        self.all_sprites_list = pygame.sprite.Group()
        # init ball
        self.ball = Ball(PIXEL_SIZE, self.curr_ball_x, self.curr_ball_y)
        self.all_sprites_list.add(self.ball)
        # init paddleOne
        self.paddleOne = Paddle(PADDLE_X * PIXEL_SIZE, PADDLE_Y * PIXEL_SIZE, 0)
        self.all_sprites_list.add(self.paddleOne)
        # init paddleTwo
        self.paddleTwo = Paddle(PADDLE_X * PIXEL_SIZE, PADDLE_Y * PIXEL_SIZE, (SIZE_X - PADDLE_X) * PIXEL_SIZE)
        self.all_sprites_list.add(self.paddleTwo)
        # init q table with random numbers or load file
        if self.training:
            for paddle1_y in range(MAX_STATES[0]):
                for ball_x in range(MAX_STATES[1]):
                    for ball_y in range(MAX_STATES[2]):
                        for vel_x in range(MAX_STATES[3]):
                            for vel_y in range(MAX_STATES[4]):

                                state = self.get_state(
                                    [paddle1_y, ball_x, ball_y, vel_x, vel_y])
                                action = {}
                                for move in range(2):
                                    action.update({move: random.uniform(-0.1, 0.1)})

                                self.q.update({state: action})
        else:
            self.q = np.load('brain.npy', allow_pickle=True)[()]

    def run_game(self):
        carry_on = True
        clock = pygame.time.Clock()
        while carry_on:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    carry_on = False

                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_w]:
                    self.curr_paddle_two_y -= 1
                if pressed[pygame.K_s]:
                    self.curr_paddle_two_y += 1

            curr_state = self.observation()
            move_up = self.decision(curr_state)
            self.action(move_up)
            self.reward(curr_state, move_up)
            # clock.tick(self.speed)
        pygame.quit()
        np.save("brain.npy", self.q)

    def get_state(self, states):
        s = states[0]
        for i in range(1, len(states)):
            s = s * MAX_STATES[i] + states[i]
        return s

    def observation(self):
        return self.get_state(
            [self.curr_paddle_one_y, self.curr_ball_x, self.curr_ball_y, self.curr_vel_x, self.curr_vel_y])

    def decision(self, curr_state):
        return self.q[curr_state][0] < self.q[curr_state][1]

    def action(self, move_up):
        # move agent
        self.curr_paddle_one_y += -1 if move_up else 1
        if self.curr_paddle_one_y < 0:
            self.curr_paddle_one_y = 0
        if self.curr_paddle_one_y > SIZE_Y - PADDLE_Y:
            self.curr_paddle_one_y = SIZE_Y - PADDLE_Y
        self.paddleOne.move(self.curr_paddle_one_y * PIXEL_SIZE)
        # move human player
        if self.curr_paddle_two_y < 0:
            self.curr_paddle_two_y = 0
        if self.curr_paddle_two_y > SIZE_Y - PADDLE_Y:
            self.curr_paddle_two_y = SIZE_Y - PADDLE_Y
        self.paddleTwo.move(self.curr_paddle_two_y * PIXEL_SIZE)
        # move ball x
        if self.curr_vel_x == 0:
            self.curr_ball_x -= 1
        else:
            self.curr_ball_x += 1
        # move ball y
        if self.curr_vel_y == 0:
            self.curr_ball_y -= 1
        else:
            self.curr_ball_y += 1
        self.ball.move(self.curr_ball_x * PIXEL_SIZE, self.curr_ball_y * PIXEL_SIZE)
        # Check if the ball is bouncing against any of the 4 walls or the player:
        if self.curr_ball_x == 0:
            self.curr_vel_x = not self.curr_vel_x
        if self.curr_ball_x == SIZE_X - 1:
            self.curr_vel_x = not self.curr_vel_x
        if self.curr_ball_y == 0:
            self.curr_vel_y = not self.curr_vel_y
        if self.curr_ball_y == SIZE_Y - 1:
            self.curr_vel_y = not self.curr_vel_y

        # update screen
        self.screen.fill(BLACK)
        self.all_sprites_list.update()
        self.all_sprites_list.draw(self.screen)
        pygame.display.flip()

    def reward(self, curr_state, move_up):
        reward = 0
        # Check if the ball is bouncing against any of the 4 walls or the player:
        if self.curr_ball_x == 0:
            # if hit the ball
            if pygame.sprite.collide_mask(self.ball, self.paddleOne):
                reward = 1
                self.ball.image.fill((0, 255, 0))
            else:
                reward = -1
                self.ball.image.fill((255, 0, 0))
                self.error += 1
            # visualize
            self.episodes += 1
            if self.episodes % 100 == 0:
                print("Error: ", self.error, "%")
                self.error = 0
        elif self.curr_ball_x == SIZE_X - 1:
            if pygame.sprite.collide_mask(self.ball, self.paddleTwo):
                self.ball.image.fill((0, 255, 0))
            else:
                self.ball.image.fill((255, 0, 0))

        # learn
        next_state = self.get_state(
            [self.curr_paddle_one_y, self.curr_ball_x, self.curr_ball_y, self.curr_vel_x, self.curr_vel_y])
        max_next_state = max([self.q[next_state][0], self.q[next_state][1]])
        q_curr_state = self.q[curr_state][move_up]
        self.q[curr_state][move_up] = q_curr_state + 0.1 * (reward + 0.9 * max_next_state - q_curr_state)

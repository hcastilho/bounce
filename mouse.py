
import pygame
import sys

screen=pygame.display.set_mode((200,200))

while True:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN: print event.button
        if event.type == pygame.QUIT: sys.exit()

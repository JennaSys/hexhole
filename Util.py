#!/usr/bin/env python
"""Mostly crappy miscellaneous functions"""

__author__ = "John Sheehan"
__email__ = "jennasys@yahoo.com"
__version__ = "1.0.0"
__date__ = "Mar-06-2013"


import pygame

def getFraction(value, denominator):
    whole_num = int(value)
    remainder = value - int(value)

    numerator = int(((remainder * denominator) + 0.5) * 10) / 10

    while numerator % 2 == 0 and numerator != 0:
        numerator = numerator / 2
        denominator = denominator / 2

    if numerator == 0:
        return "{0}".format(whole_num)
    elif whole_num != 0:
        return "{0}-{1}/{2}".format(whole_num, numerator, denominator)
    else:
        return "{0}/{1}".format(numerator, denominator)



def inputbox(screen, label, value, pos, size, bg_color, fg_color):

    # font = pygame.font.SysFont(pygame.font.get_default_font(), int(screen.get_size()[0] * 0.025))
    font = pygame.font.SysFont("Arial", int(screen.get_size()[0] * 0.02))

    lbl = font.render(label, True, fg_color)
    lbl_rect = lbl.get_rect()

    rect = pygame.Rect([0, 0, size - lbl_rect.width, int(screen.get_size()[0] * 0.025)])
    offset = (3, 1)

    rect.left = pos[0] + lbl_rect.width
    rect.top = pos[1]

    pygame.draw.rect(screen, bg_color, rect, 0)
    pygame.draw.rect(screen, (128,128,128), rect, 1)

    rect.left += offset[0]
    rect.top  += offset[1]

    if len(label) != 0:
        screen.blit(lbl, pos)
    if len(value) != 0:
        screen.blit(font.render(value, True, fg_color), rect.topleft)



if __name__=="__main__":
    num = 1.0
    while num != 0:
        num = input("Enter number:")
        if num != 0:
            print(getFraction(num, 64))



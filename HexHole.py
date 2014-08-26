#!/usr/bin/env python
"""Calculate and visualize parameters for dilled hex holes"""

__author__ = "John Sheehan"
__email__ = "jennasys@yahoo.com"
__version__ = "1.1.1"
__date__ = "Mar-12-2013"


import math
import pygame
import logging

import Util


class HexHole:
    """Object for calculating hex drill

       init pre-calculates some of the geometry

    """

    corners = 6
    side_angle = 360 / corners

    drill_increment = 1.0/64.0
    min_wall = 0

    def __init__(self, hex_size, hole_size, hole2_size=0.0):
        self.hex_size = hex_size
        self.drill_size = hole_size
        self.drill2_size = max(0,hole2_size)
        self.center_to_flat = self.hex_size / 2
        self.center_to_corner = self.center_to_flat / math.cos(math.radians(self.side_angle / 2))
        self.corner_to_corner = self.center_to_corner * 2
        self.flat_length = 2 * (self.center_to_flat * math.tan(math.radians(self.side_angle / 2)))  # == center_to_corner

        self.status = ""

        if self.center_to_corner - self.center_to_flat >= self.drill_size:
            if self.drill_size > 0.0:  # Assume starting point for best fit algorithm
                self.status = "Drill size {0:.4f} is too small and will be set to the minimum allowed: {1:.4f}".format(self.drill_size, self.center_to_corner - self.center_to_flat + 0.0001)
            self.drill_size = self.center_to_corner - self.center_to_flat + 0.0001
        elif self.drill_size >= self.center_to_corner:
            self.status = "Drill size {0:.4f} is too large and will be set to the maximum allowed: {1:.4f}".format(self.drill_size, self.center_to_corner - 0.0001)
            self.drill_size = self.center_to_corner - 0.0001

        self.drill_radius = self.drill_size / 2
        self.drill2_radius = self.drill2_size / 2
        self.center_to_drill = self.center_to_corner - self.drill_radius

        # self.min_wall = self.drill_size * 0.05



    def drill_location(self, corner):
        x_offset = self.center_to_drill * math.cos(math.radians((corner - 1) * self.side_angle))
        y_offset = self.center_to_drill * math.sin(math.radians((corner - 1) * self.side_angle))
        return x_offset, y_offset


    def drill_locations(self):
        corner_list = []
        for corner in range(HexHole.corners):
            corner_list.append(self.drill_location(corner + 1))
        return corner_list


    def corner_locations(self):
        corner_list = []
        for corner in range(HexHole.corners):
            x_offset = self.center_to_corner * math.cos(math.radians(corner * self.side_angle))
            y_offset = self.center_to_corner * math.sin(math.radians(corner * self.side_angle))
            corner_list.append((x_offset, y_offset))
        return corner_list


    def drill2_angle(self):
        H = self.drill_radius * math.sin(math.radians(self.side_angle))
        B = self.drill_radius * math.cos(math.radians(self.side_angle))
        h = H - self.drill2_radius
        C = self.drill_radius + self.drill2_radius + self.min_wall
        L = ((C**2 - h**2)**0.5) + ((h / H) * B)

        x = self.center_to_flat - self.drill2_radius
        z = ((x / self.center_to_flat) * (self.flat_length / 2)) - L

        return (self.side_angle / 2) - math.degrees(math.atan(z / x))


    def drill2_distance(self):
        H = self.drill_radius * math.sin(math.radians(self.side_angle))
        B = self.drill_radius * math.cos(math.radians(self.side_angle))
        h = H - self.drill2_radius
        C = self.drill_radius + self.drill2_radius + self.min_wall
        L = ((C**2 - h**2)**0.5) + ((h / H) * B)

        x = self.center_to_flat - self.drill2_radius
        z = ((x / self.center_to_flat) * (self.flat_length / 2)) - L

        return (z**2 + x**2)**0.5


    def drill2_location(self, corner):
        x1_offset = self.drill2_distance() * math.cos(math.radians(((corner - 1) * self.side_angle) + self.drill2_angle()))
        y1_offset = self.drill2_distance() * math.sin(math.radians(((corner - 1) * self.side_angle) + self.drill2_angle()))
        x2_offset = self.drill2_distance() * math.cos(math.radians(((corner - 1) * self.side_angle) - self.drill2_angle()))
        y2_offset = self.drill2_distance() * math.sin(math.radians(((corner - 1) * self.side_angle) - self.drill2_angle()))
        return (x1_offset, y1_offset), (x2_offset, y2_offset)


    def drill2_locations(self):
        corner_list = []
        for corner in range(HexHole.corners):
            loc = self.drill2_location(corner + 1)
            corner_list.append(loc[0])
            corner_list.append(loc[1])
        return corner_list


    def drill2_area(self):
        """ calculates the area of the hex that is removed by the small drill holes """

        if self.drill2_radius == 0:
            return 0
        elif (self.drill2_distance() - self.drill2_radius) > self.center_to_flat:
            # doesn't intersect with large hole so just return full drill area
            return (math.pi * self.drill2_radius**2) * 2
        else:
            center_to_drill2 = self.drill2_distance()

            # calc intersecting angle using law of cos:  A=acos((R^2 + d^2 - r^2)/ 2Rd)
            intersecting_angle_large = math.acos((self.center_to_flat**2 + center_to_drill2**2 - self.drill2_radius**2) / (2 * self.center_to_flat * center_to_drill2))
            # given angle, calc intersecting chord:  c=2(R*sin(A))
            intersecting_chord = 2 * self.center_to_flat * math.sin(intersecting_angle_large)
            # given angle, calc large segment:  area=(2A - sin(2A)) * R^2) / 2
            large_segment_area = (((2 * intersecting_angle_large) - math.sin(2 * intersecting_angle_large)) * (self.center_to_flat**2)) / 2
            # given chord, calc small angle: a = asin((c/2) / r)
            intersecting_angle_small = math.asin((intersecting_chord/2) / self.drill2_radius)
            # given small angle, calc small segment:  ((2a - sin(2a)) * r^2) / 2
            small_segment_area = (((2 * intersecting_angle_small) - math.sin(2 * intersecting_angle_small)) * (self.drill2_radius**2)) / 2

            return (small_segment_area - large_segment_area) * 2


    def overdrill_area(self):
        """ calculates area of drilled hole that is outside of the hex area """
        circle_segment_area = ((self.drill_radius**2) / 2) * (math.radians(self.side_angle) - math.sin(math.radians(self.side_angle))) * 2
        return circle_segment_area * HexHole.corners


    def flat(self):
        """ calculates length of flat """
        return (self.center_to_flat * math.tan(math.radians(self.side_angle / 2))) * 2


    def flat_available(self):
        """ calculates available length of flat """
        return self.flat() - (self.drill_size *  math.sin(math.radians(self.side_angle / 2)) * 2)

    def underdrill_area(self):
        """ calculates the area of the hex that is not removed with the drilled holes """

        # TODO: fix area calculations

        # calc intersecting angle using law of cos:  A=acos((R^2 + d^2 - r^2)/ 2Rd)
        intersecting_angle_large = math.acos((self.center_to_flat**2 + self.center_to_drill**2 - self.drill_radius**2) / (2 * self.center_to_flat * self.center_to_drill))
        # given angle, calc intersecting chord:  c=2(R*sin(A))
        intersecting_chord = 2 * self.center_to_flat * math.sin(intersecting_angle_large)
        # given angle, calc large segment:  area=(2A - sin(2A)) * R^2) / 2
        large_segment_area = (((2 * intersecting_angle_large) - math.sin(2 * intersecting_angle_large)) * (self.center_to_flat**2)) / 2
        # given chord, calc small angle: a = asin((c/2) / r)
        intersecting_angle_small = math.asin((intersecting_chord/2) / self.drill_radius)
        # given small angle, calc small segment:  ((2a - sin(2a)) * r^2) / 2
        small_segment_area = (((2 * intersecting_angle_small) - math.sin(2 * intersecting_angle_small)) * (self.drill_radius**2)) / 2

        # calc included hex triangle: ab/2 * 2
        hex_area = ((self.flat_length / 2 ) * self.center_to_flat)
        # subtract 60deg large segment: (pi r^2)/6
        drill_area = ((self.center_to_flat**2) * math.pi) / HexHole.corners
        # subtract area defined by:
        corner_area = small_segment_area - large_segment_area - (self.overdrill_area() / HexHole.corners)
        # small segment - large segment - overdrill_area
        underdrill_area = hex_area - drill_area - corner_area - self.drill2_area()

        return underdrill_area * HexHole.corners


    def render(self, x_screen, y_screen):

        pygame.init()

        screen = pygame.display.set_mode((x_screen, y_screen))
        pygame.display.set_caption("Drilled Hex Hole Calculator - Version: {0}".format(__version__))
        screen.fill(HexDisplay.WHITE)

        hex_display = HexDisplay(screen, self)
        input_text = ""
        self.status = ""
        mask_on = False

        # Draw initial display
        hex_display.draw(mask_on, input_text)

        # Draw the screen and process user input
        while True:
            pygame.time.wait(50)
            event = pygame.event.poll()
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mask_on = not mask_on
                elif event.key == pygame.K_UP:
                    self.__init__(self.hex_size, (self.drill_size + HexHole.drill_increment) - (self.drill_size % HexHole.drill_increment), self.drill2_size)
                    hex_display.__init__(screen, self)
                elif event.key == pygame.K_DOWN:
                    self.__init__(self.hex_size, (self.drill_size - HexHole.drill_increment) - (self.drill_size % HexHole.drill_increment), self.drill2_size)
                    hex_display.__init__(screen, self)
                elif event.key == pygame.K_RIGHT:
                    self.__init__(self.hex_size, self.drill_size, (self.drill2_size + HexHole.drill_increment) - (self.drill2_size % HexHole.drill_increment))
                    hex_display.__init__(screen, self)
                    # logging.info("drill2 angle: {0:.2f}   radius: {1:.4f}".format(self.drill2_angle(), self.drill2_distance()))
                    logging.info("drill2 area: {0:.4f}   removed: {1:.4f}".format(2 * self.drill2_radius**2 * math.pi, self.drill2_area()))
                elif event.key == pygame.K_LEFT:
                    self.__init__(self.hex_size, self.drill_size, (self.drill2_size - HexHole.drill_increment) - (self.drill2_size % HexHole.drill_increment))
                    hex_display.__init__(screen, self)
                    # logging.info("drill2 angle: {0:.2f}   radius: {1:.4f}".format(self.drill2_angle(), self.drill2_distance()))
                    logging.info("drill2 area: {0:.4f}   removed: {1:.4f}".format(2 * self.drill2_radius**2 * math.pi, self.drill2_area()))
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[0:-1]
                elif event.key == pygame.K_RETURN:
                    try:
                        if float(input_text) != self.hex_size:
                            self.__init__(float(input_text), self.drill_size, self.drill2_size)
                            hex_display.__init__(screen, self)
                    except:
                        if len(input_text) > 0:
                            self.status = "Input text '" + input_text + "' is not a valid number!"
                    finally:
                        input_text = ""
                else:
                    input_text += event.unicode.encode("ascii")

                hex_display.draw(mask_on, input_text)
                self.status = ""

            pygame.display.flip()



class HexDisplay:

    # Color list
    TRANSPARENT = (255,0,255)
    RED = (255,0,0)
    GREEN = (0,255,0)
    DARKGREEN = (0,128,0)
    BLUE = (0,0,255)
    DARKBLUE = (0,0,128)
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    PINK = (255,200,200)
    YELLOW = (255, 255, 0)

    def __init__(self, screen, hexhole):
        self.screen = screen
        self.hexhole = hexhole

        self.x_screen = screen.get_size()[0]
        self.y_screen = screen.get_size()[1]
        self.border = int(self.x_screen * 0.025)
        self.x_center = int(self.x_screen / 2)
        self.y_center = int(self.y_screen / 2)
        self.scale_factor = (self.y_screen / self.hexhole.corner_to_corner) / 1.1
        self.center_mark = int(self.x_screen * 0.015)

        self.background = pygame.Surface(screen.get_size())
        self.background.fill(HexDisplay.WHITE)
        self.mask = pygame.Surface(screen.get_size())
        self.mask.fill(HexDisplay.TRANSPARENT)
        self.mask.set_colorkey(HexDisplay.TRANSPARENT)
        self.overlay = pygame.Surface(screen.get_size())
        self.overlay.fill(HexDisplay.TRANSPARENT)
        self.overlay.set_colorkey(HexDisplay.TRANSPARENT)
        self.info = pygame.Surface(screen.get_size())
        self.info.fill(HexDisplay.TRANSPARENT)
        self.info.set_colorkey(HexDisplay.TRANSPARENT)

        # Draw desired hex
        self.hex_points = [(int(x * self.scale_factor) + self.x_center, int(y * self.scale_factor) + self.y_center) for x, y in self.hexhole.corner_locations()]
        pygame.draw.polygon(self.background, HexDisplay.BLACK, self.hex_points, 0)

        # Draw main hole
        pygame.draw.circle(self.background, HexDisplay.WHITE, (self.x_center, self.y_center), int(hexhole.center_to_flat * self.scale_factor), 0)
        pygame.draw.circle(self.background, HexDisplay.RED, (self.x_center, self.y_center), int(hexhole.center_to_flat * self.scale_factor), 1)
        pygame.draw.line(self.background, HexDisplay.RED, (self.x_center - self.center_mark, self.y_center), (self.x_center + self.center_mark, self.y_center), 1)
        pygame.draw.line(self.background, HexDisplay.RED, (self.x_center, self.y_center - self.center_mark), (self.x_center, self.y_center + self.center_mark), 1)

        # Draw corner holes
        self.drill_points = [(int(x * self.scale_factor) + self.x_center, int(-y * self.scale_factor) + self.y_center) for x, y in hexhole.drill_locations()]
        self.drill2_points = [(int(x * self.scale_factor) + self.x_center, int(-y * self.scale_factor) + self.y_center) for x, y in hexhole.drill2_locations()]
        for pos in range(hexhole.corners):
            pygame.draw.circle(self.mask, HexDisplay.WHITE, (self.drill_points[pos][0],self.drill_points[pos][1]), int(hexhole.drill_radius * self.scale_factor), 0)
            pygame.draw.circle(self.mask, HexDisplay.BLUE, (self.drill_points[pos][0],self.drill_points[pos][1]), int(hexhole.drill_radius * self.scale_factor), 1)
            pygame.draw.circle(self.overlay, HexDisplay.BLUE, (self.drill_points[pos][0],self.drill_points[pos][1]), int(hexhole.drill_radius * self.scale_factor), 0)
            pygame.draw.circle(self.overlay, HexDisplay.BLUE, (self.drill_points[pos][0],self.drill_points[pos][1]), int(hexhole.drill_radius * self.scale_factor), 1)
            pygame.draw.circle(self.background, HexDisplay.WHITE, (self.drill_points[pos][0],self.drill_points[pos][1]), int(hexhole.drill_radius * self.scale_factor), 0)
            pygame.draw.circle(self.background, HexDisplay.BLUE, (self.drill_points[pos][0],self.drill_points[pos][1]), int(hexhole.drill_radius * self.scale_factor), 1)
            pygame.draw.line(self.background, HexDisplay.BLUE, (self.drill_points[pos][0] - self.center_mark, self.drill_points[pos][1]), (self.drill_points[pos][0] + self.center_mark, self.drill_points[pos][1]), 1)
            pygame.draw.line(self.background, HexDisplay.BLUE, (self.drill_points[pos][0], self.drill_points[pos][1] - self.center_mark), (self.drill_points[pos][0], self.drill_points[pos][1] + self.center_mark), 1)

        #Overlays
        pygame.draw.polygon(self.overlay, HexDisplay.TRANSPARENT, self.hex_points, 0)
        # pygame.draw.polygon(mask, HexDisplay.RED, hex_points, 1)
        pygame.draw.polygon(self.overlay, HexDisplay.BLACK, self.hex_points, 1)
        pygame.draw.circle(self.mask, HexDisplay.WHITE, (self.x_center, self.y_center), int(hexhole.center_to_flat * self.scale_factor), 0)

        tmp_color = HexDisplay.RED
        for pos in range(hexhole.corners * 2):
            if hexhole.drill2_radius > 0:
                pygame.draw.circle(self.background, tmp_color, (self.drill2_points[pos][0],self.drill2_points[pos][1]), int(hexhole.drill2_radius * self.scale_factor), 1)
                tmp_color = HexDisplay.BLUE

        #Text
        # f_Info = pygame.font.SysFont(pygame.font.get_default_font(), int(self.x_screen * 0.025))
        # f_InfoI = pygame.font.SysFont(pygame.font.get_default_font(), int(self.x_screen * 0.025), italic=True)
        f_Info = pygame.font.SysFont("Arial", int(self.x_screen * 0.02))
        f_InfoI = pygame.font.SysFont("Arial", int(self.x_screen * 0.015), italic=True)
        self.lblHexSize = f_Info.render("Hex Size: {0:.4f}".format(hexhole.hex_size), True, HexDisplay.DARKBLUE)
        self.lblHoleSize = f_Info.render("Corner Hole Size: {0:.4f}  ({1})".format(hexhole.drill_size, Util.getFraction(hexhole.drill_size, int(1 / HexHole.drill_increment))), True, HexDisplay.DARKBLUE)
        self.lblHole2Size = f_Info.render("Small Hole Size: {0:.4f}  ({1})".format(hexhole.drill2_size, Util.getFraction(hexhole.drill2_size, int(1 / HexHole.drill_increment))), True, HexDisplay.DARKBLUE)

        self.lblInstructionsHex = f_InfoI.render("Type a number and press [ Enter ] to change the hex size", True, HexDisplay.DARKGREEN)
        self.lblInstructionsHexRect = self.lblInstructionsHex.get_rect()
        self.lblInstructionsHexRect.right = self.x_screen - self.border
        self.lblInstructionsHexRect.top = self.border
        self.lblInstructionsSize = f_InfoI.render("Press Up/Down arrows to change corner drill size", True, HexDisplay.DARKGREEN)
        self.lblInstructionsSizeRect = self.lblInstructionsSize.get_rect()
        self.lblInstructionsSizeRect.right = self.x_screen - self.border
        self.lblInstructionsSizeRect.top = self.border * 2
        self.lblInstructionsSize2 = f_InfoI.render("Press Left/Right arrows to change small drill size", True, HexDisplay.DARKGREEN)
        self.lblInstructionsSize2Rect = self.lblInstructionsSize.get_rect()
        self.lblInstructionsSize2Rect.right = self.x_screen - self.border
        self.lblInstructionsSize2Rect.top = self.border * 3
        self.lblInstructionsMask = f_InfoI.render("Press [ space bar ] to toggle overlay", True, HexDisplay.DARKGREEN)
        self.lblInstructionsMaskRect = self.lblInstructionsMask.get_rect()
        self.lblInstructionsMaskRect.right = self.x_screen - self.border
        self.lblInstructionsMaskRect.top = self.border * 4

        overdrill = hexhole.overdrill_area()
        underdrill = hexhole.underdrill_area()
        self.lblOverDrill = f_Info.render("Over drill area: {0:.6f}".format(overdrill), True, HexDisplay.DARKBLUE)
        self.lblUnderDrill = f_Info.render("Under drill area: {0:.6f}".format(underdrill), True, HexDisplay.DARKBLUE)
        self.lblRatio = f_Info.render("Ratio: {0:.3f}".format(overdrill / underdrill), True, HexDisplay.DARKBLUE)

        flat = hexhole.flat()
        flat_avail = hexhole.flat_available()
        self.lblFlat = f_Info.render("Flat Length: {0:.3f}   ({1:.1%})".format(flat_avail, flat_avail / flat), True, HexDisplay.DARKBLUE)
        self.lblFlatRect = self.lblFlat.get_rect()
        self.lblFlatRect.centerx = self.screen.get_rect().centerx
        self.lblFlatRect.top = self.y_screen - (self.border * 2)

        self.lblCorners = []
        self.lblCornersTag = []
        for idx, hole in enumerate(hexhole.drill_locations()):
            self.lblCorners.append(f_Info.render("Corner {0}: X={1:.4f}  Y={2:.4f}".format(idx + 1, hole[0], hole[1]), True, HexDisplay.DARKBLUE))
            self.lblCornersTag.append(f_Info.render("{0}".format(idx + 1), True, HexDisplay.DARKBLUE))


    def draw(self, mask_on, input_text):
        # pygame.display.update()
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.overlay, (0, 0))

        self.screen.blit(self.lblHexSize, (self.border, self.border))
        Util.inputbox(self.screen, "New Size: ", input_text, (self.border, self.border * 2), int(self.x_screen * 0.14), HexDisplay.YELLOW, HexDisplay.DARKBLUE)

        self.screen.blit(self.lblHoleSize, (self.border, self.border * 3))
        self.screen.blit(self.lblHole2Size, (self.border, self.border * 4))
        self.screen.blit(self.lblInstructionsSize, self.lblInstructionsSizeRect)
        self.screen.blit(self.lblInstructionsSize2, self.lblInstructionsSize2Rect)
        self.screen.blit(self.lblInstructionsHex, self.lblInstructionsHexRect)
        self.screen.blit(self.lblInstructionsMask, self.lblInstructionsMaskRect)
        self.screen.blit(self.lblOverDrill, (self.x_screen - int(self.x_screen * 0.25), self.y_screen - (self.border * 4)))
        self.screen.blit(self.lblUnderDrill, (self.x_screen - int(self.x_screen * 0.25), self.y_screen - (self.border * 3)))
        self.screen.blit(self.lblRatio, (self.x_screen - int(self.x_screen * 0.25), self.y_screen - (self.border * 2)))
        self.screen.blit(self.lblFlat, self.lblFlatRect)

        for pos in range(self.hexhole.corners):
            self.screen.blit(self.lblCorners[pos], (self.border, self.y_screen - (self.border * self.hexhole.corners) - self.border + (self.border * pos)))
            self.screen.blit(self.lblCornersTag[pos], (self.drill_points[pos][0] + int(self.center_mark / 2), self.drill_points[pos][1] + int(self.center_mark / 2)))

        if mask_on:
            self.screen.blit(self.mask, (0, 0))

        if len(self.hexhole.status) > 0:
            status_text = pygame.font.SysFont("Arial", int(self.x_screen * 0.018)).render(self.hexhole.status, True, HexDisplay.RED)
            status_rect = status_text.get_rect()
            status_rect.centerx = self.screen.get_rect().centerx
            status_rect.top = self.y_screen - self.border
            self.screen.blit(status_text, status_rect)
            logging.warning(self.hexhole.status)
            # print self.hexhole.status





if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)#, filename='HexHole.log')
    hex = 0.5
    ratio = 1.0
    inc = 1.0/64.0
    drill = 0.0
    oda = 0
    uda = 1

    while oda / uda < ratio:
        hole = HexHole(hex, drill)
        oda = hole.overdrill_area()
        uda = hole.underdrill_area()
        drill = (hole.drill_size + inc) - ((hole.drill_size + inc) % inc)

    locations = hole.drill_locations()

    logging.info("Calculating initial best fit...")
    for pos in range(HexHole.corners):
        logging.info("Corner {0}: X={1:.4f}  Y={2:.4f}".format(pos + 1, locations[pos][0], locations[pos][1]))

    logging.info("Over drill area: {0:.6f}".format(oda))
    logging.info("Under drill area: {0:.6f}".format(uda))
    logging.info("Ratio: {0:.3f}".format(oda / uda))

    # hole.render(640, 480)
    # hole.render(800, 600)
    hole.render(1024, 768)
    # hole.render(1280, 1024)
import math
import copy
import pygame
import random
import sys
from pygame.locals import *
from random import random

# Graphic
# def rot_center(image, rect, angle):
#         """rotate an image while keeping its center"""
#         rot_image = pygame.transform.rotate(image, angle)
#         rot_rect = rot_image.get_rect(center=rect.center)
#         return rot_image,rot_rect

def wrap(x, min, max):
	return (x - min) % (max - min) + min

def rot_sprite(self):
	a = self.sprite
	orig_center = a.rect.center  # Save original center of sprite.
	# Rotate using the original image.
	# print(self.ang)
	a.image = pygame.transform.rotate(a.orig_image, math.degrees(self.ang+math.pi/2))
	a.image.convert_alpha()
	a.image.set_colorkey((0, 0, 0))
	# Get the new rect and set its center to the original center.
	a.rect = a.image.get_rect(center=orig_center)
	self.rendered = a.image

def draw_polygon(arr, col, size=1):
    pygame.draw.lines(surface, col, True, arr, size)


def center_array(arr):
    i = []
    for p in range(len(arr)):
        c = 0
        i.append([0, 0])
        for v in range(len(arr[p])):
            i[p][v] = arr[p][v]+screen.mid[c]
            c += 1
    return i


def scale_array(arr, mag):
    i = []
    for p in range(len(arr)):
        c = 0
        i.append([0, 0])
        for v in range(len(arr[p])):
            i[p][v] = arr[p][v]*mag
            c += 1
    return i


def translate_array(arr, vec):
    i = []
    for p in range(len(arr)):
        c = 0
        i.append([0, 0])
        for v in range(len(arr[p])):
            i[p][v] = arr[p][v]+vec[c]
            c += 1
    return i


def generate_rect(x, y, width, height):  # x,y is center
    return [
        [x-width/2, y-height/2],
        [x+width/2, y-height/2],
        [x+width/2, y+height/2],
        [x-width/2, y+height/2],
    ]


# Sprite
class spritesheet():
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert()
        self.sprite_sheet.set_colorkey((0, 0, 0))

    def get_sprite(self, rect):
        sprite = pygame.Surface((rect[2], rect[3]))
        sprite.set_colorkey((0, 0, 0))
        sprite.blit(self.sprite_sheet, (0, 0), rect)
        return sprite


# def rot_sprite(image, angle, x, y):
#     rotated_image = pygame.transform.rotate(image, math.degrees(angle))
#     new_rect = rotated_image.get_rect(
#         center=image.get_rect(center=(x, y)).center)
#     return rotated_image, new_rect


# Trigonometric
def rotate(p, rv):
    Rx = [[1, 0, 0], [0, math.cos(rv[0]), -math.sin(rv[0])],
          [0, math.sin(rv[0]), math.cos(rv[0])]]
    Ry = [[math.cos(rv[1]), 0, math.sin(rv[1])], [0, 1, 0],
          [-math.sin(rv[1]), 0, math.cos(rv[1])]]
    Rz = [[math.cos(rv[2]), -math.sin(rv[2]), 0],
          [math.sin(rv[2]), math.cos(rv[2]), 0], [0, 0, 1]]
    rm = multiplyMatrix(multiplyMatrix(Rx, Ry), Rz)
    j = []
    for i in range(len(p)):
        j.append(copy.copy(p[i]))
    for i in range(len(j)):
        j[i][0] = rm[0][0]*p[i][0]+rm[0][1]*p[i][1]+rm[0][2]*p[i][2]
        j[i][1] = rm[1][0]*p[i][0]+rm[1][1]*p[i][1]+rm[1][2]*p[i][2]
        j[i][2] = rm[2][0]*p[i][0]+rm[2][1]*p[i][1]+rm[2][2]*p[i][2]
    return j


def rot(cloud, theta):
    i = []
    for j in cloud:
        i.append([
            j[0]*math.cos(theta)-j[1]*math.sin(theta),
            j[1]*math.cos(theta)+j[0]*math.sin(theta)
        ])
    return i


def multiplyMatrix(m1, m2):
    res = []
    for i in range(len(m1)):
        res.append([])
        for j in range(len(m2[1])):
            res[i].append(0)
            for k in range(len(m2)):
                res[i][j] = res[i][j]+m1[i][k]*m2[k][j]
    return res


# Converts cartesian coordinates to polar [X, Y] -> [Radius, Angle].
def car2pol(coordinate_list):
    x = coordinate_list[0]
    y = coordinate_list[1]
    return [(x**2+y**2)**0.5, math.atan2(y, x)]


# Converts polar coordinates to cartesian [Radius, Angle] -> [X, Y].
def pol2car(coordinate_list):
    r = coordinate_list[0]
    a = coordinate_list[1]
    return [r*math.cos(a), r*math.sin(a)]


# Converts cartesian to spherical coordinates [X, Y, Z] -> [Radius, Inclination, Azimuth].
def car2sph(coor):
    x = coor[0]
    y = coor[1]
    z = coor[2]
    radius = math.sqrt(math.pow(x, 2)+math.pow(y, 2)+math.pow(z, 2))
    inclination = math.acos(z/radius)
    azimuth = math.atan2(y, x)
    return [radius, inclination, azimuth]


# Converts spherical coordinates to cartesian [Radius, Inclination, Azimuth] -> [X, Y, Z].
def sph2car(coor):
    i = [coor[0]*math.cos(coor[1]), coor[0]*math.sin(coor[1])]
    z = i[1]
    i = [coor[0]*math.cos(coor[2]), coor[0]*math.sin(coor[2])]
    return [i[0], i[1], z]


def dist(i, j):
    if len(i) > 2:
        return ((i[0]-j[0])**2+(i[1]-j[1])**2+(i[2]-j[2])**2)**0.5
    else:
        return ((i[0]-j[0])**2+(i[1]-j[1])**2)**0.5


def vect(i, j):
    if len(i) > 2:
        return [i[0]-j[0], i[1]-j[1], i[2]-j[2]]
    else:
        return [i[0]-j[0], i[1]-j[1]]


def isPointInPolygon(point, polygon):
    x = point[0]
    y = point[1]
    n = len(polygon)
    c = False
    j = n-1
    for i in range(n):
        if ((polygon[i][1] > y) != (polygon[j][1] > y)) and (x < (polygon[j][0]-polygon[i][0])*(y-polygon[i][1])/(polygon[j][1]-polygon[i][1])+polygon[i][0]):
            c = not c
        j = i
    return c


def getNormalv(f):  # Get normal vector of face
    f = f.nodes
    a = vect(f[1], f[0])
    b = vect(f[2], f[0])
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]


def magnitude(coor, n):
    a = math.atan2(coor[1], coor[0])
    return [n*math.cos(a), n*math.sin(a)]


def bound(p):  # Bounds a point and returns "did/did not bound"
    a = [0, 0]
    did = False
    a[0] = max(0, min(screen.res[0], p[0]))
    a[1] = max(0, min(screen.res[1], p[1]))
    if p != a:
        did = True
    return a, did

def box_collision(box1, box2):
    if box1[0] < box2[0] + box2[2] and box1[0] + box1[2] > box2[0]:
        if box1[1] < box2[1] + box2[3] and box1[1] + box1[3] > box2[1]:
            return True
    return False

def lineCircleIntersect(a, b, c, r):
    dx, dy, A, B, C, det, t, x, y = None, None, None, None, None, None, None, None, None
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    A = dx * dx + dy * dy
    B = 2 * (dx * (a[0] - c[0]) + dy * (a[1] - c[1]))
    C = (a[0] - c[0]) * (a[0] - c[0]) + (a[1] - c[1]) * (a[1] - c[1]) - r * r
    det = B * B - 4 * A * C
    if det < 0:
        return False
    t = (-B - math.sqrt(det)) / (2 * A)
    if t < 0 or t > 1:
        return False
    x = a[0] + t * dx
    y = a[1] + t * dy
    return [x, y]



# Hardware


class screen():
    # res = [400,400]
    #res = [1920,1080]
    fps = 60
    ticks = 0
    scale = 1
    lastscale = 0
    alpha = 100
    font = []

    def init(res):
        global surface
        screen.res = res
        screen.mid = [res[0]/2, res[1]/2]
        #surface = pygame.display.set_mode((screen.res[0], screen.res[1]), pygame.FULLSCREEN)
        surface = pygame.display.set_mode((screen.res[0], screen.res[1]))
        pygame.init()
        screen.clock = pygame.time.Clock()
        # pygame.mouse.set_visible(False)
        screen.alpha_layer = pygame.Surface(screen.res)
        screen.alpha_layer.fill([0,0,0])
        for i in range(40):
            screen.font.append(pygame.font.SysFont('consolas', i))
        return surface

    def flipBuffer():
        pygame.display.flip()
        # win.blit(GUI.gameobject, GUI.backgroundRect)
        surface.fill((0, 0, 0))
        screen.clock.tick(screen.fps)
        screen.ticks += 1
        screen.lastscale = screen.scale

    def close():
        pygame.quit()

    def update():
        screen.alpha_layer.set_alpha(int(screen.alpha))
        surface.blit(screen.alpha_layer, [0,0])
        pygame.display.update()

def dtext(surface, s, coor, color, size = 24):
    text = screen.font[size].render(s, True, color)
    rect = text.get_rect()
    rect.center = coor
    surface.blit(text, rect)

class control():
    def __init__(self):
        self.key = None
        self.mus = [0, 0]
        self.spes = False
        self.pressclick = False
        self.doneclick = False
        self.reset()

        self.lastkey = None

    def controlque(self):
        self.reset()
        self.getMus()
        self.getKey()
        # self.system()

    def reset(self):
        self.state = {
            "ws":0,
            "ad":0,
            "space":False,
            "r":False,
            "enter":False,
            "e":False,
        }

    def getMus(self):
        self.doneclick = False
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # if event.type == MOUSEBUTTONDOWN:
            # 	surface.fill((255, 255, 255))
        self.lastmus = copy.copy(self.mus)
        self.mus = [pygame.mouse.get_pos(), pygame.mouse.get_pressed()]
        if self.mus[1][0] and not self.pressclick:
            self.pressclick = True
        if self.pressclick and not self.mus[1][0]:
            self.pressclick = False
            self.doneclick = True

    def getKey(self):
        self.lastkey = self.key
        self.key = pygame.key.get_pressed()
        if self.key[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if self.key[pygame.K_w]:
            self.state["ws"] = 1
        if self.key[pygame.K_s]:
            self.state["ws"] = -1
        if self.key[pygame.K_a]:
            self.state["ad"] = -1
        if self.key[pygame.K_d]:
            self.state["ad"] = 1
        if self.key[pygame.K_SPACE] and not self.lastkey[pygame.K_SPACE]:
            self.state["space"] = True
        if self.key[pygame.K_RETURN] and not self.lastkey[pygame.K_RETURN]: # Enter button
            self.state["enter"] = True
        if self.key[pygame.K_r]:
            self.state["r"] = True
        if self.key[pygame.K_e]:
            self.state["e"] = True


        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # screen.lastscale = screen.scale
                # Scroll
                if event.button == 4:
                    screen.scale = min(screen.scale + 0.15, 100)
                if event.button == 5:
                    screen.scale = max(screen.scale - 0.15, 0.001)
                

class camera():
    def __init__(self):
        self.pos = [0,0]
        self.offset = [0,0]
        self.fov = 1

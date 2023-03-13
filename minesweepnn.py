import gh, pygame, math, copy, random, time
import nn_test as nn
from pprint import pprint as pp
from random import randrange as rng
def rfloat(): return 2*(random.random()-0.5)

size = 25
root = 5
syn = [root**2,50,100,root**2]

def isrec(x,y,r):
	return x > r[0] and y > r[1] and x < r[0]+r[2] and y < r[1]+r[3]

class cell():
    def __init__(self, index):
        self.boteval = 0
        self.val = 0
        self.index = [
            index[0]*size,
            index[1]*size,
        ]
        self.mid = [
            self.index[0]+size/2,
            self.index[1]+size/2,
        ]
        self.bomb = False
        self.dug = False
        self.tag = False
        self.rect = [
            self.index[0]+1,
            self.index[1]+1,
            size-2,
            size-2
        ]
        
    def draw(self):
        pygame.draw.rect(surface, [0,0,0], [self.index[0], self.index[1], size, size])
        if self.tag:
            self.color = [255,255,0]
        else:
            self.color = [255,255,255]
        if self.dug:
            self.color = [220,250,220]
        if self.bomb and self.dug:
            self.color = [255,0,0]
        pygame.draw.rect(surface, self.color, self.rect)
        if self.dug and not self.bomb and self.val>0:
            i = max(0, min(255, (255/4)*self.val))
            gh.dtext(surface, str(self.val), self.mid, [i,0,0])
        if self.bomb and self.dug:
            pygame.draw.circle(surface, [0,0,0], self.mid, size/2-1)

    def dig(self):
        if self.dug or self.tag:
            return
        self.dug = True
        if self.val == 0:
            for x_off, y_off in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
                x_neighbour, y_neighbour = self.index[0]//size + x_off, self.index[1]//size + y_off
                if (0 <= x_neighbour < root) and (0 <= y_neighbour < root):
                    map[x_neighbour][y_neighbour].dig()

def genmap():
    test = True
    while test:
        map = []
        for x in range(root):
            row = []
            for y in range(root):
                c = cell([x,y])
                if rng(0,6) >= 5:
                    c.bomb = True
                    test = False
                row.append(c)
            map.append(row)

        for x, row in enumerate(map):
            for y, c in enumerate(row):
                for x_off, y_off in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
                    x_neighbour, y_neighbour = x+x_off, y+y_off
                    if (0 <= x_neighbour < root) and (0 <= y_neighbour < root):
                        if map[x_neighbour][y_neighbour].bomb:
                            c.val += 1
    return map

map = genmap()
bot = nn.NeuralNetwork(syn).load("msbot.nn")
bot.fitness = 0
dead = []
# for i in range(3):
#     dead.append(nn.NeuralNetwork(syn))

game = False
surface = gh.screen.init([root*size,root*size])
control = gh.control()
t = 0
runs = -1
draw=not False
win = False
best = 0
while True:
    if not game:
        t=0
        # bot.fitness = 0
        for x in map:
            for y in x:
                if y.dug and not y.bomb:
                    bot.fitness+=1
                if y.bomb and y.tag:
                    bot.fitness+=1
        if runs > 1:
            if bot.fitness > best:
                bot.save("msbot.nn")
                best = copy.copy(bot.fitness)

            runs = 0
            dead.append(bot)
            dead = sorted(dead, key=lambda x: x.fitness, reverse=True)
            dead = dead[0:10]
            # if rng(0,11)==10: dead = dead[0:2]
            print([x.fitness for x in dead])
            for i in dead[1:999]:
                i.fitness -= 0.1
            # best -= 0.1
            # print(sum(x.fitness for x in dead)/len(dead))
            # print(dead[0].fitness)
            if rng(0,2)>0:
                bot = nn.NeuralNetwork(syn)
            else:
                if rng(0,2)>0 and len(dead)>=2:
                    bot = nn.NeuralNetwork(syn, dead[rng(0,len(dead))], dead[rng(0,len(dead))])
                else:
                    bot = nn.NeuralNetwork(syn, dead[rng(0,len(dead))])
                    bot.tweak(0.1)




            bot.fitness = 0
        map = genmap()
        game = True
        runs+=1
    if t > 30:
        game = False
        t=0
    if game:
        control.controlque()

        if control.state["space"]:
            draw = not draw

        l_click = control.mus[1][0] and not l_press
        l_press = control.mus[1][0]

        r_click = control.mus[1][2] and not r_press
        r_press = control.mus[1][2]

        flatmap = []
        for row in map:
            for c in row:
                if c.dug:
                    i = c.val
                else:
                    if c.tag:
                        i = -1
                    else:
                        i = -2
                flatmap.append(i)

                if isrec(control.mus[0][0],control.mus[0][1],c.rect):
                    if l_click:
                        c.dig()
                    if r_click and not c.dug:
                        c.tag = not c.tag
                if draw: c.draw()
                if c.bomb and c.dug:
                    game = False

        get = nn.run(bot.genome, syn, flatmap)
        targ = map[0][0]
        flag = map[0][0]
        win = True
        for x in map:
            for y in x:
                if not y.dug and not y.bomb:
                    win = False
                if y.bomb and not y.tag:
                    win = False

                y.boteval=get[0]
                get=get[1:9999]
                if y.boteval > targ.boteval and y.boteval > 0:
                    if not y.dug and not y.tag:
                        targ = y
                if y.boteval < flag.boteval and y.boteval < 0:
                    if not y.dug:
                        flag = y
                # if y.dug:
                #     bot.fitness+=1

        if targ.boteval > 0: targ.dig()
        if flag.boteval < 0: flag.tag = not flag.tag
        # if targ.bomb:
        #     bot.fitness = bot.fitness / 2
        if win:
            bot.fitness += 10
            print("Won!")
            game=False
        if not win and not game:
            bot.fitness-=10
        if draw:
            pygame.draw.rect(surface, [max(155, targ.boteval*255),155,155], targ.rect)
            gh.screen.flipBuffer()
            # time.sleep(0.5)
        t+=1
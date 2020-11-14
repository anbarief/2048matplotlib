import random

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation

power_of_2 = [0, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
color = {0: (0,0,0,0), 2: (0, 0.5, 0, 0.5), 4: (0, 0.5, 0, 1), 8: (0, 1, 0, 0.5), \
         16: (0, 1, 0, 1), 32: (0, 0, 0.5, 0.5), 64: (0, 0, 0.5, 1), 128: (0, 0, 1, 0.5), \
         256: (0, 0, 1, 1), 512: (0.75, 0, 0, 0.5), 1024: (0.75, 0, 0, 1), 2048: (1, 0, 0, 1)}


class CellObject(object):
    def __init__(self, row, col, value, fig, axes):
        self.row = row
        self.col = col
        self.value = value
        self.center = self.col-0.5, self.row-0.5
        self.fig = fig; self.axes = axes
        self.start()
        self.plot()

    def start(self):
        if self.value == 0:
            self.ec = (0,0,0, 0.1)
            self.text_color = (0,0,0,0)
        else:
            self.ec = (0,0,0, 1)
            self.text_color = (1,1,1,1)

        self.fc = color[self.value]
        self.center  = self.col, self.row
        self.rect = Rectangle([self.col-0.5, self.row-0.5], \
                              1, 1, linewidth = 2, \
                              fc = self.fc,
                              ec = self.ec)
        self.text = self.axes.text(*self.center, str(self.value), \
                              color = self.text_color, \
                              ha = 'center', va = 'center', fontweight='bold')
        
    def update(self, draw=True):
        if self.value == 0:
            self.ec = (0,0,0,0.1)
            self.text_color = (0,0,0,0)
        else:
            self.ec = (0,0,0,1)
            self.text_color = (1,1,1,1)

        self.fc = color[min(2048, self.value)]
        self.rect.set_fc(self.fc);
        self.rect.set_ec(self.ec)
        self.text.set_text(str(self.value))
        self.text.set_color(self.text_color)
        
        if draw:
            self.axes.figure.canvas.draw()
            
    def plot(self):
        self.axes.add_patch(self.rect)
        self.axes.figure.canvas.draw()


class App2048(object):
    def __init__(self, n):
        if (n not in (4, 5, 6, 7, 8)):
            return None
        self.fig, self.axes = plt.subplots()
        self.n = n
        self.axes.axis('scaled')

        self.axes.set_xlim([0, n+1])
        self.axes.set_ylim([0, n+1])

        cells = []
        for i in range(1,n+1):
            row_cells = []
            for j in range(1, n+1):
                cell = CellObject(i, j, 0, \
                                  self.fig, self.axes)
                row_cells.append(cell)
            cells.append(row_cells)

        loc1 = random.randint(0, n - 1), random.randint(0, n - 1)
        loc2 = random.randint(0, n - 1), random.randint(0, n - 1)
        while loc2 == loc1:
            loc2 = random.randint(0, n - 1), random.randint(0, n - 1)
            
        cells[loc1[0]][loc1[1]].value = 2; cells[loc1[0]][loc1[1]].update()
        cells[loc2[0]][loc2[1]].value = 2; cells[loc2[0]][loc2[1]].update()

        self.cells = cells
        self.cells_2 = []
        for row in self.cells:
            self.cells_2.extend(row)
        
        self.press = False
        self.path = []

        self.connect()
        self.updating = False

        plt.show()

    @property
    def values(self):
        return [cell.value for cell in self.cells_2]
        
    def on_press(self, event):
        point = (event.xdata, event.ydata)
        if (None not in point) and (not self.updating):
            self.press = True
            self.path.append(point)

    def on_motion(self, event):
        if self.press:
            point = (event.xdata, event.ydata)
            if None not in point:
                self.path.append(point)
            else:
                self.press = False
                self.path.clear()
                return None

            dx=self.path[-1][0] - self.path[0][0]
            dy=self.path[-1][1] - self.path[0][1]

            if dx > 0.5:
                x_direction = 'right'
            elif dx < -0.5:
                x_direction = 'left'
            else:
                x_direction = None

            if dy > 0.5:
                y_direction = 'up'
            elif dy < -0.5:
                y_direction = 'down'
            else:
                y_direction = None

            if abs(dy) > abs(dx):
                direction = y_direction
            elif abs(dy) < abs(dx):
                direction = x_direction
            else:
                direction = None

            if direction != None:

                self.press = False
                self.updating = True
                
                self.path.clear()

                previous_values = self.values

                if direction == 'down':
                    self.go_down()
                elif direction == 'up':
                    self.go_up()
                elif direction == 'left':
                    self.go_left()
                elif direction == 'right':
                    self.go_right()
        
                if self.changed(previous_values):
                    self.add_new_value()
                
                self.solved_or_lost()
            
                plt.pause(0.25)
                self.updating = False
 
    def solved_or_lost(self):
        values = self.values
        if 2048 in values:
            for i in range(10):
                self.axes.set_title('Solved!!', color='blue'); self.fig.canvas.draw()
            return True
        elif 0 not in values:
            if self.solvable():
                return False
            print('not solvable')
            for i in range(10):
                self.axes.set_title('Lost!!', color='red'); self.fig.canvas.draw()
            return True
        return False

    def changed(self, previous_values):
        values = self.values
        for i in range(self.n**2):
            if previous_values[i] != values[i]:
                return True
        return False

    def solvable(self):
        for i in range(self.n):
            for j in range(self.n):
                if i+1 <= self.n-1:
                    if self.cells[i][j].value == self.cells[i+1][j].value:
                        return True 
                if i-1 >= 0:
                    if self.cells[i][j].value == self.cells[i-1][j].value:
                        return True
                if j+1 <= self.n-1:
                    if self.cells[i][j].value == self.cells[i][j+1].value:
                        return True
                if j-1 >= 0:
                    if self.cells[i][j].value == self.cells[i][j-1].value:
                        return True
        return False
                                                                    
    def on_release(self, event):
        self.press = False
        self.path.clear()

    def add_new_value(self):
        new_value = random.sample([2,2,2,2,2,2,2,4,4,4], 1)[0]
        cell = random.sample([i for i in self.cells_2 if i.value == 0], 1)[0]
        cell.value = new_value
        cell.update()
        
    def go_down(self):
        for k in range(self.n-1):
            for j in range(self.n):
                for i in range(self.n-1):
                    if self.cells[i][j].value == 0:
                        if self.cells[i+1][j].value != 0:
                            self.cells[i][j].value = self.cells[i+1][j].value
                            self.cells[i+1][j].value = 0
                            self.cells[i][j].update(draw=False); self.cells[i+1][j].update(draw=False)
        self.fig.canvas.draw()
        
        for j in range(self.n):
            for i in range(self.n-1):
                if self.cells[i][j].value != 0:
                    if self.cells[i+1][j].value == self.cells[i][j].value:
                        self.cells[i][j].value = 2*self.cells[i+1][j].value
                        self.cells[i+1][j].value = 0
                        self.cells[i][j].update(draw=False); self.cells[i+1][j].update(draw=False)

        self.fig.canvas.draw()
        for j in range(self.n):
                for i in range(self.n-1):
                    if self.cells[i][j].value == 0:
                        if self.cells[i+1][j].value != 0:
                            self.cells[i][j].value = self.cells[i+1][j].value
                            self.cells[i+1][j].value = 0
                            self.cells[i][j].update(draw=False); self.cells[i+1][j].update(draw=False)
        self.fig.canvas.draw()
                    
    def go_up(self):
        for k in range(self.n-1):
            for j in range(self.n):
                for i in range(self.n-1):
                    if self.cells[self.n-1-i][j].value == 0:
                        if self.cells[self.n-1-i-1][j].value != 0:
                            self.cells[self.n-1-i][j].value = self.cells[self.n-1-i-1][j].value
                            self.cells[self.n-1-i-1][j].value = 0
                            self.cells[self.n-1-i][j].update(draw=False); self.cells[self.n-1-i-1][j].update(draw=False)
        self.fig.canvas.draw()

        for j in range(self.n):
                for i in range(self.n-1):
                    if self.cells[self.n-1-i][j].value != 0:
                        if self.cells[self.n-1-i-1][j].value == self.cells[self.n-1-i][j].value:
                            self.cells[self.n-1-i][j].value = 2*self.cells[self.n-1-i-1][j].value
                            self.cells[self.n-1-i-1][j].value = 0
                            self.cells[self.n-1-i][j].update(draw=False); self.cells[self.n-1-i-1][j].update(draw=False)
        self.fig.canvas.draw()

        for j in range(self.n):
                for i in range(self.n-1):
                    if self.cells[self.n-1-i][j].value == 0:
                        if self.cells[self.n-1-i-1][j].value != 0:
                            self.cells[self.n-1-i][j].value = self.cells[self.n-1-i-1][j].value
                            self.cells[self.n-1-i-1][j].value = 0
                            self.cells[self.n-1-i][j].update(draw=False); self.cells[self.n-1-i-1][j].update(draw=False)
        self.fig.canvas.draw()

    def go_right(self):
        for k in range(self.n-1):
            for i in range(self.n):
                for j in range(self.n-1):
                    if self.cells[i][self.n-1-j].value == 0:
                        if self.cells[i][self.n-1-j-1].value != 0:
                            self.cells[i][self.n-1-j].value = self.cells[i][self.n-1-j-1].value
                            self.cells[i][self.n-1-j-1].value = 0
                            self.cells[i][self.n-1-j].update(draw=False); self.cells[i][self.n-1-j-1].update(draw=False)
        self.fig.canvas.draw()

        for i in range(self.n):
            for j in range(self.n-1):
                if self.cells[i][self.n-1-j].value != 0:
                    if self.cells[i][self.n-1-j-1].value == self.cells[i][self.n-1-j].value:
                        self.cells[i][self.n-1-j].value = 2*self.cells[i][self.n-1-j-1].value
                        self.cells[i][self.n-1-j-1].value = 0
                        self.cells[i][self.n-1-j].update(draw=False); self.cells[i][self.n-1-j-1].update(draw=False)
        self.fig.canvas.draw()

        for i in range(self.n):
            for j in range(self.n-1):
                if self.cells[i][self.n-1-j].value == 0:
                    if self.cells[i][self.n-1-j-1].value != 0:
                        self.cells[i][self.n-1-j].value = self.cells[i][self.n-1-j-1].value
                        self.cells[i][self.n-1-j-1].value = 0
                        self.cells[i][self.n-1-j].update(draw=False); self.cells[i][self.n-1-j-1].update(draw=False)
        self.fig.canvas.draw()

    def go_left(self):
        for k in range(self.n-1):
            for i in range(self.n):
                for j in range(self.n-1):
                    if self.cells[i][j].value == 0:
                        if self.cells[i][j+1].value != 0:
                           self.cells[i][j].value = self.cells[i][j+1].value
                           self.cells[i][j+1].value = 0
                           self.cells[i][j].update(draw=False); self.cells[i][j+1].update(draw=False)
        self.fig.canvas.draw()

        for i in range(self.n):
            for j in range(self.n-1):
                if self.cells[i][j].value != 0:
                    if self.cells[i][j+1].value == self.cells[i][j].value:
                        self.cells[i][j].value = 2*self.cells[i][j+1].value
                        self.cells[i][j+1].value = 0
                        self.cells[i][j].update(draw=False); self.cells[i][j+1].update(draw=False)
        self.fig.canvas.draw()

        for i in range(self.n):
            for j in range(self.n-1):
                if self.cells[i][j].value == 0:
                    if self.cells[i][j+1].value != 0:
                        self.cells[i][j].value = self.cells[i][j+1].value
                        self.cells[i][j+1].value = 0
                        self.cells[i][j].update(draw=False); self.cells[i][j+1].update(draw=False)
        self.fig.canvas.draw()
             
    def connect(self):
        self.button_press = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.buttone_release = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.motion_notify = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

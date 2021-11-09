import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import matplotlib.animation as animation
import numpy as np

class Sim:
    def __init__(self, callback):
        self.callback = callback

        self.X_DISTANCE = 500 # m
        self.Y_DISTANCE = 1
        self.INTERVAL = 100
        self.SCALE_FACTOR = 10

        self.CAR_WIDTH = 4
        self.CAR_HEIGHT = 2 / (self.X_DISTANCE / self.Y_DISTANCE)
        self.CAR_VELOCITY_M_S = 60 * 1000 / 3600 # km/h => m/s

        self.TX_LIGHT_X = self.X_DISTANCE * 0.5
        self.TX_LIGHT_WIDTH = 1
        self.TX_LIGHT_HEIGHT = 4 / (self.X_DISTANCE / self.Y_DISTANCE)
        self.TX_LIGHT_YELLOW_BEGIN_FRAME = 10
        self.TX_LIGHT_RED_BEGIN_FRAME = 15
        self.TX_LIGHT_GREEN_BEGIN_FRAME = 30

        gs = gridspec.GridSpec(8, 8)
        self.fig = plt.figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(gs[:, :])

        self.car_x = 0
        self.car_v = self.CAR_VELOCITY_M_S
        self.car_x_on_red = 0
        self.TX_LIGHT_state = 'green'

        _ani = animation.FuncAnimation(self.fig, self.drawFrame, frames = range(0, 40), interval = self.INTERVAL, repeat = True, blit = False)
        plt.show()

    def resetStates(self):
        self.callback.__init__()
        self.car_x = 0
        self.car_x_on_red = 0
        self.car_v = self.CAR_VELOCITY_M_S
        self.car_to_stop = False
        self.TX_LIGHT_state = 'green'

    def drawFrame(self, frame): # assume 1 frame equals to 1 second
        if (frame == 0):
            self.resetStates()

        self.ax.clear()
        self.ax.set_xlim([0, self.X_DISTANCE])
        self.ax.set_ylim([0, self.Y_DISTANCE])

        # plot traffic light
        self.ax.add_patch(patches.Rectangle((self.TX_LIGHT_X, 0), 2, 1))

        if (frame < self.TX_LIGHT_YELLOW_BEGIN_FRAME):
            self.TX_LIGHT_state = 'green'
        elif (self.TX_LIGHT_state == 'green' and frame >= self.TX_LIGHT_YELLOW_BEGIN_FRAME and frame < self.TX_LIGHT_RED_BEGIN_FRAME):
            self.TX_LIGHT_state = 'yellow'
            (self.car_to_stop, self.car_x_on_red) = self.callback.onYellowLightOn(self.TX_LIGHT_X, self.TX_LIGHT_RED_BEGIN_FRAME - self.TX_LIGHT_YELLOW_BEGIN_FRAME)
        elif (frame >= self.TX_LIGHT_RED_BEGIN_FRAME and frame < self.TX_LIGHT_GREEN_BEGIN_FRAME):
            self.TX_LIGHT_state = 'red'
        elif (frame >= self.TX_LIGHT_GREEN_BEGIN_FRAME):
            self.TX_LIGHT_state = 'green'
            self.car_v = self.CAR_VELOCITY_M_S
            self.car_to_stop = False

        self.ax.add_patch(
            patches.Rectangle(
                (self.TX_LIGHT_X, (self.Y_DISTANCE - self.TX_LIGHT_HEIGHT * self.SCALE_FACTOR) / 2),
                self.TX_LIGHT_WIDTH * self.SCALE_FACTOR,
                self.TX_LIGHT_HEIGHT * self.SCALE_FACTOR,
                facecolor = self.TX_LIGHT_state,
                fill = True
            )
        )

        # plot car: go or stop at traffic light
        self.car_v += (np.random.rand(1)[0] - 0.5) * 10 * 0.3
        self.car_x += self.car_v

        if (self.car_to_stop and self.car_x >= self.TX_LIGHT_X - self.CAR_WIDTH * self.SCALE_FACTOR):
            self.car_x = self.TX_LIGHT_X - self.CAR_WIDTH * self.SCALE_FACTOR

        self.car_y = (self.Y_DISTANCE - self.CAR_HEIGHT * self.SCALE_FACTOR) / 2
        self.ax.add_patch(patches.Rectangle((self.car_x, self.car_y), self.CAR_WIDTH * self.SCALE_FACTOR, self.CAR_HEIGHT * self.SCALE_FACTOR))

        # plot predicted car
        yellow_light_duration = self.TX_LIGHT_RED_BEGIN_FRAME - self.TX_LIGHT_YELLOW_BEGIN_FRAME
        (predict_x) = self.callback.predict(1, yellow_light_duration)
        self.callback.update(x = self.car_x)

        pred_car = patches.Rectangle(
            (predict_x, self.car_y),
            self.CAR_WIDTH * self.SCALE_FACTOR,
            self.CAR_HEIGHT * self.SCALE_FACTOR,
            fill = False
        )
        pred_car.set_linestyle('--')
        self.ax.add_patch(pred_car)

        if (self.TX_LIGHT_state != 'green'):
            pred_car = patches.Rectangle(
                (self.car_x_on_red, self.car_y),
                self.CAR_WIDTH * self.SCALE_FACTOR,
                self.CAR_HEIGHT * self.SCALE_FACTOR,
                fill = False
            )
            pred_car.set_linestyle('--')
            self.ax.add_patch(pred_car)

            if (self.car_to_stop):
                self.ax.add_patch(patches.Rectangle((self.car_x_on_red, 0), 2, 1, facecolor = 'red'))
            else:
                self.ax.add_patch(patches.Rectangle((self.car_x_on_red, 0), 2, 1, facecolor = 'green'))

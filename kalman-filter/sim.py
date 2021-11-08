import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import matplotlib.animation as animation
import numpy as np

class Sim:
    def __init__(self, callback):
        self.callback = callback

        self.FIG_SIZE = [6, 6]
        self.X_DISTANCE = 500 # m
        self.Y_DISTANCE = 1
        self.INTERVAL = 50

        self.CAR_WIDTH = 4
        self.CAR_HEIGHT = 2 / (self.X_DISTANCE / self.Y_DISTANCE)
        self.CAR_SCALE_FACTOR = 10
        self.CAR_VELOCITY_M_S = 65 * 1000 / 3600 # km/h => m/s

        self.TRAFFIC_LIGHT_X = self.X_DISTANCE * 0.75
        self.TRAFFIC_LIGHT_WIDTH = 1
        self.TRAFFIC_LIGHT_HEIGHT = 4 / (self.X_DISTANCE / self.Y_DISTANCE)
        self.TRAFFIC_LIGHT_SCALE_FACTOR = 10
        self.TRAFFIC_LIGHT_YELLOW_BEGIN_FRAME = 16
        self.TRAFFIC_LIGHT_RED_BEGIN_FRAME = 20
        self.TRAFFIC_LIGHT_GREEN_BEGIN_FRAME = 28

        gs = gridspec.GridSpec(8, 8)
        self.fig = plt.figure(figsize=(self.FIG_SIZE[0], self.FIG_SIZE[1]))
        self.ax = self.fig.add_subplot(gs[:, :])

        self.car_x = 0
        self.car_v = self.CAR_VELOCITY_M_S
        self.car_x_on_red = 0
        self.traffic_light_state = 'green'

        _ani = animation.FuncAnimation(self.fig, self.drawFrame, frames=range(0, 40), interval = self.INTERVAL, repeat=True, blit=False)
        plt.show()

    def resetStates(self):
        self.callback.__init__()
        self.car_x = 0
        self.car_x_on_red = 0
        self.car_v = self.CAR_VELOCITY_M_S
        self.car_to_stop = False
        self.traffic_light_state = 'green'

    def drawFrame(self, frame): # assume 1 frame equals to 1 second

        if (frame == 0):
            self.resetStates()

        self.ax.clear()
        self.ax.set_xlim([0, self.X_DISTANCE])
        self.ax.set_ylim([0, self.Y_DISTANCE])

        # plot traffic light
        if (frame < self.TRAFFIC_LIGHT_YELLOW_BEGIN_FRAME):
            self.traffic_light_state = 'green'
        elif (self.traffic_light_state == 'green' and frame >= self.TRAFFIC_LIGHT_YELLOW_BEGIN_FRAME and frame < self.TRAFFIC_LIGHT_RED_BEGIN_FRAME):
            self.traffic_light_state = 'yellow'
            (self.car_to_stop, self.car_x_on_red) = self.callback.onYellowLightOn(self.TRAFFIC_LIGHT_X, self.TRAFFIC_LIGHT_RED_BEGIN_FRAME - self.TRAFFIC_LIGHT_YELLOW_BEGIN_FRAME)
        elif (frame >= self.TRAFFIC_LIGHT_RED_BEGIN_FRAME and frame < self.TRAFFIC_LIGHT_GREEN_BEGIN_FRAME):
            self.traffic_light_state = 'red'
        elif (frame >= self.TRAFFIC_LIGHT_GREEN_BEGIN_FRAME):
            self.traffic_light_state = 'green'
            self.car_v = self.CAR_VELOCITY_M_S
            self.car_to_stop = False

        self.ax.add_patch(
            patches.Rectangle(
                (self.TRAFFIC_LIGHT_X, (self.Y_DISTANCE - self.TRAFFIC_LIGHT_HEIGHT * self.TRAFFIC_LIGHT_SCALE_FACTOR) / 2),
                self.TRAFFIC_LIGHT_WIDTH * self.TRAFFIC_LIGHT_SCALE_FACTOR,
                self.TRAFFIC_LIGHT_HEIGHT * self.TRAFFIC_LIGHT_SCALE_FACTOR,
                facecolor = self.traffic_light_state,
                fill = True
            )
        )

        # plot roads
        self.ax.add_patch(patches.Rectangle((self.TRAFFIC_LIGHT_X, 0), 2, 1))

        # plot car
        self.car_v += (np.random.rand(1)[0] - 0.5) * 10 * 0.3
        self.car_x += self.car_v

        if (self.car_to_stop and self.car_x >= self.TRAFFIC_LIGHT_X - self.CAR_WIDTH * self.CAR_SCALE_FACTOR):
            self.car_x = self.TRAFFIC_LIGHT_X - self.CAR_WIDTH * self.CAR_SCALE_FACTOR

        self.car_y = (self.Y_DISTANCE - self.CAR_HEIGHT * self.CAR_SCALE_FACTOR) / 2
        self.ax.add_patch(patches.Rectangle((self.car_x, self.car_y), self.CAR_WIDTH * self.CAR_SCALE_FACTOR, self.CAR_HEIGHT * self.CAR_SCALE_FACTOR))

        # plot predicted car
        (predict_x) = self.callback.predict(dt = 1)
        self.callback.update(x = self.car_x)

        if (self.traffic_light_state == 'yellow'):
            pred_car = patches.Rectangle(
                (self.car_x_on_red, self.car_y),
                self.CAR_WIDTH * self.CAR_SCALE_FACTOR,
                self.CAR_HEIGHT * self.CAR_SCALE_FACTOR,
                fill = False
            )
            pred_car.set_linestyle('--')
            self.ax.add_patch(pred_car)

            if (self.car_to_stop):
                self.ax.add_patch(patches.Rectangle((self.car_x_on_red, 0), 2, 1, facecolor = 'red'))
            else:
                self.ax.add_patch(patches.Rectangle((self.car_x_on_red, 0), 2, 1, facecolor = 'green'))

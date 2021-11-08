import numpy as np
from sim import Sim

class KalmanFilter:
    def __init__(self):
        self.x = 0

        self.x = np.matrix([
            [0], [0]]
        )

        self.P = np.matrix([
            [1000, 0],
            [0, 1000]
        ])

        self.F = np.matrix([
            [1, 1], # dt = 1 sec
            [0, 1]
        ])

        self.H = np.matrix([
            [1, 0]
        ])

        self.R = np.matrix([
            [0.01]
        ])

        self.I = np.matrix([
            [1, 0],
            [0, 1]
        ])

    def predict(self, dt):
        self.F[0, 1] = dt

        # self.P[0, 0] += 0.1
        # self.P[1, 1] += 0.1

        self.x = self.F * self.x
        self.P = self.F * self.P * np.transpose(self.F)

        F_new = np.matrix([
            [1, 4], # 4 seconds later
            [0, 1]
        ])
        x_new = F_new * self.x
        return x_new[0, 0]

        #return (self.x[0, 0])
    
    def update(self, x):
        Z = np.matrix(x)
        y = np.transpose(Z) - self.H * self.x
        S = self.H * self.P * np.transpose(self.H) + self.R
        K = self.P * np.transpose(self.H) * np.linalg.inv(S)
        self.x = self.x + K * y
        self.P = (self.I - K * self.H) * self.P

    def onYellowLightOn(self, traffic_light_x, duration):
        print('onYellowLightOn', traffic_light_x, self.x[0, 0], duration)

        F_new = np.matrix([
            [1, duration],
            [0, 1]
        ])
        x_new = F_new * self.x

        if (x_new[0, 0] < traffic_light_x):
            return [True, x_new[0, 0]]
        else:
            return [False, x_new[0, 0]]

sim = Sim(KalmanFilter())
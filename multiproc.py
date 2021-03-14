# %%
from multiprocessing import Process
from multiprocessing import Queue
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
# %%
figure, ax = plt.subplots(figsize=(5,5))
axis_range = [0, 100, 0, 100]
queue = Queue()

# %%
def point_2_ball(p, r):
    theta = np.arange(0, 2*np.pi, 0.3)
    xr = p[0] + r * np.cos(theta)
    yr = p[1] + r * np.sin(theta)

    return xr, yr

def collision_detect(b1, b2):
    d = np.sum((b1.p - b2.p)**2)
    if d < (b1.r + b2.r)**2:
        return True
    else:
        return False

def bounce_1D(v1, m1, v2, m2, a):
    v11 = (2 * m2 * v2 + (m1 - m2) * v1) / (m1 + m2)
    v22 = (2 * m1 * v1 + (m2 - m1) * v2) / (m1 + m2)
    v0 = (m1 * v1 + m2 * v2) / (m1 + m2)
    v1a = v0 + a * (v11 - v0)
    v2a = v0 + a * (v22 - v0)

    return v1a, v2a

def bounce_2D(b1, b2, a):
    i = (b1.p - b2.p) / np.sqrt(np.sum((b1.p - b2.p)**2))
    n = np.empty(2)
    n[0] = i[1]
    n[1] = -i[0]

    v1i = b1.v @ i * i
    v2i = b2.v @ i * i
    v1n = b1.v @ n * n
    v2n = b2.v @ n * n

    v1ia, v2ia = bounce_1D(v1i, b1.m, v2i, b2.m, a)

    v1f = v1ia + v1n
    v2f = v2ia + v2n

    b1.v = v1f
    b2.v = v2f

def bounce_wall(b, a):
    if b.p[0] < 0 or b.p[0] > 100:
        b.v[0] = a * -b.v[0]
    if b.p[1] < 0 or b.p[1] > 100:
        b.v[1] = -b.v[1] * a

def in_range(p):
    if p[0] < 0 or p[0] > 100:
        return False
    if p[1] < 0 or p[1] > 100:
        return False

    return True

# %%

class ball:
    def __init__(self):
        self.p = np.random.rand(2) * 100
        self.v = np.random.rand(2) * 100 - np.ones(2) * 50
        self.r = np.random.rand(1) * 20
        self.m = self.r**2

    def point_2_ball(self):
        theta = np.arange(0, 2*np.pi, 0.05)
        xr = self.p[0] + self.r * np.cos(theta)
        yr = self.p[1] + self.r * np.sin(theta)

        return xr, yr

def traction(b1, b2, dt):
    r = np.sum((b2.p - b1.p)**2)
    d1 = (b2.p - b1.p) / np.sqrt(r)
    d2 = -d1

    f = b1.m * b2.m / r * 10**8

    b1.v += f * d1 * dt / b1.m
    b2.v += f * d2 * dt / b2.m


# %%
def init_value(n):
    balls = []

    for i in range(n):
        balls.append(ball())
    return balls

# %%
def frame(queue):
    print(123)
    ftime = time.time()
    frames = 0
    g = np.array([0.0, -100])
    balls = init_value(3)
    a = 1

    tic = time.time()
    while True:
        frames += 1
        time.sleep(0.001)
        toc = time.time()
        dt = toc - tic
        tic = toc

        for ball in balls:
            ball.p += ball.v * dt
            ball.v = ball.v + g * dt

        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                # traction(balls[i], balls[j], dt)
                if collision_detect(balls[i], balls[j]):
                    bounce_2D(balls[i], balls[j], a)
                    

        for ball in balls:
            bounce_wall(ball, a)

        if queue.empty():
            fps = frames / (time.time() - ftime)
            ftime = time.time()
            frames = 0
            queue.put((balls, fps))
        

tic = time.time()
fps = 0
def draw(i):
    global tic
    global ax
    global fps
    toc = time.time()
    if i % 20 == 0:
        fps = 1 / (toc - tic)
    tic = toc
    ax.clear()
    ax.axis(axis_range)
    balls, real_fps = queue.get()
    ax.set_title('Display_FPS: ' + str(fps)[:4] + " Real_FPS: " + str(real_fps)[:4])

    for ball in balls:
        x, y = ball.point_2_ball()
        ax.scatter(x, y)

process = Process(target=frame, args=(queue, ))
process.start()

animation = FuncAnimation(
    fig=figure,
    func=draw,
    interval=10
)

plt.show()

print(process.is_alive())
process.terminate()
process.join()
print(process.is_alive())

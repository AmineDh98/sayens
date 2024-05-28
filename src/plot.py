﻿# Import necessary libraries
from kin import *  # Includes numpy import
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import math

# Robot definition
d = np.array([275.5, 0, -410, 13.3, -311.1, 0, -263.8])
q = np.array([0, -2.356194, 0.0, 0.785398, -1.570796, -1.570796, -1.570796], dtype=float)
alpha = np.array([-math.pi/2, math.pi/2, math.pi/2, math.pi/2, math.pi/2, math.pi/2, math.pi])
a = np.array([0, 0, 0, 0, 0, 0, 0])

revolute = [True, True, True, True, True, True, True]
sigma_d = np.array([300, 100, 800])  # Update this to the desired goal point

# Simulation params
dt = 1.0 / 60.0

# Drawing preparation
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d', autoscale_on=False)
ax.set_xlim([-400, 1000])
ax.set_ylim([-400, 1000])
ax.set_zlim([-400, 1000])
ax.set_title('Simulation')
ax.set_aspect('equal')
ax.grid()
line, = ax.plot([], [], 'o-', lw=2)  # Robot structure
path, = ax.plot([], [], 'c-', lw=1)  # End-effector path
point, = ax.plot([], [], 'rx')  # Target
PPx = []
PPy = []
PPz = []
time = []
# Time intervals for x-axis
arr = []
# Error in [m] for y-axis

# Simulation initialization
def init():
    line.set_data([], [])
    path.set_data([], [])
    point.set_data([], [])
    return line, path, point

# Simulation loop
def simulate(t):
    global d, q, a, alpha, revolute, sigma_d
    global PPx, PPy, PPz

    # Update robot
    T = kinematics(d, q, a, alpha)
    # Obtaining the list of transformations with respect to the base frame
    J = jacobian(T, revolute)
    # Obtaining the Jacobian
    J1 = J[0:3, :]
    # It is important to take into account the columns of the first three rows of Jacobian

    T = np.array(T)
    # Position of the end-effector
    sigma = np.array([T[-1][0][-1], T[-1][1][-1], T[-1][2][-1]])
    # Taking into account only first two elements of the translation vector (current end-effector pose) of the last matrix from list T which represents the transformation from the base frame to the end-effector

    err = (sigma_d - sigma).reshape((3, 1))
    # Computing error by substraction current end-effector pose values from the desired ones

    #dq1 = DLS(J1, 0.05) @ (K @ err)
    # Control solution for inverse Jacobian by using damped least-squares method

    #dq1 = np.transpose(J1) @ (K @ err)
    # Control solution for inverse Jacobian by using transpose of it

    #dq1 = np.linalg.pinv(J1) @ (K @ err)
    dq1 = np.linalg.pinv(J1) @ err
    # Control solution for inverse Jacobian by using pseudoinverse

    dq2 = dq1[:, 0]
    # Managing the appropriate dimension
    q += dt * dq2

    # Update drawing
    P = robotPoints3D(T)
    line.set_data(P[0, :], P[1, :])
    line.set_3d_properties(P[2, :])  # Set z-coordinates
    PPx.append(P[0, -1])
    PPy.append(P[1, -1])
    PPz.append(P[2, -1])
    path.set_data(PPx, PPy)
    path.set_3d_properties(PPz)
    point.set_data(sigma_d[0], sigma_d[1])
    point.set_3d_properties(sigma_d[2])

    #arr.append(np.linalg.norm(err))
    # Adding error at the very next moment at the list
    #time.append(t)
    # Adding time intervals at the list

    return line, path, point

# Run simulation
animation = anim.FuncAnimation(fig, simulate, np.arange(0, 10, dt),
                                interval=10, blit=True, init_func=init, repeat=True)

plt.show()

# plt.figure()
# plt.plot(time, arr)
# plt.grid()
# plt.xlabel('time[s]')
# plt.ylabel('error[m]')
# plt.title('Resolved-rate motion control')
# plt.show()
# Plotting the error depending on time

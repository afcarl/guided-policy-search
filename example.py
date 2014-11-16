import numpy as np

from numpy import pi

from controller import LQR, EnergyStabilization, Controller, MixedController
from plant import DoublePendulum

DOUBLE_PENDULUM_PARAMS = {
    'g_ms2': 9.8, # acceleration due to gravity, in m/s^2
    'l1_m': 1.0, # length of pendulum 1 in m
    'l2_m': 1.0, # length of pendulum 2 in m
    'm1_kg': 1.0, # mass of pendulum 1 in kg
    'm2_kg': 1.0, # mass of pendulum 2 in kg
    'control_limit': [-100.0, 100.0]
}


def DP_lqr():
    """Double Pendulum upright LQR stabilization example"""
    p = DoublePendulum(DOUBLE_PENDULUM_PARAMS)

    upside_state = np.array([pi, 0.0, pi, 0.0])
    # upside_state with noise in position
    perturbation = np.array([1.0, 0.0, 1.0, 0.0]) * np.random.normal(0.0, 0.1, (4,))
    initial_state = upside_state + perturbation
    print 'Starting perturbed by %s' % (perturbation,)
    # 20 seconds
    time_range = np.arange(0.0, 10.0, 0.01)

    # LQR controller focused on upside
    lqr = LQR(p, upside_state, 0)
    p.set_controller(lqr.get())

    # simulation and visualization
    y = p.simulate(initial_state, time_range, visualize=True)



def swingup_example():
    """Double Pendulum upright LQR stabilization example"""
    p = DoublePendulum(DOUBLE_PENDULUM_PARAMS)

    downside_state = np.array([0.0, 0.0, 0.0, 0.0])
    upside_state = np.array([pi, 0.0, pi, 0.0])
    # upside_state with noise in position

    initial_state = upside_state + np.array([1.0, 0.0, 1.0, 0.0]) * np.random.normal(0.0, 0.01)
    print 'Starting from %s' % (initial_state,)

    # 20 seconds
    time_range = np.arange(0.0, 20, 0.01)

    # Energy controller
    energy_ctrl = EnergyStabilization(p, upside_state, 0)

    k = [4, 2, 2]
    max_lqr_score = 500.0

    # Erection controller
    normalize_angle = lambda angle : angle % (2*pi) - pi

    def angle_controller(state, t):
        t1 = state[0]
        t2 = state[2]
        diff = t1-t2
        if abs(diff) > pi:
            new_abs = 2*pi - abs(diff)
            diff = new_abs * np.sign(diff)
        return diff

    straight_ctrl = Controller(angle_controller)
    straight_dot_ctrl = Controller(lambda state, t: -state[3] )

    swingup_controller = MixedController()
    #swingup_controller.add(k[0], energy_ctrl)
    #swingup_controller.add(k[1], straight_ctrl)
    #swingup_controller.add(k[2], straight_dot_ctrl)

    # LQR controller focused on upside
    lqr = LQR(p, upside_state, 0)
    swingup_controller.add_lqr(lqr, max_lqr_score)

    # Set the mixed controller
    p.set_controller(swingup_controller.get())

    # Just the energy
    #energy_ctrl = EnergyStabilization(p, upside_state, 0, coefficient=0.05)
    #p.set_controller(energy_ctrl.get())



    # simulation and visualization
    y = p.simulate(initial_state, time_range, visualize=False)
    #for i in range(y.shape[0]):
    #    print '%f while desired is %f' % (p.energy(y[i],0), p.energy(upside_state,0))
    p.visualize(y, time_range)
if __name__ == '__main__':
    #DP_lqr()
    swingup_example()

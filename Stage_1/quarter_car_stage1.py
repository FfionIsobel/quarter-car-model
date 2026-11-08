"""
Quarter car - Stage 1: free vibration of a mass-spring-damper
Scuderia Weekend, Round 1 (Monza)

The system: one mass (a quarter of the car body) sitting on a spring and a damper.
We pull it down 20 mm, let go, and watch how it bounces back.

Equation of motion (from a free-body diagram):
    m*x'' + c*x' + k*x = 0

solve_ivp can only handle FIRST-order equations, so we split it into two:
    x' = v                       (velocity is the rate of change of position)
    v' = -(c*v + k*x) / m        (Newton's second law rearranged for acceleration)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# ---------- 1. Parameters (roughly a Formula Student corner) ----------
m = 60.0      # sprung mass on one corner [kg]
k = 20000.0     # spring stiffness at the wheel [N/m]
zeta = 0.3   # damping ratio (0 = no damper, 1 = critically damped)



# ---------- 2. Hand-calc values (check these on paper first!) ----------
wn = np.sqrt(k / m)               # natural frequency [rad/s]
fn = wn / (2 * np.pi)             # natural frequency [Hz]
c_crit = 2 * np.sqrt(k * m)       # critical damping [N s/m]
c = zeta * c_crit                 # actual damping coefficient [N s/m]
fd = fn * np.sqrt(1 - zeta**2) if zeta < 1 else 0.0   # damped frequency [Hz]

print(f"Natural frequency  fn = {fn:.2f} Hz")
print(f"Critical damping   c_crit = {c_crit:.0f} N s/m")
print(f"Damper used        c = {c:.0f} N s/m (zeta = {zeta})")
print(f"Damped frequency   fd = {fd:.2f} Hz")


# ---------- 3. The equations for solve_ivp ----------
def mass_spring_damper(t, state, m, c, k):
    x, v = state                  # unpack position and velocity
    dxdt = v
    dvdt = -(c * v + k * x) / m
    return [dxdt, dvdt]


# ---------- 4. Solve ----------
x0 = -0.040        # start 20 mm below equilibrium [m]
v0 = 0.0           # released from rest [m/s]
t_end = 1.5        # simulate 1.5 seconds
t_eval = np.linspace(0, t_end, 1500)   # times we want answers at

sol = solve_ivp(mass_spring_damper, (0, t_end), [x0, v0],
                t_eval=t_eval, args=(m, c, k))

x_mm = sol.y[0] * 1000
print(f"Starting push:   {x_mm[0]:.1f} mm")
print(f"Biggest overshoot: {x_mm.max():.1f} mm")
print(f"Overshoot as % of push: {abs(x_mm.max() / x_mm[0]) * 100:.0f}%")

# ---------- 5. Plot ----------
plt.figure(figsize=(8, 4))
plt.plot(sol.t, sol.y[0] * 1000, label=f"zeta = {zeta}")
plt.axhline(0, color="grey", linewidth=0.8)
plt.xlabel("Time [s]")
plt.ylabel("Body displacement [mm]")
plt.title("Quarter car stage 1: free vibration")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("stage1_free_vibration.png", dpi=150)
plt.ylim(-45, 20)     # fix the vertical axis from -45 mm to +20 mm
plt.show()


# ---------- 6. Experiment: compare damping ratios ----------
plt.figure(figsize=(8, 4))
for z in [0.1, 0.3, 0.7, 1.0, 1.5]:
    c_z = z * c_crit
    s = solve_ivp(mass_spring_damper, (0, t_end), [x0, v0],
                  t_eval=t_eval, args=(m, c_z, k))
    plt.plot(s.t, s.y[0] * 1000, label=f"zeta = {z}")

plt.axhline(0, color="grey", linewidth=0.8)
plt.xlabel("Time [s]")
plt.ylabel("Body displacement [mm]")
plt.title("Effect of damping ratio")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("stage1_damping_comparison.png", dpi=150)
plt.show()

from scipy.signal import find_peaks

x_mm = sol.y[0] * 1000
peaks, _ = find_peaks(x_mm)            # indices of every peak
peak_times = sol.t[peaks]
print("Peak times [s]:", peak_times)

period = peak_times[1] - peak_times[0]
print(f"Measured period = {period:.3f} s")
print(f"Measured frequency = {1/period:.2f} Hz  (hand calc: {fd:.2f} Hz)")


plt.figure(figsize=(8, 4))
for push in [-0.020, -0.040]:
    s = solve_ivp(mass_spring_damper, (0, t_end), [push, 0.0],
                  t_eval=t_eval, args=(m, c, k))
    plt.plot(s.t, s.y[0] * 1000, label=f"push = {push*1000:.0f} mm")
plt.axhline(0, color="grey", linewidth=0.8)
plt.xlabel("Time [s]"); plt.ylabel("Body displacement [mm]")
plt.title("Same car, different push"); plt.legend(); plt.grid(alpha=0.3)
plt.show()
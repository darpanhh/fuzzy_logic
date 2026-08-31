"""
=============================================================
 AUTOMATIC FAN SPEED CONTROL USING FUZZY LOGIC (Mamdani FIS)
=============================================================
Inputs  : Temperature (0-40 C), Humidity (0-100%)
Output  : Fan Speed (0-100%)

Before running, install the library (one-time, in your terminal):
    pip install scikit-fuzzy numpy matplotlib networkx

These numbers (triangle points, rules) are EXACTLY the ones we
designed by hand in Parts 3 and 4 -- nothing here is random.
"""

# -------------------------------------------------------------
# SECTION 1: IMPORT LIBRARIES
# -------------------------------------------------------------
import numpy as np                     # for creating numeric ranges (universes of discourse)
import matplotlib.pyplot as plt        # for plotting membership functions and results
import skfuzzy as fuzz                 # core fuzzy logic functions (membership shapes, defuzzification)
from skfuzzy import control as ctrl    # high-level fuzzy control system builder (Antecedent/Consequent/Rule)


# -------------------------------------------------------------
# SECTION 2: DEFINE UNIVERSES OF DISCOURSE
# -------------------------------------------------------------
temperature_universe = np.arange(0, 41, 1)   # 0 to 40 degrees C, step of 1
humidity_universe    = np.arange(0, 101, 1)  # 0 to 100 percent, step of 1
fan_speed_universe   = np.arange(0, 101, 1)  # 0 to 100 percent, step of 1


# -------------------------------------------------------------
# SECTION 3: DEFINE MEMBERSHIP FUNCTIONS
# -------------------------------------------------------------
temperature = ctrl.Antecedent(temperature_universe, 'temperature')
humidity    = ctrl.Antecedent(humidity_universe, 'humidity')
fan_speed   = ctrl.Consequent(fan_speed_universe, 'fan_speed')

# ---- Temperature fuzzy sets ----
temperature['cold'] = fuzz.trimf(temperature_universe, [0, 0, 20])
temperature['warm'] = fuzz.trimf(temperature_universe, [0, 20, 40])
temperature['hot']  = fuzz.trimf(temperature_universe, [20, 40, 40])

# ---- Humidity fuzzy sets ----
humidity['low']    = fuzz.trimf(humidity_universe, [0, 0, 50])
humidity['medium'] = fuzz.trimf(humidity_universe, [0, 50, 100])
humidity['high']   = fuzz.trimf(humidity_universe, [50, 100, 100])

# ---- Fan Speed fuzzy sets (the OUTPUT) ----
fan_speed['slow']   = fuzz.trimf(fan_speed_universe, [0, 0, 50])
fan_speed['medium'] = fuzz.trimf(fan_speed_universe, [0, 50, 100])
fan_speed['fast']   = fuzz.trimf(fan_speed_universe, [50, 100, 100])


# -------------------------------------------------------------
# SECTION 4: VISUALIZE MEMBERSHIP FUNCTIONS
# -------------------------------------------------------------
# .view() draws onto the current matplotlib figure/axes but doesn't
# reliably return them across scikit-fuzzy versions, so we grab them
# with plt.gcf()/plt.gca() right after calling it. We do this so we
# can move the legend to a fixed, sensible spot instead of letting
# matplotlib's "best" placement drop it on top of the curves.
#
# Placing it OUTSIDE the axes (to the right, vertically centered)
# keeps it out of the way no matter what the curves look like, and
# savefig(..., bbox_inches='tight') makes sure it isn't cropped off.

def place_legend_outside(ax):
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5),
               borderaxespad=0, frameon=True)

temperature.view()
fig1, ax1 = plt.gcf(), plt.gca()
ax1.set_title("Temperature Membership Functions")
place_legend_outside(ax1)
fig1.savefig('mf_temperature.png', dpi=150, bbox_inches='tight')

humidity.view()
fig2, ax2 = plt.gcf(), plt.gca()
ax2.set_title("Humidity Membership Functions")
place_legend_outside(ax2)
fig2.savefig('mf_humidity.png', dpi=150, bbox_inches='tight')

fan_speed.view()
fig3, ax3 = plt.gcf(), plt.gca()
ax3.set_title("Fan Speed Membership Functions")
place_legend_outside(ax3)
fig3.savefig('mf_fan_speed.png', dpi=150, bbox_inches='tight')


# -------------------------------------------------------------
# SECTION 5: DEFINE FUZZY RULES
# -------------------------------------------------------------
rule1 = ctrl.Rule(temperature['cold'] & humidity['low'],    fan_speed['slow'])
rule2 = ctrl.Rule(temperature['cold'] & humidity['medium'], fan_speed['slow'])
rule3 = ctrl.Rule(temperature['cold'] & humidity['high'],   fan_speed['medium'])
rule4 = ctrl.Rule(temperature['warm'] & humidity['low'],    fan_speed['slow'])
rule5 = ctrl.Rule(temperature['warm'] & humidity['medium'], fan_speed['medium'])
rule6 = ctrl.Rule(temperature['warm'] & humidity['high'],   fan_speed['fast'])
rule7 = ctrl.Rule(temperature['hot']  & humidity['low'],    fan_speed['medium'])
rule8 = ctrl.Rule(temperature['hot']  & humidity['medium'], fan_speed['fast'])
rule9 = ctrl.Rule(temperature['hot']  & humidity['high'],   fan_speed['fast'])

all_rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9]


# -------------------------------------------------------------
# SECTION 6: CREATE CONTROL SYSTEM
# -------------------------------------------------------------
fan_ctrl_system = ctrl.ControlSystem(all_rules)
fan_simulation  = ctrl.ControlSystemSimulation(fan_ctrl_system)


# -------------------------------------------------------------
# SECTION 7: GET INPUT VALUES FROM THE USER
# -------------------------------------------------------------
# Instead of hardcoding temperature/humidity, we ask the person
# running the script to type them in. get_valid_input() keeps
# re-prompting until a usable number inside the correct range is
# entered, so the program never crashes on bad input (letters,
# empty input, or a number outside 0-40 / 0-100).

def get_valid_input(prompt_text, min_value, max_value):
    while True:
        raw_value = input(prompt_text)
        try:
            value = float(raw_value)
        except ValueError:
            print(f"  Please enter a number (you typed: '{raw_value}').")
            continue
        if value < min_value or value > max_value:
            print(f"  Please enter a value between {min_value} and {max_value}.")
            continue
        return value

print("=== Automatic Fan Speed Control (Fuzzy Logic) ===")
input_temperature = get_valid_input(
    "Enter Temperature in \u00b0C (0-40): ", 0, 40
)
input_humidity = get_valid_input(
    "Enter Humidity in % (0-100): ", 0, 100
)

fan_simulation.input['temperature'] = input_temperature
fan_simulation.input['humidity']    = input_humidity


# -------------------------------------------------------------
# SECTION 8: COMPUTE RESULT
# -------------------------------------------------------------
fan_simulation.compute()


# -------------------------------------------------------------
# SECTION 9: DISPLAY FAN SPEED
# -------------------------------------------------------------
result = fan_simulation.output['fan_speed']
print(f"\nTemperature = {input_temperature}C, "
      f"Humidity = {input_humidity}%")
print(f"==> Computed Fan Speed = {result:.2f}%")


# -------------------------------------------------------------
# SECTION 10: VISUALIZE THE RESULT
# -------------------------------------------------------------
fan_speed.view(sim=fan_simulation)
fig4, ax4 = plt.gcf(), plt.gca()
ax4.set_title("Aggregated Output & Defuzzified Fan Speed")
place_legend_outside(ax4)
fig4.savefig('output_defuzzification.png', dpi=150, bbox_inches='tight')

plt.show()
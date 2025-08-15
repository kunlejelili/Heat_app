This App was designed as a doctors'assistance software to assist during operations to access thye damaged of the body and locatrions where medications are to be applied
It works on the the basic principles of heat transfer throughout the body tissues. 
The bioheat equation was solved by numerical methods of the finite difference to study the heat transfer pattern and coded using python algorithm.
The codes inluded an animation function to study the behaviour of the heat transfer mechanism.
When using the heat equation to predict damaged areas in the human body, especially due to thermal exposure (e.g. burns, medical treatment, or simulations), the main focus areas are:

 1. Temperature Distribution Over Time
What: The heat equation models how heat spreads within tissues over time.

Why it's important: Tissue damage is closely linked to how high the temperature gets and for how long.

🧠 2. Thermal Damage Thresholds
What: Human tissues begin to suffer irreversible damage above certain temperatures (e.g. ~42–45°C for prolonged time).

How it's used: By identifying regions where temperature exceeds this threshold for a specific time, you can estimate damage zones.

🧪 3. Thermal Dose (CEM43 or Arrhenius model)
CEM43 (Cumulative Equivalent Minutes at 43°C): Converts time-temperature data into a single damage metric.

Arrhenius Model: Uses chemical kinetics to quantify damage based on temperature history.

These models go beyond temperature to quantify actual cell or tissue damage.

🏥 4. Material Properties of Tissues
What you need: Thermal conductivity, specific heat capacity, density.

Why: Different tissues (fat, muscle, bone) conduct heat differently, so accurate modeling requires using proper values.

🖥️ 5. Boundary and Initial Conditions
Initial body temperature (e.g. 37°C)

Boundary conditions (e.g. heat source, ambient cooling, blood perfusion)

These control how heat enters and leaves the body.

🧊 6. Heat Sinks – Blood Perfusion
Blood flow carries heat away from heated areas, cooling tissue.

This must be added to the heat equation (bioheat transfer equation) for realism.

🧭 7. Numerical Simulation
FEM (Finite Element Method) or FDM (Finite Difference Method) are often used to solve the heat equation in complex 2D or 3D body models.

🧬 8. Damage Prediction for Treatment Planning
Used in laser therapy, radiofrequency ablation, hyperthermia treatment, etc.

Helps to avoid damaging healthy tissue while ensuring the treatment is effective.

Great — here’s a basic Python example using the Pennes Bioheat Equation to simulate temperature distribution and tissue damage prediction in a 2D slice of human tissue.

What This Code Does:
Solves the Pennes Bioheat Equation using Finite Difference Method (FDM)

Simulates heating over time

Applies an Arrhenius damage model 
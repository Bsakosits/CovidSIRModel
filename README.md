# CovidSIRModel

The Covid SIR model is a S.usceptible, I.nfected, and R.ecovered model of contagion spread.
We modelled the spread in a local area with agents rather than using a simple R rate of infection, for added accuracy.
This allowed us to permit variable changes to social distancing ordinances, such as quarantine and mask-wearing mandates, and analyze their effects.

TO USE:
Simply run the covid model in any same folder as the "Templates" folder, which contains the front-end. 
A simple interactive html webpage will appear, allowing you to change all of the default parameters of the model, run it, and see in graphs and visualizations how Covid would spread in a local area under those parameters. The model should take no more than a minute or two to run. 

Our report runs the model many times using different mandates and generous and conservative rates of infection, and thereby concludes the effectiveness of mandated mask-wearing and quarantining at nullifying or reducing contagion spread. Additionally, the model has a tool for controlling for changes in mandates during spread, such as a drop of a quarantine mandate when the rate of infection drops below a specified number, allowing the user to simulate waves of contagion spread if governments reopen too early, and that effect on spread and death tolls.

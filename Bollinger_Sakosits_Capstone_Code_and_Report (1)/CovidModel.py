import io
import base64
import numpy as np
from scipy.integrate import odeint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from random import random, randint, choice
from flask import Flask, Response, render_template, request
import copy

def infect(personA, personB):
        if personB.state==1:
            if personA.isDist or personB.isDist:
                isdisting=True
            else:
                isdisting=False
            if personA.isMask or personB.isMask:
                ismasking=True
            else:
                ismasking=False

            if isdisting and not ismasking:
                chance=ifdistchance
            elif not isdisting and ismasking:
                chance=ifmaskchance
            elif not isdisting and not ismasking:
                chance=ifneitherchance
            else:
                chance=ifbothchance
            if personA.isAsymptomatic==True:
                chance=chance*.75
            if random() <= chance:
                personB.state=2

total_t=30 #t=5 is 1 month, t=10 is 2 months, etc
N=40
isQuarantine=False
quarantineProp=.5
isolatingOnceSick_prop=1
isAsymptomatic_prop=.4
isDist_prop=.64
isMask_prop=.59
ifneitherchance=.19
ifmaskchance=.13
ifdistchance=.17
ifbothchance=.03
tickstorecovery=4

counts=[]
change=[]
derivs=[]
t=0
FormerPeople = [[0 for i in range(N)] for j in range(N)] 

class Person:
	def __init__(self, state, isDist, isMask, recoveryT, isAsymptomatic, isIsolating):
		self.state = state
		self.isDist = isDist
		self.isMask = isMask
		self.recoveryT = recoveryT
		self.isAsymptomatic = isAsymptomatic
		self.isIsolating = isIsolating

def countStates(People):
	stateCounts = [0, 0, 0]
	for m in People:
		for n in m:
			if n.state == 1:
				stateCounts[0] += 1
			elif n.state == 2:
				stateCounts[1] += 1
			elif n.state == 3:
				stateCounts[2] += 1
			else:
				print("countStates error, state not properly generated")
	return(stateCounts)

def initialize(N, isDist_prop, isMask_prop, isQuarantine):
        global t
        for i in range(40):
                for j in range (40):
                        FormerPeople[i][j] = Person(1,random() <= isDist_prop,random() <= isMask_prop, 0, random() <= isAsymptomatic_prop, isQuarantine)
        FormerPeople[20][20].state=2
        counts.append(countStates(FormerPeople))
        t += 1

def update(FormerPeople):
    global isQuarantine
    global t
    People=copy.deepcopy(FormerPeople)
    counts.append(countStates(People))
    if counts[t][1]/1600>=quarantineProp:
        isQuarantine=True
    else:
        isQuarantine=False
#    print(isQuarantine, t, counts[t][1])
    for k in range(40):
        for j in range(40):
            if FormerPeople[k][j].state==2 and FormerPeople[k][j].recoveryT<=tickstorecovery:
                if FormerPeople[k][j].recoveryT>=1 and FormerPeople[k][j].isAsymptomatic==False and isQuarantine==False and FormerPeople[k][j].isIsolating==False:
                    People[k][j].isIsolating=(random()<=isolatingOnceSick_prop)
                if FormerPeople[k][j].recoveryT>=tickstorecovery:
                    People[k][j].state=3
                People[k][j].recoveryT+=1

                if k>0 and k<39:
                    infect(People[k][j], People[k-1][j])
                    infect(People[k][j], People[k+1][j])
                    if j>0:
                        infect(People[k][j], People[k-1][j-1])
                        infect(People[k][j], People[k][j-1])
                        infect(People[k][j], People[k+1][j-1])
                    if j<39:
                        infect(People[k][j], People[k-1][j+1])
                        infect(People[k][j], People[k][j+1])
                        infect(People[k][j], People[k+1][j+1])
                elif k==0:
                    infect(People[k][j], People[k+1][j])
                    if j>0:
                        infect(People[k][j], People[k][j-1])
                        infect(People[k][j], People[k+1][j-1])
                    if j<39:
                        infect(People[k][j], People[k][j+1])
                        infect(People[k][j], People[k+1][j+1])
                elif k==39:
                    infect(People[k][j], People[k-1][j])
                    if j>0:
                        infect(People[k][j], People[k-1][j-1])
                        infect(People[k][j], People[k][j-1])
                    if j<39:
                        infect(People[k][j], People[k-1][j+1])
                        infect(People[k][j], People[k][j+1])
                if FormerPeople[k][j].isIsolating==False and isQuarantine==False:
                    for x in range(randint(8, 24)):
                        infect(People[k][j], People[randint(0, 39)][randint(0, 39)])
    templist=[]
    if t>0:
        for i in range(3):
            if counts[t-1][i]!=0:
                templist.append(counts[t][i]/counts[t-1][i])
            else:
                templist.append(0)
    derivs.append(templist)
    t+=1
    return(People)

def modelPlot(title, peopleList, numPeople):
        fig, ax = plt.subplots()
        agent_colors = {1:'b', 2:'r', 3:'g'}
        counter = 0
        for i in peopleList:
                for j in i:
                        counter += 1
                        ax.scatter(i.index(j)+0.5, peopleList.index(i)+0.5, color=agent_colors[j.state])
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.set_xlim([0, numPeople])
        ax.set_ylim([0, numPeople])
        ax.set_xticks([])
        ax.set_yticks([])
        fontP = FontProperties()
        fontP.set_size('xx-small')
        legendElem = [Line2D([0], [0], marker='o', color='w', label='Susceptible',
                             markerfacecolor='b', markersize=8),
                      Line2D([0], [0], marker='o', color='w', label='Infected',
                             markerfacecolor='r', markersize=8),
                      Line2D([0], [0], marker='o', color='w', label='Recovered',
                             markerfacecolor='g', markersize=8)]
        ax.legend(handles=legendElem, loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=3, fancybox=True, shadow=True)
        return fig

def derivPlot(derivs):
        global total_t
        fig, ax = plt.subplots()
        ax.set_title("Derivatives")
        ax.set_xlabel("time")
        ax.set_ylabel("rates of change")
        ax.grid()
        temp0 = []
        temp1 = []
        temp2 = []
        for i in range(total_t):
                temp0.append(derivs[i][0])
                temp1.append(derivs[i][1])
                temp2.append(derivs[i][2])
        ax.plot(range(total_t), temp0, color='blue', label='Susceptible')
        ax.plot(range(total_t), temp1, color='red', label='Infected')
        ax.plot(range(total_t), temp2, color='green', label='Recovered')
        ax.legend()
        return fig

def countPlot(counts):
        global total_t
        fig, ax = plt.subplots()
        ax.set_title("Populations")
        ax.set_xlabel("time")
        ax.set_ylabel("number of people")
        ax.grid()
        temp0 = []
        temp1 = []
        temp2 = []
        for i in range(total_t):
                temp0.append(counts[i][0])
                temp1.append(counts[i][1])
                temp2.append(counts[i][2])
        ax.plot(range(total_t), temp0, color='blue', label='Susceptible')
        ax.plot(range(total_t), temp1, color='red', label='Infected')
        ax.plot(range(total_t), temp2, color='green', label='Recovered')
        ax.legend()
        return fig
        

'''initialize(N, isDist_prop, isMask_prop, isQuarantine)
for x in range(total_t):
	FormerPeople = update(FormerPeople)
for g in range(total_t):
	print(counts[g], derivs[g])'''

app = Flask(__name__, template_folder='Templates')

@app.route('/')
def main():
        return render_template('frontend.html')

@app.route('/input', methods=['GET', 'POST'])
def modelPlotView():
        global FormerPeople
        global t
        global isQuarantine
        global isolatingOnceSick_prop
        global isAsymptomatic_prop
        global isDist_prop
        global isMask_prop
        global ifneitherchance
        global ifmaskchance
        global ifdistchance
        global ifbothchance
        global tickstorecovery
        global derivs
        global counts
        global total_t
        global quarantineProp
        total_t = int(request.form.get("timeticks"))
        if request.form.get("inQuar"):
                isQuarantine = True
        quarantineProp = int(request.form.get("quarantineProp"))/100
        isolatingOnceSick_prop = int(request.form.get("isoProp"))/100
        isAsymptomatic_prop = int(request.form.get("asymProp"))/100
        isDist_prop = int(request.form.get("socDistProp"))/100
        isMask_prop = int(request.form.get("maskProp"))/100
        ifneitherchance = int(request.form.get("neitherProp"))/100
        ifmaskchance = int(request.form.get("maskEncProp"))/100
        ifdistchance = int(request.form.get("socDistEncProp"))/100
        ifbothchance = int(request.form.get("bothProp"))/100
        tickstorecovery = int(request.form.get("recTime"))
        initialize(N, isDist_prop, isMask_prop, isQuarantine)
        fig1 = modelPlot('Covid Model State Graph Start', FormerPeople, N)
        pngImage1 = io.BytesIO()
        pngImage1B64String = "data:image/png;base64,"
        pngImage2 = io.BytesIO()
        pngImage2B64String = "data:image/png;base64,"
        pngImage3 = io.BytesIO()
        pngImage3B64String = "data:image/png;base64,"
        pngImage4 = io.BytesIO()
        pngImage4B64String = "data:image/png;base64,"
        pngImage5 = io.BytesIO()
        pngImage5B64String = "data:image/png;base64,"
        pngImage6 = io.BytesIO()
        pngImage6B64String = "data:image/png;base64,"
        FigureCanvas(fig1).print_png(pngImage1)
        pngImage1B64String += base64.b64encode(pngImage1.getvalue()).decode('utf8')
        print("First model plot done!")
        temp = int(total_t/3)
        for x in range(total_t):
                FormerPeople = update(FormerPeople)
                if t == temp:
                        fig2 = modelPlot('Covid Model State Graph 1/3 Through', FormerPeople, N)
                        FigureCanvas(fig2).print_png(pngImage2)
                        pngImage2B64String += base64.b64encode(pngImage2.getvalue()).decode('utf8')
                        print("Second model plot done!")
                elif t == temp * 2:
                        fig3 = modelPlot('Covid Model State Graph 2/3 Through', FormerPeople, N)
                        FigureCanvas(fig3).print_png(pngImage3)
                        pngImage3B64String += base64.b64encode(pngImage3.getvalue()).decode('utf8')
                        print("Third model plot done!")
                elif t == total_t:
                        fig4 = modelPlot('Covid Model State Graph End', FormerPeople, N)
                        FigureCanvas(fig4).print_png(pngImage4)
                        pngImage4B64String += base64.b64encode(pngImage4.getvalue()).decode('utf8')
                        print("Fourth model plot done!")
        fig5 = derivPlot(derivs)
        FigureCanvas(fig5).print_png(pngImage5)
        pngImage5B64String += base64.b64encode(pngImage5.getvalue()).decode('utf8')
        print("Deriv plot done!")
        fig6 = countPlot(counts)
        FigureCanvas(fig6).print_png(pngImage6)
        pngImage6B64String += base64.b64encode(pngImage6.getvalue()).decode('utf8')
        print("Counts plot done!")
        t=0
        derivs=[]
        counts=[]
        isQuarantine=False
        plt.close("all")
        return render_template('frontend.html',
                               image1=pngImage1B64String,
                               image2=pngImage2B64String,
                               image3=pngImage3B64String,
                               image4=pngImage4B64String,
                               image5=pngImage5B64String,
                               image6=pngImage6B64String)
        

if __name__== '__main__':
    app.run()

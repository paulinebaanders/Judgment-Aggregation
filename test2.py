from src import Scenario
from src import Compare_Kemnash
import src.utils as utils
import matplotlib.pyplot as plt
import itertools, argparse, os, time, sys

# Some lambda lists. If other list add it with integer label to lamb dict
l0 = [round(y,3) for x in [[0.005*a for a in range(50)], [0.05*b for b in range(5,15)]] for y in x]
l1 = [0,.005,.01,.015,.02,.03,.05,.07,.1,.15,.2,.25]
l2 = [0, .01, .05, .1, .15, .25, .35, .45, .55]
l3 = [0,.01,.05,.1,.15,.2,.25,.3,.35,.4,.45,.5]
lamb_dict = {'l0': l0, 'l1':l1, 'l2':l2, 'l3':l3}
# DEFAULT VALUES.
DEFAULT_PATHSCEN = "./jaggs/conjunctive_red.jagg"
DEFAULT_FOLDER = os.path.abspath(os.getcwd())[:-4]+'Plots'

# PARSER.
parser = argparse.ArgumentParser()
# Arguments for scenario.
parser.add_argument('--path_scen', type=str, default=DEFAULT_PATHSCEN, help='Path to .jagg file for reduced scenario.')
parser.add_argument('--num_judges', type=int, default=15, help='Number of judgements/judges that are contained in every profile.')
# Arguments for initialising comparison object.
parser.add_argument('--lambs', type=str, default='l2', help='Key of lambda list in lamb_dicts.')
parser.add_argument('--sample', type=int, default=250000, help='Number of profiles in every iteration.')
parser.add_argument('--simulate', type=int, default=40000000, help='If total number of profiles exceeds this number, profile is simulated.')
# Plots
parser.add_argument('--show_plots', type=int, default=0, help='If True plot is shown (1/0 for True/False).')
parser.add_argument('--save_plots', type=int, default=1, help='If True plots saved (1/0 for True/False).')
parser.add_argument('--plot_folderDir', type=str, default=DEFAULT_FOLDER, help='Absolute dir of folder in which plot is saved.')
args = parser.parse_args()

# SCENARIO.
# Initialise the scenario object and load from file.
scen = Scenario()
scen.load_from_file(args.path_scen, args.num_judges)
lambdas = lamb_dict[args.lambs]
# Get result dictionary
result = Compare_Kemnash(scen, lambdas).result(args.sample, args.simulate)
quan_, qual_, lamb_, rest_ = [], [], [], []
for label in result:
    if label[:6] == 'symdif':
        quan_.append(result[label])
    elif label[0] == 'R':
        qual_.append(result[label])
    elif label[-2:] == 'KN':
        lamb_.append(result[label])
    else:
        rest_.append(result[label])
print('symdif   (KKN, KMH, KME, KNMH, KNME)')
for ele in quan_:
    print(ele)
print('qual     mKN/K, mMH/K, mME/K, lK/MH, lKN/MH, mdK/ME, mdKN/ME')
for ele in qual_:
    print(ele)
print('lamb     mKN, sdKN, lKN, mdKN')
for ele in lamb_:
    print(ele)
print('rest     SD-KNK, ZE10')
for ele in rest_:
    print(ele)

# PLOT DIRECTORIES.self.lambs
if args.save_plots:
    # Construct name for plot.
    if scen.num_profs > args.simulate:
        simustr = '-SIMU-'
    else:
        simustr = '-'
    nameQuan = "quan-{}-n{:.0f}{}s{:.0f}-{}.png".format(args.path_scen[8:-9], scen.number_voters, 
        simustr, args.sample, args.lambs)
    nameQual = "qual-{}-n{:.0f}{}s{:.0f}-{}.png".format(args.path_scen[8:-9], scen.number_voters, 
        simustr, args.sample, args.lambs)
    nameLamb = "lamb-{}-n{:.0f}{}s{:.0f}-{}.png".format(args.path_scen[8:-9], scen.number_voters, 
        simustr, args.sample, args.lambs)
    nameZE = "ze-{}-n{:.0f}{}s{:.0f}-{}.png".format(args.path_scen[8:-9], scen.number_voters, 
        simustr, args.sample, args.lambs)
    # Create full directory for plot.
    dir_plotQuan = args.plot_folderDir+'/'+nameQuan
    dir_plotQual = args.plot_folderDir+'/'+nameQual
    dir_plotLamb = args.plot_folderDir+'/'+nameLamb
    dir_plotZE = args.plot_folderDir+'/'+nameZE
    # Create folder directory if it doesn't exist.
    if not os.path.exists(args.plot_folderDir):
        os.makedirs(args.plot_folderDir)

# PLOTS.
# Quantative.
fig, ax = plt.subplots(1)
ax.plot(lambdas, result['symdifKemKN'], color="purple", linewidth=1, linestyle="-")
ax.plot(lambdas, result['symdifKemMaxham'], color="gray",linewidth=1, linestyle="-")
ax.plot(lambdas, result['symdifKemMaxeq'], color="gray",linewidth=1, linestyle="--")
ax.plot(lambdas, result['symdifKN-Maxham'], color="brown",linewidth=1, linestyle="-")
ax.plot(lambdas, result['symdifKN-Maxeq'], color="brown",linewidth=1, linestyle="--")
if args.save_plots:
    plt.savefig(dir_plotQuan, format='png')
if args.show_plots:
    plt.show()
# Qualitative.
fig, ax = plt.subplots(1)
ax.plot(lambdas, result['R-meanKN'], color="blue", linewidth=1, linestyle="-")
ax.plot(lambdas, result['R-meanMaxham'], color="blue", linewidth=1, linestyle="--")
ax.plot(lambdas, result['R-meanMaxeq'], color="blue", linewidth=1, linestyle="-.")
ax.plot(lambdas, result['R-lowKem'], color="black", linewidth=1, linestyle=":")
ax.plot(lambdas, result['R-lowKN'], color="black", linewidth=1, linestyle="-")
ax.plot(lambdas, result['R-maxdistKem'], color="red", linewidth=1, linestyle=":")
ax.plot(lambdas, result['R-maxdistKN'], color="red", linewidth=1, linestyle="-")
if args.save_plots:
    plt.savefig(dir_plotQual, format='png')
if args.show_plots:
    plt.show()
# Lambda
fig, ax = plt.subplots(1)
ax.plot(lambdas, result['meanKN'], color="blue", linewidth=1, linestyle="-")
ax.plot(lambdas, result['lowKN'], color="black", linewidth=1, linestyle="-")
ax.plot(lambdas, result['maxdistKN'], color="red", linewidth=1, linestyle="-")
if args.save_plots:
    plt.savefig(dir_plotLamb, format='png')
if args.show_plots:
    plt.show()
# Zero-effect
fig, ax = plt.subplots(1)
ax.plot(lambdas, result['ZE'], color="green", linewidth=1, linestyle="-")
if args.save_plots:
    plt.savefig(dir_plotZE, format='png')
if args.show_plots:
    plt.show()

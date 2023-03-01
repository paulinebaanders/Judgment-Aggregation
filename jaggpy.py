from src import Scenario
from src import CompareRules
from src import BFSolver
from src import ASPSolver 
import src.utils as utils
import argparse, itertools
# Auxialiary statements for solvers
bfs = BFSolver(binrep=True)
bfs2 = BFSolver2(binrep=True)
asp = ASPSolver(binrep=True)
asp_print = ASPSolver(binrep=True, print_asp=False)

# Scenario Endriss
E4 = Scenario()
E4.load_from_file("./jaggs/endriss_s4.jagg")
E11 = Scenario()
E11.load_from_file("./jaggs/endriss_s11.jagg")
# Scenario Lang
sLang = Scenario()
sLang.load_from_file("./jaggs/lang_s3.jagg")
# Conjunctive 
con3 = Scenario()
con3.load_from_file("./jaggs/conjunctive_s3.jagg")
con5 = Scenario()
con5.load_from_file("./jaggs/conjunctive_s5.jagg")

def printfunc(scen, solver, rule, label="dummy", lamb=0, show=True):
    outlist = []
    for outcome in solver.all_outcomes(scen, rule, lamb):
        outlist.append(outcome)
    outlist = sorted(outlist, key=lambda x: int(x,2))
    if show:
        print(str(outlist)+'    '+label)
    return outlist

def all_rules(scenario=con5, lamb=0.005):
    #####               KEMENY          #####
    # BFS
    printfunc(scenario, bfs, "kemeny", "Kemeny BFS")
    printfunc(scenario, bfs, "kemeny-original", "Kemeny original BFS")
    # ASP
    printfunc(scenario, asp, "kemeny", "Kemeny OPT ASP")
    printfunc(scenario, asp, "kemeny-sat", "Kemeny SAT ASP")
    printfunc(scenario, asp, "kemeny-original", "Kemeny OPT original ASP")
    printfunc(scenario, asp, "kemeny-original-sat", "Kemeny SAT original ASP")
    #####           KEMENY-NASH         #####
    # BFS
    printfunc(scenario, bfs, "kemnash", "Kemeny-Nash BFS")
    # ASP
    printfunc(scenario, asp, "kemnash", "Kemeny-Nash OPT ASP")
    printfunc(scenario, asp, "kemnash-sat", "Kemeny-Nash SAT ASP")
    #####   PARAMETERISED KEMENY-NASH   #####
    # BFS
    printfunc(scenario, bfs, "lamb-kemnash", "\u03BB-Kemeny-Nash BFS (\u03BB="+str(lamb)+")", lamb)
    # ASP
    printfunc(scenario, asp, "lamb-kemnash", "\u03BB-Kemeny-Nash OPT ASP (\u03BB="+str(lamb)+")", lamb)
    printfunc(scenario, asp, "lamb-kemnash-sat", "\u03BB-Kemeny-Nash OPT ASP (\u03BB="+str(lamb)+")", lamb)

if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_scen', type=str, default="./jaggs/conjunctive_s3.jagg",
                        help='Relative directory to jagg file for scenario')
    parser.add_argument('--lamb', type=float, default=0.005,
                        help='Lambda values used for the parameterised Kemeny-Nash implementations')
    args = parser.parse_args()

    scenario = Scenario()
    scenario.load_from_file(args.path_scen)
    num_in = len(scenario.in_consistent)
    num_antipodal_in = utils.count_consistentOpp(scenario.in_consistent)
    print("There are "+str(num_in)+" rational (allowed individual) judgements"
            +" cotaining "+str(num_antipodal_in)+" PAIRS of antipodal judgements.")
    all_rules(scenario, args.lamb)

    for outcome in bfs2.all_outcomes(con5, "all_rules", 0):
        print(con5.profile)
        print(outcome)


import itertools, random, math, time, sys
from more_itertools import random_combination 
from .bf_solver import BFSolver
from .asp_solver import ASPSolver 
import src.utils as utils
import matplotlib.pyplot as plt

class Compare_Kemnash():
    """ Class to compare two judgement aggregation methods (solver+rule+lambda)
    with each other. If methods are the same than analysis one a single method."""

    def __init__(self, scenario, lambs:list):
        """The class is initialized with:
        scenario;
        lamb: value of lambda-parameter for parameterised Kemeny-Nash rule"""
        self.scenario = scenario
        self.lambs = lambs
        if len(lambs) == 1:
            self.single = True
        self.prof_tot = 0
        self.prof_test = 0
        self.indices = 0
        # Useful for iteration later on
        self.rules = ['Kem', 'KN', 'Maxham', 'Maxeq']
        self.rulesComb = ['KemKN', 'KemMaxham', 'KemMaxeq', 'KN-Maxham', 'KN-Maxeq']
        self.outcomes = []


    def result(self, sample:int=250000, simulate:int=40000000):
        """ 
        all_ex: If True all examples are printed; otherwise, only the ones with different outcomes.
        num_ex: Maximal number of examples to be printed.
        sample: Number of profiles computed. If 0 all profiles computed.
        time_an: If True time (comparison) analysis is executed.
        show_res: Dictionary with results is printed (in a nice format).
        simulate: If self.prof_tot > simulate, a profile (multiset) is simulated as random 
                permutation. (To prevent RAM overflow.)"""
        ########    GROUNDWORK    ########
        # Random seed
        random.seed(time.time())
        # Variable to show time estimation (after 60s).
        first_pass = True
        prof_done = 0
        # Convenient shorthands
        bfs = BFSolver(binrep=False)

        # Computing total number of profiles (= multisets).
        self.prof_tot = self.scenario.num_profs
        # If sample > self.prof_tot all profiles are iterated and sample set 0
        if sample > self.prof_tot:
            sample = 0
        # In case self.prof_tot > simulate 
        if self.prof_tot > simulate and sample > 0:
            print('PROFILE SIMULATION')
            self.indices = [0] * sample
            self.prof_test = sample
        elif self.prof_tot > simulate:
            print('PROFILE SIMULATION')
            self.indices = [0] * self.prof_tot
            self.prof_test = self.prof_tot
        else:
            self.indices = self.compute_indices(sample)

        # Initialise dictionaries to keep counts during profile iterations for current lambda.
        cumQuan = {}
        cumQual = {}
        for rule in self.rules:
            cumQuan['sol'+rule] = 0
        for comb in self.rulesComb:
            cumQuan['o'+comb] = 0
        for count in ['mean', 'SD', 'low', 'maxdist']:
            for rule in self.rules:
                cumQual[count+rule] = 0 
        cumQual['ZE'] = 0

        # Initialise dictionary to append results for single lambda
        final = {}
        for comb in self.rulesComb:
            final['symdif'+comb] = []
        final.update({'R-meanKN':[], 'R-meanMaxham':[], 'R-meanMaxeq': [], 'R-lowKem':[], 'R-lowKN':[]})
        final.update({'R-maxdistKem':[], 'R-maxdistKN':[], 'ZE':[], 'SD-KNKem':[]})
        final.update({'meanKN':[], 'SDKN':[], 'lowKN':[], 'maxdistKN':[]})

        ########    FOR EVERY LAMBDA ITERATE THROUGH PROFILES    ########
        t0 = time.time()
        for idxl,lamb in enumerate(self.lambs):
            # TO REMOVE
            if idxl == 1:
                t1 = time.time()
                print('time   1 it:', round(t1-t0, 1))
                print('result 1 it:', final)
            # Empty cumulative dicts.
            for label in cumQuan:
                cumQuan[label] = 0
            for label in cumQual:
                cumQual[label] = 0

            for index in self.indices:
                # Constructing profile corresponding to index
                self.scenario.profile = self.construct_profile(index)

                # Using the modified Jaggpy solvers to compute outcomes of profile.
                self.outcomes = bfs.all_outcomes(self.scenario, "all_rules", lamb)

                #  Updating quantitative analysis dict 
                cumQuan = self.quantitative_analysis(cumQuan)
                #  Updating qualitative analysis dict
                cumQual = self.qualitative_analysis(cumQual)

                ###  TIMER  ###
                # After 60s it will give an estimate of duration
                prof_done += 1
                t = time.time()
                if t - t0 > 60 and first_pass and idxl == 0:
                    time_est = int((self.prof_test * (t - t0)) / (prof_done * 60))
                    print('TIME INDICATION: '+str(prof_done)+'/'+str(self.prof_test) + ' took ' +\
                    str(int(t-t0))+'s. Estimate total time: ' + str(time_est) + 'min.')
                    first_pass = False

            ############    PROCESSING RESULTS    ############
            for comb in self.rulesComb:
                r1 = comb[:3]
                if r1[-1] == '-':
                    r1 = r1[:-1]
                r2 = comb[3:]
                final['symdif'+comb].append( round((cumQuan['sol'+r1]+cumQuan['sol'+r2]-2*cumQuan['o'+comb] ) / (
                    cumQuan['sol'+r1]+cumQuan['sol'+r2]-cumQuan['o'+comb]), 3))
            final['R-meanKN'].append(round( cumQual['meanKN']/cumQual['meanKem'], 2))
            final['R-meanMaxham'].append(round( cumQual['meanMaxham']/cumQual['meanKem'], 2))
            final['R-meanMaxeq'].append(round( cumQual['meanMaxeq']/cumQual['meanKem'], 2))
            final['R-lowKem'].append(round( cumQual['lowKem']/cumQual['lowMaxham'], 3))
            final['R-lowKN'].append(round( cumQual['lowKN']/cumQual['lowMaxham'], 3))
            final['R-maxdistKem'].append(round( cumQual['maxdistKem']/cumQual['maxdistMaxeq'], 3))
            final['R-maxdistKN'].append(round( cumQual['maxdistKN']/cumQual['maxdistMaxeq'], 3))
            final['SD-KNKem'].append(round( cumQual['SDKN']/cumQual['SDKem'], 2))
            final['ZE'].append(round( cumQual['ZE'] / self.prof_test, 4))
            final['meanKN'].append(round( cumQual['meanKN']/self.prof_test, 2))
            final['SDKN'].append(round( cumQual['SDKN']/self.prof_test, 2))
            final['lowKN'].append(round( cumQual['lowKN']/self.prof_test, 2))
            final['maxdistKN'].append(round( cumQual['maxdistKN']/self.prof_test, 2))
        return final

    def quantitative_analysis(self, cumQuan):
        """Updates counts necessary for symmetric difference computations"""
        # Adding number of solutions.
        for idx,rule in enumerate(self.rules):
            cumQuan['sol'+rule] += len(self.outcomes[idx])

        outKem, outKN, outMaxham, outMaxeq = self.outcomes
        rules1 = [outKem, outKem, outKem, outKN, outKN]
        rules2 = [outKN, outMaxham, outMaxeq, outMaxham, outMaxeq]
        for idx,comb in enumerate(self.rulesComb):
            for out1 in rules1[idx]:
                for out2 in rules2[idx]:
                    if out1 == out2:
                        cumQuan['o'+comb] += 1
        return cumQuan

    def qualitative_analysis(self, cumQual):
        """Comparing utalitarian and egalitarian measures."""
        # Computations. 
        agr_msets = [[utils.agr(self.scenario, out) for out in outcomes] for outcomes in self.outcomes] 
        means = [[sum(agr_mset)/float(len(agr_mset)) for agr_mset in agr_mseti] for agr_mseti in agr_msets] 
        dists2 = [[[(agr_msets[ridx][oidx][nidx] - means[ridx][oidx])**2 for nidx in range(self.scenario.number_voters)]
            for oidx in range(len(self.outcomes[ridx]))] for ridx in range(4)] 
        SDs = [[math.sqrt(sum(dists)/float(len(dists))) for dists in dists2i] for dists2i in dists2]
        lows = [[min(agr_mset) for agr_mset in agr_mseti] for agr_mseti in agr_msets]
        maxdists = [[max(agr_msets[ridx][oidx]) - min(agr_msets[ridx][oidx]) for oidx in range(
            len(self.outcomes[ridx]))] for ridx in range(4)]
        # Zero effect
        ZE = float([min([bool(SDs[1][KNIdx] > SDs[0][KemIdx]) for KemIdx in range(len(self.outcomes[0]))])
            for KNIdx in range(len(self.outcomes[1]))].count(True) / len(self.outcomes[1]))
        for idx,rule in enumerate(self.rules):
            cumQual['mean'+rule] += sum(means[idx])/float(len(means[idx]))
            cumQual['SD'+rule] += sum(SDs[idx])/float(len(SDs[idx]))
            cumQual['low'+rule] += sum(lows[idx])/float(len(lows[idx]))
            cumQual['maxdist'+rule] += sum(maxdists[idx])/float(len(maxdists[idx]))
        cumQual['ZE'] += ZE
        return cumQual

    def compute_indices(self, sample:int):
        """We build an iterator all_indices that contains tuples that represent
        the indices of consistent judgements in the corresponding profile """
        all_indices = itertools.combinations_with_replacement(
            range(len(self.scenario.in_consistent)), self.scenario.number_voters)
        if sample > 0:
            self.prof_test = sample
            # randomly draw indices from the set of all indices
            all_indices = random_combination(all_indices, self.prof_test)
        else:
            self.prof_test = self.prof_tot
            all_indices = random_combination(all_indices, self.prof_test)
        return all_indices

    def construct_profile(self, index):
        profile = []
        if index == 0:
            profile_permutation = []
            for judge in range(self.scenario.number_voters):
                profile_permutation.append(random.randrange(len(self.scenario.in_consistent)))
            for i in range(len(self.scenario.in_consistent)):
                num_occur = profile_permutation.count(i)
                if num_occur > 0:
                    profile.append([num_occur, utils.jdict_to_js(self.scenario.in_consistent[i])])
        else:
            for i in range(len(self.scenario.in_consistent)):
                num_occur = list(index).count(i)
                if num_occur > 0:
                    profile.append([num_occur, utils.jdict_to_js(self.scenario.in_consistent[i])])
        return profile
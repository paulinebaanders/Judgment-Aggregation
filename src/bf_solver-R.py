#####################################################################
## Module from JAGGPY, some rules added.
## Modifications include moving computing the consistent outcomes
## to .src.classes
#####################################################################

import copy, math, warnings, time
from itertools import combinations
from functools import reduce
from nnf import Var, Or, And # pylint: disable=unused-import
from .classes import Solver
from .parser import Parser
import src.utils as utils

class BFSolver(Solver):
    """A brute force solver for Judgment Aggregation."""
    def __init__(self, binrep=False):
        self.binrep = binrep

    def all_outcomes(self, scenario, rule, lamb=0):
        """Given a scenario object and the name of a rule
        this function will yield a list with all the outcomes
        of the judgment aggregation. The rule should be given
        as a string and can be one of the following lowercase commands:
            - kemeny            (New Kemeny implementation)
            - kemnash           (Kemeny-Nash implementation - with lamb=0)
            - lamb-kemnash      (Kemeny-Nash implementation - with lamb>0)
            - kemeny-original (Kemeny from JAGGPY)
        The utility of a player with judgment J_i when outcome is J is calculated
        as U_i = agr(J_i,J)+lamb.
        """
        # We determine the outcome with a helper function for corresponding rule.
        # Kemeny rule.
        if rule == "kemeny":
            outcomes = self.solve_kemeny(scenario)
        # Kemeny-Nash rule.
        elif rule == "kemnash":
            if lamb > 0:
                warnings.warn("For nonzero values of \u03BB for use parameterised Kemeny-Nash rule, now \u03BB is set to 0.")
            outcomes = self.solve_kemnash(scenario, 0)
        # Parameterised Kemeny-Nash rule.
        elif rule == "lamb-kemnash":
            outcomes = self.solve_kemnash(scenario, lamb)
        # Original Kemeny rule implementation from JAGGPY package.
        elif rule == "kemeny-original":
            outcomes = self.solve_kemeny_original(scenario)
        else:
            raise Exception (f"{rule} is not a recognized aggregation rule.")
        if self.binrep:
            outcomes = [utils.jdict_to_bin(d) for d in outcomes]
        return outcomes

    def support_number(self, agenda, profile):
        """The function support_number gets an agenda and profile and returns a dictionary, 
        containing label,occurence pairs.
        Not used in new implementation; however, utils.agr is based on it."""
        support_count = dict()
        for formula in agenda.values():
            support_count[formula] = 0
        for judgement_set in profile:
            times_accepted = judgement_set[0]
            accepted_formula = judgement_set[1]
            for formula in accepted_formula:
                support_count[formula] += times_accepted
        return support_count

    def solve_kemeny(self, scenario):
        """New implementation based on list comprehension. Effect on performance is 
        neglectable."""
        agr_vecs = [utils.agr(scenario, outcome) for outcome in scenario.out_consistent]
        agr_sums = [reduce((lambda x,y: x+y), agr_vec) for agr_vec in agr_vecs]
        idxs_max = [idx for idx,agr in enumerate(agr_sums) if agr == max(agr_sums)]
        outcomes = [scenario.out_consistent[idx] for idx in idxs_max]
        return outcomes

    def solve_kemnash(self, scenario, lamb=0):
        """New implementation based on list comprehension. Effect on performance is 
        neglectable."""
        agr_vecs = [utils.agr(scenario, outcome, lamb) for outcome in scenario.out_consistent]
        agr_prods = [reduce((lambda x,y: x*y), agr_vec) for agr_vec in agr_vecs]
        idxs_max = [idx for idx,agr in enumerate(agr_prods) if agr == max(agr_prods)]
        outcomes = [scenario.out_consistent[idx] for idx in idxs_max]
        return outcomes

    def solve_kemeny_original(self, scenario):
        """Slightly modified to be compatible with implementation."""
        # Keep track of the maximum agreement score and initiate list of outcomes.
        max_agreement = 0
        outcomes = []
        # Check agreement score for each outcome and update list of outcomes accordingly.
        for outcome in scenario.out_consistent:
            agreement_score = 0
            # For each formula in the pre-agenda, check how many agents agree
            # with the outcome and update agreement score.
            for issue in outcome.keys():
                support = self.support_number(scenario.agenda, scenario.profile)
                if outcome[issue]:
                    agreement_score += support[issue]
                else:
                    agreement_score += scenario.number_voters - support[issue]
            if agreement_score == max_agreement:
                outcomes.append(outcome)
            elif agreement_score > max_agreement:
                max_agreement = agreement_score
                outcomes = [outcome]
        return outcomes

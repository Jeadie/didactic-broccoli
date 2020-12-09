import numpy as np
from typing import List, Union

def payoff_to_odds(payoffs: List[float]) -> List[float]:
    """ Converts a list of payoffs, to their equal value probabilities. 

    Args:
        payoffs: A list of payoffs of the for 1:x for each x in payoff. 

    Returns
    """
    odds = 1/np.array(payoffs)
    return np.array(odds) / sum(odds)

def simulate_race(horse_prob: Union[np.array, List[float]], n: int) -> np.array:
    """ Simulates race results based on winning probabilities.

    Args:
        horse_probs: Probability of each horse winning. 
        n: The number of simulations to run. n > 0.

    Returns:
        A np matrix of size n x len(horse_prob) where each row corresponds to
        a simulated race.
    """
    p_horse = np.array(horse_prob) / sum(horse_prob)
    if n <= 0:
        return [[]]

    trials = np.repeat(p_horse[:, np.newaxis], n, axis=1)
    run = lambda p:np.random.choice(len(p), size=len(p), p =p, replace=False)
    return np.array([ run(trials[:,i])  for i in range(n)])

def top_k(results, k):
    n, horses= results.shape
    winners = results[:,:k]
    return dict([(i, (winners[winners==i]).size/n ) for i in range(horses)])

def winning(results):
    return top_k(results, 1)

n=50000
payoffs = [40,15,4,5,6,7]
#p_horse = [0.5, 0.1, 0.1, 0.1, 0.2]
results = simulate_race(payoff_to_odds(payoffs), n)

winners = results[:,0].copy() 
one_race = ((winners==0) *payoffs[0]) + ((winners==1) * payoffs[1])
#print(winners)
#print(one_race)
print(np.sum(one_race), np.var(one_race))
print(np.mean(one_race ==0))

results_2 = simulate_race(payoff_to_odds(payoffs), n)
winners_2 = results_2[:,0]
winners = results[:,0].copy() 

first_race = (winners==0) *payoffs[0]
second_race = (winners_2==1) *payoffs[1]
two_race = first_race + second_race
#print(two_race)
print(np.sum(two_race), np.var(two_race))
print(np.mean(one_race == 0))

1/0

print("TOP 3", top_k(results, 3))
print("Winner", winning(results))


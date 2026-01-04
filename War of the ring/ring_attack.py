import numpy as np

def sim_attack(units, leaders, num_for_combat_hit = 5, num_for__leadership_hit = 5):
    units = min(5, units)
    leaders = min(5, leaders)
    def prob_hit(num_for_hit):
        return (6 - num_for_hit + 1) / 6.
    hits = np.random.binomial(units, prob_hit(num_for_combat_hit))
    rerolls = max(0, leaders - hits)
    hits += np.random.binomial(rerolls, prob_hit(num_for__leadership_hit))
    return hits

NUM_ITERS = 10000
UNITS = 5
LEADERS = 5
total_hits = 0.

hits_array = [0] * 6
for i in xrange(NUM_ITERS):
    hits_array[sim_attack(UNITS, LEADERS)] += 1
    total_hits += sim_attack(UNITS, LEADERS)

for hits, count in enumerate(hits_array):
    print("Hits: {0}, Frequency: {1}".format(hits, 1.0 * count / NUM_ITERS))
print('AVG HITS: %f' % (total_hits / NUM_ITERS))

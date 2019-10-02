solution = open('perfect_solution.txt', 'r')
guess = open('Guess (example).txt', 'r')

# Maps song to position
sol_dict = {}
i = 0
for l in solution:
    sol_dict[int(l.split('-')[1])] = i
    i += 1

num_songs = i

guess_dict = {}
j = 0
for l in guess:
    guess_dict[int(l.split('-')[1])] = j
    j += 1

if j != num_songs or len(sol_dict) != len(guess_dict):
    print('Wrong number of songs!')
    exit()

kd_distance = 0

for song1 in range(1, num_songs + 1):
    for song2 in range(song1 + 1, num_songs + 1):
        if (sol_dict[song1] < sol_dict[song2]) != \
            (guess_dict[song1] < guess_dict[song2]):
            kd_distance += 1

print('Your score is: %d. (Lower is better, 0 is perfect)' % kd_distance)

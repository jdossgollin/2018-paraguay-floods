# Parameters for additional weather type runs
# Will calculate weather types for each centroid
# but fewer iterations than the "best" choice of
# number of centroids
VARXPL2 = 0.95
NSIM2 = 75
WTK := $(shell seq 2 1 10) # all years

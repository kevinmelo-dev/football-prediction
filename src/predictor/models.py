import numpy as np
from scipy.stats import poisson
from sklearn.linear_model import LogisticRegression

def poisson_prob_matrix(lambda_home, lambda_away, max_goals=5):
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            matrix[i][j] = poisson.pmf(i, lambda_home) * poisson.pmf(j, lambda_away)
    return matrix

def compute_1x2_prob(matrix):
    return np.tril(matrix, -1).sum(), np.trace(matrix), np.triu(matrix, 1).sum()

def compute_btts(matrix):
    btts_yes = sum(matrix[i][j] for i in range(1, 6) for j in range(1, 6))
    return btts_yes, 1 - btts_yes

def compute_over25(matrix):
    total = 0
    for i in range(6):
        for j in range(6):
            if i + j > 2:
                total += matrix[i][j]
    return total, 1 - total

import keras.backend as K
import numpy as np

def negative_profit_loss(y_true, y_pred):
    """
    The function implements the custom loss function
    
    Inputs
    true : [m x n x 4] where 4 is [0|1, 1|0, odds_a, odds_b]
    pred : [m x n x 3] where 3 is [(0-1), (0-1), (0-1)] where sum([(0-1), (0-1), (0-1)]) = 1
    
    Returns 
    the loss value = -profit
    """
    win_home_team = y_true[:, 0:1]
    win_away = y_true[:, 1:2]
    odds_a = y_true[:, 2:3]
    odds_b = y_true[:, 3:4]
    gain_loss_vector = K.concatenate([win_home_team * (odds_a - 1) + (1 - win_home_team) * -1,
                                      win_away * (odds_b - 1) + (1 - win_away) * -1,
                                      K.zeros_like(odds_a)], axis=1)
    return(-1 * K.mean(K.sum(gain_loss_vector * y_pred, axis=1)))

def inverse_profit_loss(y_true, y_pred):
    """
    The function implements the custom loss function
    
    Inputs
    true : [m x n x 4] where 4 is [0|1, 1|0, odds_a, odds_b]
    pred : [m x n x 3] where 3 is [(0-1), (0-1), (0-1)] where sum([(0-1), (0-1), (0-1)]) = 1
    
    Returns 
    the loss value = 1/profit
    """
    win_home_team = y_true[:, 0:1]
    win_away = y_true[:, 1:2]
    odds_a = y_true[:, 2:3]
    odds_b = y_true[:, 3:4]
    gain_loss_vector = K.concatenate([win_home_team * (odds_a - 1) + (1 - win_home_team) * -1,
                                      win_away * (odds_b - 1) + (1 - win_away) * -1,
                                      K.zeros_like(odds_a)], axis=1)
    return(1 / K.mean(K.sum(gain_loss_vector * y_pred, axis=1)))

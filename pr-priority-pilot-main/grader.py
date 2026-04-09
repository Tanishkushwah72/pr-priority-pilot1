def grader_fn(pred, truth):
    if pred == truth:
        return 0.9
    elif abs(pred - truth) == 1:
        return 0.6
    else:
        return 0.3

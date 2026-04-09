def grader_fn(pred, truth):
    # Safety checks
    try:
        pred = int(pred)
        truth = int(truth)
    except:
        return 0.1  # strong penalty for invalid output

    # Clamp values
    pred = max(0, min(2, pred))
    truth = max(0, min(2, truth))

    diff = abs(pred - truth)

    # Smooth scoring
    if diff == 0:
        score = 0.95
    elif diff == 1:
        score = 0.65
    else:
        score = 0.35

    return round(score, 3)

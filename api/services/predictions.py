from api.services.users import update_user_stats
from api.options import Method

PERFECT = 25
WINNER_ROUND = 22
WINNER_METHOD_EXCL_DEC = 17
WINNER_FINISH = 14
WINNER_DECISION = 20
WINNER_ONLY = 10


def is_decision(method):
    return method is not None and method in {Method.DEC, Method.DEC_U, Method.DEC_MAJ, Method.DEC_SPLIT}


def is_finishing_method(method):
    return method is not None and method in {Method.KO, Method.KOTKO, Method.SUB}


def is_finish_predicted(prediction):
    return (
        prediction.predicted_method is not None
        and prediction.predicted_method == Method.FINISH
    )


def calculate_total_points(prediction):
    if not prediction.winner_correct:
        return 0

    # Decision predictions are considered perfect,
    # but intentionally score lower than full perfects
    if prediction.decision_correct:
        return WINNER_DECISION

    if prediction.perfect_prediction:
        return PERFECT

    if prediction.round_correct:
        return WINNER_ROUND

    if prediction.method_correct and not is_decision(prediction.predicted_method):
        return WINNER_METHOD_EXCL_DEC

    if prediction.finish_correct:
        return WINNER_FINISH

    return WINNER_ONLY


def calculate_potential_points(prediction):
    if not prediction.predicted_winner:
        return 0

    # Decision predictions are considered perfect,
    # but intentionally score lower than full perfects
    if is_decision(prediction.predicted_method):
        return WINNER_DECISION

    if prediction.predicted_method and prediction.predicted_round:
        return PERFECT

    if prediction.predicted_round:
        return WINNER_ROUND

    if prediction.predicted_method == Method.FINISH:
        return WINNER_FINISH

    if prediction.predicted_method and not is_decision(prediction.predicted_method):
        return WINNER_METHOD_EXCL_DEC

    return WINNER_ONLY


def evaluate_prediction(prediction):
    fight = prediction.fight

    prediction.winner_correct = prediction.predicted_winner == fight.winner
    prediction.decision_correct = is_decision(
        prediction.predicted_method
    ) and is_decision(fight.winning_method)

    prediction.method_correct = (
        prediction.predicted_method is not None
        and prediction.predicted_method == fight.winning_method
    )
    prediction.finish_correct = is_finish_predicted(prediction) and is_finishing_method(
        fight.winning_method
    )
    prediction.round_correct = (
        prediction.predicted_round is not None
        and prediction.predicted_round == fight.winning_round
    )

    prediction.perfect_prediction = prediction.winner_correct and (
        (prediction.method_correct and prediction.round_correct)
        or prediction.decision_correct
    )


def score_prediction(prediction):
    evaluate_prediction(prediction)

    prediction.points_earned = calculate_total_points(prediction)
    prediction.points_potential = calculate_potential_points(prediction)

    prediction.save(
        update_fields=[
            "winner_correct",
            "method_correct",
            "round_correct",
            "finish_correct",
            "points_earned",
            "points_potential",
            "perfect_prediction",
        ]
    )

    update_user_stats(prediction)

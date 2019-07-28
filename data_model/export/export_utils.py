from collections import namedtuple
from typing import Dict

from trueskill import TrueSkill, rate_1vs1, Rating

from data_model.enums import LabelActionType
from kono_data.utils import timing

RATING_REPETITION_TARGET = 15  # 12  # TrueSkill documentation mentions 12 as nr. of iterations for convergence

RatingScore = namedtuple('RatingScore', ['rating', 'score', 'normalised_score'])


def get_scores_from_labels(labels, keys, label_name, normalise=True) -> Dict[str, RatingScore]:
    rating_env = create_rating_env(labels)
    key_to_rating_dict = get_ratings_from_labels(labels, keys, label_name, rating_env)

    key_to_rating_score_dict = {key: RatingScore(rating, rating_env.expose(rating), 0) for key, rating in
                                key_to_rating_dict.items()}
    if normalise:
        # set negative scores to 0
        key_to_rating_score_dict = {
            key: rating._replace(score=rating.score if rating.score >= 0 else 0)
            for key, rating in key_to_rating_score_dict.items()
        }

        # normalise
        scores = [kr.score for kr in key_to_rating_score_dict.values()]
        max_score, min_score = max(scores), min(scores)
        key_to_rating_score_dict = {
            key: rating._replace(normalised_score=normalise_value(rating.score, max_score, min_score))
            for key, rating in key_to_rating_score_dict.items()
        }

    return key_to_rating_score_dict


@timing
def get_ratings_from_labels(labels, keys, label_name, rating_env,
                            repetition_count=RATING_REPETITION_TARGET) -> Dict[str, Rating]:
    key_to_rating_dict = init_key_to_rating_score_dict(keys, rating_env)
    key_to_count = {key: 0 for key in keys}

    for iter_count, label in enumerate(x for _ in range(repetition_count) for x in labels):
        is_draw = label.action == LabelActionType.skip.value

        if is_draw:
            key1, key2 = label.key1, label.key2
        else:
            winner_key = label.data.get(label_name)
            if not winner_key:
                continue

            loser_key = label.key1 if label.key1 != winner_key else label.key2
            key1, key2 = winner_key, loser_key

        try:
            rating1, rating2 = key_to_rating_dict[key1], key_to_rating_dict[key2]
        except KeyError:
            continue

        # if both keys already have more comparisons than repetition_count, we can skip
        is_keys_compared_more_often_than_repetition_count = key_to_count[key1] >= repetition_count and \
                                                            key_to_count[key2] >= repetition_count

        if iter_count > 1 and is_keys_compared_more_often_than_repetition_count:
            continue

        key_to_rating_dict[key1], key_to_rating_dict[key2] = rate_1vs1(rating1, rating2, drawn=is_draw, env=rating_env)
        key_to_count[key1] += 1
        key_to_count[key2] += 1

    return key_to_rating_dict


def init_key_to_rating_score_dict(keys, rating_env: TrueSkill) -> Dict[str, Rating]:
    return {key: rating_env.create_rating() for key in keys}


def create_rating_env(labels) -> TrueSkill:
    nr_draws = labels.filter(action=LabelActionType.skip.value).count()
    nr_all_tasks = labels.count()
    draw_probability = nr_draws / nr_all_tasks
    return TrueSkill(draw_probability=draw_probability)


def normalise_value(val, max_val, min_val):
    return (val - min_val) / (max_val - min_val)

from collections import namedtuple
from typing import Dict

from trueskill import TrueSkill, rate_1vs1, Rating

from data_model.enums import LabelActionType

RatingScore = namedtuple('RatingScore', ['rating', 'score', 'normalised_score'])


def get_scores_from_queryset(queryset, keys, label_name, normalise=True) -> Dict[str, RatingScore]:
    rating_env = create_rating_env(queryset)
    key_to_rating_dict = create_ratings_dict_from_queryset(queryset, keys, label_name, rating_env)

    key_to_rating_score_dict = {key: RatingScore(rating, rating_env.expose(rating), 0) for key, rating in
                                key_to_rating_dict.items()}
    if normalise:
        scores = [kr.score for kr in key_to_rating_score_dict.values()]
        max_score, min_score = max(scores), min(scores)
        key_to_rating_score_dict = {key: rating._replace(normalised_score=
                                                         normalise_value(rating.score, max_score, min_score))
                                    for key, rating in key_to_rating_score_dict.items()}

    return key_to_rating_score_dict


def create_ratings_dict_from_queryset(queryset, keys, label_name, rating_env, repetition_count=12) -> dict:
    key_to_rating_dict = create_key_to_rating_score_dict(keys, rating_env)

    for label in (x for _ in range(repetition_count) for x in queryset):
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

        key_to_rating_dict[key1], key_to_rating_dict[key2] = rate_1vs1(rating1, rating2, drawn=is_draw, env=rating_env)

    return key_to_rating_dict


def create_key_to_rating_score_dict(keys, rating_env) -> Dict[str, Rating]:
    return {key: rating_env.create_rating() for key in keys}


def create_rating_env(queryset) -> TrueSkill:
    nr_draws = queryset.filter(action=LabelActionType.skip.value).count()
    nr_all_tasks = queryset.count()
    draw_probability = nr_draws / nr_all_tasks
    return TrueSkill(draw_probability=draw_probability)


def normalise_value(val, max_val, min_val):
    return (val - min_val) / (max_val - min_val)

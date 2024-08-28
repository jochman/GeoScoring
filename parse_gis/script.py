import numpy as np


def get_score(min_max_values: tuple[int, int], bounds: tuple[int, int]):
    """This is a callback to calculate the score.
    It receives the parameters to process and return a function that get a value as an input"""

    def _get_score(value):
        """"""
        try:
            score = (
                bounds[0]
                + (
                    (value - min_max_values[0])
                    / (min_max_values[1] - min_max_values[0])
                )
                * (bounds[1] - 1)
            )
            return np.floor(score)
        except Exception as exc:
            print(f"something bad happened {exc=}")
            return None

    return _get_score
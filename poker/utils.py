from typing import List


def find_matches(array: List[any]) -> List[any]:
    """Ишет совпадения в списке"""
    matches = []
    for i in range(len(array)):
        matches.append(0)
        for j in array:
            if array[i] == j:
                matches[i] += 1

    return matches
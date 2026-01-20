"""
Transition types and management for video concatenation.
"""

import random
from typing import List


# Available transitions that work well for slideshows
TRANSITION_TYPES = [
    'fade',          # Classic crossfade (most common)
    'dissolve',      # Dissolve effect
    'pixelize',      # Pixelated transition
    'slideleft',     # Slide from right
    'slideright',    # Slide from left
    'slideup',       # Slide from bottom
    'slidedown',     # Slide from top
    'smoothleft',    # Smooth slide left
    'smoothright',   # Smooth slide right
    'smoothup',      # Smooth slide up
    'smoothdown',    # Smooth slide down
    'fadeblack',     # Fade through black
    'fadewhite',     # Fade through white
    'circleopen',    # Circle reveal
    'wipeleft',      # Wipe from right
    'wiperight',     # Wipe from left
]


def get_random_transition(exclude: List[str] = None) -> str:
    """
    Get a random transition type.

    Args:
        exclude: List of transitions to exclude from random selection

    Returns:
        Transition type string

    Raises:
        ValueError: If all transitions are excluded

    Example:
        trans = get_random_transition()
        # Returns: 'fade' or any other random transition

        trans = get_random_transition(exclude=['fade', 'dissolve'])
        # Returns: Any transition except 'fade' or 'dissolve'
    """
    available = TRANSITION_TYPES.copy()
    if exclude:
        available = [t for t in available if t not in exclude]

    if not available:
        raise ValueError("No transitions available after exclusions")

    return random.choice(available)


def validate_transition(transition: str) -> bool:
    """
    Validate that a transition type is supported.

    Args:
        transition: Transition type to validate

    Returns:
        True if valid, False otherwise

    Example:
        if validate_transition('fade'):
            print("Transition is supported")
    """
    return transition in TRANSITION_TYPES

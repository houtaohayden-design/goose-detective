# tests/test_theme.py
from ui.theme import player_color, PLAYER_COLORS

def test_player_color_first():
    assert player_color(0) == "#F5C842"

def test_player_color_wraps_around():
    # 16 colors, index 16 wraps to index 0
    assert player_color(16) == player_color(0)
    assert player_color(17) == player_color(1)

def test_sixteen_distinct_colors():
    assert len(set(PLAYER_COLORS)) == 16

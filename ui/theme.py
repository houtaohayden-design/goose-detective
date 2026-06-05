# ui/theme.py

# Player color pool (16 colors, for max 16 players in Goose Goose Duck)
PLAYER_COLORS = [
    "#F5C842",  # goose yellow   player 1
    "#4A9EE0",  # lake blue      player 2
    "#E05555",  # duck red       player 3
    "#55C87A",  # grass green    player 4
    "#C855C8",  # purple         player 5
    "#E08C4A",  # orange         player 6
    "#55C8C8",  # cyan           player 7
    "#E0E055",  # yellow-green   player 8
    "#9B59B6",  # deep purple    player 9
    "#E91E8C",  # rose           player 10
    "#1ABC9C",  # teal           player 11
    "#E74C3C",  # deep red       player 12
    "#3498DB",  # blue           player 13
    "#F39C12",  # gold           player 14
    "#2ECC71",  # green          player 15
    "#95A5A6",  # gray           player 16
]

BG_DARK   = "#1a2a3a"
BORDER    = "#f5c842"
TEXT_MAIN = "#f0e6cc"
TEXT_DIM  = "#8a9aaa"

SUSPICION_HIGH   = "#e05555"
SUSPICION_MED    = "#e08c4a"
SUSPICION_LOW    = "#55c87a"

def player_color(index: int) -> str:
    """0-based index -> hex color string. Wraps around for >16."""
    return PLAYER_COLORS[index % len(PLAYER_COLORS)]

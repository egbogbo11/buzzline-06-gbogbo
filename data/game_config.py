"""
Game Configuration
Team names, player rosters, and game simulation parameters
"""

# Team Configuration
TEAMS = {
    'home': {
        'name': 'Lakers',
        'players': [
            'LeBron James',
            'Anthony Davis',
            'Austin Reaves',
            'D\'Angelo Russell',
            'Rui Hachimura'
        ]
    },
    'away': {
        'name': 'Warriors',
        'players': [
            'Stephen Curry',
            'Klay Thompson',
            'Draymond Green',
            'Andrew Wiggins',
            'Chris Paul'
        ]
    }
}

# Game Simulation Parameters
GAME_PARAMS = {
    'quarters': 4,
    'minutes_per_quarter': 12,
    'seconds_between_scores': (15, 45),  # Min and max seconds between scoring events
    'three_point_probability': 0.35,  # 35% of shots are 3-pointers
}

# Scoring probabilities (which team scores)
SCORING_BALANCE = {
    'home_team_probability': 0.50,  # 50% chance home team scores (balanced game)
}

def get_team_name(team_type: str) -> str:
    """Get team name by type (home or away)"""
    return TEAMS.get(team_type, {}).get('name', 'Unknown')

def get_player_roster(team_type: str) -> list:
    """Get player roster by team type (home or away)"""
    return TEAMS.get(team_type, {}).get('players', [])

def get_all_team_names() -> tuple:
    """Get both team names as tuple (home, away)"""
    return TEAMS['home']['name'], TEAMS['away']['name']
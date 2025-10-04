"""
Message Validator
Validates JSON message format for basketball scoring events
"""

import json
from typing import Dict, Any, Optional

def validate_message(message: str) -> tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Validate a basketball scoring event message
    
    Args:
        message: JSON string to validate
    
    Returns:
        Tuple of (is_valid, parsed_data, error_message)
    """
    # Required fields
    required_fields = [
        'timestamp',
        'game_time',
        'team',
        'player',
        'points',
        'score_home',
        'score_away'
    ]
    
    try:
        # Parse JSON
        data = json.loads(message)
        
        # Check all required fields exist
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, None, f"Missing required fields: {missing_fields}"
        
        # Validate points value (should be 2 or 3)
        if data['points'] not in [2, 3]:
            return False, None, f"Invalid points value: {data['points']}. Must be 2 or 3."
        
        # Validate scores are non-negative integers
        if not isinstance(data['score_home'], int) or data['score_home'] < 0:
            return False, None, f"Invalid score_home: {data['score_home']}"
        
        if not isinstance(data['score_away'], int) or data['score_away'] < 0:
            return False, None, f"Invalid score_away: {data['score_away']}"
        
        # All checks passed
        return True, data, None
        
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON format: {str(e)}"
    except Exception as e:
        return False, None, f"Validation error: {str(e)}"


def create_message(timestamp: str, game_time: str, team: str, player: str, 
                   points: int, score_home: int, score_away: int) -> str:
    """
    Create a valid basketball scoring event message
    
    Args:
        timestamp: Event timestamp
        game_time: Game clock time (e.g., "Q2 8:45")
        team: Team name
        player: Player name
        points: Points scored (2 or 3)
        score_home: Current home team score
        score_away: Current away team score
    
    Returns:
        JSON string of the message
    """
    message = {
        'timestamp': timestamp,
        'game_time': game_time,
        'team': team,
        'player': player,
        'points': points,
        'score_home': score_home,
        'score_away': score_away
    }
    return json.dumps(message)
"""
Basketball Producer
Generates simulated basketball scoring events and streams them to Kafka
"""

#####################################
# Import Modules
#####################################

import json
import random
import time
from datetime import datetime

# Import from existing utils
from utils.utils_producer import (
    verify_services,
    create_kafka_producer,
    create_kafka_topic,
    logger
)

# Import game configuration
from data.game_config import (
    TEAMS,
    GAME_PARAMS,
    SCORING_BALANCE,
    get_team_name,
    get_player_roster
)

#####################################
# Configuration
#####################################

TOPIC_NAME = "basketball-game"

#####################################
# Game Simulation Functions
#####################################

def format_game_time(quarter: int, minutes: int, seconds: int) -> str:
    """Format game time as 'Q# MM:SS'"""
    return f"Q{quarter} {minutes:02d}:{seconds:02d}"

def generate_scoring_event(score_home: int, score_away: int, quarter: int, 
                          minutes: int, seconds: int) -> dict:
    """
    Generate a single scoring event
    
    Returns:
        Dictionary containing scoring event data
    """
    # Determine which team scores
    if random.random() < SCORING_BALANCE['home_team_probability']:
        team_type = 'home'
    else:
        team_type = 'away'
    
    # Get team name and random player
    team_name = get_team_name(team_type)
    players = get_player_roster(team_type)
    player = random.choice(players)
    
    # Determine if it's a 2-pointer or 3-pointer
    if random.random() < GAME_PARAMS['three_point_probability']:
        points = 3
    else:
        points = 2
    
    # Update scores
    if team_type == 'home':
        score_home += points
    else:
        score_away += points
    
    # Create event
    event = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'game_time': format_game_time(quarter, minutes, seconds),
        'team': team_name,
        'player': player,
        'points': points,
        'score_home': score_home,
        'score_away': score_away
    }
    
    return event, score_home, score_away

def simulate_basketball_game(producer, topic_name: str):
    """
    Simulate a complete basketball game and stream events to Kafka
    
    Args:
        producer: KafkaProducer instance
        topic_name: Kafka topic to send messages to
    """
    logger.info("Starting basketball game simulation...")
    logger.info(f"{TEAMS['home']['name']} vs {TEAMS['away']['name']}")
    
    # Initialize game state
    score_home = 0
    score_away = 0
    total_events = 0
    
    # Simulate all quarters
    for quarter in range(1, GAME_PARAMS['quarters'] + 1):
        logger.info(f"\n=== Quarter {quarter} ===")
        
        # Track time in quarter (counting down)
        minutes = GAME_PARAMS['minutes_per_quarter']
        seconds = 0
        
        # Generate scoring events for this quarter
        quarter_events = random.randint(8, 15)  # 8-15 scoring events per quarter
        
        for _ in range(quarter_events):
            # Generate scoring event
            event, score_home, score_away = generate_scoring_event(
                score_home, score_away, quarter, minutes, seconds
            )
            
            # Convert to JSON
            message = json.dumps(event)
            
            # Send to Kafka
            try:
                producer.send(topic_name, value=message)
                total_events += 1
                
                # Log the event
                logger.info(
                    f"{event['game_time']} - {event['team']}: {event['player']} "
                    f"scores {event['points']} points! "
                    f"Score: {score_home}-{score_away}"
                )
                
            except Exception as e:
                logger.error(f"Error sending message: {e}")
            
            # Simulate time passing
            time_delay = random.uniform(
                GAME_PARAMS['seconds_between_scores'][0],
                GAME_PARAMS['seconds_between_scores'][1]
            )
            time.sleep(time_delay / 10)  # Speed up simulation (divide by 10)
            
            # Update game clock (decrement)
            seconds_passed = random.randint(20, 60)
            total_seconds = minutes * 60 + seconds - seconds_passed
            
            if total_seconds < 0:
                total_seconds = 0
            
            minutes = total_seconds // 60
            seconds = total_seconds % 60
    
    # Flush remaining messages
    producer.flush()
    
    logger.info("\n" + "="*50)
    logger.info("GAME FINAL")
    logger.info(f"{TEAMS['home']['name']}: {score_home}")
    logger.info(f"{TEAMS['away']['name']}: {score_away}")
    logger.info(f"Total scoring events: {total_events}")
    logger.info("="*50)

#####################################
# Main Function
#####################################

def main():
    """Main entry point for basketball producer"""
    
    logger.info("Basketball Producer Starting...")
    
    # Verify Kafka is ready
    verify_services()
    
    # Create topic (fresh start)
    create_kafka_topic(TOPIC_NAME)
    
    # Create producer
    producer = create_kafka_producer()
    
    if producer is None:
        logger.error("Failed to create Kafka producer. Exiting...")
        return
    
    try:
        # Run game simulation
        simulate_basketball_game(producer, TOPIC_NAME)
        
    except KeyboardInterrupt:
        logger.info("\nGame simulation interrupted by user.")
    except Exception as e:
        logger.error(f"Error during game simulation: {e}")
    finally:
        # Close producer
        logger.info("Closing Kafka producer...")
        producer.close()
        logger.info("Producer closed. Goodbye!")

#####################################
# Conditional Execution
#####################################

if __name__ == "__main__":
    main()
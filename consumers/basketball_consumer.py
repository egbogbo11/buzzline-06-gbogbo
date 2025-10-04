"""
Basketball Consumer
Consumes basketball scoring events from Kafka and performs real-time analytics
"""

#####################################
# Import Modules
#####################################

import json
from collections import deque

# Import from existing utils
from utils.utils_consumer import create_kafka_consumer
from utils.utils_logger import logger
from utils.message_validator import validate_message

# Import visualizer
from consumers.visualizer import BasketballVisualizer

# Import game configuration
from data.game_config import get_all_team_names

#####################################
# Configuration
#####################################

TOPIC_NAME = "basketball-game"
CONSUMER_GROUP = "basketball-analytics-group"
MAX_EVENTS_TO_DISPLAY = 50  # Keep last 50 events for visualization

#####################################
# Analytics Class
#####################################

class BasketballAnalytics:
    """Processes basketball scoring events and maintains game state"""
    
    def __init__(self):
        """Initialize analytics tracking"""
        self.home_team, self.away_team = get_all_team_names()
        
        # Score tracking
        self.score_home = 0
        self.score_away = 0
        
        # Event counting
        self.events_per_team = {
            self.home_team: 0,
            self.away_team: 0
        }
        
        # Data for visualization (using deque for efficient FIFO)
        self.game_times = deque(maxlen=MAX_EVENTS_TO_DISPLAY)
        self.home_scores = deque(maxlen=MAX_EVENTS_TO_DISPLAY)
        self.away_scores = deque(maxlen=MAX_EVENTS_TO_DISPLAY)
        
        # Momentum tracking
        self.last_scoring_team = None
        self.consecutive_scores = 0
        
        self.total_events = 0
        
        logger.info(f"Analytics initialized: {self.home_team} vs {self.away_team}")
    
    def process_event(self, event_data: dict):
        """
        Process a single scoring event
        
        Args:
            event_data: Dictionary containing scoring event information
        """
        self.total_events += 1
        
        # Extract event details
        game_time = event_data['game_time']
        team = event_data['team']
        player = event_data['player']
        points = event_data['points']
        self.score_home = event_data['score_home']
        self.score_away = event_data['score_away']
        
        # Update event count
        if team in self.events_per_team:
            self.events_per_team[team] += 1
        
        # Track momentum
        if team == self.last_scoring_team:
            self.consecutive_scores += points
        else:
            self.consecutive_scores = points
            self.last_scoring_team = team
        
        # Check for momentum shift (6+ consecutive points)
        if self.consecutive_scores >= 6:
            logger.info(f" MOMENTUM SHIFT: {team} has scored {self.consecutive_scores} consecutive points!")
        
        # Add to visualization data
        self.game_times.append(game_time)
        self.home_scores.append(self.score_home)
        self.away_scores.append(self.score_away)
        
        # Calculate point differential
        differential = abs(self.score_home - self.score_away)
        leader = self.home_team if self.score_home > self.score_away else self.away_team
        
        # Log event
        logger.info(
            f"Event #{self.total_events} | {game_time} | "
            f"{team}: {player} scores {points} pts | "
            f"Score: {self.score_home}-{self.score_away} | "
            f"{leader} leads by {differential}"
        )
    
    def get_visualization_data(self) -> dict:
        """
        Get current data for visualization
        
        Returns:
            Dictionary containing visualization data
        """
        return {
            'game_times': list(self.game_times),
            'home_scores': list(self.home_scores),
            'away_scores': list(self.away_scores),
            'home_team': self.home_team,
            'away_team': self.away_team,
            'current_home_score': self.score_home,
            'current_away_score': self.score_away
        }
    
    def get_summary(self) -> str:
        """Generate game summary statistics"""
        differential = abs(self.score_home - self.score_away)
        leader = self.home_team if self.score_home > self.score_away else self.away_team
        
        summary = f"\n{'='*50}\n"
        summary += "GAME SUMMARY\n"
        summary += f"{'='*50}\n"
        summary += f"{self.home_team}: {self.score_home} ({self.events_per_team[self.home_team]} scores)\n"
        summary += f"{self.away_team}: {self.score_away} ({self.events_per_team[self.away_team]} scores)\n"
        summary += f"Leader: {leader} by {differential} points\n"
        summary += f"Total events processed: {self.total_events}\n"
        summary += f"{'='*50}\n"
        
        return summary

#####################################
# Main Consumer Function
#####################################

def consume_basketball_events():
    """
    Main consumer function that reads from Kafka and processes events
    """
    logger.info("Basketball Consumer Starting...")
    logger.info(f"Subscribing to topic: {TOPIC_NAME}")
    
    # Create Kafka consumer
    try:
        consumer = create_kafka_consumer(
            topic_provided=TOPIC_NAME,
            group_id_provided=CONSUMER_GROUP
        )
    except Exception as e:
        logger.error(f"Failed to create consumer: {e}")
        return
    
    # Initialize analytics
    analytics = BasketballAnalytics()
    
    # Initialize visualizer
    visualizer = BasketballVisualizer(analytics)
    
    logger.info("Consumer ready. Waiting for messages...")
    logger.info("Press Ctrl+C to stop.\n")
    
    try:
        # Start visualization in a separate thread
        visualizer.start()
        
        # Consume messages
        for message in consumer:
            try:
                # Get message value (already deserialized to string by utils_consumer)
                message_str = message.value
                
                # Validate message
                is_valid, event_data, error_msg = validate_message(message_str)
                
                if not is_valid:
                    logger.warning(f"Invalid message: {error_msg}")
                    continue
                
                # Process the event
                analytics.process_event(event_data)
                
                # Update visualization
                visualizer.update()
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    except KeyboardInterrupt:
        logger.info("\nConsumer interrupted by user.")
    except Exception as e:
        logger.error(f"Consumer error: {e}")
    finally:
        # Print final summary
        logger.info(analytics.get_summary())
        
        # Stop visualizer
        visualizer.stop()
        
        # Close consumer
        logger.info("Closing Kafka consumer...")
        consumer.close()
        logger.info("Consumer closed. Goodbye!")

#####################################
# Main Entry Point
#####################################

def main():
    """Main entry point"""
    consume_basketball_events()

#####################################
# Conditional Execution
#####################################

if __name__ == "__main__":
    main()
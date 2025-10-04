"""
Basketball Visualizer
Handles real-time Matplotlib animation of basketball game scores
"""

#####################################
# Import Modules
#####################################

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from consumers.basketball_consumer import BasketballAnalytics

from utils.utils_logger import logger

#####################################
# Visualizer Class
#####################################

class BasketballVisualizer:
    """Manages real-time visualization of basketball game scores"""
    
    def __init__(self, analytics: 'BasketballAnalytics'):
        """
        Initialize the visualizer
        
        Args:
            analytics: BasketballAnalytics instance to get data from
        """
        self.analytics = analytics
        self.fig: Figure = None
        self.ax: Axes = None
        self.animation_obj = None
        self.running = False
        
        logger.info("Visualizer initialized")
    
    def setup_plot(self):
        """Set up the matplotlib figure and axes"""
        plt.style.use('seaborn-v0_8-darkgrid')
        
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.fig.suptitle('Live Basketball Game Score Tracker - Kafka Stream', 
                         fontsize=16, fontweight='bold')
        
        self.ax.set_xlabel('Game Progression', fontsize=12)
        self.ax.set_ylabel('Points', fontsize=12)
        self.ax.set_ylim(0, 120)
        self.ax.grid(True, alpha=0.3)
        
        logger.info("Plot setup complete")
    
    def animate(self, frame):
        """
        Animation function called by FuncAnimation
        
        Args:
            frame: Frame number (unused but required by FuncAnimation)
        """
        # Get current data from analytics
        data = self.analytics.get_visualization_data()
        
        # Clear previous plot
        self.ax.clear()
        
        # Re-apply styling
        self.ax.set_xlabel('Game Progression', fontsize=12)
        self.ax.set_ylabel('Points', fontsize=12)
        self.ax.set_ylim(0, 120)
        self.ax.grid(True, alpha=0.3)
        
        # Only plot if we have data
        if len(data['game_times']) > 0:
            # Create x-axis (just indices for simplicity)
            x_vals = list(range(len(data['game_times'])))
            
            # Plot both teams' scores
            self.ax.plot(x_vals, data['home_scores'], 
                        marker='o', linewidth=2, markersize=6,
                        color='#1f77b4', label=data['home_team'])
            
            self.ax.plot(x_vals, data['away_scores'], 
                        marker='o', linewidth=2, markersize=6,
                        color='#ff7f0e', label=data['away_team'])
            
            # Update x-axis labels with game times (show subset to avoid crowding)
            step = max(1, len(data['game_times']) // 10)
            tick_positions = x_vals[::step]
            tick_labels = [data['game_times'][i] for i in tick_positions]
            
            self.ax.set_xticks(tick_positions)
            self.ax.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            # Calculate point differential
            differential = abs(data['current_home_score'] - data['current_away_score'])
            if data['current_home_score'] > data['current_away_score']:
                leader = data['home_team']
            elif data['current_away_score'] > data['current_home_score']:
                leader = data['away_team']
            else:
                leader = "Tied"
            
            # Add legend with current scores
            legend_text = [
                f"{data['home_team']}: {data['current_home_score']}",
                f"{data['away_team']}: {data['current_away_score']}"
            ]
            self.ax.legend(legend_text, loc='upper left', fontsize=10)
            
            # Add annotation with game status
            if leader != "Tied":
                status_text = f"{leader} leads by {differential}"
            else:
                status_text = "Game is tied!"
            
            self.ax.text(0.98, 0.02, status_text,
                        transform=self.ax.transAxes,
                        fontsize=11, fontweight='bold',
                        ha='right', va='bottom',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        else:
            # No data yet
            self.ax.text(0.5, 0.5, 'Waiting for game data...',
                        transform=self.ax.transAxes,
                        fontsize=14, ha='center', va='center')
        
        plt.tight_layout()
    
    def start(self):
        """Start the visualization in a separate thread"""
        if self.running:
            logger.warning("Visualizer already running")
            return
        
        self.running = True
        
        # Set up plot
        self.setup_plot()
        
        # Create animation
        # interval=1000 means update every 1000ms (1 second)
        self.animation_obj = animation.FuncAnimation(
            self.fig, 
            self.animate,
            interval=1000,
            cache_frame_data=False
        )
        
        logger.info("Starting visualization...")
        
        # Start plot in non-blocking mode
        plt.ion()
        plt.show()
    
    def update(self):
        """Force an update of the visualization"""
        if self.running and self.fig is not None:
            try:
                self.fig.canvas.draw_idle()
                self.fig.canvas.flush_events()
            except Exception as e:
                logger.debug(f"Update error (likely normal during shutdown): {e}")
    
    def stop(self):
        """Stop the visualization"""
        if not self.running:
            return
        
        logger.info("Stopping visualizer...")
        self.running = False
        
        if self.animation_obj is not None:
            self.animation_obj.event_source.stop()
        
        plt.close(self.fig)
        logger.info("Visualizer stopped")
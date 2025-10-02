# buzzline-06-gbogbo

# Basketball Game Score Tracker - Kafka Streaming Analytics

## Overview

This project demonstrates real-time streaming analytics using Apache Kafka to simulate and visualize a live basketball game. The system streams scoring events through Kafka and provides dynamic visualization of the game's progression, showing running scores, point differentials, and momentum shifts between two competing teams.

## Project Focus

Real-time basketball game simulation that streams scoring events through Kafka and visualizes the running score, point differential, and momentum shifts between two teams throughout a game.

## Key Features

- **Kafka-based streaming architecture** for distributed message processing
- **Real-time score tracking** for home and away teams
- **Dynamic visualization** using Matplotlib animations
- **Momentum detection** to identify scoring runs
- **Simulated game data** with realistic pacing and scoring patterns

## Use Case

This project simulates the backend of a sports analytics dashboard, similar to what you'd see on ESPN or sports betting platforms, where live game data is streamed and processed to provide instant insights and visualizations to fans and analysts.

## Technologies Used

- **Apache Kafka** - Message streaming platform
- **Python** - Producer and consumer implementation
- **Matplotlib** - Real-time data visualization
- **Docker** - Containerized Kafka/Zookeeper setup
- **JSON** - Message serialization format
#!/bin/bash

# Start Django server
echo "Starting Django server..."
python ../manage.py runserver &
DJANGO_PID=$!

# Wait for Django to start
sleep 5

# Start user simulator
echo "Starting user simulator..."
python user_simulator.py &
USER_SIM_PID=$!

# Start camera simulator
echo "Starting camera simulator..."
python camera_simulator.py

# Cleanup when camera simulator exits
kill $DJANGO_PID
kill $USER_SIM_PID

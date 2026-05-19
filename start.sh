#!/bin/bash
cd "$(dirname "$0")" && python3 server.py &
sleep 0.4 && open http://localhost:8766/todos.html

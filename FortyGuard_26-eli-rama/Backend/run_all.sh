#!/bin/bash
source venv/bin/activate
alembic revision --autogenerate -m "initial"
alembic upgrade head
echo "Starting backend..."
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
SERVER_PID=$!
sleep 5
echo "Running smoke tests..."
python test_smoke.py http://127.0.0.1:8000
TEST_EXIT=$?
kill $SERVER_PID
exit $TEST_EXIT

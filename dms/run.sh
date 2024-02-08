#!/bin/bash
set -e

echo service preprocess start.
mkdir -p /tmp/llm-bench-sys/log/
touch /tmp/llm-bench-sys/log/access.log
touch /tmp/llm-bench-sys/log/error.log
chmod 777 src
echo service preprocess finish.

echo service start ...

exec gunicorn manager:app \
        --bind 0.0.0.0:8000 \
        --preload \
        --workers 4 \
        --log-level debug \
        --access-logfile=/tmp/llm-bench-sys/log/access.log \
        --error-logfile=/tmp/llm-bench-sys/log/error.log


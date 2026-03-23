#!/bin/bash
# Test for lesson03_project

# Run the test (example: compare output of solution.py)
output=$(python3 solution.py 2>&1)
expected="Hello, World!"

if [ "$output" == "$expected" ]; then
    echo "✅ Test passed"
    exit 0
else
    echo "❌ Test failed"
    echo "Expected: $expected"
    echo "Got: $output"
    exit 1
fi

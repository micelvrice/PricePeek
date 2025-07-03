#!/bin/bash

# Check if product name is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 \"product name\""
    echo "Example: $0 \"Sony WH-1000XM5 headphones\""
    exit 1
fi

# Configuration
API_TOKEN="xxx"
PRODUCT_NAME="$1"

echo "Searching for: $PRODUCT_NAME"
echo "Creating job..."

# Create job and capture response
JOB_RESPONSE=$(curl -s "https://api.priceapi.com/v2/jobs" \
    -X POST \
    -d "token=$API_TOKEN" \
    -d "country=us" \
    -d "source=google_shopping" \
    -d "topic=search_results" \
    -d "key=term" \
    -d "max_age=43200" \
    -d "max_pages=1" \
    -d "sort_by=ranking_descending" \
    -d "condition=any" \
    -d "values=$PRODUCT_NAME")

# Extract job ID using grep and sed
JOB_ID=$(echo "$JOB_RESPONSE" | grep -o '"job_id":"[^"]*' | sed 's/"job_id":"//')

if [ -z "$JOB_ID" ]; then
    echo "Error: Failed to create job"
    echo "Response: $JOB_RESPONSE"
    exit 1
fi

echo "Job created with ID: $JOB_ID"
echo "Waiting for job to complete..."

# Wait for job to complete (check every 2 seconds, max 30 seconds)
COUNTER=0
MAX_WAIT=30

while [ $COUNTER -lt $MAX_WAIT ]; do
    sleep 2
    COUNTER=$((COUNTER + 2))
    
    # Check job status
    STATUS_RESPONSE=$(curl -s "https://api.priceapi.com/v2/jobs/$JOB_ID?token=$API_TOKEN")
    STATUS=$(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*' | sed 's/"status":"//')
    
    if [ "$STATUS" = "finished" ]; then
        echo "Job completed!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "Job failed!"
        exit 1
    fi
    
    echo "Status: $STATUS (waited ${COUNTER}s)"
done

if [ $COUNTER -ge $MAX_WAIT ]; then
    echo "Timeout: Job did not complete within $MAX_WAIT seconds"
    exit 1
fi

# Download results
echo "Downloading results..."
RESULTS=$(curl -s -L "https://api.priceapi.com/v2/jobs/$JOB_ID/download.json?token=$API_TOKEN")

# Extract prices and calculate average
echo "Calculating average price..."

# Extract all prices (excluding shipping) and filter out suspicious prices
PRICES=$(echo "$RESULTS" | grep -o '"price":"[^"]*' | sed 's/"price":"//' | grep -v '^$')
MIN_PRICES=$(echo "$RESULTS" | grep -o '"min_price":"[^"]*' | sed 's/"min_price":"//' | grep -v '^$')

# Combine all prices
ALL_PRICES=$(echo -e "$PRICES\n$MIN_PRICES" | grep -v '^$' | sort -n | uniq)

# Filter out unrealistic prices (less than $10 or more than $10000)
FILTERED_PRICES=$(echo "$ALL_PRICES" | awk '$1 >= 10 && $1 <= 10000 {print}')

# Count valid prices
COUNT=$(echo "$FILTERED_PRICES" | wc -l | tr -d ' ')

if [ "$COUNT" -eq 0 ]; then
    echo "No valid prices found"
    exit 1
fi

# Calculate average
AVERAGE=$(echo "$FILTERED_PRICES" | awk '{sum += $1} END {if (NR > 0) printf "%.2f", sum/NR}')

# Get min and max for context
MIN_PRICE=$(echo "$FILTERED_PRICES" | head -n1)
MAX_PRICE=$(echo "$FILTERED_PRICES" | tail -n1)

# Output results
echo ""
echo "=== PRICE ANALYSIS ==="
echo "Product: $PRODUCT_NAME"
echo "Valid prices found: $COUNT"
echo "Average price: \$$AVERAGE"
echo "Price range: \$$MIN_PRICE - \$$MAX_PRICE"
echo "===================="

# Optional: Save detailed results
if [ ! -z "$2" ] && [ "$2" = "--save" ]; then
    FILENAME="price_report_$(date +%Y%m%d_%H%M%S).json"
    echo "$RESULTS" > "$FILENAME"
    echo "Full results saved to: $FILENAME"
fi

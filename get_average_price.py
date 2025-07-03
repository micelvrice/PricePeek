#!/usr/bin/env python3

import requests
import json
import time
import sys
import statistics
from typing import List, Dict, Optional

class PriceAPI:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.priceapi.com/v2"
    
    def create_job(self, product_name: str) -> Optional[str]:
        """Create a price search job and return the job ID"""
        data = {
            "token": self.token,
            "country": "us",
            "source": "google_shopping",
            "topic": "search_results",
            "key": "term",
            "max_age": "43200",
            "max_pages": "1",
            "sort_by": "ranking_descending",
            "condition": "any",
            "values": product_name
        }
        
        try:
            response = requests.post(f"{self.base_url}/jobs", data=data)
            response.raise_for_status()
            job_data = response.json()
            return job_data.get("job_id")
        except Exception as e:
            print(f"Error creating job: {e}")
            return None
    
    def wait_for_job(self, job_id: str, max_wait: int = 30) -> bool:
        """Wait for job to complete"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.base_url}/jobs/{job_id}?token={self.token}")
                response.raise_for_status()
                status = response.json().get("status")
                
                if status == "finished":
                    return True
                elif status == "failed":
                    print("Job failed!")
                    return False
                
                print(f"Status: {status} (waited {int(time.time() - start_time)}s)")
                time.sleep(2)
                
            except Exception as e:
                print(f"Error checking status: {e}")
                return False
        
        print(f"Timeout: Job did not complete within {max_wait} seconds")
        return False
    
    def get_results(self, job_id: str) -> Optional[Dict]:
        """Download job results"""
        try:
            response = requests.get(f"{self.base_url}/jobs/{job_id}/download.json?token={self.token}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error downloading results: {e}")
            return None
    
    def extract_prices(self, results: Dict) -> List[float]:
        """Extract valid prices from results"""
        prices = []
        
        if not results or "results" not in results:
            return prices
        
        for result in results["results"]:
            if "content" in result and "search_results" in result["content"]:
                for item in result["content"]["search_results"]:
                    # Extract individual prices
                    if "price" in item and item["price"]:
                        try:
                            price = float(str(item["price"]).replace(",", ""))
                            if 10 <= price <= 10000:  # Filter unrealistic prices
                                prices.append(price)
                        except (ValueError, TypeError):
                            pass
                    
                    # Extract min prices from product listings
                    if "min_price" in item and item["min_price"]:
                        try:
                            price = float(str(item["min_price"]).replace(",", ""))
                            if 10 <= price <= 10000:  # Filter unrealistic prices
                                prices.append(price)
                        except (ValueError, TypeError):
                            pass
        
        return prices
    
    def get_average_price(self, product_name: str) -> Optional[Dict[str, float]]:
        """Get average price for a product"""
        print(f"Searching for: {product_name}")
        
        # Create job
        print("Creating job...")
        job_id = self.create_job(product_name)
        if not job_id:
            return None
        
        print(f"Job created with ID: {job_id}")
        print("Waiting for job to complete...")
        
        # Wait for completion
        if not self.wait_for_job(job_id):
            return None
        
        print("Job completed!")
        print("Downloading results...")
        
        # Get results
        results = self.get_results(job_id)
        if not results:
            return None
        
        # Extract and analyze prices
        print("Calculating average price...")
        prices = self.extract_prices(results)
        
        if not prices:
            print("No valid prices found")
            return None
        
        # Calculate statistics
        average = statistics.mean(prices)
        median = statistics.median(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        return {
            "product": product_name,
            "count": len(prices),
            "average": round(average, 2),
            "median": round(median, 2),
            "min": round(min_price, 2),
            "max": round(max_price, 2),
            "prices": sorted(prices)
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python get_average_price.py \"product name\"")
        print("Example: python get_average_price.py \"Sony WH-1000XM5 headphones\"")
        sys.exit(1)
    
    # API token
    token = "xxx"
    
    # Get product name from command line
    product_name = sys.argv[1]
    
    # Initialize API client
    api = PriceAPI(token)
    
    # Get average price
    result = api.get_average_price(product_name)
    
    if result:
        print("\n=== PRICE ANALYSIS ===")
        print(f"Product: {result['product']}")
        print(f"Valid prices found: {result['count']}")
        print(f"Average price: ${result['average']}")
        print(f"Median price: ${result['median']}")
        print(f"Price range: ${result['min']} - ${result['max']}")
        print("====================")
        
        # Save to JSON if requested
        if len(sys.argv) > 2 and sys.argv[2] == "--json":
            filename = f"price_analysis_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nFull results saved to: {filename}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

import requests
import sys
import time

def send_request(url):
    """
    Sends a single, proper HTTP GET request to the specified URL.
    """
    print(f"Attempting to connect to: {url}\n")
    
    try:
        # 1. Start timer
        start_time = time.time()
        
        # 2. Send the request. 
        #    requests.get() handles all the complexity:
        #    - DNS lookup
        #    - TCP connection (not UDP)
        #    - SSL/TLS handshake for HTTPS
        #    - Sending the HTTP headers
        response = requests.get(url, timeout=5) # 5-second timeout
        
        # 3. Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # 4. Print the results
        print("--- Connection Result ---")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed_time:.2f} seconds")
        
        if response.status_code == 200:
            print("Result: Success (200 OK)")
        else:
            print(f"Result: Connected, but site returned a non-200 status.")

    # Handle specific errors
    except requests.exceptions.ConnectionError as e:
        print("--- Connection Result ---")
        print("Failed: A connection error occurred.")
        print("Error details (e.g., DNS failure, connection refused):")
        print(e)
    except requests.exceptions.Timeout:
        print("--- Connection Result ---")
        print("Failed: The request timed out (took longer than 5 seconds).")
    except requests.exceptions.RequestException as e:
        # A catch-all for any other 'requests' library error
        print("--- Connection Result ---")
        print(f"Failed: An unexpected error occurred: {e}")

# --- Main part of the script ---
if __name__ == "__main__":
    
    # Check if a URL was given as a command-line argument
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        # If no URL is given, use a default and inform the user
        target_url = "https://example.com"
        print(f"No URL provided. Using default: {target_url}\n")
    
    # Run the function to send the request
    send_request(target_url)

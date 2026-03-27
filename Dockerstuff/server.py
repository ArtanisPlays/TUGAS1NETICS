from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
from datetime import datetime, timezone, timedelta

# Record the start time
START_TIME = time.time()
# Set timezone to WIB (UTC+7)
WIB = timezone(timedelta(hours=7))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Strictly check that the path is exactly /health
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            uptime_seconds = time.time() - START_TIME
            
            response = {
                "nama": "Rendy Tanuwijaya",
                "nrp": "5025241099",
                "status": "UP",
                "timestamp": datetime.now(WIB).isoformat(),
                "uptime": f"{int(uptime_seconds)} seconds"
            }
            # Send the JSON payload
            self.wfile.write(json.dumps(response).encode())
        else:
            # Reject any other path like / or /test
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

# Start the server on port 8080
server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
print("Python API running on port 8080...")
server.serve_forever()
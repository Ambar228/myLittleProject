from flask import Flask, Response, request
import requests
import hashlib
import redis
import html
import json
import socket
import time
from datetime import datetime

app = Flask(__name__)
cache = redis.StrictRedis(host='redis', port=6379, db=0)
salt = "UNIQUE_SALT"
default_name = 'Vadim Cucold'

class LogstashLogger:
    def __init__(self, host='logstash', port=5001):
        self.host = host
        self.port = port
        self.timeout = 2
        
    def send_log(self, level, message, extra_data=None):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "message": message,
            "service": "identidock",
            "hostname": socket.gethostname()
        }
        
        if extra_data:
            log_entry.update(extra_data)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            sock.send((json.dumps(log_entry) + "\n").encode())
            sock.close()
            print(f"Log sent: {message}")
            return True
        except Exception as e:
            print(f"Failed to send log: {e}")
            return False

logger = LogstashLogger(host='logstash', port=5001)

@app.before_request
def log_request_start():
    if request.endpoint and request.endpoint != 'static':
        request.start_time = time.time()
        logger.send_log("INFO", f"Request started: {request.method} {request.path}", {
            "endpoint": request.endpoint,
            "method": request.method,
            "path": request.path,
            "user_agent": request.headers.get('User-Agent', ''),
            "ip": request.remote_addr
        })

@app.after_request
def log_request_end(response):
    if hasattr(request, 'start_time') and request.endpoint and request.endpoint != 'static':
        response_time = time.time() - request.start_time
        logger.send_log("INFO", f"Request completed: {request.method} {request.path} - {response.status_code}", {
            "endpoint": request.endpoint,
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "response_time": round(response_time, 3),
            "response_size": len(response.get_data()) if response.get_data() else 0
        })
    return response

@app.route('/', methods=['GET', 'POST'])
def mainpage():
    name = default_name
    if request.method == 'POST':
        name = html.escape(request.form['name'], quote=True)
        logger.send_log("INFO", f"User submitted name: {name}", {
            "endpoint": "/",
            "form_data": {"name": name}
        })

    salted_name = salt + name
    name_hash = hashlib.sha256(salted_name.encode()).hexdigest()

    header = '<html><head><title>Identidock</title></head><body>'
    body = '''<form method="POST">
    Hello <input type="text" name="name" value="{0}">
    <input type="submit" value="submit">
    </form>
    <p>You look like a:
    <img src="/monster/{1}"/>
    '''.format(name, name_hash)
    footer = '</body></html>'

    logger.send_log("INFO", f"Main page rendered for: {name}", {
        "endpoint": "/",
        "name_hash": name_hash
    })

    return header + body + footer

@app.route('/monster/<name>')
def get_identicon(name):
    logger.send_log("INFO", f"Monster generation requested", {
        "endpoint": "/monster",
        "requested_name": name
    })
    
    name = html.escape(name, quote=True)
    image = cache.get(name)
    
    if image is None:
        logger.send_log("INFO", f"Cache miss for: {name}", {
            "endpoint": "/monster",
            "cache_status": "miss"
        })
        try:
            r = requests.get(f'http://dnmonster:8080/monster/{name}?size=80', timeout=5)
            r.raise_for_status()
            image = r.content
            cache.set(name, image)
            logger.send_log("INFO", f"Image generated and cached", {
                "endpoint": "/monster",
                "cache_status": "set",
                "image_size": len(image)
            })
        except requests.exceptions.RequestException as e:
            logger.send_log("ERROR", f"Failed to generate monster: {e}", {
                "endpoint": "/monster",
                "error": str(e),
                "cache_status": "error"
            })
            return "Error generating image", 500
    else:
        logger.send_log("INFO", f"Cache hit for: {name}", {
            "endpoint": "/monster", 
            "cache_status": "hit",
            "image_size": len(image)
        })

    return Response(image, mimetype='image/png')

@app.errorhandler(404)
def not_found(error):
    logger.send_log("WARNING", f"Page not found: {request.path}", {
        "endpoint": "error",
        "error_type": "404",
        "path": request.path
    })
    return "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    logger.send_log("ERROR", f"Internal server error: {error}", {
        "endpoint": "error", 
        "error_type": "500",
        "path": request.path
    })
    return "Internal server error", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

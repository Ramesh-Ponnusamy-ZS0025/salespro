"""
Single Flask server to serve all microsites on one port
Each microsite accessible at: http://localhost:3001/<microsite_id>
"""
from flask import Flask, send_from_directory, abort
from pathlib import Path
import logging
import threading

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store microsite paths: {microsite_id: directory_path}
MICROSITE_PATHS = {}
MICROSITES_BASE_DIR = Path(__file__).parent / "microsites"

def register_microsite(microsite_id: str, directory_path: str):
    """Register a new microsite with its directory path"""
    MICROSITE_PATHS[microsite_id] = directory_path
    logger.info(f"Registered microsite: {microsite_id} -> {directory_path}")

def unregister_microsite(microsite_id: str):
    """Unregister a microsite"""
    if microsite_id in MICROSITE_PATHS:
        del MICROSITE_PATHS[microsite_id]
        logger.info(f"Unregistered microsite: {microsite_id}")

@app.route('/')
def index():
    """Root endpoint - show list of available microsites"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Microsite Server</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
        <div class="container mx-auto px-4 py-16">
            <div class="max-w-4xl mx-auto">
                <h1 class="text-5xl font-bold text-white mb-4 text-center bg-gradient-to-r from-pink-500 to-violet-500 bg-clip-text text-transparent">
                    🚀 Microsite Server
                </h1>
                <p class="text-xl text-gray-300 text-center mb-12">
                    All your microsites in one place
                </p>

                <div class="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl">
                    <h2 class="text-2xl font-semibold text-white mb-6">Active Microsites ({count})</h2>
                    {microsites}
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    if not MICROSITE_PATHS:
        microsites_html = '<p class="text-gray-400 text-center py-8">No microsites deployed yet</p>'
    else:
        microsites_html = '<div class="space-y-4">'
        for microsite_id, path in MICROSITE_PATHS.items():
            microsites_html += f'''
            <a href="/{microsite_id}/" class="block p-4 bg-white/5 hover:bg-white/10 rounded-lg transition-all hover:scale-105">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-white font-semibold">/{microsite_id}/</p>
                        <p class="text-gray-400 text-sm">{Path(path).name}</p>
                    </div>
                    <svg class="w-6 h-6 text-pink-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
                    </svg>
                </div>
            </a>
            '''
        microsites_html += '</div>'

    return html.format(count=len(MICROSITE_PATHS), microsites=microsites_html)

@app.route('/<microsite_id>/')
@app.route('/<microsite_id>/<path:filename>')
def serve_microsite(microsite_id, filename='index.html'):
    """Serve files for a specific microsite"""
    if microsite_id not in MICROSITE_PATHS:
        abort(404, description=f"Microsite '{microsite_id}' not found")

    microsite_dir = MICROSITE_PATHS[microsite_id]

    try:
        # If filename is empty or just '/', serve index.html
        if not filename or filename == '/':
            filename = 'index.html'

        return send_from_directory(microsite_dir, filename)
    except FileNotFoundError:
        abort(404, description=f"File '{filename}' not found in microsite '{microsite_id}'")

# Global server instance
_server_thread = None
_server_started = False

def start_microsite_server(port=3001):
    """Start the Flask server in a background thread"""
    global _server_thread, _server_started

    if _server_started:
        logger.info("Microsite server already running")
        return

    def run_server():
        logger.info(f"Starting microsite server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

    _server_thread = threading.Thread(target=run_server, daemon=True)
    _server_thread.start()
    _server_started = True

    logger.info(f"✓ Microsite server started on http://localhost:{port}")

def is_server_running():
    """Check if the server is running"""
    return _server_started

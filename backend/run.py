"""
Run Script for SalesPro Backend
Fixes the module import issue by running from correct directory
Configures Windows event loop for Playwright support
"""

import sys
from pathlib import Path
import asyncio
import platform

# Add parent directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Fix for Windows - Set event loop policy to support Playwright subprocesses
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    print("✓ Windows event loop policy set for Playwright support")

# Now import and run
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )

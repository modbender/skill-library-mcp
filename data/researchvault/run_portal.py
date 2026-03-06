
import sys
import os
import uvicorn

if __name__ == "__main__":
    # Add the current directory to sys.path so we can import 'scripts' and 'portal'
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    host = os.getenv("RESEARCHVAULT_PORTAL_HOST", "127.0.0.1")
    port = int(os.getenv("RESEARCHVAULT_PORTAL_PORT", "8000"))
    reload = os.getenv("RESEARCHVAULT_PORTAL_RELOAD", "true").lower() == "true"
    
    # Run the uvicorn server
    uvicorn.run("portal.backend.app.main:app", host=host, port=port, reload=reload)

import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    port_string = os.getenv("PORT", "8000")
    port_number = int(port_string)
    uvicorn.run("main:app", host="0.0.0.0", port=port_number, reload=True)

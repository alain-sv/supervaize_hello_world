from supervaizer_control import app, sv_server

# Expose the FastAPI app instance
__all__ = ["app"]


sv_server.launch(start_uvicorn=False)

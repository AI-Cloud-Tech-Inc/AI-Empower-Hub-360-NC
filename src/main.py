"""AI Empower Hub 360 - Main Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from src.core.config import config


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=config.app_name,
        version=config.app_version,
        description="Practical AI solutions for startups, entrepreneurs, and growing businesses",
        debug=config.debug,
    )

    # Configure CORS
    if config.get("api.cors.enabled", True):
        origins = config.get("api.cors.origins", ["*"])
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include routers
    from src.api import chatbot, automation, consulting
    app.include_router(chatbot.router, prefix=config.api_prefix)
    app.include_router(automation.router, prefix=config.api_prefix)
    app.include_router(consulting.router, prefix=config.api_prefix)

    # Serve static files from website directory
    website_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "website")
    
    @app.get("/")
    async def serve_index():
        """Serve the main index.html"""
        return FileResponse(os.path.join(website_path, "index.html"))
    
    @app.get("/api")
    async def api_root():
        """API root endpoint."""
        return {
            "name": config.app_name,
            "version": config.app_version,
            "api_version": "v1",
            "status": "running",
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    @app.get("/{path:path}")
    async def serve_static(path: str):
        """Serve static files"""
        file_path = os.path.join(website_path, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        # Try with .html extension
        html_path = os.path.join(website_path, f"{path}.html")
        if os.path.isfile(html_path):
            return FileResponse(html_path)
        # Fallback to index.html
        return FileResponse(os.path.join(website_path, "index.html"))

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=config.server_host,
        port=config.server_port,
        reload=config.debug,
    )
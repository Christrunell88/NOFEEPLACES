
# API Integration for Data Pipeline
# Add these routes to your FastAPI server.py

from fastapi import APIRouter, HTTPException
from datetime import datetime
import json
import asyncio
import subprocess
import sys
from pathlib import Path

pipeline_router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

@pipeline_router.get("/status")
async def get_pipeline_status():
    """Get current pipeline status"""
    try:
        status_file = Path('/app/data_pipeline/pipeline_status.json')
        if status_file.exists():
            with open(status_file, 'r') as f:
                status = json.load(f)
        else:
            status = {'status': 'not_deployed', 'message': 'Pipeline not found'}
        
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pipeline status: {e}")

@pipeline_router.post("/start")
async def start_pipeline():
    """Start the data gathering pipeline"""
    try:
        controller_path = Path('/app/data_pipeline/pipeline_controller.py')
        
        if not controller_path.exists():
            raise HTTPException(status_code=404, detail="Pipeline controller not found")
        
        # Start pipeline asynchronously
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(controller_path), 'start',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        return {
            "success": True,
            "message": "Pipeline started successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting pipeline: {e}")

@pipeline_router.post("/test")
async def test_pipeline():
    """Run pipeline tests"""
    try:
        controller_path = Path('/app/data_pipeline/pipeline_controller.py')
        
        if not controller_path.exists():
            raise HTTPException(status_code=404, detail="Pipeline controller not found")
        
        # Run tests
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(controller_path), 'test',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        success = process.returncode == 0
        
        return {
            "success": success,
            "message": "Tests completed",
            "test_results": stdout.decode()[-500:],  # Last 500 chars
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing pipeline: {e}")

# Add this to your main server.py:
# app.include_router(pipeline_router)

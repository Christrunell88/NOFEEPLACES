#!/usr/bin/env python3
"""
Data Pipeline Controller
Control and monitor the data gathering pipeline
"""
import asyncio
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

class PipelineController:
    def __init__(self):
        self.pipeline_dir = Path('/app/data_pipeline')
        self.scripts_dir = self.pipeline_dir / 'scripts'
        self.logs_dir = Path('/app/logs')
        self.status_file = self.pipeline_dir / 'pipeline_status.json'
    
    def get_status(self):
        """Get current pipeline status"""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                return json.load(f)
        return {'status': 'stopped', 'last_run': None}
    
    def update_status(self, status, details=None):
        """Update pipeline status"""
        status_data = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    async def start_pipeline(self):
        """Start the data pipeline"""
        print("🚀 Starting data gathering pipeline...")
        
        self.update_status('running', {'action': 'pipeline_start'})
        
        try:
            # Run the main pipeline
            pipeline_script = self.scripts_dir / 'real_estate_data_pipeline.py'
            
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(pipeline_script),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                print("✅ Pipeline completed successfully")
                self.update_status('completed', {
                    'return_code': process.returncode,
                    'output_lines': len(stdout.decode().split('\n'))
                })
            else:
                print("❌ Pipeline failed")
                self.update_status('failed', {
                    'return_code': process.returncode,
                    'error': stderr.decode()[:500]
                })
            
            return process.returncode == 0
            
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            self.update_status('error', {'exception': str(e)})
            return False
    
    def stop_pipeline(self):
        """Stop the pipeline (if running)"""
        print("🛑 Stopping pipeline...")
        self.update_status('stopped', {'action': 'manual_stop'})
    
    async def test_pipeline(self):
        """Run pipeline tests"""
        print("🧪 Running pipeline tests...")
        
        self.update_status('testing')
        
        try:
            test_script = self.scripts_dir / 'pipeline_edge_case_testing.py'
            
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(test_script),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            success = process.returncode == 0 and "100.0%" in stdout.decode()
            
            if success:
                print("✅ All tests passed")
                self.update_status('test_passed')
            else:
                print("❌ Some tests failed")
                self.update_status('test_failed')
            
            return success
            
        except Exception as e:
            print(f"❌ Test error: {e}")
            self.update_status('test_error', {'exception': str(e)})
            return False

async def main():
    controller = PipelineController()
    
    if len(sys.argv) < 2:
        print("Usage: python pipeline_controller.py [start|stop|test|status]")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'start':
        await controller.start_pipeline()
    elif command == 'stop':
        controller.stop_pipeline()
    elif command == 'test':
        await controller.test_pipeline()
    elif command == 'status':
        status = controller.get_status()
        print(f"Pipeline Status: {status}")
    else:
        print("Invalid command. Use: start, stop, test, or status")

if __name__ == "__main__":
    asyncio.run(main())

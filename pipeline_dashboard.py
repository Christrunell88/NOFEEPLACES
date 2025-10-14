#!/usr/bin/env python3
"""
Data Pipeline Production Dashboard
Monitor and control the deployed data gathering pipeline
"""
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

class PipelineDashboard:
    def __init__(self):
        self.pipeline_dir = Path('/app/data_pipeline')
        self.config_dir = Path('/app/config')
        self.logs_dir = Path('/app/logs')
        
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces_database')
    
    async def get_pipeline_health(self):
        """Get comprehensive pipeline health status"""
        health_data = {
            'deployment_status': 'unknown',
            'components_status': {},
            'database_status': {},
            'last_execution': {},
            'system_metrics': {}
        }
        
        try:
            # Check deployment config
            config_file = self.config_dir / 'deployment_config.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                health_data['deployment_status'] = config.get('status', 'unknown')
            
            # Check pipeline status
            status_file = self.pipeline_dir / 'pipeline_status.json'
            if status_file.exists():
                with open(status_file, 'r') as f:
                    status = json.load(f)
                health_data['last_execution'] = status
            
            # Check database health
            client = AsyncIOMotorClient(self.mongo_url)
            db = client[self.db_name]
            
            apartment_count = await db.apartments.count_documents({})
            verified_count = await db.apartments.count_documents({'is_verified': True})
            
            health_data['database_status'] = {
                'total_apartments': apartment_count,
                'verified_apartments': verified_count,
                'verification_rate': f"{(verified_count/apartment_count*100):.1f}%" if apartment_count > 0 else "0%"
            }
            
            client.close()
            
            # Check component files
            components = ['pipeline_controller.py', 'scheduler.py']
            for component in components:
                component_path = self.pipeline_dir / component
                health_data['components_status'][component] = component_path.exists()
            
        except Exception as e:
            health_data['error'] = str(e)
        
        return health_data
    
    async def get_execution_history(self):
        """Get pipeline execution history"""
        history = []
        
        try:
            # Check log files for execution history
            log_files = list(self.logs_dir.glob('*.log'))
            
            for log_file in log_files[-5:]:  # Last 5 log files
                try:
                    with open(log_file, 'r') as f:
                        content = f.read()
                        lines = content.split('\n')[-10:]  # Last 10 lines
                        
                    history.append({
                        'file': log_file.name,
                        'size': log_file.stat().st_size,
                        'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat(),
                        'recent_lines': len([l for l in lines if l.strip()])
                    })
                except Exception:
                    continue
                    
        except Exception as e:
            history.append({'error': str(e)})
        
        return history
    
    async def show_dashboard(self):
        """Display comprehensive pipeline dashboard"""
        print("📊 DATA PIPELINE PRODUCTION DASHBOARD")
        print("=" * 70)
        print(f"🕐 Dashboard Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Get health data
        health = await self.get_pipeline_health()
        
        print(f"\n🏥 PIPELINE HEALTH STATUS")
        print("-" * 40)
        print(f"Deployment Status: {health['deployment_status'].upper()}")
        
        if 'database_status' in health:
            db_status = health['database_status']
            print(f"Total Apartments: {db_status.get('total_apartments', 0)}")
            print(f"Verified Apartments: {db_status.get('verified_apartments', 0)}")
            print(f"Verification Rate: {db_status.get('verification_rate', '0%')}")
        
        print(f"\n🔧 COMPONENT STATUS")
        print("-" * 40)
        if 'components_status' in health:
            for component, status in health['components_status'].items():
                status_icon = "✅" if status else "❌"
                print(f"{status_icon} {component}")
        
        print(f"\n⚡ LAST EXECUTION")
        print("-" * 40)
        if 'last_execution' in health:
            last_exec = health['last_execution']
            print(f"Status: {last_exec.get('status', 'Unknown')}")
            print(f"Timestamp: {last_exec.get('timestamp', 'Unknown')}")
            if 'details' in last_exec:
                details = last_exec['details']
                print(f"Return Code: {details.get('return_code', 'Unknown')}")
        
        # Get execution history
        history = await self.get_execution_history()
        
        print(f"\n📈 EXECUTION HISTORY")
        print("-" * 40)
        if history:
            for entry in history[-3:]:  # Show last 3
                if 'error' not in entry:
                    print(f"• {entry['file']}: {entry['size']} bytes, {entry['recent_lines']} recent entries")
        else:
            print("No execution history available")
        
        print(f"\n🎛️  CONTROL COMMANDS")
        print("-" * 40)
        print("Manual Control:")
        print("  python /app/data_pipeline/pipeline_controller.py [start|test|status]")
        print("")
        print("API Control:")
        print("  GET  /api/pipeline/status")
        print("  POST /api/pipeline/activate")
        print("")
        print("Scheduled Execution:")
        print("  Daily at 3:00 AM (automatic)")
        print("  Weekly tests on Sunday 2:00 AM")
        
        return health

async def main():
    """Run pipeline dashboard"""
    dashboard = PipelineDashboard()
    health = await dashboard.show_dashboard()
    
    # Export dashboard data
    dashboard_data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'health_status': health
    }
    
    dashboard_file = Path('/app/logs/pipeline_dashboard.json')
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"\n💾 Dashboard data exported to: {dashboard_file}")

if __name__ == "__main__":
    asyncio.run(main())
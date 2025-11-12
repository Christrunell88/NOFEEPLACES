#!/usr/bin/env python3
"""
Data Pipeline Backend Testing Suite
Comprehensive testing of deployed data gathering pipeline as requested
"""
import asyncio
import aiohttp
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import time

class DataPipelineTestSuite:
    def __init__(self):
        # Get backend URL from environment
        self.backend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://auth-revamp-8.preview.emergentagent.com')
        self.api_base = f"{self.backend_url}/api"
        
        # Pipeline paths
        self.pipeline_dir = Path('/app/data_pipeline')
        self.controller_path = self.pipeline_dir / 'pipeline_controller.py'
        self.status_file = self.pipeline_dir / 'pipeline_status.json'
        
        # Test results
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
    
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        self.test_results['total_tests'] += 1
        if success:
            self.test_results['passed_tests'] += 1
            status = "✅ PASS"
        else:
            self.test_results['failed_tests'] += 1
            status = "❌ FAIL"
        
        result = {
            'test': test_name,
            'status': status,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results['test_details'].append(result)
        print(f"{status}: {test_name}")
        if details and not success:
            print(f"   Details: {details}")
    
    async def test_api_endpoints(self):
        """Test 1: API Endpoint Verification"""
        print("\n🔌 TESTING API ENDPOINTS")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            # Test GET /api/pipeline/status
            try:
                async with session.get(f"{self.api_base}/pipeline/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'success' in data and 'data' in data:
                            self.log_test("GET /api/pipeline/status endpoint", True, f"Status: {data.get('data', {}).get('status', 'unknown')}")
                        else:
                            self.log_test("GET /api/pipeline/status endpoint", False, "Invalid response format")
                    else:
                        self.log_test("GET /api/pipeline/status endpoint", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_test("GET /api/pipeline/status endpoint", False, str(e))
            
            # Test POST /api/pipeline/activate
            try:
                async with session.post(f"{self.api_base}/pipeline/activate") as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'success' in data and 'message' in data:
                            self.log_test("POST /api/pipeline/activate endpoint", True, data.get('message', ''))
                        else:
                            self.log_test("POST /api/pipeline/activate endpoint", False, "Invalid response format")
                    else:
                        self.log_test("POST /api/pipeline/activate endpoint", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_test("POST /api/pipeline/activate endpoint", False, str(e))
    
    def test_pipeline_controller(self):
        """Test 2: Pipeline Controller Testing"""
        print("\n🎛️  TESTING PIPELINE CONTROLLER")
        print("=" * 50)
        
        # Test controller file exists
        if self.controller_path.exists():
            self.log_test("Pipeline controller file exists", True, str(self.controller_path))
        else:
            self.log_test("Pipeline controller file exists", False, f"Not found at {self.controller_path}")
            return
        
        # Test controller status command
        try:
            result = subprocess.run([
                sys.executable, str(self.controller_path), 'status'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log_test("Pipeline controller status command", True, "Status command executed successfully")
            else:
                self.log_test("Pipeline controller status command", False, f"Exit code: {result.returncode}, Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.log_test("Pipeline controller status command", False, "Command timed out")
        except Exception as e:
            self.log_test("Pipeline controller status command", False, str(e))
        
        # Test controller test command
        try:
            result = subprocess.run([
                sys.executable, str(self.controller_path), 'test'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log_test("Pipeline controller test command", True, "Test command executed successfully")
            else:
                self.log_test("Pipeline controller test command", False, f"Exit code: {result.returncode}, Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.log_test("Pipeline controller test command", False, "Command timed out")
        except Exception as e:
            self.log_test("Pipeline controller test command", False, str(e))
    
    async def test_database_integration(self):
        """Test 3: Database Integration Testing"""
        print("\n💾 TESTING DATABASE INTEGRATION")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            # Test apartment count (should maintain 23+ apartments)
            try:
                async with session.get(f"{self.api_base}/apartments/search/stats") as response:
                    if response.status == 200:
                        data = await response.json()
                        total_apartments = data.get('total_apartments', 0)
                        
                        if total_apartments >= 23:
                            self.log_test("Database apartment count maintained", True, f"Found {total_apartments} apartments (≥23 required)")
                        else:
                            self.log_test("Database apartment count maintained", False, f"Only {total_apartments} apartments found, expected ≥23")
                    else:
                        self.log_test("Database apartment count check", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_test("Database apartment count check", False, str(e))
            
            # Test data quality metrics
            try:
                async with session.get(f"{self.api_base}/apartments?limit=10") as response:
                    if response.status == 200:
                        data = await response.json()
                        apartments = data.get('apartments', [])
                        
                        if apartments:
                            verified_count = sum(1 for apt in apartments if apt.get('is_verified', False))
                            verification_rate = (verified_count / len(apartments)) * 100
                            
                            if verification_rate >= 90:
                                self.log_test("Data quality verification rate", True, f"{verification_rate:.1f}% verification rate")
                            else:
                                self.log_test("Data quality verification rate", False, f"Only {verification_rate:.1f}% verified")
                        else:
                            self.log_test("Data quality verification rate", False, "No apartments found")
                    else:
                        self.log_test("Data quality verification rate", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_test("Data quality verification rate", False, str(e))
    
    def test_component_health(self):
        """Test 4: Component Health Verification"""
        print("\n🏥 TESTING COMPONENT HEALTH")
        print("=" * 50)
        
        # Test pipeline directory structure
        required_dirs = [
            self.pipeline_dir,
            self.pipeline_dir / 'scripts',
            self.pipeline_dir / 'data',
            self.pipeline_dir / 'backups'
        ]
        
        for directory in required_dirs:
            if directory.exists():
                self.log_test(f"Directory exists: {directory.name}", True, str(directory))
            else:
                self.log_test(f"Directory exists: {directory.name}", False, f"Missing: {directory}")
        
        # Test pipeline components
        required_files = [
            self.pipeline_dir / 'pipeline_controller.py',
            self.pipeline_dir / 'scheduler.py',
            self.pipeline_dir / 'scripts' / 'real_estate_data_pipeline.py',
            self.pipeline_dir / 'scripts' / 'comprehensive_data_analysis.py',
            self.pipeline_dir / 'scripts' / 'pipeline_edge_case_testing.py'
        ]
        
        for file_path in required_files:
            if file_path.exists():
                self.log_test(f"Component file: {file_path.name}", True, str(file_path))
            else:
                self.log_test(f"Component file: {file_path.name}", False, f"Missing: {file_path}")
        
        # Test configuration files
        config_files = [
            Path('/app/config/deployment_config.json'),
            self.status_file
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        json.load(f)
                    self.log_test(f"Config file readable: {config_file.name}", True, str(config_file))
                except json.JSONDecodeError:
                    self.log_test(f"Config file readable: {config_file.name}", False, "Invalid JSON")
            else:
                self.log_test(f"Config file readable: {config_file.name}", False, f"Missing: {config_file}")
    
    async def test_execution_flow(self):
        """Test 5: Execution Flow Testing"""
        print("\n⚡ TESTING EXECUTION FLOW")
        print("=" * 50)
        
        # Test pipeline status tracking
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    status_data = json.load(f)
                
                required_fields = ['status', 'timestamp']
                has_all_fields = all(field in status_data for field in required_fields)
                
                if has_all_fields:
                    self.log_test("Pipeline status tracking", True, f"Status: {status_data.get('status')}")
                else:
                    self.log_test("Pipeline status tracking", False, "Missing required status fields")
            except Exception as e:
                self.log_test("Pipeline status tracking", False, str(e))
        else:
            self.log_test("Pipeline status tracking", False, "Status file not found")
        
        # Test error handling
        try:
            # Try to run controller with invalid command
            result = subprocess.run([
                sys.executable, str(self.controller_path), 'invalid_command'
            ], capture_output=True, text=True, timeout=10)
            
            # Should fail gracefully, not crash
            if result.returncode != 0 and "Invalid command" in result.stdout:
                self.log_test("Pipeline error handling", True, "Graceful error handling for invalid commands")
            else:
                self.log_test("Pipeline error handling", False, "Did not handle invalid command properly")
        except Exception as e:
            self.log_test("Pipeline error handling", False, str(e))
    
    async def test_performance_stability(self):
        """Test 6: Performance & Stability"""
        print("\n🚀 TESTING PERFORMANCE & STABILITY")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            # Test API response times
            start_time = time.time()
            try:
                async with session.get(f"{self.api_base}/pipeline/status") as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200 and response_time < 5.0:
                        self.log_test("API response time", True, f"{response_time:.2f}s (< 5s required)")
                    else:
                        self.log_test("API response time", False, f"{response_time:.2f}s (too slow or failed)")
            except Exception as e:
                self.log_test("API response time", False, str(e))
            
            # Test concurrent access
            try:
                tasks = []
                for i in range(3):
                    task = session.get(f"{self.api_base}/pipeline/status")
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                successful_responses = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
                
                if successful_responses >= 2:
                    self.log_test("Concurrent API access", True, f"{successful_responses}/3 requests succeeded")
                else:
                    self.log_test("Concurrent API access", False, f"Only {successful_responses}/3 requests succeeded")
                    
                # Close responses
                for response in responses:
                    if hasattr(response, 'close'):
                        response.close()
                        
            except Exception as e:
                self.log_test("Concurrent API access", False, str(e))
            
            # Test main application performance (apartments API should still work)
            start_time = time.time()
            try:
                async with session.get(f"{self.api_base}/apartments?limit=5") as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200 and response_time < 3.0:
                        self.log_test("Main app performance impact", True, f"Apartments API: {response_time:.2f}s")
                    else:
                        self.log_test("Main app performance impact", False, f"Apartments API slow or failed: {response_time:.2f}s")
            except Exception as e:
                self.log_test("Main app performance impact", False, str(e))
    
    async def run_comprehensive_tests(self):
        """Run all pipeline tests"""
        print("🧪 DATA PIPELINE COMPREHENSIVE TESTING")
        print("=" * 70)
        print(f"Backend URL: {self.backend_url}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 70)
        
        # Run all test suites
        await self.test_api_endpoints()
        self.test_pipeline_controller()
        await self.test_database_integration()
        self.test_component_health()
        await self.test_execution_flow()
        await self.test_performance_stability()
        
        # Print summary
        print("\n📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed_tests']}")
        print(f"Failed: {self.test_results['failed_tests']}")
        
        success_rate = (self.test_results['passed_tests'] / self.test_results['total_tests']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 PIPELINE TESTING: EXCELLENT")
            print("✅ Data pipeline is production-ready")
        elif success_rate >= 75:
            print("\n⚠️  PIPELINE TESTING: GOOD WITH MINOR ISSUES")
            print("✅ Data pipeline is mostly functional")
        else:
            print("\n❌ PIPELINE TESTING: NEEDS ATTENTION")
            print("❌ Data pipeline has significant issues")
        
        # Show failed tests
        failed_tests = [t for t in self.test_results['test_details'] if not t['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        return success_rate >= 75

async def main():
    """Main test execution"""
    tester = DataPipelineTestSuite()
    success = await tester.run_comprehensive_tests()
    
    if success:
        print(f"\n✅ DATA PIPELINE TESTING COMPLETED SUCCESSFULLY")
        print(f"   Pipeline is ready for automated daily execution")
    else:
        print(f"\n❌ DATA PIPELINE TESTING REVEALED ISSUES")
        print(f"   Please address failed tests before production use")

if __name__ == "__main__":
    asyncio.run(main())
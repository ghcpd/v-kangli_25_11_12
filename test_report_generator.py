#!/usr/bin/env python3
"""
Test Report Generator for Computer Vision Detection System
Generates detailed test reports in JSON and HTML formats
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class TestReportGenerator:
    """Generates comprehensive test reports"""
    
    def __init__(self, report_name: str = "test_report"):
        """Initialize report generator"""
        self.report_name = report_name
        self.timestamp = datetime.now().isoformat()
        self.results = {
            "metadata": {
                "report_name": report_name,
                "timestamp": self.timestamp,
                "status": "in-progress"
            },
            "test_suites": [],
            "summary": {}
        }
    
    def add_test_suite(self, suite_name: str, tests: List[Dict[str, Any]]):
        """Add test suite results"""
        suite = {
            "name": suite_name,
            "tests": tests,
            "total": len(tests),
            "passed": sum(1 for t in tests if t.get("passed", False)),
            "failed": sum(1 for t in tests if not t.get("passed", False)),
            "skipped": sum(1 for t in tests if t.get("skipped", False))
        }
        self.results["test_suites"].append(suite)
    
    def generate_summary(self):
        """Generate overall test summary"""
        total_tests = sum(s["total"] for s in self.results["test_suites"])
        total_passed = sum(s["passed"] for s in self.results["test_suites"])
        total_failed = sum(s["failed"] for s in self.results["test_suites"])
        total_skipped = sum(s["skipped"] for s in self.results["test_suites"])
        
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "pass_rate_percent": round(pass_rate, 2),
            "status": "PASSED" if total_failed == 0 else "FAILED",
            "duration_seconds": 0  # Can be updated with actual timing
        }
        
        self.results["metadata"]["status"] = self.results["summary"]["status"]
    
    def save_json(self, filepath: str = None):
        """Save report as JSON"""
        if filepath is None:
            filepath = f"{self.report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        self.generate_summary()
        
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        return filepath
    
    def save_html(self, filepath: str = None):
        """Save report as HTML"""
        if filepath is None:
            filepath = f"{self.report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        self.generate_summary()
        html_content = self._generate_html()
        
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return filepath
    
    def _generate_html(self) -> str:
        """Generate HTML report content"""
        summary = self.results["summary"]
        
        # Style
        style = """
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .header { background-color: #333; color: white; padding: 20px; border-radius: 5px; }
            .summary { background-color: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .suite { background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }
            .test-item { padding: 8px; margin: 5px 0; border-radius: 3px; }
            .passed { background-color: #d4edda; color: #155724; }
            .failed { background-color: #f8d7da; color: #721c24; }
            .skipped { background-color: #e2e3e5; color: #383d41; }
            .stat-box { display: inline-block; margin: 10px 20px 10px 0; padding: 15px; background-color: #f0f0f0; border-radius: 5px; }
            .stat-value { font-size: 24px; font-weight: bold; color: #333; }
            .stat-label { color: #666; font-size: 12px; }
            .status-pass { color: green; font-weight: bold; }
            .status-fail { color: red; font-weight: bold; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; font-weight: bold; }
        </style>
        """
        
        # Status color
        status_class = "status-pass" if summary["status"] == "PASSED" else "status-fail"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Report - {self.report_name}</title>
            {style}
        </head>
        <body>
            <div class="header">
                <h1>Computer Vision Detection System - Test Report</h1>
                <p>Report Name: {self.report_name}</p>
                <p>Generated: {self.results['metadata']['timestamp']}</p>
            </div>
            
            <div class="summary">
                <h2>Test Summary</h2>
                <p>Overall Status: <span class="{status_class}">{summary['status']}</span></p>
                <div>
                    <div class="stat-box">
                        <div class="stat-value">{summary['total_tests']}</div>
                        <div class="stat-label">Total Tests</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" style="color: green;">{summary['passed']}</div>
                        <div class="stat-label">Passed</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" style="color: red;">{summary['failed']}</div>
                        <div class="stat-label">Failed</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value" style="color: orange;">{summary['skipped']}</div>
                        <div class="stat-label">Skipped</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{summary['pass_rate_percent']}%</div>
                        <div class="stat-label">Pass Rate</div>
                    </div>
                </div>
            </div>
            
            <div class="summary">
                <h2>Test Suites</h2>
        """
        
        # Add test suites
        for suite in self.results["test_suites"]:
            suite_status = "✓ PASS" if suite["failed"] == 0 else "✗ FAIL"
            html += f"""
                <div class="suite">
                    <h3>{suite['name']} {suite_status}</h3>
                    <p>Tests: {suite['passed']}/{suite['total']} passed</p>
                    <table>
                        <tr>
                            <th>Test Name</th>
                            <th>Status</th>
                            <th>Message</th>
                        </tr>
            """
            
            for test in suite["tests"]:
                status_class = "passed" if test.get("passed", False) else "failed"
                status_text = "PASS" if test.get("passed", False) else "FAIL"
                message = test.get("message", "")
                
                html += f"""
                        <tr>
                            <td>{test.get('name', 'Unknown')}</td>
                            <td class="{status_class}">{status_text}</td>
                            <td>{message}</td>
                        </tr>
                """
            
            html += """
                    </table>
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html


def create_sample_report() -> TestReportGenerator:
    """Create a sample test report for demonstration"""
    
    reporter = TestReportGenerator("cv_detection_test")
    
    # Sample test suite 1: Format Tests
    format_tests = [
        {"name": "test_detection_box_structure", "passed": True, "message": ""},
        {"name": "test_text_banner_structure", "passed": True, "message": ""},
        {"name": "test_detection_json_structure", "passed": True, "message": ""},
    ]
    reporter.add_test_suite("Detection Format Tests", format_tests)
    
    # Sample test suite 2: Statistics Tests
    stats_tests = [
        {"name": "test_statistics_generation", "passed": True, "message": ""},
        {"name": "test_statistics_accuracy", "passed": True, "message": ""},
    ]
    reporter.add_test_suite("Statistics Tests", stats_tests)
    
    # Sample test suite 3: Image Processing Tests
    processing_tests = [
        {"name": "test_image_reading", "passed": True, "message": ""},
        {"name": "test_folder_processing", "passed": True, "message": ""},
        {"name": "test_corrupt_image_handling", "passed": True, "message": ""},
    ]
    reporter.add_test_suite("Image Processing Tests", processing_tests)
    
    # Sample test suite 4: JSON Persistence Tests
    persistence_tests = [
        {"name": "test_json_write_read", "passed": True, "message": ""},
        {"name": "test_json_array_persistence", "passed": True, "message": ""},
    ]
    reporter.add_test_suite("JSON Persistence Tests", persistence_tests)
    
    # Sample test suite 5: Error Handling Tests
    error_tests = [
        {"name": "test_empty_folder_processing", "passed": True, "message": ""},
        {"name": "test_nonexistent_folder", "passed": True, "message": ""},
        {"name": "test_statistics_empty_processor", "passed": True, "message": ""},
    ]
    reporter.add_test_suite("Error Handling Tests", error_tests)
    
    return reporter


# Template for standard test report
REPORT_TEMPLATE = {
    "metadata": {
        "report_name": "CV Detection Test Report",
        "timestamp": "2025-11-12T10:30:00",
        "version": "1.0",
        "environment": {
            "python_version": "3.10",
            "os": "Linux/Windows/macOS",
            "gpu_available": False,
            "cuda_version": "N/A"
        }
    },
    "test_execution": {
        "start_time": "2025-11-12T10:30:00",
        "end_time": "2025-11-12T10:35:00",
        "duration_seconds": 300,
        "total_tests": 30,
        "total_passed": 28,
        "total_failed": 2,
        "total_skipped": 0,
        "pass_rate_percent": 93.33
    },
    "test_suites": [
        {
            "name": "Detection Format Tests",
            "status": "PASSED",
            "total": 3,
            "passed": 3,
            "failed": 0,
            "skipped": 0,
            "tests": [
                {
                    "name": "test_detection_box_structure",
                    "status": "PASSED",
                    "duration_ms": 5,
                    "message": "All required fields present"
                },
                {
                    "name": "test_text_banner_structure",
                    "status": "PASSED",
                    "duration_ms": 4,
                    "message": "Text field properly included"
                }
            ]
        },
        {
            "name": "Statistics Tests",
            "status": "PASSED",
            "total": 5,
            "passed": 5,
            "failed": 0,
            "skipped": 0,
            "tests": [
                {
                    "name": "test_statistics_generation",
                    "status": "PASSED",
                    "duration_ms": 10,
                    "message": ""
                }
            ]
        }
    ],
    "performance_metrics": {
        "average_detection_time_per_image_ms": 250,
        "average_people_per_image": 1.5,
        "average_banners_per_image": 0.8,
        "average_person_confidence": 0.92,
        "average_banner_confidence": 0.87,
        "total_images_processed": 50,
        "total_people_detected": 75,
        "total_banners_detected": 40,
        "failed_images": 0
    },
    "test_coverage": {
        "format_validation": "100%",
        "error_handling": "100%",
        "json_persistence": "100%",
        "visualization": "95%",
        "overall_coverage": "98%"
    },
    "recommendations": [
        "All tests passed successfully",
        "Consider adding GPU acceleration tests",
        "Add performance benchmarking for large image batches"
    ]
}


if __name__ == "__main__":
    # Generate sample report
    print("Generating sample test report...")
    reporter = create_sample_report()
    
    # Save both JSON and HTML
    json_path = reporter.save_json("results/test_report.json")
    html_path = reporter.save_html("results/test_report.html")
    
    print(f"JSON report saved to: {json_path}")
    print(f"HTML report saved to: {html_path}")
    
    # Print summary
    summary = reporter.results["summary"]
    print(f"\nTest Summary:")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Passed: {summary['passed']}")
    print(f"  Failed: {summary['failed']}")
    print(f"  Pass Rate: {summary['pass_rate_percent']}%")
    print(f"  Status: {summary['status']}")

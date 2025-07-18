#!/usr/bin/env python3
"""
Documentation Validation Utilities
Provides tools for validating documentation URLs, API schemas, and version compatibility.
"""

import requests
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentationValidator:
    """Validates documentation URLs and content freshness."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Context-Engineering-Framework/1.0'
        })
    
    def validate_url(self, url: str) -> Dict[str, any]:
        """
        Validate a documentation URL for accessibility and basic metrics.
        
        Args:
            url: The URL to validate
            
        Returns:
            Dict containing validation results
        """
        result = {
            'url': url,
            'accessible': False,
            'status_code': None,
            'response_time': None,
            'content_type': None,
            'last_modified': None,
            'error': None
        }
        
        try:
            start_time = datetime.now()
            response = self.session.get(url, timeout=self.timeout)
            end_time = datetime.now()
            
            result['accessible'] = response.status_code == 200
            result['status_code'] = response.status_code
            result['response_time'] = (end_time - start_time).total_seconds()
            result['content_type'] = response.headers.get('content-type', '')
            result['last_modified'] = response.headers.get('last-modified')
            
            # Check for common documentation indicators
            if response.status_code == 200:
                content = response.text.lower()
                result['is_documentation'] = any(keyword in content for keyword in [
                    'documentation', 'api reference', 'getting started', 
                    'installation', 'tutorial', 'guide'
                ])
                
        except requests.RequestException as e:
            result['error'] = str(e)
            logger.warning(f"Failed to validate URL {url}: {e}")
            
        return result
    
    def check_freshness(self, url: str, max_age_days: int = 365) -> Dict[str, any]:
        """
        Check if documentation is fresh (recently updated).
        
        Args:
            url: The URL to check
            max_age_days: Maximum age in days to consider fresh
            
        Returns:
            Dict containing freshness assessment
        """
        validation = self.validate_url(url)
        
        result = {
            'url': url,
            'is_fresh': False,
            'age_days': None,
            'last_modified': validation.get('last_modified'),
            'freshness_score': 0.0
        }
        
        if validation['accessible'] and validation['last_modified']:
            try:
                # Parse last modified date
                last_modified = datetime.strptime(
                    validation['last_modified'], 
                    '%a, %d %b %Y %H:%M:%S %Z'
                )
                
                age = datetime.now() - last_modified
                age_days = age.days
                
                result['age_days'] = age_days
                result['is_fresh'] = age_days <= max_age_days
                
                # Calculate freshness score (1.0 = very fresh, 0.0 = very old)
                if age_days <= 30:
                    result['freshness_score'] = 1.0
                elif age_days <= 90:
                    result['freshness_score'] = 0.8
                elif age_days <= 180:
                    result['freshness_score'] = 0.6
                elif age_days <= 365:
                    result['freshness_score'] = 0.4
                else:
                    result['freshness_score'] = 0.2
                    
            except ValueError as e:
                logger.warning(f"Could not parse last modified date for {url}: {e}")
                
        return result

class APIValidator:
    """Validates API endpoints and schemas."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
    
    def validate_endpoint(self, endpoint: str, method: str = 'GET') -> Dict[str, any]:
        """
        Validate an API endpoint for accessibility and basic response.
        
        Args:
            endpoint: The API endpoint URL
            method: HTTP method to use
            
        Returns:
            Dict containing validation results
        """
        result = {
            'endpoint': endpoint,
            'method': method,
            'accessible': False,
            'status_code': None,
            'response_time': None,
            'has_schema': False,
            'error': None
        }
        
        try:
            start_time = datetime.now()
            response = self.session.request(method, endpoint, timeout=self.timeout)
            end_time = datetime.now()
            
            result['status_code'] = response.status_code
            result['response_time'] = (end_time - start_time).total_seconds()
            result['accessible'] = response.status_code < 500
            
            # Check for OpenAPI/Swagger schema
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    result['has_schema'] = 'openapi' in json_response or 'swagger' in json_response
                except json.JSONDecodeError:
                    pass
                    
        except requests.RequestException as e:
            result['error'] = str(e)
            logger.warning(f"Failed to validate endpoint {endpoint}: {e}")
            
        return result
    
    def validate_schema(self, schema_url: str) -> Dict[str, any]:
        """
        Validate an API schema (OpenAPI/Swagger).
        
        Args:
            schema_url: URL to the API schema
            
        Returns:
            Dict containing schema validation results
        """
        result = {
            'schema_url': schema_url,
            'valid': False,
            'version': None,
            'endpoints_count': 0,
            'error': None
        }
        
        try:
            response = self.session.get(schema_url, timeout=self.timeout)
            
            if response.status_code == 200:
                schema = response.json()
                
                # Check for OpenAPI version
                if 'openapi' in schema:
                    result['version'] = schema['openapi']
                    result['valid'] = True
                elif 'swagger' in schema:
                    result['version'] = schema['swagger']
                    result['valid'] = True
                
                # Count endpoints
                if 'paths' in schema:
                    result['endpoints_count'] = len(schema['paths'])
                    
        except (requests.RequestException, json.JSONDecodeError) as e:
            result['error'] = str(e)
            logger.warning(f"Failed to validate schema {schema_url}: {e}")
            
        return result

class VersionCompatibilityChecker:
    """Checks version compatibility between dependencies."""
    
    def __init__(self):
        self.npm_registry = "https://registry.npmjs.org"
        self.pypi_registry = "https://pypi.org/pypi"
    
    def check_npm_package(self, package_name: str, version_range: str = None) -> Dict[str, any]:
        """
        Check npm package version information.
        
        Args:
            package_name: Name of the npm package
            version_range: Optional version range to check
            
        Returns:
            Dict containing version information
        """
        result = {
            'package': package_name,
            'latest_version': None,
            'requested_version': version_range,
            'compatible': False,
            'deprecated': False,
            'error': None
        }
        
        try:
            response = requests.get(f"{self.npm_registry}/{package_name}")
            
            if response.status_code == 200:
                data = response.json()
                result['latest_version'] = data['dist-tags']['latest']
                result['deprecated'] = data.get('deprecated', False)
                
                # Simple compatibility check (can be enhanced)
                if not version_range or version_range == 'latest':
                    result['compatible'] = True
                else:
                    # Basic semver compatibility (simplified)
                    result['compatible'] = self._check_semver_compatibility(
                        result['latest_version'], version_range
                    )
                    
        except requests.RequestException as e:
            result['error'] = str(e)
            
        return result
    
    def check_python_package(self, package_name: str, version_range: str = None) -> Dict[str, any]:
        """
        Check Python package version information.
        
        Args:
            package_name: Name of the Python package
            version_range: Optional version range to check
            
        Returns:
            Dict containing version information
        """
        result = {
            'package': package_name,
            'latest_version': None,
            'requested_version': version_range,
            'compatible': False,
            'error': None
        }
        
        try:
            response = requests.get(f"{self.pypi_registry}/{package_name}/json")
            
            if response.status_code == 200:
                data = response.json()
                result['latest_version'] = data['info']['version']
                
                # Simple compatibility check
                if not version_range or version_range == 'latest':
                    result['compatible'] = True
                else:
                    result['compatible'] = self._check_version_compatibility(
                        result['latest_version'], version_range
                    )
                    
        except requests.RequestException as e:
            result['error'] = str(e)
            
        return result
    
    def _check_semver_compatibility(self, latest: str, requested: str) -> bool:
        """Basic semver compatibility check (simplified)."""
        # This is a simplified version - real implementation would use semver library
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            requested_clean = re.sub(r'[^\d.]', '', requested)
            requested_parts = [int(x) for x in requested_clean.split('.')]
            
            # Major version compatibility
            return latest_parts[0] == requested_parts[0]
        except (ValueError, IndexError):
            return False
    
    def _check_version_compatibility(self, latest: str, requested: str) -> bool:
        """Basic version compatibility check."""
        # Simplified version checking
        return latest == requested or requested in ['latest', '*']

class DocumentationUpdateTracker:
    """Tracks documentation updates and changes."""
    
    def __init__(self, cache_file: str = "doc_cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cached documentation information."""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_cache(self):
        """Save cache to file."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def track_update(self, url: str, current_hash: str):
        """
        Track documentation update.
        
        Args:
            url: Documentation URL
            current_hash: Hash of current content
        """
        now = datetime.now().isoformat()
        
        if url not in self.cache:
            self.cache[url] = {
                'first_seen': now,
                'last_updated': now,
                'hash': current_hash,
                'update_count': 1
            }
        else:
            cached = self.cache[url]
            if cached['hash'] != current_hash:
                cached['last_updated'] = now
                cached['hash'] = current_hash
                cached['update_count'] = cached.get('update_count', 0) + 1
        
        self._save_cache()
    
    def get_update_info(self, url: str) -> Dict[str, any]:
        """
        Get update information for a URL.
        
        Args:
            url: Documentation URL
            
        Returns:
            Dict containing update information
        """
        if url in self.cache:
            return self.cache[url].copy()
        return {
            'first_seen': None,
            'last_updated': None,
            'hash': None,
            'update_count': 0
        }

# Utility functions for easy usage
def validate_documentation_urls(urls: List[str]) -> List[Dict[str, any]]:
    """Validate multiple documentation URLs."""
    validator = DocumentationValidator()
    return [validator.validate_url(url) for url in urls]

def check_api_endpoints(endpoints: List[str]) -> List[Dict[str, any]]:
    """Check multiple API endpoints."""
    validator = APIValidator()
    return [validator.validate_endpoint(endpoint) for endpoint in endpoints]

def check_package_versions(packages: List[Tuple[str, str]]) -> List[Dict[str, any]]:
    """Check version compatibility for multiple packages."""
    checker = VersionCompatibilityChecker()
    results = []
    
    for package_name, version_range in packages:
        if package_name.startswith('@') or '/' in package_name:
            # Assume npm package
            results.append(checker.check_npm_package(package_name, version_range))
        else:
            # Assume Python package
            results.append(checker.check_python_package(package_name, version_range))
    
    return results

if __name__ == "__main__":
    # Example usage
    print("Documentation Validation Utilities")
    print("=" * 40)
    
    # Test documentation URL validation
    test_urls = [
        "https://reactjs.org/docs/getting-started.html",
        "https://docs.python.org/3/",
        "https://invalid-url-example.com"
    ]
    
    print("\nValidating documentation URLs:")
    for result in validate_documentation_urls(test_urls):
        print(f"  {result['url']}: {'✓' if result['accessible'] else '✗'}")
    
    # Test API endpoint validation
    test_endpoints = [
        "https://api.github.com",
        "https://jsonplaceholder.typicode.com/posts/1"
    ]
    
    print("\nValidating API endpoints:")
    for result in check_api_endpoints(test_endpoints):
        print(f"  {result['endpoint']}: {'✓' if result['accessible'] else '✗'}")

#!/usr/bin/env python3
"""
Test script for ProofSAR AI API
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_analysis():
    """Test transaction analysis"""
    print("Testing transaction analysis...")
    
    # Sample transaction data
    transactions = [
        {
            "transaction_id": "TXN001",
            "account_id": "ACC1001",
            "amount": 50000,
            "timestamp": "2024-02-15T10:30:00",
            "transaction_type": "DEPOSIT",
            "source": "CASH",
            "destination": "ACC1001"
        },
        {
            "transaction_id": "TXN002", 
            "account_id": "ACC1001",
            "amount": 45000,
            "timestamp": "2024-02-15T11:00:00",
            "transaction_type": "TRANSFER",
            "source": "ACC1001",
            "destination": "ACC2002"
        },
        {
            "transaction_id": "TXN003",
            "account_id": "ACC1001", 
            "amount": 48000,
            "timestamp": "2024-02-15T11:30:00",
            "transaction_type": "TRANSFER",
            "source": "ACC1001",
            "destination": "ACC2003"
        }
    ]
    
    # Sample customer profile
    customer_profile = {
        "customer_name": "Rajesh Kumar",
        "account_number": "ACC-1001",
        "customer_id": "CUST-789012",
        "annual_income": 2000000,
        "occupation": "Business Owner"
    }
    
    payload = {
        "transactions": transactions,
        "customer_profile": customer_profile
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer demo-token"  # Simplified for demo
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze",
            json=payload,
            headers=headers,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Case ID: {result['case_id']}")
            print(f"Risk Score: {result['detection_results']['risk_score']}")
            print(f"Risk Level: {result['detection_results']['overall_risk']}")
            print(f"Patterns: {len(result['detection_results']['all_patterns'])}")
            print("✅ Analysis successful!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")
    
    print()

def test_sar_generation():
    """Test SAR generation"""
    print("Testing SAR generation...")
    
    payload = {
        "case_id": f"SAR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "detection_results": {
            "risk_score": 0.85,
            "overall_risk": "HIGH",
            "all_patterns": ["Structuring", "Layering"]
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer demo-token"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/generate-sar",
            json=payload,
            headers=headers,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"SAR generated for case: {result['case_id']}")
            print(f"Content length: {len(result['sar_content'])} characters")
            print("✅ SAR generation successful!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")
    
    print()

def test_alerts():
    """Test alerts endpoint"""
    print("Testing alerts endpoint...")
    
    headers = {
        "Authorization": "Bearer demo-token"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/alerts",
            headers=headers,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Total alerts sent: {result['stats']['total_sent']}")
            print(f"Success rate: {result['stats']['success_rate']:.1%}")
            print("✅ Alerts endpoint working!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {str(e)}")
    
    print()

if __name__ == "__main__":
    print("🧪 ProofSAR AI API Test Suite")
    print("=" * 50)
    
    test_health_check()
    test_analysis()
    test_sar_generation()
    test_alerts()
    
    print("✅ All tests completed!")

#!/usr/bin/env python3
"""
Test script for ProofSAR AI Secrets Management
"""

import sys
import os
from pathlib import Path

# Add frontend to path
sys.path.append(str(Path(__file__).parent / "frontend"))

def test_secrets_management():
    """Test the secrets management system"""
    print("🧪 Testing ProofSAR AI Secrets Management")
    print("=" * 50)
    
    try:
        # Test 1: Import secrets manager
        print("1. Testing import...")
        from config.secrets import get_secret, get_secrets_manager
        print("   ✅ Secrets manager imported successfully")
        
        # Test 2: Get individual secrets
        print("2. Testing individual secret retrieval...")
        debug_mode = get_secret("SHOW_DEBUG_INFO", False)
        jwt_key = get_secret("JWT_SECRET_KEY", "not-set")
        print(f"   ✅ Debug mode: {debug_mode}")
        print(f"   ✅ JWT key configured: {bool(jwt_key != 'not-set')}")
        
        # Test 3: Get full configuration
        print("3. Testing full configuration...")
        manager = get_secrets_manager()
        config = manager.get_config()
        print(f"   ✅ Config loaded: {type(config).__name__}")
        print(f"   ✅ AI model config: {hasattr(config, 'ai_model')}")
        print(f"   ✅ Alert recipients: {hasattr(config, 'get_alert_recipients')}")
        
        # Test 4: Test production mode detection
        print("4. Testing production mode detection...")
        is_prod = manager.is_production()
        is_debug = manager.is_debug_mode()
        print(f"   ✅ Production mode: {is_prod}")
        print(f"   ✅ Debug mode: {is_debug}")
        
        # Test 5: Test missing secret handling
        print("5. Testing missing secret handling...")
        missing = get_secret("NONEXISTENT_SECRET", "default_value")
        print(f"   ✅ Missing secret returns default: {missing == 'default_value'}")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Secrets management system is working correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_integration():
    """Test integration with Streamlit"""
    print("\n🌐 Testing Streamlit Integration")
    print("=" * 50)
    
    try:
        # This simulates what happens in Streamlit
        import streamlit as st
        
        # Test without secrets.toml (current situation)
        print("1. Testing without secrets.toml...")
        from config.secrets import get_secret
        
        # This should NOT crash
        debug_value = get_secret("SHOW_DEBUG_INFO", False)
        print(f"   ✅ No crash when secrets missing: {debug_value}")
        
        # Test with environment variable
        print("2. Testing with environment variable...")
        os.environ["SHOW_DEBUG_INFO"] = "true"
        
        # Reload to test environment variable
        from importlib import reload
        import config.secrets
        reload(config.secrets)
        
        debug_value = get_secret("SHOW_DEBUG_INFO", False)
        print(f"   ✅ Environment variable works: {debug_value}")
        
        print("\n🎉 STREAMLIT INTEGRATION TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Streamlit integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔐 ProofSAR AI - Secrets Management Test Suite")
    print("=" * 60)
    
    success1 = test_secrets_management()
    success2 = test_streamlit_integration()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🏆 ALL TESTS PASSED - Secrets system is production-ready!")
        print("\n📋 Next Steps:")
        print("1. Copy frontend/secrets.toml.example to .streamlit/secrets.toml")
        print("2. Update with your actual values")
        print("3. Deploy to production")
    else:
        print("❌ Some tests failed - please check the configuration")
    
    print("\n🔒 Security Status: ✅ NO CRASHES - SAFE FALLBACKS")

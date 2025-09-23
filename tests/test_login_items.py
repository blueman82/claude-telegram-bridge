#!/usr/bin/env python3
"""
Test script to verify Login Items automation capability (TDD approach)
Tests if we can programmatically add/remove login items on macOS
"""
import os
import subprocess
import tempfile
import time
import shutil
from pathlib import Path


class LoginItemsTest:
    def __init__(self):
        self.test_app_name = "TelegramListenerTest"
        self.test_app_path = Path.home() / "Applications" / f"{self.test_app_name}.app"
        self.results = []

    def log_result(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append((test_name, passed, message))
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")

    def create_test_app(self):
        """Create a minimal test app bundle"""
        try:
            # Create app bundle structure
            contents_dir = self.test_app_path / "Contents"
            macos_dir = contents_dir / "MacOS"
            macos_dir.mkdir(parents=True, exist_ok=True)

            # Create executable script
            executable = macos_dir / self.test_app_name
            executable.write_text(f'''#!/bin/bash
# Test app for login items automation
echo "Test login item started at $(date)" >> ~/telegram_test.log
sleep 2
echo "Test login item finished at $(date)" >> ~/telegram_test.log
''')
            executable.chmod(0o755)

            # Create Info.plist
            info_plist = contents_dir / "Info.plist"
            info_plist.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{self.test_app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.test.{self.test_app_name.lower()}</string>
    <key>CFBundleName</key>
    <string>{self.test_app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>''')

            self.log_result("Create test app bundle", True, f"Created at {self.test_app_path}")
            return True

        except Exception as e:
            self.log_result("Create test app bundle", False, f"Error: {e}")
            return False

    def test_add_login_item(self):
        """Test adding login item via osascript"""
        try:
            cmd = [
                'osascript', '-e',
                f'tell application "System Events" to make login item at end with properties {{path:"{self.test_app_path}", hidden:true}}'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self.log_result("Add login item", True, "osascript executed successfully")
                return True
            else:
                self.log_result("Add login item", False, f"osascript error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.log_result("Add login item", False, "osascript timed out (may need user permission)")
            return False
        except Exception as e:
            self.log_result("Add login item", False, f"Error: {e}")
            return False

    def test_verify_login_item(self):
        """Test verifying login item was added"""
        try:
            cmd = [
                'osascript', '-e',
                'tell application "System Events" to get the name of every login item'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                login_items = result.stdout.strip()
                if self.test_app_name in login_items:
                    self.log_result("Verify login item", True, f"Found in list: {login_items}")
                    return True
                else:
                    self.log_result("Verify login item", False, f"Not found in: {login_items}")
                    return False
            else:
                self.log_result("Verify login item", False, f"osascript error: {result.stderr}")
                return False

        except Exception as e:
            self.log_result("Verify login item", False, f"Error: {e}")
            return False

    def test_remove_login_item(self):
        """Test removing login item"""
        try:
            cmd = [
                'osascript', '-e',
                f'tell application "System Events" to delete login item "{self.test_app_name}"'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self.log_result("Remove login item", True, "osascript executed successfully")
                return True
            else:
                self.log_result("Remove login item", False, f"osascript error: {result.stderr}")
                return False

        except Exception as e:
            self.log_result("Remove login item", False, f"Error: {e}")
            return False

    def cleanup(self):
        """Clean up test files"""
        try:
            # Remove test app
            if self.test_app_path.exists():
                shutil.rmtree(self.test_app_path)

            # Remove test log file
            test_log = Path.home() / "telegram_test.log"
            if test_log.exists():
                test_log.unlink()

            self.log_result("Cleanup", True, "Test files removed")

        except Exception as e:
            self.log_result("Cleanup", False, f"Error: {e}")

    def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Testing Login Items Automation Capability")
        print("=" * 50)

        # Test sequence
        if self.create_test_app():
            if self.test_add_login_item():
                time.sleep(1)  # Give system time to process
                self.test_verify_login_item()
                self.test_remove_login_item()

        # Always cleanup
        self.cleanup()

        # Summary
        print("\n📊 Test Results Summary:")
        print("=" * 50)

        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)

        for test_name, success, message in self.results:
            status = "✅" if success else "❌"
            print(f"{status} {test_name}")

        print(f"\nResult: {passed}/{total} tests passed")

        if passed >= 4:  # All core tests pass
            print("\n🎉 Login Items automation is VIABLE for setup script!")
            return True
        else:
            print("\n⚠️  Login Items automation has issues - manual approach needed")
            return False


def main():
    """Run the test"""
    tester = LoginItemsTest()
    return tester.run_all_tests()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
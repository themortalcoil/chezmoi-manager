#!/usr/bin/env python3
"""Quick test script for ChezmoiWrapper."""

from chezmoi import ChezmoiWrapper

print("Testing ChezmoiWrapper...")
print("=" * 50)

# Test 1: Check if chezmoi is installed
print("\n1. Checking if chezmoi is installed...")
if ChezmoiWrapper.check_installed():
    print("   ✓ chezmoi is installed")
    version = ChezmoiWrapper.get_version()
    print(f"   Version: {version}")
else:
    print("   ✗ chezmoi not found")
    exit(1)

# Test 2: Get source directory
print("\n2. Getting source directory...")
try:
    source_dir = ChezmoiWrapper.get_source_dir()
    print(f"   ✓ Source dir: {source_dir}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Get managed files
print("\n3. Getting managed files...")
try:
    files = ChezmoiWrapper.get_managed_files()
    print(f"   ✓ Found {len(files)} managed files")
    for f in files[:5]:  # Show first 5
        print(f"     - {f}")
    if len(files) > 5:
        print(f"     ... and {len(files) - 5} more")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Get status
print("\n4. Getting status...")
try:
    status = ChezmoiWrapper.get_status()
    if status.strip():
        print(f"   ✓ Status output ({len(status)} chars)")
        lines = status.split("\n")
        for line in lines[:3]:
            print(f"     {line}")
        if len(lines) > 3:
            print(f"     ... and {len(lines) - 3} more lines")
    else:
        print("   ✓ No pending changes")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Get template data
print("\n5. Getting template data...")
try:
    data = ChezmoiWrapper.get_data()
    if data:
        print(f"   ✓ Got template data with {len(data)} top-level keys")
        for key in list(data.keys())[:5]:
            print(f"     - {key}")
    else:
        print("   ✓ No template data")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 6: Run doctor
print("\n6. Running doctor...")
try:
    doctor_output = ChezmoiWrapper.doctor()
    print(f"   ✓ Doctor output ({len(doctor_output)} chars)")
    lines = doctor_output.split("\n")
    for line in lines[:5]:
        if line.strip():
            print(f"     {line}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 50)
print("All tests completed!")

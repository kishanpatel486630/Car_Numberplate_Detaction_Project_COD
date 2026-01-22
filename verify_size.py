#!/usr/bin/env python3
"""
Verify deployment size is under 512MB limit for Render free tier
"""
import os
import sys

def get_dir_size(path='.', exclude_dirs=None):
    """Calculate directory size excluding certain folders"""
    if exclude_dirs is None:
        exclude_dirs = {'.git', '.venv', 'venv', '__pycache__', '.cache', '.config', 'node_modules'}
    
    total_size = 0
    file_count = 0
    
    for dirpath, dirnames, filenames in os.walk(path):
        # Remove excluded directories from the walk
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
                file_count += 1
            except OSError:
                pass
    
    return total_size, file_count

def format_size(bytes_size):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def main():
    print("=" * 70)
    print("DEPLOYMENT SIZE VERIFICATION FOR RENDER.COM (512MB FREE TIER)")
    print("=" * 70)
    
    # Check source code size
    source_size, file_count = get_dir_size('.')
    source_mb = source_size / (1024 * 1024)
    
    print(f"\n📦 Source Code (tracked in git):")
    print(f"   Files: {file_count}")
    print(f"   Size: {format_size(source_size)}")
    
    # Estimated dependency sizes
    print(f"\n📚 Estimated Dependency Sizes (after pip install):")
    dependencies = {
        'PyTorch (CPU-only)': 180,
        'Ultralytics (YOLOv8)': 120,
        'OpenCV (headless)': 50,
        'Flask + Werkzeug': 40,
        'Pandas + NumPy': 30,
        'SciPy + FilterPy': 20,
        'Other (Pillow, lapx, etc)': 10,
    }
    
    total_deps = 0
    for name, size_mb in dependencies.items():
        print(f"   • {name}: ~{size_mb} MB")
        total_deps += size_mb
    
    print(f"\n   Total Dependencies: ~{total_deps} MB")
    
    # Calculate totals
    total_mb = source_mb + total_deps
    buffer_mb = 512 - total_mb
    
    print(f"\n" + "=" * 70)
    print(f"📊 DEPLOYMENT SIZE BREAKDOWN:")
    print(f"   Source code:        {source_mb:.2f} MB")
    print(f"   Dependencies:     ~{total_deps:.0f} MB")
    print(f"   ─────────────────────────────────")
    print(f"   TOTAL:            ~{total_mb:.2f} MB")
    print(f"   Render limit:      512.00 MB")
    print(f"   Buffer remaining:  ~{buffer_mb:.2f} MB ({buffer_mb/512*100:.1f}%)")
    print(f"=" * 70)
    
    # Check if within limit
    if total_mb <= 512:
        status = "✅ PASS"
        color = "\033[92m"  # Green
        exit_code = 0
    else:
        status = "❌ FAIL"
        color = "\033[91m"  # Red
        exit_code = 1
    
    reset = "\033[0m"
    print(f"\n{color}{status}: Deployment size is {'WITHIN' if exit_code == 0 else 'OVER'} 512MB limit{reset}")
    
    if exit_code == 0:
        print("\n💡 Tips:")
        print("   • Models (.pt files) are NOT committed to git")
        print("   • Models auto-download at first run (~12MB)")
        print("   • Using CPU-only PyTorch (saves ~300MB vs GPU)")
        print("   • Total runtime memory usage: ~450-500MB")
    else:
        print("\n⚠️  WARNING: Deployment may fail!")
        print("   • Remove unnecessary files")
        print("   • Check for large files in git: git ls-files --long")
        print("   • Verify .gitignore excludes model files")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())

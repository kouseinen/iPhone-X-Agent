import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Sys Path: {sys.path}")

try:
    import PIL
    print(f"PIL Version: {PIL.__version__}")
    print(f"PIL File: {PIL.__file__}")
except ImportError as e:
    print(f"Failed to import PIL: {e}")

try:
    from PIL import Image
    print("Successfully imported Image from PIL")
except ImportError as e:
    print(f"Failed to import Image from PIL: {e}")

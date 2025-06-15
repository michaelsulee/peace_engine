# main.py
import sys
import os

# Ensure the src directory is in the Python path
# This allows the scripts inside 'src' to find each other.
sys.path.append(os.path.abspath('src'))

# Now we can import the Engine class
from engine import Engine

if __name__ == "__main__":
    print("Starting PEACE Engine...")
    try:
        # Create and run the engine
        peace_engine = Engine(1280, 720)
        peace_engine.run()
    except Exception as e:
        print(f"An unhandled exception occurred in the engine: {e}")
        # In a real build, you would log this to a file
        import traceback
        traceback.print_exc()
    finally:
        print("PEACE Engine has shut down.")
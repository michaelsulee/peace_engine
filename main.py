# main.py
import sys
import os
import traceback

# This is a standard practice to ensure that modules inside the 'src' directory
# can be imported correctly, regardless of where you run the script from.
sys.path.append(os.path.abspath('src'))

# We import our core Engine class.
from engine import Engine

if __name__ == "__main__":
    print("Initializing the PEACE Engine...")
    try:
        # We create an instance of our engine with a specified window resolution.
        peace_engine = Engine(1920, 1080)
        # We start the main loop of the engine.
        peace_engine.run()
    except Exception as e:
        # Robust error handling is critical in complex applications.
        # This will catch any uncaught exceptions from the engine's loop,
        # print a detailed traceback, and ensure the application exits gracefully.
        print(f"\nA fatal error occurred in the PEACE Engine: {e}")
        traceback.print_exc()
    finally:
        # This message confirms that the engine has completed its lifecycle.
        print("\nPEACE Engine has shut down.")
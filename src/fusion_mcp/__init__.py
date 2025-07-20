from .fusion_mcp import mcp
import argparse

def main():
    """
    Fusion MCP: Build with thought not skill.
    """
    arguments = argparse.ArgumentParser(
        description="Fusion360 Commands"
    )

    mcp.run()

if __name__ == "__main__":
    main()
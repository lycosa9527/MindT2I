"""
ASCII Banner for MindT2I
========================

Displays a stylish ASCII art banner at application startup.
"""

from config.settings import config


def print_banner():
    """Print MindT2I ASCII banner with dynamic version"""
    
    version = config.VERSION
    
    banner = f"""
===============================================================================
                                                                               
   ███╗   ███╗██╗███╗   ██╗██████╗ ████████╗██████╗ ██╗                      
   ████╗ ████║██║████╗  ██║██╔══██╗╚══██╔══╝╚════██╗██║                      
   ██╔████╔██║██║██╔██╗ ██║██║  ██║   ██║    █████╔╝██║                      
   ██║╚██╔╝██║██║██║╚██╗██║██║  ██║   ██║   ██╔═══╝ ██║                      
   ██║ ╚═╝ ██║██║██║ ╚████║██████╔╝   ██║   ███████╗██║                      
   ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝    ╚═╝   ╚══════╝╚═╝                      
                                                                               
   Version: {version:<20}  Made by: MindSpring Team                 
   Author: lycosa9527                License: AGPLv3                          
                                                                               
===============================================================================
    """
    
    print(banner)


def print_startup_info(host: str, port: int, debug: bool = False):
    """
    Print startup information after banner.
    
    Args:
        host: Server host address
        port: Server port number
        debug: Debug mode enabled
    """
    
    print("\n[*] Server Configuration:")
    print(f"   - Host: {host}")
    print(f"   - Port: {port}")
    print(f"   - Debug: {'ON' if debug else 'OFF'}")
    print(f"\n[*] Quick Links:")
    print(f"   - Web Interface: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/")
    print(f"   - Debug Page: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/debug")
    print(f"   - API Docs: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
    print(f"   - ReDoc: http://{host if host != '0.0.0.0' else 'localhost'}:{port}/redoc")
    print(f"\n[*] API Endpoints:")
    print(f"   - POST /generate        - Intelligent routing (image/video)")
    print(f"   - POST /generate-image  - Generate images")
    print(f"   - POST /generate-video  - Generate videos")
    print(f"   - GET  /health          - Health check")
    print("")
    print("=" * 79)
    print("")


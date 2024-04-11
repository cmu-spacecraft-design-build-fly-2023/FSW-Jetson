"""
Main Entry Point for the flight software

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

from flight.payload import PayloadManager

if __name__ == "__main__":

    payload = PayloadManager()
    payload.run()

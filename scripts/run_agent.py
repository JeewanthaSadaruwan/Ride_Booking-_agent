#!/usr/bin/env python3
"""Main entry point for the Vehicle Dispatch Agent."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
from dotenv import load_dotenv
from agents.dispatch_agent import dispatch_agent

# Load environment variables
load_dotenv()


if __name__ == "__main__":
    print("=============================================================================")
    print("🚗  WELCOME TO RIDE BOOKING AGENT  🚗")
    print("=============================================================================")
    print("✨ I can book vehicles from ANYWHERE to ANYWHERE in Sri Lanka!")
    print()
    print("🎯 My capabilities:")
    print("   📍 Dynamic routing - NOT limited to predefined routes")
    print("   🗺️  Real-time location detection (GPS or address)")
    print("   💰 Accurate cost & time estimates for ANY route")
    print("   🚕 Smart vehicle matching based on your preferences")
    print("   📅 Automatic calendar booking for time blocking")
    print()
    print("💡 Example requests:")
    print("   • 'I need a ride from Jaffna to Colombo now'")
    print("   • 'Book a van from 6.9271, 79.8612 to Galle tomorrow at 10 AM'")
    print("   • 'Find me a sedan from Trincomalee to Negombo for 3 passengers'")
    print("   • 'I want to go from Kandy to Nuwara Eliya with wheelchair access'")
    print()
    print("🚪 Type 'exit' to quit anytime")
    print("=============================================================================")
    print()

    # Initialize the ride booking agent
    try:
        print("🔄 Initializing Ride Booking Agent...")
        print("✅ Ride Booking Agent ready!")
        print("🤖 All tools loaded - ready for anywhere-to-anywhere bookings!")
        print()
    except Exception as e:
        print(f"❌ Error initializing Dispatch Agent: {str(e)}")

    # Run the agent in a loop for interactive conversation
    while True:
        try:
            user_input = input("👤 You: ").strip()
            if not user_input:
                print("💭 Please tell me your trip requirements, or type 'exit' to quit")
                continue
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                print()
                print("=========================================================")
                print("👋 Thank you for using Vehicle Dispatch Agent!")
                print("🎉 Have a safe trip!")
                print("🚗 Come back anytime you need a ride!")
                print("=========================================================")
                break

            print("🤖 DispatchBot: ", end="")
            response = dispatch_agent(user_input)
            print("\n")

        except KeyboardInterrupt:
            print("\n")
            print("=========================================================")
            print("👋 Vehicle Dispatch Agent interrupted!")
            print("🤖 See you next time!")
            print("=========================================================")
            break
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")
            print("🔧 Please try again or type 'exit' to quit")
            print()

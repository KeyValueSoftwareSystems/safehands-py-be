#!/usr/bin/env python3
"""
Development setup script for SafeHands Senior AI Assistant
"""
import os
import sys
from pathlib import Path

def setup_environment():
    """Set up the development environment"""
    print("🚀 SafeHands Senior AI Assistant - Development Setup")
    print("=" * 50)
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file from template...")
        env_example = Path("env.example")
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("✅ .env file created from env.example")
        else:
            print("❌ env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    
    # Get OpenAI API key
    print("\n🔑 OpenAI API Key Setup")
    print("You need an OpenAI API key to use the AI features.")
    print("Get your API key from: https://platform.openai.com/api-keys")
    
    current_key = os.getenv("OPENAI_API_KEY")
    if current_key:
        print(f"Current API key: {'*' * 20}{current_key[-4:]}")
        use_current = input("Use current API key? (y/N): ").lower().strip()
        if use_current == 'y':
            return True
    
    api_key = input("Enter your OpenAI API key (sk-...): ").strip()
    
    if not api_key.startswith("sk-"):
        print("❌ Invalid API key format. Should start with 'sk-'")
        return False
    
    # Update .env file
    print("📝 Updating .env file...")
    env_content = env_file.read_text()
    
    # Replace the OpenAI API key
    lines = env_content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("OPENAI_API_KEY="):
            lines[i] = f"OPENAI_API_KEY={api_key}"
            break
    
    env_file.write_text('\n'.join(lines))
    print("✅ .env file updated with your OpenAI API key")
    
    # Set environment variable for current session
    os.environ["OPENAI_API_KEY"] = api_key
    print("✅ Environment variable set for current session")
    
    return True

def main():
    """Main setup function"""
    print("Setting up SafeHands Senior AI Assistant for development...")
    
    # Setup environment
    if not setup_environment():
        print("❌ Setup failed")
        sys.exit(1)
    
    print("\n🎉 Development Setup Complete!")
    print("=" * 50)
    print("Your SafeHands Senior AI Assistant is ready for development!")
    print("\nNext steps:")
    print("1. Start the backend: ./start.sh")
    print("2. Start the test interface: ./start_test_interface.sh")
    print("3. Open http://localhost:3000 to test the web interface")
    
    print("\n📚 Available AI Models:")
    print("- GPT-3.5-turbo: Text generation and intent recognition")
    print("- GPT-4-Vision: Image analysis and screen understanding")
    print("- Whisper: Speech-to-text transcription")
    print("- TTS: Text-to-speech generation")

if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Terminal testing script for the Brow Studio Bot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from bot_logic import BrowStudioBot

def test_bot_terminal():
    """Run the bot in terminal mode for testing"""
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("🌟 Teste do Bot - Brow Studio 🌟")
        print("Digite 'sair' para encerrar o teste.")
        print("-" * 50)
        
        # Create bot instance
        bot = BrowStudioBot()
        
        while True:
            # Get user input
            user_input = input("\nVocê: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\nEncerrando teste do bot...")
                break
            
            # Get bot response
            try:
                response = bot.get_response(user_input)
                print(f"\nBot: {response}")
            except Exception as e:
                print(f"\nErro: {str(e)}")
                print("Verifique se o banco de dados foi configurado corretamente.")

if __name__ == "__main__":
    test_bot_terminal()
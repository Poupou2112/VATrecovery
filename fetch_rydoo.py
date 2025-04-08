import os
import requests

def get_tickets():
    # Simulation de tickets pour test
    return [
        {
            "file": "app/static/test_ticket1.jpg",  # à adapter selon ton répertoire
            "email": "comercio@example.com"
        }
    ]

# Plus tard, tu remplacerais par une vraie connexion à Rydoo avec OAuth2

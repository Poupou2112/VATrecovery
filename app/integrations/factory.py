from typing import Dict, Any
from loguru import logger
from app.integrations.base import ExpenseProviderBase
from app.integrations.rydoo import RydooProvider
from app.integrations.sap_concur import SAPConcurProvider

class ExpenseProviderFactory:
    """Factory pour créer le fournisseur d'application de gestion des dépenses approprié"""
    
    @staticmethod
    def create_provider(provider_type: str, config: Dict[str, Any]) -> ExpenseProviderBase:
        """
        Crée une instance du fournisseur approprié selon le type
        
        Args:
            provider_type: Type de fournisseur ("rydoo" ou "sap_concur")
            config: Configuration spécifique au fournisseur
            
        Returns:
            Une instance de ExpenseProviderBase
        """
        if provider_type.lower() == "rydoo":
            if "api_key" not in config or "organization_id" not in config:
                raise ValueError("Rydoo configuration requires 'api_key' and 'organization_id'")
                
            return RydooProvider(
                api_key=config["api_key"],
                organization_id=config["organization_id"]
            )
        elif provider_type.lower() == "sap_concur":
            if "client_id" not in config or "client_secret" not in config or "refresh_token" not in config:
                raise ValueError("SAP Concur configuration requires 'client_id', 'client_secret', and 'refresh_token'")
                
            return SAPConcurProvider(
                client_id=config["client_id"],
                client_secret=config["client_secret"], 
                refresh_token=config["refresh_token"]
            )
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

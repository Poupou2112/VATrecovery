import redis
import json
import uuid
import time
from typing import Dict, Any, List, Callable, Optional, Union
from datetime import datetime, timedelta
from loguru import logger

class RedisQueue:
    """Gestionnaire de file d'attente Redis pour traitement asynchrone des tâches"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, 
                 password: Optional[str] = None, ssl: bool = False):
        """
        Initialise la connexion à Redis
        
        Args:
            host: Hôte Redis
            port: Port Redis
            db: Index de la base de données Redis
            password: Mot de passe Redis (optionnel)
            ssl: Utiliser SSL pour la connexion
        """
        connection_params = {
            "host": host,
            "port": port,
            "db": db,
            "decode_responses": True
        }
        
        if password:
            connection_params["password"] = password
            
        if ssl:
            connection_params["ssl"] = True
            connection_params["ssl_cert_reqs"] = None
            
        try:
            self.redis = redis.Redis(**connection_params)
            self.redis.ping()  # Vérifier la connexion
            logger.info(f"Connected to Redis at {host}:{port}")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def enqueue(self, queue_name: str, data: Dict[str, Any], 
                delay: Optional[int] = None) -> str:
        """
        Ajoute une tâche à la file d'attente
        
        Args:
            queue_name: Nom de la file d'attente
            data: Données de la tâche
            delay: Délai en secondes avant le traitement (optionnel)
            
        Returns:
            ID de la tâche
        """
        task_id = str(uuid.uuid4())
        
        task = {
            "id": task_id,
            "data": data,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            # Stocke la tâche comme une hash
            task_key = f"task:{task_id}"
            self.redis.hset(task_key, mapping={
                "id": task_id,
                "data": json.dumps(data),
                "status": "pending",
                "created_at": task["created_at"],
                "updated_at": task["updated_at"],
                "queue": queue_name
            })
            
            # Si un délai est spécifié, on utilise un stream différé
            if delay:
                process_time = time.time() + delay
                self.redis.zadd(f"delayed:{queue_name}", {task_id: process_time})
                logger.info(f"Task {task_id} enqueued to {queue_name} with {delay}s delay")
            else:
                # Ajoute l'ID de la tâche à la file d'attente
                self.redis.lpush(f"queue:{queue_name}", task_id)
                logger.info(f"Task {task_id} enqueued to {queue_name}")
                
            return task_id
        except Exception as e:
            logger.error(f"Error enqueueing task to {queue_name}: {e}")
            raise
    
    def process_delayed_tasks(self, queue_name: str) -> int:
        """
        Déplace les tâches dont le délai est écoulé vers la file d'attente principale
        
        Args:
            queue_name: Nom de la file d'attente
            
        Returns:
            Nombre de tâches déplacées
        """
        delayed_key = f"delayed:{queue_name}"
        now = time.time()
        
        try:
            # Récupère les tâches dont le délai est écoulé
            task_ids = self.redis.zrangebyscore(delayed_key, 0, now)
            
            if not task_ids:
                return 0
                
            # Déplace les tâches vers la file d'attente principale
            with self.redis.pipeline() as pipe:
                for task_id in task_ids:
                    pipe.lpush(f"queue:{queue_name}", task_id)
                    pipe.zrem(delayed_key, task_id)
                pipe.execute()
                
            logger.info(f"Moved {len(task_ids)} delayed tasks to {queue_name}")
            return len(task_ids)
        except Exception as e:
            logger.error(f"Error processing delayed tasks for {queue_name}: {e}")
            return 0
    
    def dequeue(self, queue_name: str, wait: bool = True, timeout: int = 1) -> Optional[Dict[str, Any]]:
        """
        Récupère une tâche de la file d'attente
        
        Args:
            queue_name: Nom de la file d'attente
            wait: Attendre si la file est vide
            timeout: Timeout en secondes pour l'attente
            
        Returns:
            Tâche ou None si la file est vide
        """
        queue_key = f"queue:{queue_name}"
        processing_key = f"processing:{queue_name}"
        
        try:
            # Traite d'abord les tâches différées
            self.process_delayed_tasks(queue_name)
            
            if wait:
                # Attend qu'une tâche soit disponible
                result = self.redis.brpoplpush(queue_key, processing_key, timeout)
            else:
                # Ne pas attendre
                result = self.redis.rpoplpush(queue_key, processing_key)
                
            if not result:
                return None
                
            task_id = result
            task_key = f"task:{task_id}"
            
            # Récupère les données de la tâche
            task_data = self.redis.hgetall(task_key)
            if not task_data:
                logger.warning(f"Task {task_id} not found")
                return None
                
            # Met à jour le statut de la tâche
            self.redis.hset(task_key, "status", "processing")
            self.redis.hset(task_key, "updated_at", datetime.utcnow().isoformat())
            
            # Convertit les données JSON
            task_data["data"] = json.loads(task_data["data"])
            
            logger.info(f"Dequeued task {task_id} from {queue_name}")
            return task_data
        except Exception as e:
            logger.error(f"Error dequeuing task from {queue_name}: {e}")
            return None
    
    def complete_task(self, queue_name: str, task_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Marque une tâche comme complétée
        
        Args:
            queue_name: Nom de la file d'attente
            task_id: ID de la tâche
            result: Résultat de la tâche (optionnel)
            
        Returns:
            True si la tâche a été complétée, False sinon
        """
        processing_key = f"processing:{queue_name}"
        task_key = f"task:{task_id}"
        
        try:
            # Vérifie que la tâche existe
            if not self.redis.exists(task_key):
                logger.warning(f"Task {task_id} not found")
                return False
                
            # Met à jour le statut et le résultat
            with self.redis.pipeline() as pipe:
                pipe.hset(task_key, "status", "completed")
                pipe.hset(task_key, "updated_at", datetime.utcnow().isoformat())
                
                if result:
                    pipe.hset(task_key, "result", json.dumps(result))
                    
                pipe.lrem(processing_key, 1, task_id)
                pipe.execute()
                
            logger.info(f"Task {task_id} completed")
            return True
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}")
            return False
    
    def fail_task(self, queue_name: str, task_id: str, error: str) -> bool:
        """
        Marque une tâche comme échouée
        
        Args:
            queue_name: Nom de la file d'attente
            task_id: ID de la tâche
            error: Message d'erreur
            
        Returns:
            True si la tâche a été marquée comme échouée, False sinon
        """
        processing_key = f"processing:{queue_name}"
        task_key = f"task:{task_id}"
        
        try:
            # Vérifie que la tâche existe
            if not self.redis.exists(task_key):
                logger.warning(f"Task {task_id} not found")
                return False
                
            # Met à jour le statut et l'erreur
            with self.redis.pipeline() as pipe:
                pipe.hset(task_key, "status", "failed")
                pipe.hset(task_key, "updated_at", datetime.utcnow().isoformat())
                pipe.hset(task_key, "error", error)
                pipe.lrem(processing_key, 1, task_id)
                pipe.execute()

         logger.error(f"Task {task_id} failed: {error}")
         return True
     except Exception as e:
         logger.error(f"Error failing task {task_id}: {e}")
         return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations d'une tâche par son ID.

        Args:
            task_id: ID de la tâche

        Returns:
            Dictionnaire contenant les informations de la tâche ou None
        """
        task_key = f"task:{task_id}"
        try:
            task_data = self.redis.hgetall(task_key)
            if not task_data:
                logger.warning(f"No task found for ID {task_id}")
                return None
            if "data" in task_data:
                task_data["data"] = json.loads(task_data["data"])
            if "result" in task_data:
                task_data["result"] = json.loads(task_data["result"])
            return task_data
        except Exception as e:
            logger.error(f"Error retrieving status for task {task_id}: {e}")
            return None

    def requeue_task(self, queue_name: str, task_id: str) -> bool:
        """
        Réinsère une tâche dans la file d'attente (ex: après échec).

        Args:
            queue_name: Nom de la file d'attente
            task_id: ID de la tâche

        Returns:
            True si réinsertion réussie, False sinon
        """
        task_key = f"task:{task_id}"
        processing_key = f"processing:{queue_name}"
        queue_key = f"queue:{queue_name}"

        try:
            if not self.redis.exists(task_key):
                logger.warning(f"Task {task_id} not found")
                return False

            with self.redis.pipeline() as pipe:
                pipe.lrem(processing_key, 1, task_id)
                pipe.hset(task_key, "status", "pending")
                pipe.hset(task_key, "updated_at", datetime.utcnow().isoformat())
                pipe.lpush(queue_key, task_id)
                pipe.execute()

            logger.info(f"Task {task_id} requeued to {queue_name}")
            return True
        except Exception as e:
            logger.error(f"Error requeuing task {task_id}: {e}")
            return False

import redis
import json
import uuid
import time
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger


class RedisQueue:
    """Gestionnaire de file d'attente Redis pour traitement asynchrone des tâches"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0,
                 password: Optional[str] = None, ssl: bool = False):
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
            self.redis.ping()
            logger.info(f"✅ Connected to Redis at {host}:{port}")
        except redis.exceptions.ConnectionError as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise

    def enqueue(self, queue_name: str, data: Dict[str, Any], delay: Optional[int] = None) -> str:
        task_id = str(uuid.uuid4())
        created = datetime.utcnow().isoformat()

        try:
            task_key = f"task:{task_id}"
            self.redis.hset(task_key, mapping={
                "id": task_id,
                "data": json.dumps(data),
                "status": "pending",
                "created_at": created,
                "updated_at": created,
                "queue": queue_name
            })

            if delay:
                self.redis.zadd(f"delayed:{queue_name}", {task_id: time.time() + delay})
                logger.info(f"🕒 Task {task_id} enqueued to {queue_name} with {delay}s delay")
            else:
                self.redis.lpush(f"queue:{queue_name}", task_id)
                logger.info(f"📩 Task {task_id} enqueued to {queue_name}")

            return task_id
        except Exception as e:
            logger.error(f"❌ Error enqueueing task to {queue_name}: {e}")
            raise

    def process_delayed_tasks(self, queue_name: str) -> int:
        delayed_key = f"delayed:{queue_name}"
        now = time.time()

        try:
            task_ids = self.redis.zrangebyscore(delayed_key, 0, now)
            if not task_ids:
                return 0

            with self.redis.pipeline() as pipe:
                for task_id in task_ids:
                    pipe.lpush(f"queue:{queue_name}", task_id)
                    pipe.zrem(delayed_key, task_id)
                pipe.execute()

            logger.info(f"🔁 Moved {len(task_ids)} delayed tasks to {queue_name}")
            return len(task_ids)
        except Exception as e:
            logger.error(f"❌ Error processing delayed tasks for {queue_name}: {e}")
            return 0

    def dequeue(self, queue_name: str, wait: bool = True, timeout: int = 1) -> Optional[Dict[str, Any]]:
        queue_key = f"queue:{queue_name}"
        processing_key = f"processing:{queue_name}"

        try:
            self.process_delayed_tasks(queue_name)

            result = (
                self.redis.brpoplpush(queue_key, processing_key, timeout)
                if wait else self.redis.rpoplpush(queue_key, processing_key)
            )

            if not result:
                return None

            task_id = result
            task_key = f"task:{task_id}"
            task_data = self.redis.hgetall(task_key)

            if not task_data:
                logger.warning(f"⚠️ Task {task_id} not found")
                return None

            self.redis.hset(task_key, mapping={
                "status": "processing",
                "updated_at": datetime.utcnow().isoformat()
            })

            task_data["data"] = json.loads(task_data["data"])
            logger.info(f"✅ Dequeued task {task_id} from {queue_name}")
            return task_data
        except Exception as e:
            logger.error(f"❌ Error dequeuing task from {queue_name}: {e}")
            return None

    def complete_task(self, queue_name: str, task_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        processing_key = f"processing:{queue_name}"
        task_key = f"task:{task_id}"

        try:
            if not self.redis.exists(task_key):
                logger.warning(f"⚠️ Task {task_id} not found")
                return False

            with self.redis.pipeline() as pipe:
                pipe.hset(task_key, mapping={
                    "status": "completed",
                    "updated_at": datetime.utcnow().isoformat()
                })

                if result:
                    pipe.hset(task_key, "result", json.dumps(result))

                pipe.lrem(processing_key, 1, task_id)
                pipe.execute()

            logger.info(f"✅ Task {task_id} marked as completed")
            return True
        except Exception as e:
            logger.error(f"❌ Error completing task {task_id}: {e}")
            return False

    def fail_task(self, queue_name: str, task_id: str, error: str) -> bool:
        processing_key = f"processing:{queue_name}"
        task_key = f"task:{task_id}"

        try:
            if not self.redis.exists(task_key):
                logger.warning(f"⚠️ Task {task_id} not found")
                return False

            with self.redis.pipeline() as pipe:
                pipe.hset(task_key, mapping={
                    "status": "failed",
                    "updated_at": datetime.utcnow().isoformat(),
                    "error": error
                })
                pipe.lrem(processing_key, 1, task_id)
                pipe.execute()

            logger.error(f"❌ Task {task_id} failed: {error}")
            return True
        except Exception as e:
            logger.error(f"❌ Error failing task {task_id}: {e}")
            return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        task_key = f"task:{task_id}"
        try:
            task_data = self.redis.hgetall(task_key)
            if not task_data:
                logger.warning(f"❓ No task found for ID {task_id}")
                return None

            if "data" in task_data:
                task_data["data"] = json.loads(task_data["data"])
            if "result" in task_data:
                task_data["result"] = json.loads(task_data["result"])

            return task_data
        except Exception as e:
            logger.error(f"❌ Error retrieving task status for {task_id}: {e}")
            return None

    def requeue_task(self, queue_name: str, task_id: str) -> bool:
        task_key = f"task:{task_id}"
        processing_key = f"processing:{queue_name}"
        queue_key = f"queue:{queue_name}"

        try:
            if not self.redis.exists(task_key):
                logger.warning(f"⚠️ Task {task_id} not found")
                return False

            with self.redis.pipeline() as pipe:
                pipe.lrem(processing_key, 1, task_id)
                pipe.hset(task_key, mapping={
                    "status": "pending",
                    "updated_at": datetime.utcnow().isoformat()
                })
                pipe.lpush(queue_key, task_id)
                pipe.execute()

            logger.info(f"🔄 Task {task_id} requeued to {queue_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error requeuing task {task_id}: {e}")
            return False

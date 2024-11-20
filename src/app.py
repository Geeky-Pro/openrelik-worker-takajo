# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import redis
from celery.app import Celery

# Retrieve Redis URL from environment variables
REDIS_URL = os.getenv("REDIS_URL")

# Initialize Celery app
celery = Celery(
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.automagic_timeline"]          # New Takajo worker task module
)

# Redis client for additional operations if needed
redis_client = redis.Redis.from_url(REDIS_URL)

### OpenRelik worker for running Hayabusa on input files

This worker use the tool `takajo` from Yamato-Security.
See https://github.com/Yamato-Security/takajo for more information.

#### Installation instructions
Add to your docker-compose configuration:
```
  openrelik-worker-tajako:
    container_name: openrelik-worker-takajo
    image: ghcr.io/geeky-pro/openrelik-worker-takajo:latest
    restart: always
    environment:
      - REDIS_URL=redis://openrelik-redis:6379
    volumes:
      - ./data:/usr/share/openrelik/data
    command: "celery --app=src.app worker --task-events --concurrency=4 --loglevel=INFO -Q openrelik-worker-takajo"
```


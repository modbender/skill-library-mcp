# Essential Commands — Docker

Quick reference for common Docker operations.

## Container Lifecycle

```bash
docker run -d --name app -p 8080:80 image    # start detached
docker ps                                      # list running
docker ps -a                                   # list all
docker stop app && docker rm app              # cleanup
docker logs -f app                            # follow logs
docker exec -it app sh                        # shell into
```

## Image Management

```bash
docker build -t myapp:1.0 .                   # build
docker images                                  # list
docker pull nginx:alpine                       # fetch
docker push registry/myapp:1.0                # publish
docker rmi $(docker images -q --filter dangling=true)  # prune
```

## Compose

```bash
docker compose up -d                          # start stack
docker compose down                           # stop & remove
docker compose logs -f                        # follow all logs
docker compose ps                             # stack status
docker compose exec web sh                    # shell into service
```

## Cleanup

```bash
docker container prune                        # remove stopped
docker image prune                            # remove dangling
docker volume prune                           # remove unused (DESTRUCTIVE)
docker system prune -a --volumes              # remove everything (DESTRUCTIVE)
```

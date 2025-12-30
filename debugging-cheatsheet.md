# Docker Debugging Cheatsheet

## Container Management

### List running containers

docker ps

### List all containers (including stopped)

docker ps -a

### Stop container

docker stop autom8_api

### Start stopped container

docker start autom8_api

### Restart container

docker restart autom8_api

### Remove container

docker rm autom8_api
docker rm -f autom8_api # Force remove (even if running)

## Logs and Debugging

### View logs

docker logs autom8_api
docker logs -f autom8_api # Follow (real-time)
docker logs --tail 100 autom8_api # Last 100 lines
docker compose logs -f

### Execute comand inside running container

docker exec -it autom8_api bash
Exit with: exit

### Inspect container

docker inspect autom8_api

## Image Management

### List images

docker images

### Remove image

docker rmi autom8:latest
docker rmi -f autom8:latest # Force remove

### Remove unused images

docker image prune
docker image prune -a # Remove all unused images

## Volume Management

### List volumes

docker volume ls

### Inspect volume

docker volume inspect autom8_data

### Remove volume

docker volume rm autom_data

### Remove all unused volumes

docker volume prune

## Network Management

### List networks

docker network ls

### Inspect network

docker network inspect autom8_network

## Docker Compose

### Start services

docker compose up -d

### Stop services

docker compose down

### Rebuild and start

docker compose up -d --build

### Scale service (multiple instances)

docker compose up -d --scale api=3

## System Cleanup

### Remove all stopped containers

docker container prune

### Remove all unused resources

docker system prune
docker system prune -a # Including unused images

### Check disk usage

docker system df

## Common Issues

### "Port already in use" (Stop container using port)

docker ps # Find container ID
docker stop <container_id>

### Change port mapping

docker run -p 5001:5000 ... # Use host port 5001

### "Cannot connect to Docker daemon"

Solution: Start Docker Desktop

### " Permission denied"

Windows: Run PowerShell as Administrator
Linux: Add user to docker group
sudo usermod -aG docker $USER

### Container exits immediately

Check logs for error
docker logs <container_name>

### Run interactively to debug

docker run -it autom8:latest bash

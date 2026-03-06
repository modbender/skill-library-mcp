# Docker Setup Guide for OpenClaw / Guía de Docker para OpenClaw

## Why Docker? / ¿Por qué Docker?

Running OpenClaw without container isolation means it has full access to your server: files, network, processes, and system configurations. A compromised skill or prompt injection attack could give an attacker complete control of your machine.

Docker creates an isolated environment where OpenClaw can only access what you explicitly allow. This is the single most effective security measure you can implement.

Sin aislamiento de contenedor, OpenClaw tiene acceso completo a tu servidor. Docker crea un entorno aislado donde OpenClaw solo puede acceder a lo que tú permitas explícitamente. Es la medida de seguridad más efectiva que puedes implementar.

---

## Prerequisites / Requisitos Previos

- Ubuntu 20.04+ or Debian 11+ (recommended)
- Root or sudo access
- At least 2GB free RAM
- At least 10GB free disk space

---

## Step 1: Install Docker / Paso 1: Instalar Docker

```bash
# Remove old versions / Remover versiones anteriores
sudo apt-get remove docker docker-engine docker.io containerd runc 2>/dev/null

# Install prerequisites / Instalar prerequisitos
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker GPG key / Agregar clave GPG de Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository / Agregar repositorio de Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker / Instalar Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify installation / Verificar instalación
sudo docker run hello-world
```

---

## Step 2: Create the Dockerfile / Paso 2: Crear el Dockerfile

Create a file called `Dockerfile` in your OpenClaw directory:

Crea un archivo llamado `Dockerfile` en tu directorio de OpenClaw:

```dockerfile
FROM node:20-slim

# Install Python and security tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sudo \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for OpenClaw
RUN useradd -m -s /bin/bash openclaw

# Set working directory
WORKDIR /home/openclaw/.openclaw

# Copy OpenClaw files (adjust path as needed)
COPY . /home/openclaw/.openclaw/

# Set ownership
RUN chown -R openclaw:openclaw /home/openclaw

# Switch to non-root user
USER openclaw

# Expose only necessary port
EXPOSE 3000

# Start OpenClaw
CMD ["node", "gateway.js"]
```

---

## Step 3: Create docker-compose.yml / Paso 3: Crear docker-compose.yml

This is the recommended approach because it makes managing the container much easier.

Este es el enfoque recomendado porque facilita la gestión del contenedor.

```yaml
version: '3.8'

services:
  openclaw:
    build: .
    container_name: openclaw
    restart: unless-stopped

    # Security settings / Configuración de seguridad
    security_opt:
      - no-new-privileges:true
    read_only: false

    # Resource limits / Límites de recursos
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

    # Network / Red
    ports:
      - "127.0.0.1:3000:3000"  # Only accessible from localhost

    # Volumes - only mount what's needed / Solo montar lo necesario
    volumes:
      - openclaw-data:/home/openclaw/.openclaw/data
      - openclaw-skills:/home/openclaw/.openclaw/skills
      - openclaw-credentials:/home/openclaw/.openclaw/credentials

    # Environment / Variables de entorno
    environment:
      - NODE_ENV=production

    # Capabilities - drop all, add only what's needed
    # Capacidades - remover todas, agregar solo las necesarias
    cap_drop:
      - ALL

volumes:
  openclaw-data:
  openclaw-skills:
  openclaw-credentials:
```

---

## Step 4: Build and Run / Paso 4: Construir y Ejecutar

```bash
# Build the image / Construir la imagen
sudo docker compose build

# Start the container / Iniciar el contenedor
sudo docker compose up -d

# Verify it's running / Verificar que está corriendo
sudo docker compose ps

# View logs / Ver logs
sudo docker compose logs -f openclaw
```

---

## Step 5: Install LobsterGuard Inside Docker / Paso 5: Instalar LobsterGuard Dentro de Docker

```bash
# Enter the container / Entrar al contenedor
sudo docker exec -it openclaw bash

# Inside the container, clone and install LobsterGuard
# Dentro del contenedor, clonar e instalar LobsterGuard
git clone https://github.com/jarb02/lobsterguard.git /tmp/lobsterguard
cd /tmp/lobsterguard
sudo bash install.sh
```

---

## Managing the Container / Gestión del Contenedor

```bash
# Stop / Detener
sudo docker compose stop

# Start / Iniciar
sudo docker compose start

# Restart / Reiniciar
sudo docker compose restart

# View logs / Ver logs
sudo docker compose logs -f

# Enter shell / Entrar al shell
sudo docker exec -it openclaw bash

# Destroy and recreate (data persists in volumes)
# Destruir y recrear (los datos persisten en volúmenes)
sudo docker compose down
sudo docker compose up -d

# Full reset including data / Reset completo incluyendo datos
sudo docker compose down -v
sudo docker compose up -d
```

---

## Security Best Practices / Mejores Prácticas de Seguridad

### 1. Network Isolation / Aislamiento de Red

The `docker-compose.yml` above binds port 3000 to `127.0.0.1` only, meaning the service is only accessible from the server itself. If you need external access, use a reverse proxy like Nginx:

El `docker-compose.yml` anterior vincula el puerto 3000 solo a `127.0.0.1`, lo que significa que el servicio solo es accesible desde el servidor mismo. Si necesitas acceso externo, usa un reverse proxy como Nginx:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Regular Updates / Actualizaciones Regulares

```bash
# Update Docker images / Actualizar imágenes Docker
sudo docker compose pull
sudo docker compose up -d --build
```

### 3. Backup Volumes / Respaldo de Volúmenes

```bash
# Backup / Respaldo
sudo docker run --rm -v openclaw-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/openclaw-data-backup.tar.gz -C /data .

# Restore / Restaurar
sudo docker run --rm -v openclaw-data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/openclaw-data-backup.tar.gz -C /data
```

### 4. Monitor Container / Monitorear Contenedor

```bash
# Resource usage / Uso de recursos
sudo docker stats openclaw

# Security audit / Auditoría de seguridad
sudo docker inspect openclaw | grep -i "privileged\|cap\|security"
```

---

## Troubleshooting / Solución de Problemas

**Container won't start / El contenedor no inicia:**
```bash
sudo docker compose logs openclaw
```

**Permission denied errors / Errores de permisos:**
```bash
sudo docker exec -it openclaw ls -la /home/openclaw/.openclaw/
```

**OpenClaw can't reach Telegram / OpenClaw no puede comunicarse con Telegram:**
Make sure DNS is working inside the container:
Asegúrate de que el DNS funciona dentro del contenedor:
```bash
sudo docker exec -it openclaw ping -c 1 api.telegram.org
```

**Need to update OpenClaw / Necesitas actualizar OpenClaw:**
```bash
sudo docker compose down
# Update your OpenClaw files
sudo docker compose up -d --build
```

---

## What Changes with Docker / Qué Cambia con Docker

| Without Docker / Sin Docker | With Docker / Con Docker |
|-----|-----|
| OpenClaw has full server access / Acceso completo al servidor | Limited to container only / Limitado al contenedor |
| A compromised skill affects everything / Un skill comprometido afecta todo | Damage contained to container / Daño contenido al contenedor |
| Manual cleanup on compromise / Limpieza manual al ser comprometido | Destroy and recreate container / Destruir y recrear contenedor |
| LobsterGuard score: 95/100 max | LobsterGuard score: 100/100 |

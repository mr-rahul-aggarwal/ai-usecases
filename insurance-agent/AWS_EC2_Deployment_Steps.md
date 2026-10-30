# Build and Run the Insurance Agent on AWS EC2

This guide builds the Docker image from the repository on an Ubuntu EC2 instance. For Docker Desktop on a Mac or Windows laptop, follow the [Docker Deployment Guide](Docker_Deployment_Guide.md).

## 1. Launch an EC2 instance

In the AWS Console, launch an instance with an Ubuntu Server LTS image. Choose an instance with enough memory to build and run the application; its Docker image includes PyTorch and ChromaDB, so a small micro instance may run out of memory during the build.

Create or select a key pair and save the private key securely. In the instance's security group, allow:

- SSH (port 22) from your own IP address.
- HTTP (port 80) from the addresses that need to access the app. For public access, this may be `0.0.0.0/0`.

The application serves HTTP on port 80 in this guide. Do not enable HTTPS unless you also configure a TLS certificate and a web server or load balancer to terminate HTTPS.

After the instance starts, copy its public IPv4 address.

## 2. Connect to the instance

From a terminal on your Mac or Windows computer, connect using the private key and public IP address from the previous step. Replace the example names with your actual file and address:

```bash
ssh -i "YOUR_KEY_FILE.pem" ubuntu@YOUR_EC2_PUBLIC_IP
```

## 3. Install Docker and Git

Run these commands after connecting to the Ubuntu instance:

```bash
sudo apt update
sudo apt install -y docker.io git
sudo systemctl enable --now docker
```

- `sudo apt update` refreshes Ubuntu's package list.
- `sudo apt install -y docker.io git` installs Docker Engine and Git.
- `sudo systemctl enable --now docker` starts Docker and enables it after a reboot.

The Docker commands below use `sudo`, so adding your account to the Docker group is not needed.

## 4. Clone the project and set up the API credentials

```bash
git clone https://github.com/Gr8Learning-2312/insurance-agent.git
cd insurance-agent
cp .env.example .env
nano .env
```

In the editor, replace the placeholder API key and check that `OPENAI_BASE_URL` matches the endpoint associated with your key. Keep values unquoted, for example:

```env
OPENAI_API_KEY=your_real_api_key
OPENAI_BASE_URL=https://your-provider.example/v1
```

If you use the standard OpenAI API, set the base URL to `https://api.openai.com/v1`. Save and exit nano with Ctrl+O, Enter, then Ctrl+X. Restrict access to the credentials file:

```bash
chmod 600 .env
```

Do not commit `.env` or copy it into the image. Docker receives it when the container starts.

## 5. Build the Docker image

Run this from the repository folder:

```bash
sudo docker build -t insurance-agent:local .
```

- `docker build` reads the `Dockerfile`, installs the dependencies, and creates an image.
- `-t insurance-agent:local` names the image `insurance-agent` and tags it `local`.
- `.` sets the current repository folder as the build context. The `.dockerignore` file excludes `.env`, local ChromaDB data, and development files.

The first build downloads the Python base image and dependencies, so it can take several minutes.

## 6. Start the container

```bash
sudo docker run -d --name insurance-agent --restart unless-stopped --env-file .env -p 80:8501 insurance-agent:local
```

- `-d` runs the container in the background.
- `--name insurance-agent` assigns a name for later commands.
- `--restart unless-stopped` restarts the container after a reboot unless it was manually stopped.
- `--env-file .env` passes the API settings into the container at startup.
- `-p 80:8501` maps EC2 port 80 to the app's port 8501 (`host:container`).

If port 80 is allowed by the security group, open `http://YOUR_EC2_PUBLIC_IP` in a browser. Use `http://`, because this setup does not configure HTTPS.

## 7. Check the app and manage the container

Check whether the container is running and view its latest logs:

```bash
sudo docker ps
sudo docker logs --tail 100 insurance-agent
```

Use these commands to control the existing container:

```bash
sudo docker stop insurance-agent
sudo docker start insurance-agent
sudo docker restart insurance-agent
```

- `stop` pauses the app but keeps the container so it can be started again.
- `start` resumes a stopped container with its original settings.
- `restart` stops and starts the same container; it does not read changed environment settings or a rebuilt image.

If you change `.env` or the image, recreate the container so it receives the new settings or image. For changed project code, rebuild first:

```bash
sudo docker build -t insurance-agent:local .
sudo docker rm -f insurance-agent
sudo docker run -d --name insurance-agent --restart unless-stopped --env-file .env -p 80:8501 insurance-agent:local
```

`docker rm -f` removes the container, not the image. This run command does not mount persistent storage; removing the container can discard ChromaDB data written inside it. For long-running use, configure a Docker volume for `CHROMA_PERSIST_DIR`.

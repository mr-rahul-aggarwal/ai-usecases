# Run the Insurance Agent with Docker

Use these steps on a Mac or Windows laptop. [Install Docker Desktop](https://docs.docker.com/get-started/get-docker/) for your operating system, start it, and wait until it shows that Docker is running. Open Terminal on Mac or PowerShell on Windows, then go to the project folder before running the commands. Do not use `sudo` with Docker Desktop.

## Choose how to get the image

| Option | What it does | Choose this path when |
| --- | --- | --- |
| Pull from Docker Hub | Downloads the already-built `gr8learning/insurance-agent:v1` image. | You want to run the published version without building it yourself. |
| Build from this project | Builds an image from the local `Dockerfile` and project files. | You want to build from the source code in this repository, include your code changes, or explore how the Dockerfile creates an image. |

Both options need an API key for the OpenAI-compatible endpoint configured in `.env`. The published image is for `linux/amd64`; on Apple Silicon, Docker Desktop may show a platform warning and use emulation.

## Prepare the environment file

From the project folder, make a copy of `.env.example` named `.env` using Finder, File Explorer, or your editor. Put your API key in `.env`. The example contains the GreatLearning endpoint; keep it only if your key is for that service. For the standard OpenAI API, set `OPENAI_BASE_URL=https://api.openai.com/v1`. Keep values unquoted, because Docker's `--env-file` passes quote characters literally. Do not commit `.env` or include it in an image.

## Option 1: Pull and run the Docker Hub image

### Download and inspect the image

```bash
docker pull gr8learning/insurance-agent:v1
docker image ls gr8learning/insurance-agent
```

- `docker pull` downloads the published image to your computer.
- `docker image ls` lists downloaded images and tags. `v1` is the version tag.

### Start the container

```bash
docker run -d --name insurance-agent --restart unless-stopped --env-file .env -p 8501:8501 gr8learning/insurance-agent:v1
```

- `docker run` creates and starts a container from an image.
- `-d` runs it in the background, leaving the terminal available.
- `--name insurance-agent` assigns a name for later commands.
- `--restart unless-stopped` restarts it if Docker Desktop restarts, unless you have stopped it yourself.
- `--env-file .env` passes settings from `.env` into the container when it starts.
- `-p 8501:8501` maps port 8501 on your laptop to port 8501 in the container (`laptop:container`).
- `gr8learning/insurance-agent:v1` is the image to run.

Open [http://localhost:8501](http://localhost:8501). Check the container and its output with:

```bash
docker ps
docker logs -f insurance-agent
```

`docker ps` lists running containers. `docker logs -f` follows the app logs; press Ctrl+C to stop viewing logs without stopping the container.

## Option 2: Build and run from this project

This option reads the `Dockerfile`, installs the dependencies, and copies the app into a local image. Docker may download the base image `python:3.11-slim` if it is not already on your computer. The `.dockerignore` file keeps `.env`, local ChromaDB data, and development files out of the image build.

### Build the image

Run this from the project folder:

```bash
docker build -t insurance-agent:local .
```

- `docker build` creates an image using the Dockerfile.
- `-t insurance-agent:local` gives the image the name `insurance-agent` and tag `local`.
- `.` means the current project folder is the build context, the files Docker can use during the build. Docker uses the `Dockerfile` in that folder by default.

### Start a container from the local image

```bash
docker run -d --name insurance-agent --restart unless-stopped --env-file .env -p 8501:8501 insurance-agent:local
```

The options are the same as in Option 1; the final image name selects the locally built image. Open [http://localhost:8501](http://localhost:8501).

## Stop, start, restart, or recreate the container

These commands work for either image option. A container is an instance of an image. Stopping, starting, and restarting reuse that same container and its original settings.

### Stop it temporarily

```bash
docker stop insurance-agent
```

Use this when you want to shut the app down for now. The stopped container remains available to start again.

### Start it again

```bash
docker start insurance-agent
```

Use this after `docker stop` when you want to resume the existing container with its original image, ports, and environment settings.

### Restart it

```bash
docker restart insurance-agent
```

Use this to stop and start the same container, for example if the app is unresponsive. Restarting does not read a changed `.env` file or update the image.

### Recreate it after changing settings or the image

Use this when you have changed `.env`, port mappings, container options, or want to run a newer image. A running container does not pick up those changes automatically.

If only `.env` or the run options changed, remove the old container and rerun the same `docker run` command for the image you chose; there is no need to pull or rebuild the image.

To refresh the published `v1` image, pull it, remove the old container, then rerun the Option 1 `docker run` command. If the publisher releases a new tag, use that tag in both the pull and run commands:

```bash
docker pull gr8learning/insurance-agent:v1
docker rm -f insurance-agent
```

For changed local project code, rebuild the image, remove the old container, then rerun the Option 2 `docker run` command:

```bash
docker build -t insurance-agent:local .
docker rm -f insurance-agent
```

`docker rm -f` stops and removes the container; it does not remove the image. These run examples do not attach a persistent data volume, so removing the container can discard ChromaDB data written inside it. For a temporary learning run this may be acceptable; for longer use, configure persistent storage.

## Which option should I choose?

Choose **Option 1** to run the published application quickly. Choose **Option 2** to build an image from this repository and see how the Dockerfile packages the application. To try both, complete Option 1 first, then stop and remove its container before starting Option 2. Both paths use the container name `insurance-agent`.

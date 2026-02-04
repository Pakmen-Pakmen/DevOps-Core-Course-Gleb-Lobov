## Docker Best Practices Applied

### Non-root user
```dockerfile
RUN useradd -m appuser
USER appuser
```
Running containers as non-root reduces the impact of potential container breakouts.

### Layer caching
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
Dependencies are installed before application code to leverage Docker layer caching and speed up rebuilds.


## Image Information & Decisions

The final image size of ~47.7MB is acceptable for a Python Flask service and significantly smaller than full Python images.

Layer structure is optimized by installing dependencies before copying application code, allowing Docker to reuse cached layers when only code changes.


## Build & Run Process

### Build
```bash
docker build -t devops-info-service .
[+] Building 62.3s (12/12) FINISHED                                                 docker:desktop-linux
 => [internal] load build definition from Dockerfile                                                0.1s
 => => transferring dockerfile: 261B                                                                0.0s
 => [internal] load metadata for docker.io/library/python:3.13-slim                                22.8s
 => [auth] library/python:pull token for registry-1.docker.io                                       0.0s
 => [internal] load .dockerignore                                                                   0.1s
 => => transferring context: 125B                                                                   0.0s 
 => [1/6] FROM docker.io/library/python:3.13-slim@sha256:2b9c9803c6a287cafa0a8c917211dddd23dcd2016  8.4s 
 => => resolve docker.io/library/python:3.13-slim@sha256:2b9c9803c6a287cafa0a8c917211dddd23dcd2016  0.1s 
 => => sha256:8a3ca8cbd12dc4a76ad33ca83aebbcb13a6da17018dacb336bc37d9eac65dd1d 1.29MB / 1.29MB      1.1s 
 => => sha256:0c8d55a45c0dc58de60579b9cc5b708de9e7957f4591fc7de941b67c7e245da0 29.78MB / 29.78MB    4.2s 
 => => sha256:b3639af2341969e7f62cde77631753501fb03cbe8dd811e74d50bf127a8a34ad 11.79MB / 11.79MB    7.7s
 => => sha256:0da4a108bcf2485b81d202f1df5743a4fce83c36dd004a09d536d5ed866d3303 251B / 251B          2.5s
 => => extracting sha256:0c8d55a45c0dc58de60579b9cc5b708de9e7957f4591fc7de941b67c7e245da0           0.7s 
 => => extracting sha256:8a3ca8cbd12dc4a76ad33ca83aebbcb13a6da17018dacb336bc37d9eac65dd1d           0.1s 
 => => extracting sha256:b3639af2341969e7f62cde77631753501fb03cbe8dd811e74d50bf127a8a34ad           0.4s
 => => extracting sha256:0da4a108bcf2485b81d202f1df5743a4fce83c36dd004a09d536d5ed866d3303           0.0s
 => [internal] load build context                                                                   0.1s
 => => transferring context: 4.47kB                                                                 0.0s
 => [2/6] RUN useradd -m appuser                                                                    0.6s
 => [3/6] WORKDIR /app                                                                              0.1s 
 => [4/6] COPY requirements.txt .                                                                   0.1s 
 => [5/6] RUN pip install --no-cache-dir -r requirements.txt                                       28.2s 
 => [6/6] COPY app.py .                                                                             0.1s 
 => exporting to image                                                                              1.5s 
 => => exporting layers                                                                             1.0s 
 => => exporting manifest sha256:6e2ec6eaf2a329229628665bcba85894e51d85366beba9e0f18bca80564929c7   0.0s 
 => => exporting config sha256:59383ed6ed1d928c071e18b3a24237757ecbd5715348d22943eaa1e17ac8bec8     0.0s 
 => => exporting attestation manifest sha256:1ba997cda059a82e0162dd9919ad91385f7900382e77009027de0  0.1s 
 => => exporting manifest list sha256:0785c8399c2fe6cee7b908b7555dd45bf96022db21645283522114fa0e72  0.0s 
 => => naming to docker.io/library/lab02-devops-info:latest                                         0.0s 
 => => unpacking to docker.io/library/lab02-devops-info:latest                                      0.3s 
 ```
### Run
```bash
docker run -p 5000:5000 pakmengamer/devops-info-service
2026-02-04 16:05:30,618 - INFO - Starting DevOps Info Service...
 * Serving Flask app 'app'
 * Debug mode: off
2026-02-04 16:05:30,624 - INFO - WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://172.17.0.3:5000
2026-02-04 16:05:30,624 - INFO - Press CTRL+C to quit
```
Endpoint testing
```bash
curl http://localhost:5000/health
{"status":"healthy","timestamp":"2026-02-04T16:07:20.908757+00:00","uptime_seconds":110}

```
### Docker Hub repository:
https://hub.docker.com/r/PakmenGamer/devops-info-service

## Technical Analysis

The Dockerfile uses proper instruction ordering to maximize layer caching.

Running the container as a non-root user improves security.

The .dockerignore file prevents unnecessary files from being included in the image.

If application code were copied before dependency installation, any code change would invalidate the cache and force a full dependency reinstall.

## Challenges & Solutions

Problem: Docker image push failed because the repository name contained uppercase letters.

Solution: Docker Hub requires lowercase repository names, so the image was retagged using lowercase naming.
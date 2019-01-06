## Usage

```bash
# build and run containers
docker-compose up -d && \
printf "Open http://$(curl -s http://icanhazip.com):8020/ to use the tool.\n"
```

Now navigate to `http://{you_machine_ip}:8020/` to use the tool

![Screenshot](screenshot.png?raw=true "Screenshot")

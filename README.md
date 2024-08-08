# Fully automated bot for artifacts

## Firstly

copy `.env.example -> .env` and fill you credentials

## Local run

install dependencies: ```pip3 install -r requirements.txt```

run bots: ```python3 main.py```

## Docker

to run image run: ```sh start.sh```

on new commits just run (it also runs `monitoring.sh`):

```sh redeploy.sh```

you can escape monitoring with `Ctrl-C`

also you can run monitor anytime:

```sh monitoring.sh```

# Minecraft Server On-Demand (MSOD)

An AWS-backed Minecraft server that only launches when requested via Discord and
shuts down automatically when idle.

## Features

- Start the server with a single Discord command `/start`
- Stop the server with `/stop`
- Stop the server automatically when idle
- Runs in a low-cost VPC

## Implementation

- Uses AWS Lambda, EC2, API Gateway (HTTP API v2), and a Discord bot
- Fully typed Python (with `mypy-boto3` and `aws-lambda-typing`)
- CDK v2 infrastructure as code

## Requirements

- AWS CLI (configured)
- AWS CDK v2 (`npm install -g aws-cdk`)

## Running It

- Bootstrap with `cdk bootstrap`
- Deploy with `cdk deploy`
- Output should look like:

```
StartApiEndpoint = https://xxxx.amazonaws.com/start
StopApiEndpoint  = https://xxxx.amazonaws.com/stop
```

- Take note of these for the Discord bot
- Create a Discord bot at
  [Discord Applications](https://discord.com/developers/applications)
- Enable "Message Content Intent"
- Install the bot into a server
- Create a .env file:

```bash
DISCORD_TOKEN=your_bot_token
START_API_URL=https://xxxx.amazonaws.com/start
STOP_API_URL=https://xxxx.amazonaws.com/stop
```

- Run the bot with `python bot.py`

## Using It

- In the Discord server, `/start` will run the server
- The bot should reply with "Starting Minecraft server…"

## Development

- To lint and format, run `make lint`

## Cost

- EC2: Pay only while the server is running
- VPC: Free (no NAT gateway)
- Lambda: Very cheap
- API Gateway: Minimal monthly cost
- Discord bot: Free

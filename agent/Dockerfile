FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache docker-cli

COPY agent /app/agent
RUN pip install --no-cache-dir requests

ENV CENTER_URL="http://center:8003"
ENV FALCO_LOG="/var/log/falco/events.json"

CMD ["sh", "-c", "python agent/kubanomaly_agent.py --log $FALCO_LOG --center $CENTER_URL & python agent/kubanomaly_hardware.py --center $CENTER_URL"]

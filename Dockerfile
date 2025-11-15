FROM python:3.11-slim-bookworm AS base

WORKDIR /opt/finansy/url_shortener


FROM base AS builder

COPY src src
COPY pyproject.toml .

RUN python3.11 -m venv venv && \
    venv/bin/pip3 install . && \
    venv/bin/pip3 install uvicorn


FROM base AS production

COPY --from=builder /opt/finansy/url_shortener/venv ./venv
COPY start.sh \
     configs/production .

RUN chmod a+x *.sh && \
    mkdir dbs

EXPOSE 5001

ENTRYPOINT ["./start.sh"]
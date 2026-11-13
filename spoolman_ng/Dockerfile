# Thin wrapper over the published Spoolman image (#89). Home Assistant passes the matching per-arch
# image from build.yaml as BUILD_FROM. nginx exposes a Supervisor-only ingress listener;
# the original Spoolman listener remains available for direct API clients.
ARG BUILD_FROM
FROM ${BUILD_FROM}

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/*
COPY run.sh /run.sh
COPY supervise.py /supervise.py
COPY nginx.conf /etc/nginx/nginx.conf
RUN chmod +x /run.sh

# The supervisor starts Spoolman's own entrypoint, preserving its privilege drop.
ENTRYPOINT []
CMD ["/run.sh"]

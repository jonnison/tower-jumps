FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.5.28 /uv /uvx /bin/
LABEL maintainer="jonnison@ufpi.edu.br"

# Set environment variables for security
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies for GeoDjango
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libspatialindex-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

# Set working directory
WORKDIR /app

# Create a non-root user
RUN adduser --disabled-password --gecos '' --home /app appuser && chown -R appuser /app
USER appuser
ENV HOME=/app

# Instale o uv como appuser, garantindo que vai para ~/.local/bin
RUN mkdir -p /app/.local/bin && curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/app/.local/bin/:$PATH"

# Install Python dependencies
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
# RUN uv sync --frozen
ENV PATH="/app/.venv/bin:$PATH"

# Copy the application code
COPY --chown=appuser:appuser . .

# Expose port
EXPOSE 8000

# ENTRYPOINT ["uv", "run", "--"]
CMD [ "gunicorn","config.wsgi:application","--bind","0.0.0.0:8000","-t","40","--log-level","DEBUG" ]

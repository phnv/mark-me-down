FROM python:3.11-slim

WORKDIR /app

# Install git (required for some packages) and curl (for uv)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv globally
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL="/usr/local/bin" sh

# Copy only the dependency files first (for Docker caching)
COPY pyproject.toml ./

# Install the production dependencies using uv
RUN uv sync --no-dev

# Copy the rest of the application code
COPY . .

# Cloud Run injects PORT environment variable
ENV PORT=8080
EXPOSE 8080

# Start the Starlette ASGI server using uv run
CMD ["sh", "-c", "uv run uvicorn agents.v2.a2a_server:app --host 0.0.0.0 --port ${PORT}"]

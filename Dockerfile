FROM python:3.11-slim-bookworm

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        p7zip-full \
        git && \
    rm -rf /var/lib/apt/lists/*

# Mark the `/github/workspace` directory as "safe" for Git operations.
RUN git config --system --add safe.directory /github/workspace
RUN git config --global pull.ff only

WORKDIR /app

COPY requirements.txt release_zips/release_zips.py ./
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "release_zips.py"]

# Stage for making a Ubuntu compatible executable
FROM ubuntu:18.04 AS build

WORKDIR /usr/src/app

# Make sure we never get asked a question
ENV DEBIAN_FRONTEND=noninteractive

RUN \
    # Update, quietly
    apt-get update -yqq  && \
    # Install Python 3
    apt-get install -yqq python3 python3-pip && \
    # Remove artifacts, cache, other junk
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Make python3 and pip3 the defaults
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10 && \
    update-alternatives --install /usr/local/bin/python python /usr/bin/python3.6 10 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10

# Uncomment this to sanity check we're getting Python 3.6 or later
# RUN python3 --version

# Install builder
RUN pip install pyinstaller

# Add dependencies, which isn't strictly necessary except for our forked
# ConfigArgParse 'cause they haven't merged my PR yet
COPY deps/ deps/
# Copy in the app code
COPY setup.py setup.py
COPY turo_parser/ turo_parser/

# Install dependencies
RUN pip install --find-links /usr/src/app/deps --no-index .

# Building executable
RUN pyinstaller --onefile turo_parser/main.py

# Stage for executable container
FROM python:3.6 AS final

# Copy artifacts from previous build
COPY --from=build /usr/src/app/dist/main /usr/local/bin/turo-parser

# Use our command for container runtime
ENTRYPOINT ["/usr/local/bin/turo-parser"]

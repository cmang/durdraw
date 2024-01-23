# syntax=docker/dockerfile:1
FROM python:3.8-alpine

WORKDIR /durdraw
COPY . .
RUN pip install --upgrade .
ENV TERM=xterm-256color
ENTRYPOINT ["durdraw"]

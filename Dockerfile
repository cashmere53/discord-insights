FROM python:3.10-slim-bullseye

RUN apt update && \
    apt upgrade -y

RUN adduser melon
ENV HOME /home/melon
WORKDIR ${HOME}
USER melon

COPY . .
RUN python -m pip install .

EXPOSE 443

CMD [ "python", "-m", "dinsights" ]

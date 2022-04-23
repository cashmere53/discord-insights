FROM python:slim-bullseye

RUN apt update && \
    apt upgrade -y && \
    apt install -y git && \
    pip install git+https://github.com/cashmere53/discord-insights

RUN adduser melon
ENV HOME /home/melon
WORKDIR ${HOME}
USER melon

COPY ./token.txt ${HOME}

EXPOSE 443

CMD [ "python", "-m", "dinsights" ]

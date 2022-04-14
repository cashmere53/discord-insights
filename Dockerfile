FROM python:slim-bullseye

RUN apt update && \
    apt upgrade -y && \
    mkdir /workdir

COPY ./token.txt /workdir
COPY ./dist/dinsights-0.1.1-py3-none-any.whl /workdir

WORKDIR /workdir
RUN pip install dinsights-0.1.1-py3-none-any.whl

EXPOSE 443

CMD [ "python", "-m", "dinsights" ]

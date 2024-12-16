FROM python:3.10-slim
WORKDIR /work

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y install \
        python3-pip ffmpeg libsm6 libxext6

RUN pip3 install opencv-python flask

COPY main.py /work/

CMD ["python3", "/work/main.py"]
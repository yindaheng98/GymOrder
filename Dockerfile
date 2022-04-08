FROM python:3.9
RUN pip install Pillow==8.2.0 requests==2.25.1 selenium==3.141.0
COPY *.py /
COPY Models /Models
WORKDIR /
RUN mkdir /logs
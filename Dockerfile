FROM python:3

WORKDIR /usr/src/esmanager

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY esmanager.py .

USER nobody:nogroup
ENTRYPOINT ["python3", "esmanager.py"]
CMD ["input.json"]

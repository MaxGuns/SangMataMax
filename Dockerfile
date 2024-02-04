FROM ohshin/ubot:dev

WORKDIR /app

RUN ls -l

COPY requirements.txt .

RUN ls -l

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN ls -l

CMD ["python", "-m", "sangmata.py"]

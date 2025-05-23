FROM python:3.13-slim   

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/manimahesh/streamlit.git .

RUN pip install -r requirements.txt

ENV OPENAI_API_KEY=$OPENAI_API_KEY

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT [ "streamlit", "run", "app/web_app.py", "--server.port=8501", "--server.address=0.0.0.0" ]


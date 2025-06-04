FROM python:3.11@sha256:68a8863d0625f42d47e0684f33ca02f19d6094ef859a8af237aaf645195ed477 AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix="/install" -r requirements.txt

COPY . .


# Stage 2: Runtime
FROM python:3.11@sha256:68a8863d0625f42d47e0684f33ca02f19d6094ef859a8af237aaf645195ed477

RUN useradd --create-home --shell /bin/bash appuser

USER appuser


COPY --from=builder --chown=appuser:appuser /install /usr/local

COPY --from=builder --chown=appuser:appuser /app .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=""

EXPOSE 5000

CMD ["python", "app.py"]
FROM python:3.11@sha256:68a8863d0625f42d47e0684f33ca02f19d6094ef859a8af237aaf645195ed477

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

#RUN python -m compileall -q /app
#ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "-u", "-m", "src.app"]


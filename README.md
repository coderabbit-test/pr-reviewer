# PR Reviewer bot
A bot that helps you to review the PRs in your repository.

## Get started

### Install the dependencies
```bash
pip3 install -r requirements.txt
```

### To run the bot
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Forward the port using ngrok
```bash
ngrok http 8000
```
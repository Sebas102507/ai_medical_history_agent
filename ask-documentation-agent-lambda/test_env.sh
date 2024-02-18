aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 118846062185.dkr.ecr.us-east-1.amazonaws.com
docker build -t ask-documentation-agent-container-test .
docker tag ask-documentation-agent-container-test:latest 118846062185.dkr.ecr.us-east-1.amazonaws.com/ask-documentation-agent-container-test:latest
docker push 118846062185.dkr.ecr.us-east-1.amazonaws.com/ask-documentation-agent-container-test:latest
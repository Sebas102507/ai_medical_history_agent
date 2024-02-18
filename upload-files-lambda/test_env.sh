aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 118846062185.dkr.ecr.us-east-1.amazonaws.com
docker build -t upload-documentation-container-test .
docker tag upload-documentation-container-test:latest 118846062185.dkr.ecr.us-east-1.amazonaws.com/upload-documentation-container-test:latest
docker push 118846062185.dkr.ecr.us-east-1.amazonaws.com/upload-documentation-container-test:latest
#!/bin/sh
tag=latest
image=pipeline-python
region=us-west-1
account=$(aws sts get-caller-identity --query Account --output text)


# Get the account number associated with the current IAM credentials
fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}:${tag}"
docker build -t ${fullname} .


# If the repository doesn't exist in ECR, create it.
aws ecr describe-repositories --region ${region} --repository-names "${image}" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "creating ECR repository : ${fullname} "
    aws ecr create-repository --region ${region} --repository-name "${image}" > /dev/null
fi

# Login to the ECR repogitory
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${account}.dkr.ecr.${region}.amazonaws.com
docker push ${fullname}

if [ $? -eq 0 ]; then
	echo "Amazon ECR URI: ${fullname}"
else
	echo "Error: Image build and push failed"
	exit 1
fi
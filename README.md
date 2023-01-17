# Upload Large Files on AWS

This repository contains  all the files related to data upload of large files in AWS.

Link to the tutorial [video](https://www.youtube.com/watch?v=rCTBXrV3EY8&list=PL4-b39mx2Kpa949b5A_noyozjyuuTzngv&index=9&t=924s)

### Problem statement

The client has to send a large payload from the frontend but:
- API Gateway has a payload limit, it only supports 10MB of payload.
- Lambda invocation maximum payload is 6MB (Synchronous).

### Solution: Upload to S3 using S3 pre-signed URLs.

1. Upload the large payload (synchronously).
2. S3 Bucket will trigger an event when an object is added to the bucket.
3. The event asynchronously invokes a Lambda function. The event will send metadata about the object uploaded, in concrete, the bucket name and the object key.
4. With the given information Lambda can then query the object. The Lambda does not receive the full object but rather the metadata which is only a few kilobytes.
5. SNS is added as a Lambda destination. Why do we need SNS as a Lambda destination? The reason is, as this process is an asynchronous invocation (the Lambda), the request is no longer waiting for a response. The client only receives a response from S3 saying the object was successfully uploaded. The Lambda destination is an AWS feature that allows Lambda functions to invoke other services when its execution is finished. By invoking SNS we can then give the client a response via SNS topics.

### S3 pre-signed URLs.

Why do we need pre-signed URLs?

We could directly upload the payload to S3 if the bucket was configured as public. But that would mean that anyone in the internet could upload data into your bucket and that is a major security issue. We must block this public access and require some permission that must be checked when uploading from the client.

To solve this we will create pre-signed URLs which are created by a Lambda function that is invoked via API Gateway. The pre-signed URL will then allow the client to upload the large object into the S3 bucket. The pre-signed URL consists of temporary credentials which expire after a certain amount of time which we can configure.

### Important notes

**Can we use Cognito instead of pre-signed URLs?**

We can avoid using pre-signed URLs if we have temporary credentials issued by Cognito. In the future this will be the best option since we will be using Cognito and thus pre-signed URLs won't be necessary.

**What is the maximum file size that I can upload using this solution?**

Answer is 5GB. We can see that the author uses a single PUT operation to upload file to S3. According to this [docs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/upload-objects.html):
> Upload an object in a single operation using the AWS SDKs, REST API, or AWS CLI—With a single PUT operation, you can upload a single object up to 5 GB in size.

![](https://i.imgur.com/FEVXi5Q.png)

### Creating the architecture using serverless framework

To get started with serverless you can check this [video](https://www.youtube.com/watch?v=woqLi6NEW58). 

First thing you need to install [serverless](https://www.serverless.com/framework/docs/getting-started). Second, you need to have an AWS account with the necessary permissions and AWS CLI access correctly configured. Once you have all this, to deploy the serverless stack, from a terminal `cd` into the `serverless.yml` file and run: `serverless deploy`.

After deploying the stack you will see some things:
1. A `.serverless` folder is created at the same level as `serverless.yml`. This folder contains:
    - `cloudformation-template-create-stack.json`:
    - `cloudformation-template-update-stack.json`: 
    - `yourServiceName.zip`:
    - `serverless-state.json`:
2. Some stuff was created in our AWS account:
    - A CloudFormation stack.
    - An REST API on API Gateway named `dev-largeFileTutorialApi`.
    - Two Lambda functions named `largeFileTutorialApi-dev-executePayload` and `largeFileTutorialApi-dev-getSignedUrl`.
    - Two S3 buckets named `large-file-upload-tutorial` and `largefiletutorialapi-dev-serverlessdeploymentbuck-bdb7t36cy1vm`

    ### Notes

1. Before running the `serverless deploy` command check you have the latest dependencies versions installed. You can do this by:
```
sudo npm i -g npm-check-updates
ncu -u
npm install
```

2. Update the CORS under the S3 bucket permissions section:
```
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "PUT",
            "POST",
            "DELETE",
            "GET"
        ],
        "AllowedOrigins": [
            "http://127.0.0.1:8080" # "http://www.example1.com" 
        ],
        "ExposeHeaders": []
    }
]
```
3. To run `index.html` from the terminal run `html-server` and a new window on `localhost` will pop up.
4. To get notified on your email for a successfull execution remember to subscribe to the SNS topic.

# Further improvements

- This architecture's SNS topic could send back a notification to the front-end and display it for the user instead of emailing him. 
- Some quality assurance could be made. For example, which files are allowed to be uploaded.
- Better data management. Instead of uploading files to an all-purpose bucket we could upload each user's files to their respective folder. Another solution could be uploading to a generic bucket and then with a data management lambda move the object to their correct location and delete them afterwards.
- We could avoid using pre-signed URLs and use Cognito.

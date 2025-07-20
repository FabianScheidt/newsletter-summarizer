# Newsletter Summarizer

Summarizes the articles from my local newspaper's newsletter.

The script will
- Read incoming emails from AWS SES
- Find referenced articles
- Sign in to the website and extract the article texts
- To be implemented: Summarize the articles with AWS Bedrock
- Update the newsletter with the summaries
- Send the result via email

## Deployment on AWS

All of this should probably be automated, but here's the gist.

Set up an incoming email integration in SES. The integration should be configured to store the email in S3 and then trigger AWS Lambda.

AWS Lambda should be configured to use a Python runtime. The entrypoint should be `newsletter_summarizer.lambda_handler`. It should have an IAM role that grants access to CloudWatch, S3 and SES. Be sure to configure the environment variables.

Package and deploy the code:

```bash
uv sync

./package_lambda.sh

aws lambda update-function-code \                            
  --function-name <put-function-name-here> \
  --zip-file fileb://lambda_package.zip
```

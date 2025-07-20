#!/bin/bash
awslocal s3api create-bucket --bucket "$NEWSLETTER_SUMMARIZER_BUCKET"
awslocal s3 cp --recursive /data/emails "s3://$NEWSLETTER_SUMMARIZER_BUCKET/emails"

#!/bin/bash
awslocal s3api create-bucket --bucket newsletter-summarizer
awslocal s3 cp --recursive /data/emails s3://newsletter-summarizer/emails

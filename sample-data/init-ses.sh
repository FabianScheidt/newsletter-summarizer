#!/bin/bash
awslocal ses verify-email-identity --email "$NEWSLETTER_SUMMARIZER_SENDER"
awslocal ses list-identities

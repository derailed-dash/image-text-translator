#!/bin/bash

### Environment setup to be repeated with each new session ###

export PROJECT_ID=$(gcloud config list --format='value(core.project)')
export REGION=europe-west4
export SVC_ACCOUNT=image-text-translator-sa
export SVC_ACCOUNT_EMAIL=$SVC_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com

# For local development, use Application Default Credentials (ADC):
# gcloud auth application-default login
# (No static service account key file required)

# Functions
export FUNCTIONS_PORT=8081
export BACKEND_GCF=https://$REGION-$PROJECT_ID.cloudfunctions.net/extract-and-translate

# Flask
export FLASK_SECRET_KEY=secret-1234
export FLASK_RUN_PORT=8080

echo "Environment variables configured:"
echo PROJECT_ID="$PROJECT_ID"
echo REGION="$REGION"
echo SVC_ACCOUNT="$SVC_ACCOUNT"
echo SVC_ACCOUNT_EMAIL="$SVC_ACCOUNT_EMAIL"
echo BACKEND_GCF="$BACKEND_GCF"
echo FUNCTIONS_PORT="$FUNCTIONS_PORT"
echo FLASK_RUN_PORT="$FLASK_RUN_PORT"

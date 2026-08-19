##############################################################
# One-time creation of deployment sa account for use with GH #
##############################################################

# First, authenticate as a user who can create service accounts
# gcloud auth login

# Check correct project is selected
# gcloud config list project
# export PROJECT_ID=<enter your project ID>
# gcloud config set project $PROJECT_ID

export PROJECT_ID=$(gcloud config list --format='value(core.project)')

export MY_ORG=<enter your org domain>
export GH_SVC_ACCOUNT=image-text-translator-gh-sa
export GH_SVC_ACCOUNT_EMAIL=$GH_SVC_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com

gcloud iam service-accounts create $GH_SVC_ACCOUNT

######################################
# Grant roles to the service account #
######################################

# Allow service account to access GCS Cloud Build bucket
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$GH_SVC_ACCOUNT_EMAIL" \
  --role="roles/storage.admin"

# Allow service account to run and manage Cloud Build jobs
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$GH_SVC_ACCOUNT_EMAIL" \
  --role="roles/cloudbuild.builds.editor"

# Allow service account access to logs
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$GH_SVC_ACCOUNT_EMAIL" \
  --role="roles/logging.viewer"

# Allow this service account to deploy
gcloud iam service-accounts add-iam-policy-binding $GH_SVC_ACCOUNT_EMAIL \
  --member="serviceAccount:$GH_SVC_ACCOUNT_EMAIL" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$GH_SVC_ACCOUNT_EMAIL" \
  --role=roles/run.admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$GH_SVC_ACCOUNT_EMAIL" \
  --role=roles/cloudfunctions.admin

### Authentication Recommendation: Workload Identity Federation (WIF) ###
# Do NOT create downloadable service account keys.
# Instead, configure Workload Identity Federation for GitHub Actions:
# https://cloud.google.com/iam/docs/workload-identity-federation
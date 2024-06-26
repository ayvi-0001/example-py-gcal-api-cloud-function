gcloud functions deploy \
    example-cf-gcal-api \
    --region=us-west1  \
    --source=. \
    --entry-point=main \
    --runtime=python311 \
    --allow-unauthenticated  \
    --trigger-http  \
    --env-vars-file=./.env.yaml \
    --timeout=540s

# submit-feedback-functions
Cloud Functions for submit feedback to firestore

## Deploy Cloud Functions

set .env file

```bash
# Set the values you want to use
PROJECT_ID="your-actual-project-id"
FIRESTORE_COLLECTION="your-firestore-collection-name"
CF_NAME=submit-feedback
REGION=us-central1

# Copy the file to .env
cp .env.yaml.example .env.yaml

# Use sed to replace the placeholders with actual values
sed -i '' "s/\$PROJECT_ID/$PROJECT_ID/g" .env.yaml
sed -i '' "s/\$FIRESTORE_COLLECTION/$FIRESTORE_COLLECTION/g" .env.yaml
```

Deploy Cloud Functions

```bash
gcloud functions deploy $CF_NAME \
--gen2 \
--runtime=python311 \
--region=$REGION \
--source=. \
--entry-point=main \
--env-vars-file=.env.yaml \
--trigger-http
```

## OpenAPI Spec

```
openapi: "3.0.0"
info:
  version: 1.0.0
  title: Feedback Agent Tool API
  description: Manage feedback from users interaction with AI Agents
servers:
- url: https://us-central1-nuttee-lab-00.cloudfunctions.net/submit-feedback
paths:
  /submit_feedback:
    post:
      operationId: submitFeedback
      summary: Submit a user feedback
      parameters:
      - name: session_id
        in: query
        description: ID of session to return
        required: true
        schema:
          $ref: '@dialogflow/sessionId'
      requestBody:
        content:
          application/json:
            schema:
              required:
              - topic
              - sentiment
              - details
              type: object
              properties:
                topic:
                  type: string
                  description: Topic name of the reporting feedback from user. Example format [System Name] - [Issue Type]
                details:
                  type: string
                  description: String containing the issue details and example of question and answer that user reported. Must use \ to escape double quote string.
                  example: "The answer was incorrect and irrelevant to the question. For example, when asked 'What is the capital of France?', the model responded with 'The capital of France is Berlin.'"
                sentiment:
                  type: string
                  description: Feedback sentiment
                  enum: [positive, neutral, negative]
                  example: negative
      responses:
        '200':
          description: Successfully submit feedback
        '400':
          description: Invalid request body
        '401':
          description: Unauthorized
        '500':
          description: Internal server error
```
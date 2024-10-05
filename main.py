"""Retail recommendations and search"""

import json
import os
import random
import string

import firebase_admin
from firebase_functions import https_fn
import flask
import google.auth
import google.auth.transport.requests
from google.cloud import firestore

app = flask.Flask(__name__)

creds, project = google.auth.default()
PROJECT_ID = os.environ.get("PROJECT_ID", "nuttee-lab-00")
FIRESTORE_COLLECTION = os.environ.get("FIRESTORE_COLLECTION", "feedback")

firebase_admin.initialize_app()
db = firestore.Client(project=PROJECT_ID)


@app.post("/submit_feedback")
def submit_feedback():
    """Add feedback to firestore.

    Returns:
        status.
    """
    if not (flask.request.args and "session_id" in flask.request.args):
        return flask.jsonify({"status": "error: session_id not found"})
    session_id = flask.request.args["session_id"]
    session_doc_ref = db.collection("feedback").document(session_id)
    # Get the document. Create it if it doesn't exist.
    session_doc = session_doc_ref.get()
    if not session_doc.exists:
        session_doc_ref.set({"feedback": []})  # Create the document with an empty feedback list
        session_doc = session_doc_ref.get()  # Get the newly created document

    session_doc = session_doc.to_dict()  # Now convert to dictionary

    if "topic" not in flask.request.get_json():
        return {"status": "error: Missing topic"}
    topic = flask.request.get_json()["topic"]
    if "sentiment" not in flask.request.get_json():
        return {"status": "error: Missing sentiment"}
    sentiment = flask.request.get_json()["sentiment"]
    if "details" not in flask.request.get_json():
        return {"status": "error: Missing details"}
    details = flask.request.get_json()["details"]

    feedback = session_doc.get("feedback", [])  # Get existing feedback or initialize as empty list

    # Append new feedback as a dictionary
    feedback.append({
        "topic": topic,
        "sentiment": sentiment,
        "details": details
    })
    
    session_doc_ref.set({"feedback": feedback}, merge=True)
    return {
            "status": "successfully submit feedback",
            "referenceId": session_id
        }

@https_fn.on_request()
def main(req: https_fn.Request) -> https_fn.Response:
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    print("Creds", creds)
    with app.request_context(req.environ):
        return app.full_dispatch_request()

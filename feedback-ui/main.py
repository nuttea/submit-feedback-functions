import os
import time
import google.auth
import google.auth.transport.requests
import mesop as me
import mesop.labs as mel
from google.cloud import firestore
import firebase_admin
import pandas as pd

# Initialize Firebase
creds, project = google.auth.default()
try:
    firebase_admin.initialize_app()
except Exception as e:
    pass
db = firestore.Client()
feedback_data = []

# ===== Styles (inspired by mesop_examples) =====
BACKGROUND_COLOUR = "#f0f4f8"

STYLE_BACK = me.Style(
    background=BACKGROUND_COLOUR,
    height="100%",
    overflow_y="scroll",
)

STYLE_BOX_HOLDING = me.Style(
    background="#f0f4f8",
    margin=me.Margin(left="auto", right="auto"),
    padding=me.Padding(top=24, left=24, right=24, bottom=0),
    width="min(1024px, 100%)",
    display="flex",
    flex_direction="column",
)

STYLE_BOX_WHITE = me.Style(
    flex_basis="max(480px, calc(50% - 48px))",
    background="#fff",
    border_radius=10,
    box_shadow=(
        "0 3px 1px -2px #0003, 0 2px 2px #00000024, 0 1px 5px #0000001f"
    ),
    padding=me.Padding(top=16, left=16, right=16, bottom=16),
    display="flex",
    flex_direction="column",
)

# ===== State class =====

@me.stateclass
class State:
    project_id: str = "nuttee-lab-00"
    collection_name: str = "feedback"

# ===== Event handlers =====
def on_project_id_change(e: me.InputEvent):
    state = me.state(State)
    state.project_id = e.value

def on_collection_name_change(e: me.InputEvent):
    state = me.state(State)
    state.collection_name = e.value

def on_submit_click(e: me.ClickEvent):
    state = me.state(State)
    print(f"Project ID: {state.project_id}")
    print(f"Collection Name: {state.collection_name}")
    if state.project_id and state.collection_name:
        feedback_data = get_feedback_data(state.project_id, state.collection_name) 

# ===== Data fetching and display =====

def get_feedback_data(project_id: str, collection_name: str):
    """Fetches the last 20 feedback documents from Firestore."""

    try:
        global db
        db = firestore.Client(project=project_id)
        feedback_ref = db.collection(collection_name)
        feedback_query = feedback_ref.limit(20)

        feedback_docs = feedback_query.stream()
        global feedback_data
        for doc in feedback_docs:
            feedback = doc.to_dict()
            feedback["session-id"] = doc.id
            for item in feedback["feedback"]:
                item["session-id"] = doc.id
                feedback_data.append(item)

        return feedback_data

    except Exception as e:
        return [{"error": f"Error fetching data: {str(e)}"}]

def display_feedback():
    """Displays the feedback data in a user-friendly format."""

    if "error" in feedback_data[0]:
        me.text(feedback_data[0]["error"])
        return

    # Convert feedback_data to a Pandas DataFrame
    df = pd.DataFrame(feedback_data)

    # Display the DataFrame as a table
    with me.box(style=STYLE_BOX_WHITE):
        me.table(df, header=me.TableHeader(sticky=True))
    me.text(text="", type="body-1")

# ===== Page setup =====

@me.page(path="/", title="Feedback Viewer")
def app():
    state = me.state(State)

    with me.box(style=STYLE_BACK):
        with me.box(style=STYLE_BOX_HOLDING):
            me.text("Feedback Viewer", type="headline-4")

            with me.box(style=STYLE_BOX_WHITE):
                me.input(label="Project ID", 
                        value=state.project_id, 
                        on_input=on_project_id_change)

                me.input(label="Firestore Collection", 
                        value=state.collection_name, 
                        on_input=on_collection_name_change)

                me.button(label="Submit", 
                          type="raised", 
                          on_click=on_submit_click)

            me.text(text="", type="body-1")
            me.divider()
            me.text(text="", type="body-1")

            if feedback_data:
                display_feedback()


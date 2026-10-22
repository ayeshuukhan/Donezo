# Donezo

A web service for keeping track of tasks. You can add a task, look at your tasks, change one, or delete one. It's built with FastAPI, checked with pytest, and can run inside Docker.

Tasks are stored in memory, so they disappear when you stop the server. That's fine for learning and testing.

## What you need

- Python 3.10 or newer
- Docker (only if you want to run on container)

## Run it on your computer

Open a terminal in the project folder and run these one by one:

    python -m venv .venv
    pip install -r requirements-dev.txt
    uvicorn app.main:app --reload

Before the second command, activate the virtual environment:

- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

Now open http://localhost:8000/docs in your browser. You'll see a page where you can try every endpoint by clicking "Try it out".

## Run the tests

    pytest -v

If everything is fine you'll see all tests marked as passed.

## Run it with Docker

    docker build -t task-manager-api .
    docker run --rm -p 8000:8000 task-manager-api

Then open http://localhost:8000/docs again.

If Docker says the port is already in use, something else is using 8000 (maybe the local server from above). Stop it, or run Docker on another port:

    docker run --rm -p 8080:8000 task-manager-api

and open http://localhost:8080/docs.

## What you can do

| What you want        | Request            | You get back | If something's wrong                          |
|----------------------|--------------------|--------------|-----------------------------------------------|
| Add a task           | POST /tasks        | 201          | 422 if the data is invalid                    |
| See all tasks        | GET /tasks         | 200          | 422 if the filter or page values are invalid  |
| See one task         | GET /tasks/{id}    | 200          | 404 if it doesn't exist                       |
| Change a task        | PATCH /tasks/{id}  | 200          | 400 if you send nothing, 404 if not found     |
| Delete a task        | DELETE /tasks/{id} | 204          | 404 if it doesn't exist                       |
| Check the app is up  | GET /health        | 200          |                                               |

A task has a title (required), an optional description, a status (`todo`, `in_progress` or `done`), and a priority from 1 to 5.

## Try it with curl

Add a task:

    curl -X POST localhost:8000/tasks -H "Content-Type: application/json" \
         -d '{"title":"Learn FastAPI","priority":4}'

Mark it as done:

    curl -X PATCH localhost:8000/tasks/1 -H "Content-Type: application/json" \
         -d '{"status":"done"}'

On Windows PowerShell, the quotes work differently, so using the /docs page is easier.

## Project layout

    app/
      main.py           starts the app
      routes.py         the endpoints
      models.py         rules for what a valid task looks like
      repository.py     where tasks are stored
      dependencies.py   hands the storage to the endpoints
    tests/
      test_tasks.py     automatic checks for every endpoint
    Dockerfile          recipe for the container
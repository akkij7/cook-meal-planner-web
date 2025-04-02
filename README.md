# Cook Bhaiyya Meal Planner - Web Version

This is a web application version of the Cook Bhaiyya Meal Planner, built using Python and Flask.

It allows users to choose between planning Lunch or Dinner, select main dishes and staples from provided lists (including historical and suggested Rajasthani vegetarian options), add custom requests, and generate a formatted message for the cook.

## Features

*   Web interface accessible from a browser.
*   Initial choice between planning Lunch or Dinner.
*   Checkbox selection for multiple main dishes and staples (Roti, Chawal, Salad).
*   Includes mandatory lunch items ("Protein Shake", "Chach").
*   Parses historical meal data to include past dishes in options.
*   Includes additional suggested dishes.
*   Allows adding optional custom text requests.
*   Generates a conversational, formatted message in Hindi/English.
*   Provides a button to easily copy the generated message.

## Project Structure

```
/
|-- app.py              # Main Flask application file
|-- requirements.txt    # Python dependencies
|-- README.md           # This file
|-- cook_meal_planner.py # Original Tkinter script (kept for reference)
|-- .env                # Old file for Tkinter version (not used by web app)
|-- templates/
|   |-- index.html      # Initial choice page
|   |-- plan.html       # Meal planning form
|   |-- result.html     # Result display page
```

## Setup and Running Locally

1.  **Prerequisites:**
    *   Python 3.6+
    *   `pip` (Python package installer)

2.  **Clone or Download:** Get the project files.

3.  **Create Virtual Environment (Recommended):**
    Open your terminal or command prompt in the project directory and run:
    ```bash
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Install Dependencies:**
    While the virtual environment is active, run:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the Flask App:**
    ```bash
    python app.py
    ```
    The application will start, usually on `http://127.0.0.1:5000/`. Open this URL in your web browser.

## How to Use

1.  Open the application URL in your browser.
2.  Click either "Lunch (Subah)" or "Dinner (Shaam)".
3.  On the planning page, check the boxes for the desired main dishes and staples.
4.  Optionally, type any additional instructions in the "Kuch Aur Kehna Hai?" box.
5.  Click "Generate Meal Plan Message".
6.  The next page will display the formatted message.
7.  Click "Copy Message" to copy it to your clipboard.
8.  Click "Plan Another Meal" to return to the start page.

## Deployment to a Free Server (General Steps)

Deploying Flask apps involves specific steps depending on the hosting provider (e.g., PythonAnywhere, Heroku, Render). Here's a general outline:

1.  **Choose a Provider:** Select a platform that offers a free tier suitable for Python/Flask apps.
2.  **Prepare for Production:**
    *   **WSGI Server:** You'll need a production-ready WSGI server like `gunicorn` (Linux/macOS) or `waitress` (Windows/Linux/macOS). Add it to `requirements.txt` (e.g., `gunicorn` or `waitress`).
    *   **Procfile (Heroku/some others):** Create a `Procfile` (no extension) telling the host how to run your app. Example using `gunicorn`:
        ```
        web: gunicorn app:app
        ```
        Example using `waitress`:
        ```
        web: waitress-serve --host=0.0.0.0 --port=$PORT app:app 
        ```
    *   **Runtime File (Optional):** Some hosts might need a `runtime.txt` file specifying the Python version (e.g., `python-3.10.4`).
    *   **Secret Key:** Set the `app.secret_key` using an environment variable provided by the host for better security, instead of hardcoding it or using `os.urandom()` directly on startup.
    *   **Debug Mode:** Ensure `app.run(debug=True)` is **OFF** in production. The WSGI server handles running the app.
3.  **Sign Up & Create App:** Follow the provider's instructions to sign up and create a new application instance.
4.  **Deployment Method:**
    *   **Git:** Most common method. Initialize a git repository, commit your files (`app.py`, `requirements.txt`, `templates/`, `Procfile`, etc. - **DO NOT commit `venv`**), and push to the remote repository provided by the host (e.g., Heroku remote, GitHub connected to Render).
    *   **CLI Tools:** Some providers have command-line tools for deployment.
    *   **Web UI Upload:** Some might allow uploading a zip file.
5.  **Configuration:** Configure environment variables (like `SECRET_KEY`) on the host platform if needed.
6.  **Launch:** The host will typically build the environment from `requirements.txt` and launch your app using the `Procfile` or other configuration.

Refer to the specific documentation of your chosen hosting provider for detailed instructions. 
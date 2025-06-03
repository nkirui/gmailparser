# Gmail API Interaction Project

This project demonstrates how to interact with the Google Gmail API to fetch user profile information, email labels, and recent email messages. It's built with Python, leveraging asynchronous operations for efficient API communication and includes a robust data transformation layer.

## ✨ Features

* **Google OAuth 2.0 Integration:** Securely authenticates with Google services.
* **Asynchronous API Calls:** Utilizes `asyncio` for non-blocking network requests, enhancing performance.
* **Concurrent Message Fetching:** Fetches detailed email messages concurrently within a rate limit.
* **Standardized Data Output:** Transforms raw Gmail API payloads into a clean, consistent Python dictionary format.
* **Modular Design:** Separates API interaction logic, data transformation, and main application flow for maintainability.

---

## 🚀 Getting Started

To run this project, you'll need to set up Google API credentials and install the necessary Python dependencies using `pipenv`.

### Prerequisites

* **Python 3.9+** (Python 10+ recommended for best compatibility and features)
* `pipenv` (Refer to the [official Pipenv installation guide](https://pipenv.pypa.io/en/latest/) for detailed installation instructions.)

### 1. Google API Credentials Setup

This project uses Google's OAuth 2.0 for authentication. Follow these steps to obtain your `credentials.json` file. **Note: This setup is suitable for development and testing. For production environments, consult Google's official documentation for secure credential management.**

1. **Go to Google Cloud Console:**
   * Open your web browser and navigate to [https://console.cloud.google.com/](https://console.cloud.google.com/).
2. **Create a New Project:**
   * In the Google Cloud Console, select an existing project or click "Create Project" to start a new one. Give it a meaningful name (e.g., "Gmail API Demo").
3. **Enable Gmail API:**
   * Once your project is selected, go to "APIs & Services" > "Enabled APIs & Services".
   * Click "+ Enable APIs and Services".
   * Search for "Gmail API" and enable it.
4. **Create OAuth Consent Screen:**
   * Navigate to "APIs & Services" > "OAuth consent screen".
   * Choose "External" as the User Type (unless you are part of a Google Workspace organization and want to restrict access to your organization's users).
   * Fill in the required information (App name, User support email, Developer contact information).
   * **Add Scopes:** On the "Scopes" page, click "Add or Remove Scopes" and search for `.../auth/gmail.readonly` (or "Gmail API read-only access"). Select it and add it to your scopes.
   * **Add Test Users:** If your publishing status is "Testing", you *must* add the Google accounts you'll use for testing under "Test users".
   * Save and continue through all steps until your OAuth consent screen is configured.
5. **Create OAuth Client ID:**
   * Go to "APIs & Services" > "Credentials".
   * Click "+ Create Credentials" and choose "OAuth client ID".
   * For "Application type", select **"Desktop app"**.
   * Give your client a descriptive name (e.g., "GmailReaderDesktop").
   * Click "Create".
6. **Download `credentials.json`:**
   * After creation, a dialog will appear showing your client ID and client secret.
   * Click the "Download JSON" button.
   * **Save this downloaded file as `credentials.json`** in the root directory of your project (the same directory as `main.py`).
   * **Security Note:** The `credentials.json` file contains sensitive information. Keep it confidential and never commit it to public version control repositories. For production applications, more secure methods of handling credentials (e.g., environment variables, Google Secret Manager) should be used.

### 2. Installation

Clone the repository and install the required Python packages using `pipenv`:

```bash
git clone https://github.com/nkirui/gmailparser.git
cd gmailparser
pipenv install
```


This command will:

* Create a virtual environment for your project if one doesn't exist.
* Install all dependencies specified in the `Pipfile` (or create one if it doesn't exist by inspecting your imports).
* Generate a `Pipfile.lock` for deterministic builds.

### 3. Usage

After installation, activate your virtual environment and run the main script:

**Bash**

```
pipenv shell # Activates the virtual environment
python main.py
```

Alternatively, you can run the script directly without explicitly entering the shell:

**Bash**

```
pipenv run python main.py
```

The first time you run it, a browser window will open, prompting you to log in with your Google account and grant the requested permissions. After successful authentication, a `token.json` file will be created to store your credentials for future runs, preventing repeated browser prompts.

The script will then fetch and display:

* Your Gmail user profile.
* A list of your Gmail labels.
* Details of the 10 most recent emails in your inbox.


### Running Tests

To ensure the integrity and correctness of the data transformation logic, you can run the unit tests using `pytest`.

First, make sure your `pipenv` environment is activated:

**Bash**

```
pipenv shell
```

Then, run the tests:

**Bash**

```
pytest
```

You should see output similar to this, indicating that all tests have passed:

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.4.0, pluggy-1.6.0
rootdir: /home/your_user/your_project_folder
collected 7 items

test_gmail_api_handler.py .......                                        [100%]

============================== 7 passed in 0.07s ===============================
```

This output confirms that `pytest` discovered and successfully ran 7 test cases defined in `test_gmail_api_handler.py`.

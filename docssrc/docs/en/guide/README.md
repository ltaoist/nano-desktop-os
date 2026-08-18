# Usage Guide

## Startup and Login

Run the following command in the project root to start the service:

```bash
python src/backend/launch.py
```

The terminal prints the frontend URL (default `http://localhost:5173`) and the default account (`admin` / `admin`). Open that URL in a browser.

![System startup](/assets/system_launch.png)

You will see the login screen:

![Login screen](/assets/login.png)

Enter the username and password. After authentication passes, you enter the main interface.

## Main Interface and App Management

After login, the left side of the main interface is the function panel and the right side is the content window area. The three entries at the top of the left panel can be switched at any time:

- **Launcher** (+): shows the list of installed apps. Clicking an app icon creates a thread and starts working. The system preinstalls two apps: calc.App (calculator) and snake.App (Snake).
- **Installer** (📦): install new apps (folder or ZIP), uninstall apps, or clear an app's persistent data.
- **Notification Center** (🔔): view system notifications, delete a single one, or clear all.

Below the function buttons is the **thread list**, showing all running threads. Click a list item to switch between windows; switching does not interrupt background work. The bottom button collapses the panel for a larger workspace.

![Main interface](/assets/browse_apps.png)

![Create a thread](/assets/start_thread.png)

## Threads and Windows

When you click an app in the launcher, the system creates a logical thread for that app: it starts the app's backend process, opens a content window to load the frontend page, and the thread appears in the left list. You can create multiple threads for the same app, each running independently.

Each thread window has a title bar at the top showing the thread name and a close button (×). Double-click the title bar to rename the thread. Clicking × closes the thread; the system terminates that thread's backend process, and temporary in-memory state is lost. Data already persisted to disk (such as the Snake leaderboard) is not affected by closing.

## Built-in Examples

The system preinstalls two example apps. You can open them directly, and they also demonstrate two typical frontend-backend interaction patterns:

- **calc.App (calculator)**: request-response pattern. The frontend sends an expression and the backend evaluates it and returns the result. Calculation history is kept in memory and is not retained after the thread closes.

![Calculator](/assets/calc.png)

- **snake.App (Snake)**: data persistence pattern. The game logic runs in the browser; after the game ends the user can submit a score to the backend leaderboard. The leaderboard uses a file lock to make concurrent writes from multiple threads safe, and data is persisted.

![Snake](/assets/snake.png)

## Stopping the Service

The server can keep running, and you can close the browser window at any time without affecting background work. To fully stop the service, press **Ctrl+C** in the terminal running launch.py. The system shuts down (terminates thread processes and releases the port). Do not stop the service while data is still being written to disk or before the port is released, or data loss may occur.

After stopping, persistent data (leaderboard, app installation state) is fully retained; in-memory state (calculation history, unsubmitted scores) is lost; all threads are destroyed and must be recreated on the next startup.

---

- Next: [App Development](../dev/) — learn to write Nano Desktop OS applications

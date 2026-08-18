# Writing an App

An application must import the SDK correctly and write an entry function.

## Importing the SDK

The backend adds `src/backend/` to `sys.path` and then imports the needed SDK modules:

```python
# Import path handling and system modules
import os, sys

# Go up four levels from this file to find the project root, then append src/backend/
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "src", "backend")

# Put the SDK directory at the front of the module search path so nano_tob etc. can be found
sys.path.insert(0, backend_dir)

# Import the TOB client, used for frontend-backend communication
import nano_tob

# Import other SDK modules as needed, for example:
# from data_storage import getAppPathData, setAppPathData
```

The frontend includes `nano_tob.js` via a `<script>` tag, after which the TOB functions are available as global variables:

```html
<script src="/nano_tob.js"></script>
```

See the [TOB Programming](../tob/) chapter for details on using TOB.

## App mode

App mode is for applications with complex logic and UI. An application should provide a backend Python file and a frontend HTML file; the frontend may use any tech stack. The preinstalled calc.App and snake.App both use App mode.

App-mode applications are placed in a directory with the same name plus the `.App` suffix:

```
myapp.App/
├── main.py         # backend
├── index.html      # frontend
└── static/         # static resources (JS, CSS, images, etc.; optional)
```

The backend must implement the `__nanoAppMain` function.

```python
# Import the async event loop, path handling, and system modules
import asyncio, os, sys

# Go up four levels from this file to find the project root, then append src/backend/
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "src", "backend")

# Put the SDK directory at the front of the module search path
sys.path.insert(0, backend_dir)

# Import the SDK modules you need
# import nano_tob
# from data_storage import ...

async def __nanoAppMain():
    #
    # Application backend entry.
    # The system calls this function in a separate Python process when the thread starts.
    #

    # Keep the event loop running
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        pass
```

The frontend must provide an `index.html`.

```html
<!DOCTYPE html>
<html><body>
<div id="app"></div>
<script src="/nano_tob.js"></script>
<script>
//
// Application frontend entry.
//
//
//
</script>
</body></html>
```

The frontend accesses application resources via URLs under `/app-content/{app_name}/`. Requests under that path are returned by the backend from the `static/` directory. For example, `<script src="/app-content/myapp.App/game.js"></script>` returns `myapp.App/static/game.js`. SDK paths that start with `/`, such as `/nano_tob.js`, are served directly by the frontend service.

Typically the backend can initialize TOB in the entry function, create a TOB object and name it (for example `"app"`), and mount business logic onto it as methods; the frontend can then call those methods remotely. The frontend can initialize TOB in the page, wait for that named TOB to become ready, call its methods, render the UI, and handle interaction. The frontend can also create its own TOB and mount methods on it for the backend to call in reverse — for example to push progress updates or notifications.

## Single-script mode

Single-script mode is for simple, logic-oriented utility applications. The application only needs a Python file, with no separate frontend HTML file.

Single-script applications are placed in a directory with the same name plus the `.py` suffix, containing a `.py` file with the same name:

```
myscript.py/
└── myscript.py
```

When a single-script application opens its content window, Nano Desktop OS automatically loads a default HTML page (`/html/scriptContentWindow.html`). That page automatically includes `nano_tob.js` and `nano_script_app.js`, connects to TOB, waits for a TOB named `"scriptAppBackendPublic"` to become ready, calls its `get_html()` method to get an HTML string, and renders it.

For this, the backend should initialize TOB in `__nanoAppMain`, create a TOB named `"scriptAppBackendPublic"`, and mount a `get_html` method:

```python
# Import the async event loop, path handling, and system modules
import asyncio, os, sys

# Go up four levels from this file to find the project root, then append src/backend/
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "src", "backend")

# Put the SDK directory at the front of the module search path
sys.path.insert(0, backend_dir)

# Import the TOB client
import nano_tob

# Define the function that returns the frontend HTML content
def get_html():
    return """<!DOCTYPE html>
<html><body>
<h1>Hello</h1>
<script src="/nano_tob.js"></script>
<script>
//
// After the HTML returned by get_html is rendered, nano_tob.js has loaded.
// You can initialize TOB here, call backend methods, and handle interaction.
//
</script>
</body></html>"""

async def __nanoAppMain():
    #
    # Application backend entry.
    # The system calls this function in a separate Python process when the thread starts.
    #

    # Establish the connection to the TOB message bus
    await nano_tob.initializeTOBM()

    # Create a TOB object for communication and method mounting
    tob = await nano_tob.createTOB()

    # Mount the get_html function on the TOB so the frontend can call it
    nano_tob.mountTOBMethod(tob, "get_html", get_html)

    # Name the TOB using the system-agreed name the default page looks for
    await nano_tob.nameTOB(tob, "scriptAppBackendPublic")

    #
    # Initialization is now complete. The system default page automatically connects
    # to scriptAppBackendPublic, calls get_html to obtain and render the page content,
    # and the rendered page can then call backend methods through TOB.
    #

    # Keep the event loop running while waiting for frontend calls
    try:
        # Wait forever until the coroutine is cancelled
        await asyncio.Future()

    # When the thread closes, the event loop raises CancelledError
    except asyncio.CancelledError:
        # Exit normally, no extra handling needed
        pass

    # Clean up the connection whether exiting normally or due to an error
    finally:
        # Close the TOB connection and release resources
        await nano_tob.closeTOBM()
```

---

- [Install & Distribute](./debug-install)

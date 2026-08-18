# Install & Distribute

Copy an application directory (`.App` or `.py`) into `Data/AppData/` to install it. After restarting the service or refreshing the page, the app appears in the launcher. Multiple applications can be placed under `Data/AppData/`:

```
Data/
└── AppData/
    ├── calc.App/
    │   ├── main.py
    │   ├── index.html
    │   └── static/
    ├── snake.App/
    │   ├── main.py
    │   ├── index.html
    │   └── static/
    ├── myscript.py/
    │   └── myscript.py
    └── ...
```

You can also upload a ZIP package through the installer (📦) in the UI; the installer extracts it into `Data/AppData/`. Uninstalling deletes the corresponding directory, and clearing app data deletes the corresponding directory under `Data/AppDataStore/`.

To distribute an app, package the app directory as a ZIP file. The ZIP's root must be the app directory name (`.App` or `.py` directory):

```
myapp.App.zip
└── myapp.App/
    ├── main.py
    ├── index.html
    └── static/
        └── ...
```

```
myscript.py.zip
└── myscript.py/
    └── myscript.py
```

---

- [TOB Programming](../tob/) — complete API reference for frontend-backend interop
- [calc.App Example](../calc/) · [snake.App Example](../snake/) — learn through code

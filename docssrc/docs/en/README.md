# About Nano Desktop OS

Nano Desktop OS is a general-purpose platform built around the **Logical Thread Programming** paradigm, unifying the backend and frontend into a single whole for organizing how applications run. The system arranges work into multiple parallel logical threads; each thread carries one ongoing working session with its own state, logic, and UI. Users enter a thread's content window through the browser to interact with the application, and can switch freely between windows without interrupting background work.

In Nano Desktop OS, an application consists of two parts: the **Backend** and the **Frontend**. The backend is a program running in the Python interpreter, executed in a separate background process, and is responsible for business logic, computation, and persistence. The frontend is an HTML/JavaScript program loaded and run in the browser, and is responsible for presentation and interaction. Between the two, the built-in **[Thread Objects Broker (TOB)](./tob/)** provides a structured interop channel so programs in different environments can call each other's methods as if they were local objects. It also provides per-application private data storage keyed by application name, binding each application's data to the application itself. Applications follow a minimal contract: place them in the designated directory and they run.

This documentation was prepared with the assistance of generative AI. If you find errors, unclear wording, or missing content, feedback is welcome.

---

- [Usage Guide](./guide/) — the full flow from startup to use
- [App Development](./dev/) — writing Nano Desktop OS applications
- [TOB Programming](./tob/) — the core mechanism for frontend-backend interop
- [calc.App Example](./calc/) — learn TOB programming through a calculator
- [snake.App Example](./snake/) — learn TOB programming further through a Snake game
- [Branch Development](./branch/) — getting the source code and setting up a dev environment
- [Minimal System](./minimal/) — implementation principles of the core components

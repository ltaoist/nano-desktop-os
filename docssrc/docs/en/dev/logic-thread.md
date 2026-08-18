# Logical Thread Programming

Logical Thread Programming is the programming paradigm Nano Desktop OS uses to organize how applications run. To understand it, it helps to look at the historical thread of distributed computing.

CORBA (Common Object Request Broker Architecture) in the 1990s introduced the Object Request Broker (ORB) concept: objects in different processes and different languages call each other's methods through an ORB. The caller holds a proxy object, and calling a method feels like a local method call. CORBA's ideal was to make distributed programming as transparent as local programming, but its specification was enormously complex — IDL definitions, object lifecycle, naming services, transactions, and more kept piling up, making it hard to adopt in practice. Later RPC (Remote Procedure Call) frameworks — from early ONC RPC to modern gRPC and Thrift — simplified the problem to remote procedure calls, dropping the weight of "distributed objects" and focusing on function-level request-response, which became widely used in server development.

Logical Thread Programming is an adjustment of the programming perspective built on these foundations. Its focus is not "how to call a remote object's method" nor "how to call a remote function," but rather **treating an ongoing working session itself as the basic unit of programming**. Each logical thread is an independent working session with its own state, logic, and UI. Users interact with threads, and threads interoperate with each other through a proxy mechanism, but a thread is not a "service" or an "object" — it is an ongoing process with a beginning, interaction, and an end. The backend process carries the thread's computation and state, while the frontend page carries the thread's presentation and interaction; the two are two faces of the same thread in different environments.

This idea is not entirely new. Many large multi-process, multi-threaded applications — each open project in an IDE is a working session, each tab in a browser is an independent process, each window in a desktop environment corresponds to a running program — embody the idea of logical threads at the system level. But in those systems, logical threads are usually an internal implementation mechanism, not exposed to application developers as a programming paradigm. Nano Desktop OS makes the logical thread the core abstraction of the platform: developers do not write a "service" or a "page," but the backend and frontend of a logical thread. The system is responsible for thread creation, process management, window management, and frontend-backend interop.

The name TOB (Thread Objects Broker) comes from exactly this — it is a broker between thread objects, with an intellectual lineage back to CORBA's ORB.

---

- [Writing an App](./app-basics) — SDK imports, two application forms, and the entry function

**Local Python Server for NetLogo Interaction**

This solution provides a robust framework for high-performance integration between NetLogo and Python. By establishing a dedicated local server, it mitigates the significant overhead typically associated with initializing large or complex Python processes for each call. This architecture ensures a more efficient and responsive user experience.



**When to Use This Feature**

Please use this local server feature in the following situations:

* When using the **Complex** accessibility model.
* When your daily plan version is set to **Typical** or **Full** and you need to generate routes.



**How to Use**

**Step 1: Install Dependencies (One-Time Only)**

This step prepares the necessary environment and only needs to be performed once.

* **On Windows:** Double-click the (for Win) Install\_Dependencies.bat file. This will check for a Python installation and install the necessary libraries from requirements.txt.
* **On macOS:** Open your Terminal, navigate to the Python\_Server directory, and run the following command:

*pip3 install -r requirements.txt*



**Step 2: Start the Server**

Before you run your NetLogo model, you must start the server.

* **On Windows:** Double-click the (for Win) Start\_Server.bat file.
* **On macOS:** Double-click the (for Mac) Start\_Server.sh file.

A terminal or command prompt window will appear, indicating that the server is running.



**Step 3: Keep the Server Running**

Important: Do not close the server window while you are using the NetLogo model. The server must remain active for NetLogo to communicate with Python. You can close the server window after you have finished your work in NetLogo.




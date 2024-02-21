# Fun-Chat App ReadMe
## Overview
Fun-Chat App is a chat software designed for seamless communication. It is implemented with a focus on simplicity and efficiency, providing a platform for individual and group chats. The project utilizes backend and frontend technologies to deliver a robust chatting experience.


## Technologies Used
  ### Backend:
  - Python Websockets
  * MySQL Database
  + SQLAlchemy ORM

  ### Frontend:
  - HTML
  * CSS
  + JavaScript

## Supported Features
  ### 1. Individual Chats:
  - Engage in private conversations with individual contacts.
  ### 2. Group Chats:
  - Create and participate in group chats for collaborative discussions.
  ### 3. Add Contact:
  - Easily add new contacts to expand your network.
  ### 4. Block Contact:
  - Manage your contacts by blocking unwanted communication.
  ### 5. Get Chat Messages:
  - Retrieve chat messages for a comprehensive view of your conversations.
  ### 6. Send Messages:
  - Send messages in real-time to stay connected with your contacts.

## How to use
  ### Installation:
  - Clone the repository to your local machine.
    `git clone https://github.com/SravanJangamDev/Fun-Chat.git`

  ### Backend Setup:
  - Navigate to the backend directory.
    `cd Fun-Chat/backend`

  - Install dependencies.
    pip install -r requirements.txt
  
  - Install MySql
    - [Reference Doc](https://ubuntu.com/server/docs/databases-mysql).
  
  - Update config file.
    ```
    Example:
      DEBUG_MODE = True
      ERROR_LOG = ""
      APP_HOST = "127.0.0.1"
      APP_PORT = 8500
      MYSQL_USERNAME = "Your Yysql username"
      MYSQL_PASSWORD = "Your Mysql password"
      MYSQL_HOST = "localhost"
      MYSQL_PORT = 3306
      MYSQL_DBNAME = "Your DB name"
      MYSQL_DEBUG_MODE = False
    ```

  - Run the backend server.
    python app.py

  ### Frontend Setup:
  - Open the frontend directory.
    `cd Fun-Chat/frontend`

  - Open `index.html` in your preferred web browser.

  ### Usage:
  - Create an account and start enjoying the features of the Fun-Chat App.

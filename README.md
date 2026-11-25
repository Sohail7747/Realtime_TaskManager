# Realtime Task Manager

A real-time task management web application built using **Django, Django REST Framework, Django Channels, WebSockets, and PostgreSQL**.

The application allows users to register, log in, create and manage tasks, and track task status changes in real time without refreshing the page.

## 🚀 Features

### 1. User Authentication
- User registration.
- User login and logout.
- Authentication-protected APIs.
- User-specific task management.

### 2. Task Management
- Create new tasks.
- View all tasks.
- Edit existing tasks.
- Delete tasks.
- Set task date and time.
- Start and stop tasks.
- Track task status.

### 3. Real-Time Updates
- Implemented using Django Channels and WebSockets.
- Task status changes are broadcast to connected users.
- Updates appear without refreshing the browser.
- Asynchronous communication between clients and the server.

### 4. Task History
- Maintain a history of task status changes.
- Track which user performed an action.
- Store timestamps for status changes.
- View overall task history.
- View individual task history.

### 5. Admin Management
- Manage users.
- Create, update, and delete tasks.
- Monitor task information.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Backend framework |
| Django REST Framework | REST API development |
| Django Channels | Real-time communication |
| WebSockets | Two-way real-time communication |
| PostgreSQL | Database |
| Redis | Channels message broker |
| HTML5 | Frontend structure |
| CSS3 | Styling |
| JavaScript | Frontend functionality |
| Bootstrap | Responsive UI |
| ASGI | Asynchronous server interface |

## 📁 Project Structure

```text
RealtimeTaskManager/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── ...
│
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── tasks/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── consumers.py
│   ├── routing.py
│   ├── urls.py
│   └── ...
│
├── templates/
├── static/
├── media/
│
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Installation and Setup

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Navigate into the project directory:

```bash
cd RealtimeTaskManager
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory.

Configure your database and other required environment variables according to `.env.example`.

### 5. Configure PostgreSQL

Create a PostgreSQL database named:

```sql
CREATE DATABASE realtime_task_manager;
```

Update your database configuration in `settings.py` or your environment variables.

### 6. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a Superuser

```bash
python manage.py createsuperuser
```

### 8. Start Redis

Make sure Redis is running and configured as the Django Channels channel layer.

### 9. Run the Development Server

```bash
python manage.py runserver
```

Open the application:

```text
http://127.0.0.1:8000/
```

## 🔄 How Real-Time Functionality Works

The application uses Django Channels and WebSockets for real-time communication.

**Communication flow:**

1. A user starts or stops a task.
2. The frontend sends the request to the backend.
3. Django processes the task status update.
4. Django Channels sends a message through the channel layer.
5. Redis helps distribute the message to connected clients.
6. WebSocket consumers receive the broadcast.
7. Connected users receive the updated task information without refreshing the page.

## 🔌 API Development

The backend uses Django REST Framework to provide RESTful APIs.

Main API responsibilities include:

- User registration.
- User authentication.
- Task creation and management.
- Task status updates.
- Task history retrieval.
- User and task administration.

### Example API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks/history/` | Retrieve task history |
| GET | `/api/tasks/7/history/` | Retrieve individual task history |
| DELETE | `/api/tasks/7/` | Delete a task |

*Note: The task ID in these examples is illustrative. Refer to the application's URL configuration for the complete endpoint list.*

## 🎯 Project Objective

The main objective of this project is to develop a task management system that demonstrates practical knowledge of:

- Django backend development.
- REST API architecture.
- Serializers and ORM operations.
- Authentication and authorization.
- Asynchronous programming.
- WebSocket communication.
- Django Channels.
- Redis integration.
- PostgreSQL database management.

## 👨‍💻 Developer

**Sohail Khan**

Backend Developer | Python | Django | REST APIs

---

*Built as a practical backend development project to understand REST APIs, asynchronous communication, and real-time web application development.*

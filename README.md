# Chat Application

A real-time chat application built with FastAPI (backend) and React (frontend), featuring WebSocket support for one-on-one and group chats.

## Features

- **User Authentication**: Register and login functionality
- **One-on-One Chat**: Direct messaging between two users
- **Group Chat**: Conversation with multiple users
- **Real-Time Updates**: WebSocket-based live message exchange
- **Online Status**: See who's currently active in a chat
- **Message History**: View previous messages in a chat

## Project Structure

```
chat/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── models/      # Pydantic data models
│   │   ├── routes/      # API endpoints
│   │   └── services/    # Business logic & WebSocket management
│   ├── main.py          # FastAPI application entry point
│   └── requirements.txt  # Python dependencies
│
└── frontend/            # React frontend
    ├── public/          # Static files
    ├── src/
    │   ├── components/  # React components
    │   ├── App.js       # Main app component
    │   └── index.js     # React entry point
    └── package.json     # Node dependencies
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the server:
```bash
python main.py
```

The backend will start on `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will open at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/users` - Get all users

### Chat Management
- `POST /api/chats/` - Create a new chat
- `GET /api/chats/{chat_id}` - Get chat details
- `GET /api/chats/{chat_id}/messages` - Get chat messages
- `GET /api/chats/{chat_id}/active-users` - Get active users

### WebSocket
- `WS /api/chats/ws/{chat_id}/{user_id}` - WebSocket connection for real-time messaging

## Usage

1. **Register/Login**:
   - Create a new account or login with existing credentials

2. **Create Chat**:
   - Click "+ New Chat" button
   - Select user(s) for one-on-one or group chat
   - Click "Start 1-on-1 Chat" or "Create Group Chat"

3. **Send Messages**:
   - Select a chat from the list
   - Type message in the input field
   - Click "Send" or press Enter

4. **View Online Status**:
   - Active users count shown in the chat header
   - Users appear/disappear as they connect/disconnect

## Technologies Used

### Backend
- **FastAPI**: Modern Python web framework
- **WebSockets**: Real-time bidirectional communication
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Frontend
- **React 18**: UI library
- **React Router**: Navigation
- **Axios**: HTTP client
- **CSS3**: Styling

## Notes for Production

Before deploying to production, consider:

1. **Security**:
   - Implement proper JWT-based authentication
   - Hash passwords using bcrypt or similar
   - Use HTTPS/WSS
   - Implement CORS restrictions
   - Add rate limiting

2. **Database**:
   - Replace in-memory storage with a real database
   - Set up SQLAlchemy ORM
   - Implement database migrations

3. **Deployment**:
   - Use Docker for containerization
   - Set up CI/CD pipeline
   - Use environment variables for configuration
   - Implement proper logging and monitoring

4. **Performance**:
   - Implement message pagination
   - Add caching layer (Redis)
   - Use connection pooling for database

5. **Testing**:
   - Write unit tests
   - Add integration tests
   - Test WebSocket connections

## License

This project is open source and available under the MIT License.

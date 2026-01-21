# Chat API Contract

## Endpoints

### POST /api/chat

Send a message and get an AI response.

**Request:**
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": "optional-uuid"
}
```

**Response:**
```json
{
  "message": "I've added 'buy groceries' to your task list.",
  "conversation_id": "uuid-of-conversation"
}
```

**Headers:**
- `Authorization: Bearer <jwt-token>` (required)
- `Content-Type: application/json`

**Status Codes:**
- 200: Success
- 401: Unauthorized (missing/invalid token)
- 422: Validation error
- 500: Server error

---

### GET /api/chat/conversations

List user's conversations.

**Response:**
```json
{
  "conversations": [
    {
      "id": "uuid",
      "title": "Task management",
      "created_at": "2026-01-15T10:00:00Z",
      "messages": []
    }
  ]
}
```

---

### GET /api/chat/conversations/{id}

Get conversation with messages.

**Response:**
```json
{
  "id": "uuid",
  "title": "Task management",
  "created_at": "2026-01-15T10:00:00Z",
  "messages": [
    {
      "role": "user",
      "content": "Show me all my tasks",
      "created_at": "2026-01-15T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Here are your tasks:\n1. buy groceries (pending)",
      "created_at": "2026-01-15T10:00:01Z"
    }
  ]
}
```

---

### DELETE /api/chat/conversations/{id}

Delete a conversation.

**Response:**
```json
{
  "message": "Conversation deleted"
}
```

## OpenAPI 3.1 Specification

```yaml
openapi: 3.1.0
info:
  title: Todo AI Chatbot API
  version: 1.0.0

paths:
  /api/chat:
    post:
      summary: Send chat message
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChatRequest'
      responses:
        '200':
          description: AI response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChatResponse'

  /api/chat/conversations:
    get:
      summary: List conversations
      security:
        - bearerAuth: []
      responses:
        '200':
          description: List of conversations
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConversationListResponse'

  /api/chat/conversations/{id}:
    get:
      summary: Get conversation
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Conversation with messages
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ConversationResponse'
    delete:
      summary: Delete conversation
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Conversation deleted

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    ChatRequest:
      type: object
      required:
        - message
      properties:
        message:
          type: string
        conversation_id:
          type: string
          format: uuid

    ChatResponse:
      type: object
      required:
        - message
        - conversation_id
      properties:
        message:
          type: string
        conversation_id:
          type: string
          format: uuid

    MessageResponse:
      type: object
      properties:
        role:
          type: string
          enum: [user, assistant, system, tool]
        content:
          type: string
        created_at:
          type: string
          format: date-time

    ConversationResponse:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
        created_at:
          type: string
          format: date-time
        messages:
          type: array
          items:
            $ref: '#/components/schemas/MessageResponse'

    ConversationListResponse:
      type: object
      properties:
        conversations:
          type: array
          items:
            $ref: '#/components/schemas/ConversationResponse'
```

# System Architecture Overview

This document provides a high-level overview of the application's architecture, based on the implementation plan. It covers the database design, API structure and routing, and the core application workflow.

## 1. General Application Workflow

The application is a backend API designed to support a collaborative worldbuilding platform. The core idea is that users create "Worlds" which act as containers for various types of content. A key design principle is **content immutability**—once a piece of content is created, it cannot be edited or deleted, preserving the history and collaborative nature of the world's development.

The typical user flow is as follows:

1.  **Registration & Authentication**: A new user registers for an account and logs in. The server provides a **JWT (JSON Web Token)** upon successful login. This token must be included in all subsequent requests to prove their identity.
2.  **World Creation**: The authenticated user creates a `World`. They are designated as the creator of this world and have special permissions to manage its settings.
3.  **Content Creation**: The user (or other collaborators) adds content to the world. This can be a `Page` (like a wiki entry), an `Essay`, a `Character` profile, a `Story`, or an `Image`. The system automatically attributes the content to the user who created it.
4.  **Organization**: As content is added, users can create `Tags` (e.g., "Magic System," "Royal Family") and apply them to content to create logical groupings. They can also create direct `Links` between related pieces of content (e.g., linking a `Character` to a `Story` they appear in).
5.  **Exploration & Discovery**: Users can browse the content within a world. The API provides features to view content chronologically (as a timeline), filter it by type, author, or tags, and perform full-text searches.

---

## 2. Database Usage and Design

The application uses a **PostgreSQL** database, chosen for its robustness and support for advanced features like full-text search. The data is structured around a few core concepts:

*   **`World`**: The central model. It acts as a container for all other content and has a designated `creator`.
*   **`ContentBase` (Abstract Model)**: A base for all content types. It includes common fields like `author`, `created_at`, `world`, and contains the logic to enforce **immutability** (i.e., preventing updates after creation).
*   **Content Types**: These models inherit from `ContentBase` and represent the different kinds of information a user can create:
    *   `Page`: For wiki-style entries.
    *   `Essay`: For long-form articles or lore documents.
    *   `Character`: For structured character profiles.
    *   `Story`: For narrative content.
    *   `Image`: Handles file uploads and associated metadata.
*   **Tagging and Linking**:
    *   `Tag`: A simple label that is unique within a `World`.
    *   `ContentTag`: A through-model that links a `Tag` to a piece of content using a generic foreign key, allowing any content type to be tagged.
    *   `ContentLink`: A model to create a directional link from one piece of content to another, forming a web of interconnected information.

Database performance is optimized with **indexes** on frequently queried fields and **full-text search indexes** on content fields to power the search functionality.

---

## 3. URL Routing and API Structure

The API is built using Django REST Framework (DRF) and follows RESTful principles. The URL structure is designed to be logical and hierarchical.

### Authentication Endpoints (JWT)

User authentication is handled via a set of dedicated endpoints provided by the `djangorestframework-simplejwt` library. These are the entry points for the user session.

| Method | Endpoint              | Description                                  |
| :----- | :-------------------- | :------------------------------------------- |
| `POST` | `/api/register/`      | Creates a new user account.                  |
| `POST` | `/api/token/`         | Submits credentials to get a new token pair. |
| `POST` | `/api/token/refresh/` | Submits a refresh token for a new access token. |
| `POST` | `/api/token/verify/`  | Checks if a token is valid.                  |

### Resource Endpoints

All application-specific data is accessed under the `/api/collab/` namespace. The structure is nested to reflect the relationship between worlds and their content.

*   **Worlds**: `/api/collab/worlds/`
    *   `GET`: List all worlds.
    *   `POST`: Create a new world.
    *   `/api/collab/worlds/{world_id}/`
        *   `GET`: Retrieve a single world's details.
        *   `PUT`/`PATCH`: Update a world (restricted to the creator).
        *   `DELETE`: Delete a world (restricted to the creator).

*   **Content within Worlds**: The endpoints for `pages`, `essays`, `characters`, etc., are nested under their parent world.
    *   **Example (`Page` content):**
        *   `GET /api/collab/worlds/{world_id}/pages/`: List all pages in the world.
        *   `POST /api/collab/worlds/{world_id}/pages/`: Create a new page in the world.
        *   `GET /api/collab/worlds/{world_id}/pages/{page_id}/`: Retrieve a single page.
    *   **Note**: Due to the immutability rule, there are no `PUT`, `PATCH`, or `DELETE` methods on these content endpoints.

*   **Tagging and Linking Endpoints**: These endpoints manage the relationships between content.
    *   `POST /api/collab/content/{content_type}/{id}/tags/`: Add a tag to a piece of content.
    *   `POST /api/collab/content/{content_type}/{id}/links/`: Link one piece of content to another.

---

## 4. Views, Filters, and Search

The API provides rich ways to query and view data, which are handled by DRF **ViewSets**.

*   **Views**: Each model (`World`, `Page`, `Character`, etc.) has a corresponding `ViewSet` that defines the API behavior (e.g., `WorldViewSet`, `PageViewSet`). The ViewSets for content are configured to be "create-only" and "read-only" to enforce immutability.

*   **Filters**: The API supports filtering lists of content based on multiple criteria. A frontend application can construct queries to fetch specific data, for example:
    *   Get all content of type `Story`: `GET /api/collab/worlds/{id}/stories/`
    *   Get all content by a specific author.
    *   Get all content marked with a specific `Tag`.

*   **Chronological View**: A dedicated API view will provide a "timeline" of all content in a world, sorted by its creation date. This is crucial for understanding the history and evolution of the world.

*   **Search**: The API will include a search endpoint that uses the database's full-text search capabilities to find content within a world based on keywords.
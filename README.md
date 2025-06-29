# PongArcadia

## Web Application Features

- **User Registration & Management**: Register, log in, update information, and manage profiles.
- **Live Chat**: Direct messaging between users using websockets, including game invites and blocking options.
- **Live Pong Game**: Play a classic Pong game directly on the website.
- **Remote Players**: Compete against remote opponents.
- **Tournament System**: Organize and display tournament matchups and player order.
- **Matchmaking System**: Automatically pair players for matches and announce upcoming games.
- **Game Customization**: Customize the Pong game experience with various options.
- **Two-Factor Authentication (2FA)**: Enhance security with an additional verification layer.
- **Multi-Language Support**: Multiple language support (French, English, Spanish, Italian).
- **Notifications System**: Receive notifications on friends invite, blocked, unblocked or game invite.
- **Cross-Browser Compatibility**: Consistent experience across different web browsers.
- **Single-Page Application**: Functions as a single-page application with browser navigation.
- **Browser Compatibility**: Compatible with the latest stable version of Google Chrome.
</br>

| **Other Functionalities**                         | **Description**                                                                                                 |
|-------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| **User Authentication & Authorization**   | Users must be signed in for access to protected routes. Integration with OAuth 2.0 and secure session management is used. |
| **Server-Side Integration**               | Server-Side Rendering (SSR) is implemented for performance and SEO. The server-side Pong game synchronizes game states between server and client. |
| **Data Consistency**                      | PostgreSQL is used to ensure data consistency. Implement data validation and sanitization to prevent SQL injections and XSS. |
| **Compatibility**                         | The application is compatible with multiple browsers. |
| **User Experience**                       | Smooth and engaging user experience with optimized loading times and performance. |
| **Security**                              | Implemented Two-Factor Authentication (2FA), used HTTPS for all connections, and utilized JWT for secure session management. |
| **Form and user input validation**        | Implemented validation for forms and any user input on the server-side. |


## Tech Stack

- Frontend: NextJS, TypeScript, Tailwind CSS
- Backend: Django Rest Framework (Python)
- Database: Postgresql
- Containerization: Docker


## How to run the project
Docker is used to simplify the process of running all the services of the application (frontend, backend, database, redis, nginx). To run the project on:
### Windows
Run Docker and execute the following command: `docker-compose up -d`.
### MacOS & Linux
It's much easier to run the project on these operating systems, a Makefile exists that automates most of the tasks. So, simply run `make`, then you're done.
<img width="1510" alt="Screenshot 2025-06-29 at 23 27 38" src="https://github.com/user-attachments/assets/df4436f3-20f0-4fd1-a8a9-c06fa55ba425" />



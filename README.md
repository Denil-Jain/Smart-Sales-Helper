# Smart Sales Helper

[Live Link](https://smart-sales-helper-35e5871a5be9.herokuapp.com/login)

[YouTube Demo Link](https://youtu.be/6iEPmnqClho)

To get access for the sales role to try out this app, email me at dj325@njit.edu.

## Description

Smart Sales Helper is a web application designed to streamline and enhance the sales process by leveraging advanced AI capabilities and robust data management features. This app aims to assist sales representatives by providing an intelligent CRM (Customer Relationship Management) system that not only captures leads but also offers suggestions during sales calls to help navigate deals smoothly.

### Features and Functionality

1. **Lead Management**:
   - Capture and manage customer leads effectively.
   - Add, edit, and delete lead information.
   - Store lead details such as customer name, enterprise name, lead type, domain, to-do actions, next follow-up dates, and action needed status.

2. **Voice Input Integration**:
   - Utilize voice input to capture customer interactions and automatically parse this input into structured lead information.
   - Periodic API calls (every 60 Seconds) to OpenAI's GPT-3.5 model for generating suggestions based on the captured voice input.

3. **Lead Analytics Dashboard**:
   - Visualize lead data using various charts and graphs.
   - Analyze lead distribution by type and status.

4. **Role-Based Access Control**:
   - Secure access with role-based permissions (Admin, Sales).
   - Different functionalities accessible based on user roles.

### Development Tools Used

- **Python**: The core programming language used for backend development.
- **Flask**: A lightweight WSGI web application framework used to build the server-side of the application.
- **Bootstrap**: A CSS framework used to create responsive and mobile-first web pages.
- **Jinja2**: A templating engine for Python used to dynamically generate HTML pages.

### APIs Used

- **OpenAI API**: Utilized for integrating the GPT-3.5 model to provide intelligent suggestions and parsing capabilities based on voice input.

### Assets Used

- **Chart.js**: A JavaScript library used to create beautiful and interactive charts on the lead analytics dashboard.

### Libraries Used

- **Flask-Login**: For handling user session management and authentication.
- **Flask-WTF**: For form handling and validation.
- **Flask-Principal**: For role-based access control.
- **SQLAlchemy**: An SQL toolkit and Object-Relational Mapping (ORM) library for database management.
- **SpeechRecognition**: A library to convert speech to text for capturing voice input.

### Relevant Problem Statement

The primary goal of Smart Sales Helper is to address the challenges faced by sales representatives in managing leads and conducting effective sales calls. Traditional CRM systems often require manual data entry and lack intelligent assistance during calls, leading to inefficiencies and missed opportunities. By integrating AI capabilities and voice recognition, Smart Sales Helper aims to automate data capture, provide real-time suggestions, and improve overall sales performance.

---

Feel free to reach out if you have any questions or need further assistance in trying out the application.

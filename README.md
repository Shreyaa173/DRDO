# 🛰️ DRDO Internship Application Management System
A full-stack web application developed to streamline and manage internship applications for DRDO (Defence Research and Development Organisation). The platform provides a seamless experience for students to apply for internships and for admins to manage those applications efficiently.

## 📁 Project Structure
DRDO_Project/
├── backend/ # Express.js + MongoDB (API & authentication)
├── frontend/ # React + Tailwind CSS (UI for students and admins)
├── selenium_tests/ # Selenium automation scripts for testing

## 🔑 Core Features
### 🧑‍🎓 Student Module
- Student registration & login
- Application submission form
- Resume upload (PDF format)
- Application status tracking

### 🧑‍💼 Admin Module
- Admin login portal
- View and manage all applications
- Approve / Reject / Hold applications
- Resume download option

### 🔐 Security & Authorization
- JWT-based authentication
- bcrypt password hashing
- Role-based access control (Admin vs Student)
- CORS and rate-limiting middleware

## ⚙️ Tech Stack
### Frontend:
- React 19
- React Router DOM
- Tailwind CSS
- Recharts
- Axios

### Backend:
- Node.js + Express.js
- MongoDB + Mongoose
- JSON Web Tokens (JWT)
- bcryptjs
- Multer (for file uploads)

### Testing:
- Selenium WebDriver (Python)
- Unittest module

## 🧪 Selenium Testing
All automation scripts are located in the `/selenium_tests/` folder.

Example test cases:
- Student login flow
- Admin login flow
- Resume upload verification
- Application submission validation

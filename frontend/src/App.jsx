import { useEffect, useState } from "react";
import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
  useLocation,
} from "react-router-dom";
import { UserProvider } from "../src/contexts/userContext";
import AdminDashboard from "./adminDashboard";
import axios from "./api/axiosConfig";
import LoginForm from "./components/LoginForm";
import SignupForm from "./components/Signup";
import StudentDashboard from "./studentDashboard";
import ForgetPassword from "./components/ForgetPassword";
import ResetPassword from "./components/ResetPassword";

const AppContent = ({
  currentUser,
  setCurrentUser,
  applications,
  setApplications,
  notifications,
  setNotifications,
  students,
  setStudents,
  universities,
  setUniversities,
}) => {
  const location = useLocation();

  const handleLogout = () => {
    setCurrentUser(null);
    localStorage.removeItem("authToken");
    localStorage.removeItem("currentUser");
    delete axios.defaults.headers.common["Authorization"];
  };

  return (
    <div className="flex bg-gray-50">
      <main className="flex-1">
        <div className="flex w-full min-h-screen">
          <Routes>
            {/* Default route */}
            <Route
              path="/"
              element={
                currentUser ? (
                  currentUser.role === "admin" ? (
                    <Navigate to="/admin" replace />
                  ) : (
                    <Navigate to="/student" replace />
                  )
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />

            {/* Student Dashboard */}
            <Route
              path="/student/*"
              element={
                currentUser && currentUser.role === "student" ? (
                  <StudentDashboard
                    currentUser={currentUser}
                    setCurrentUser={setCurrentUser}
                    applications={applications}
                    setApplications={setApplications}
                    onLogout={handleLogout}
                  />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />

            {/* Admin Dashboard */}
            <Route
              path="/admin/*"
              element={
                currentUser && currentUser.role === "admin" ? (
                  <AdminDashboard
                    currentUser={currentUser}
                    setCurrentUser={setCurrentUser}
                    students={students}
                    setStudents={setStudents}
                    applications={applications}
                    setApplications={setApplications}
                    universities={universities}
                    setUniversities={setUniversities}
                    notifications={notifications}
                    setNotifications={setNotifications}
                    onLogout={handleLogout}
                  />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />

            {/* Auth Routes */}
            <Route
              path="/login"
              element={
                currentUser ? (
                  currentUser.role === "admin" ? (
                    <Navigate to="/admin" replace />
                  ) : (
                    <Navigate to="/student" replace />
                  )
                ) : (
                  <LoginForm setCurrentUser={setCurrentUser} />
                )
              }
            />

            <Route
              path="/signup"
              element={
                currentUser ? (
                  currentUser.role === "admin" ? (
                    <Navigate to="/admin" replace />
                  ) : (
                    <Navigate to="/student" replace />
                  )
                ) : (
                  <SignupForm setCurrentUser={setCurrentUser} />
                )
              }
            />

            {/* ✅ Password Reset Routes - No auth needed, before catch-all */}
            <Route path="/forgot-password" element={<ForgetPassword />} />
            <Route path="/reset-password/:token" element={<ResetPassword />} />

            {/* Catch-All */}
            <Route
              path="*"
              element={<Navigate to="/login" replace />}
            />
          </Routes>
        </div>
      </main>
    </div>
  );
};

const App = () => {
  const [currentUser, setCurrentUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [applications, setApplications] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [students, setStudents] = useState([]);
  const [universities, setUniversities] = useState([]);

  const setCurrentUserWithPersistence = (userData) => {
    setCurrentUser(userData);
    if (userData) {
      localStorage.setItem("currentUser", JSON.stringify(userData));
    } else {
      localStorage.removeItem("currentUser");
      localStorage.removeItem("authToken");
      delete axios.defaults.headers.common["Authorization"];
    }
  };

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const savedUser = localStorage.getItem("currentUser");
        const savedToken = localStorage.getItem("authToken");

        if (savedUser && savedToken) {
          const userData = JSON.parse(savedUser);

          if (userData && userData.id && userData.role) {
            axios.defaults.headers.common["Authorization"] = `Bearer ${savedToken}`;

            try {
              const response = await axios.get("/auth/verify");
              if (response.data.valid) {
                const updatedUser = response.data.user;
                setCurrentUser(updatedUser);
                localStorage.setItem("currentUser", JSON.stringify(updatedUser));
              }
            } catch (error) {
              console.error("Token verification failed:", error);
              localStorage.removeItem("currentUser");
              localStorage.removeItem("authToken");
              delete axios.defaults.headers.common["Authorization"];
            }
          } else {
            localStorage.removeItem("currentUser");
            localStorage.removeItem("authToken");
          }
        }
      } catch (error) {
        console.error("Error loading saved user:", error);
        localStorage.removeItem("currentUser");
        localStorage.removeItem("authToken");
        delete axios.defaults.headers.common["Authorization"];
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <UserProvider>
      <Router>
        <AppContent
          currentUser={currentUser}
          setCurrentUser={setCurrentUserWithPersistence}
          applications={applications}
          setApplications={setApplications}
          notifications={notifications}
          setNotifications={setNotifications}
          students={students}
          setStudents={setStudents}
          universities={universities}
          setUniversities={setUniversities}
        />
      </Router>
    </UserProvider>
  );
};

export default App;
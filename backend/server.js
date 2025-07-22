const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();
const path = require('path');
const app = express();

// Connect to MongoDB
mongoose.connect(process.env.MONGO_URI)
.then(() => console.log("✅ MongoDB connected successfully"))
.catch((err) => console.error("❌ MongoDB connection error:", err));

// Middleware
app.use(cors({
  origin: [
    "https://drdo-6eek.vercel.app",
    "https://*.vercel.app"
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  optionsSuccessStatus: 200
}));

app.use(express.json()); // Add this for JSON parsing
app.use(express.urlencoded({ extended: true })); // Add this for form data

// Serve static files for resume downloads
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

app.options('*', (req, res) => {
  res.header('Access-Control-Allow-Origin', 'https://drdo-6eek.vercel.app');
  res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
  res.sendStatus(200);
});

// Routes
const authRoutes = require('./routes/authRoutes');
const applicationRoutes = require('./routes/applicationRoutes');
const userRoutes = require('./routes/userRoutes');

app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/applications', applicationRoutes);

// Root route
app.get("/", (req, res) => {
  res.send("🚀 DRDO Internship Backend is running successfully!");
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Server Error:', error);
  res.status(500).json({ error: 'Internal Server Error' });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`📝 Routes available:`);
  console.log(`   POST /api/auth/signup`);
  console.log(`   POST /api/auth/login`);
  console.log(`   GET  /api/auth/verify`);
  console.log(`   GET  /api/applications`);
  console.log(`   GET  /api/applications/student/mine`);
  console.log(`   POST /api/applications`);
  console.log(`   GET  /api/applications/:id`);
  console.log(`   GET  /api/applications/resume/:filename`);
  console.log(`   PUT  /api/applications/:id/status`);
});
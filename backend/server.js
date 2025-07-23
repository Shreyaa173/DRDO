const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const app = express();

// 🔧 Auto-create uploads folder if it doesn't exist
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir);
  console.log('📁 uploads folder created automatically');
}

// 🔌 Connect to MongoDB
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB connected successfully"))
  .catch((err) => console.error("❌ MongoDB connection error:", err));

// 🌐 Middleware
app.use(cors({
  origin: [
    "http://localhost:5173",
    "https://drdointernshipapplicationproject.netlify.app/"
  ],
  credentials: true
}));
app.use(express.json()); // Parse JSON bodies
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded bodies

// 🗂️ Serve uploaded resumes statically
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// 📦 Routes
const authRoutes = require('./routes/authRoutes');
const applicationRoutes = require('./routes/applicationRoutes');
const userRoutes = require('./routes/userRoutes');

app.use('/api/auth', authRoutes);
app.use('/api/users', userRoutes);
app.use('/api/applications', applicationRoutes);

// 🌍 Root route
app.get("/", (req, res) => {
  res.send("🚀 DRDO Internship Backend is running successfully!");
});

// ❌ Error handler
app.use((error, req, res, next) => {
  console.error('Server Error:', error);
  res.status(500).json({ error: 'Internal Server Error' });
});

// 🚀 Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📝 Routes available:`);
  console.log(`   POST /api/auth/signup`);
  console.log(`   POST /api/auth/login`);
  console.log(`   GET  /api/applications`);
  console.log(`   GET  /api/applications/student/mine`);
  console.log(`   POST /api/applications`);
  console.log(`   GET  /api/applications/:id`);
  console.log(`   GET  /api/applications/resume/:filename`);
  console.log(`   PUT  /api/applications/:id/status`);
});

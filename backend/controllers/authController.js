const User = require('../models/User');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

// REGISTER a new user
exports.register = async (req, res) => {
  console.log('🔍 Registration attempt received');
  console.log('Request body:', req.body);
  
  const { name, email, password, role } = req.body;
  
  // Input validation
  if (!name || !email || !password) {
    console.log('❌ Missing required fields');
    return res.status(400).json({ error: "Name, email, and password are required" });
  }

  if (password.length < 6) {
    console.log('❌ Password too short');
    return res.status(400).json({ error: "Password must be at least 6 characters long" });
  }

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    console.log('❌ Invalid email format');
    return res.status(400).json({ error: "Invalid email format" });
  }
  
  try {
    // Check if user already exists
    const existingUser = await User.findOne({ email: email.toLowerCase() });
    if (existingUser) {
      console.log('❌ User already exists:', email);
      return res.status(400).json({ error: "Email already exists" });
    }
    
    const hashedPassword = await bcrypt.hash(password, 12); // Increased from 10 to 12 for better security
    console.log('🔍 Password hashed successfully');

    const user = await User.create({
      name: name.trim(),
      email: email.toLowerCase().trim(),
      password: hashedPassword,
      role: role || 'student' // Default to student if no role provided
    });

    console.log('✅ User created successfully:', email);
    res.status(201).json({ 
      message: "User created successfully",
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role
      }
    });

  } catch (err) {
    console.error("❌ Register Error:", err);
    if (err.code === 11000) {
      // MongoDB duplicate key error
      return res.status(400).json({ error: "Email already exists" });
    }
    res.status(500).json({ error: "Registration failed. Please try again." });
  }
};

// LOGIN controller with enhanced debugging
exports.login = async (req, res) => {
  console.log('🔍 Login attempt received');
  console.log('Request body:', req.body);
  console.log('Request headers:', req.headers);
  
  const { email, password } = req.body;

  // Input validation
  if (!email || !password) {
    console.log('❌ Missing email or password');
    return res.status(400).json({ error: "Email and password are required" });
  }

  try {
    const normalizedEmail = email.toLowerCase().trim();
    console.log('🔍 Searching for user:', normalizedEmail);
    const user = await User.findOne({ email: normalizedEmail });

    if (!user) {
      console.log('❌ User not found:', normalizedEmail);
      
      // Debug: Check how many users exist
      const userCount = await User.countDocuments();
      console.log('📊 Total users in database:', userCount);
      
      // Debug: List all users (emails only) - limit to 10 for security
      const allUsers = await User.find({}).select('email').limit(10);
      console.log('📋 Sample users in database:', allUsers.map(u => u.email));
      
      return res.status(401).json({ error: "Invalid email or password" });
    }

    console.log('✅ User found:', user.email);
    console.log('🔍 User ID:', user._id);

    const isMatch = await bcrypt.compare(password, user.password);
    console.log('🔍 Password match result:', isMatch);
    
    if (!isMatch) {
      console.log('❌ Password mismatch for user:', user.email);
      return res.status(401).json({ error: "Invalid email or password" });
    }

    // Check JWT_SECRET
    if (!process.env.JWT_SECRET) {
      console.log('❌ JWT_SECRET not found in environment variables');
      return res.status(500).json({ error: "Server configuration error" });
    }

    const token = jwt.sign(
      { id: user._id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: "7d" }
    );

    console.log('✅ Login successful for:', user.email);

    // Create a clean user object (exclude password)
    const userData = {
      id: user._id,
      name: user.name,
      email: user.email,
      role: user.role,
      phone: user.phone,
      branch: user.branch,
      cgpa: user.cgpa,
      year: user.year,
      university: user.university,
      location: user.location,
    };

    // Return token + user
    res.json({ valid: true, token: token, user: userData });

  } catch (err) {
    console.error("❌ Login Error:", err);
    if (!res.headersSent) {
      res.status(500).json({ error: "Server error. Please try again." });
    }
  }
};

// VERIFY TOKEN controller
exports.verifyToken = async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select("-password");
    if (!user) {
      return res.status(404).json({ error: "User not found" });
    }

    const userData = {
      id: user._id,
      name: user.name,
      email: user.email,
      role: user.role,
      phone: user.phone,
      branch: user.branch,
      cgpa: user.cgpa,
      year: user.year,
      university: user.university,
      location: user.location,
    };

    // Optional: Return token again (if frontend refresh is designed to update token)
    const token = jwt.sign(
      { id: user._id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: "7d" }
    );

    res.json({ valid: true, user: userData, token });

  } catch (error) {
    console.error("Verify Token Error:", error);
    if (!res.headersSent) {
      res.status(500).json({ error: "Server error" });
    }
  }
};

// AUTHENTICATE middleware
exports.authenticateToken = (req, res, next) => {
  const authHeader = req.headers["authorization"];
  const token = authHeader && authHeader.split(" ")[1];

  if (!token) {
    return res.status(401).json({ error: "Access token required" });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.status(403).json({ error: "Invalid or expired token" });
    }
    req.user = decoded;
    next();
  });
};

// UPDATE PROFILE controller
exports.updateProfile = async (req, res) => {
  try {
    const updatedUser = await User.findByIdAndUpdate(
      req.user.id,
      req.body,
      { new: true, select: "-password" }
    );

    if (!updatedUser) {
      return res.status(404).json({ error: "User not found" });
    }

    res.json({ success: true, user: updatedUser });
  } catch (error) {
    console.error("Update Profile Error:", error);
    res.status(500).json({ error: "Server error" });
  }
};

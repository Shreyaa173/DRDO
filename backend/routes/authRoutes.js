const express = require('express');
const router = express.Router();
const crypto = require('crypto');
const nodemailer = require('nodemailer');
const bcrypt = require('bcryptjs');
const User = require('../models/User');
const authController = require('../controllers/authController');

// Existing Routes
router.post('/signup', authController.register);
router.post('/login', authController.login);
router.get('/verify', authController.authenticateToken, authController.verifyToken);
router.put('/profile', authController.authenticateToken, authController.updateProfile);

// POST /api/auth/forgot-password
router.post('/forgot-password', async (req, res) => {
  const { email } = req.body;
  console.log("📧 Forgot password request for:", email);

  try {
    const user = await User.findOne({ email });
    console.log("👤 User found:", user ? "Yes" : "No");

    if (!user) return res.status(404).json({ error: 'No account with that email.' });

    // Generate token
    const token = crypto.randomBytes(32).toString('hex');
    user.resetPasswordToken = token;
    user.resetPasswordExpires = Date.now() + 3600000; // 1 hour
    await user.save();
    console.log("✅ Token saved to user");

    // Send email
    const transporter = nodemailer.createTransport({
      service: 'Gmail',
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
      },
    });

    const resetURL = `${process.env.FRONTEND_URL}/reset-password/${token}`;
    console.log("🔗 Reset URL:", resetURL);

    await transporter.sendMail({
      from: process.env.EMAIL_USER,
      to: user.email,
      subject: 'Password Reset Request - DRDO Internship',
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #2563eb;">Password Reset Request</h2>
          <p>Hi ${user.name},</p>
          <p>You requested a password reset for your DRDO Internship account.</p>
          <p>Click the button below to reset your password (valid for 1 hour):</p>
          <a href="${resetURL}" 
             style="display: inline-block; background-color: #2563eb; color: white; 
                    padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 16px 0;">
            Reset Password
          </a>
          <p>If you didn't request this, please ignore this email.</p>
          <p>This link expires in 1 hour.</p>
        </div>
      `,
    });

    console.log("✅ Reset email sent to:", user.email);
    res.json({ message: 'Reset link sent to your email.' });

  } catch (err) {
    console.error("❌ Forgot password error:", err);
    res.status(500).json({ error: 'Server error. Please try again.' });
  }
});

// POST /api/auth/reset-password/:token
router.post('/reset-password/:token', async (req, res) => {
  const { token } = req.params;
  const { password } = req.body;
  console.log("🔑 Reset password attempt with token:", token);

  try {
    const user = await User.findOne({
      resetPasswordToken: token,
      resetPasswordExpires: { $gt: Date.now() },
    });

    if (!user) {
      console.log("❌ Token invalid or expired");
      return res.status(400).json({ error: 'Token is invalid or has expired.' });
    }

    console.log("👤 User found for reset:", user.email);

    // Hash and save new password
    user.password = await bcrypt.hash(password, 10);
    user.resetPasswordToken = undefined;
    user.resetPasswordExpires = undefined;
    await user.save();

    console.log("✅ Password reset successful for:", user.email);
    res.json({ message: 'Password has been reset successfully.' });

  } catch (err) {
    console.error("❌ Reset password error:", err);
    res.status(500).json({ error: 'Server error. Please try again.' });
  }
});

module.exports = router;
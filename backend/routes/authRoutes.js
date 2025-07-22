// backend/routes/authRoutes.js
const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

router.post('/signup', authController.register);
router.post('/login', authController.login);
router.get('/verify', authController.authenticateToken, authController.verifyToken);
// Add this missing route:
router.put('/profile', authController.authenticateToken, authController.updateProfile);

module.exports = router;
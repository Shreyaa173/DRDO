const express = require('express');
const router = express.Router();
const {
  createApplication,
  getAllApplications,
  getApplication,
  updateStatus,
  getStudentApplications,
  getResume,
  deleteApplication 
} = require('../controllers/applicationController');

const authMiddleware = require('../middlewares/authMiddleware');
const upload = require('../middlewares/multer');

// ✅ Application Creation - now accepts ONLY 1 resume
router.post('/', upload.single('resume'), authMiddleware, createApplication);

// Admin Routes
router.get('/', authMiddleware, getAllApplications);

// ⚠️ IMPORTANT: Put specific routes BEFORE parameterized routes
router.get('/student/mine', authMiddleware, getStudentApplications);
router.get('/resume/:filename', getResume);

// Parameterized routes come AFTER specific routes
router.get('/:id', authMiddleware, getApplication);
router.put('/:id/status', authMiddleware, updateStatus);
router.delete('/:id', authMiddleware, deleteApplication);

module.exports = router;
# API Endpoint

Kevin say: why make five file when one file do trick?

## Without kevin

```
routes/
  userRoutes.js        (router)
schemas/
  userSchema.js        (validation schema)
controllers/
  userController.js    (request handling)
services/
  userService.js       (business logic)
repositories/
  userRepository.js    (data access)
```

```javascript
// userRoutes.js
const express = require('express');
const router = express.Router();
const userController = require('../controllers/userController');
router.get('/:id', userController.getUser);
module.exports = router;

// userSchema.js
const Joi = require('joi');
const getUserSchema = Joi.object({ id: Joi.string().required() });
module.exports = { getUserSchema };

// userController.js
const userService = require('../services/userService');
const { getUserSchema } = require('../schemas/userSchema');
const getUser = async (req, res) => {
  const { error } = getUserSchema.validate(req.params);
  if (error) return res.status(400).json({ error: error.message });
  try {
    const user = await userService.getUserById(req.params.id);
    if (!user) return res.status(404).json({ error: 'Not found' });
    res.json(user);
  } catch (err) {
    res.status(500).json({ error: 'Internal server error' });
  }
};
module.exports = { getUser };

// ... and so on
```

Files: **5**. Lines: **80+**. Tokens: **~900**.

## With kevin

```javascript
// routes.js
router.get('/users/:id', async (req, res) => {
  const user = await db.users.findById(req.params.id);
  if (!user) return res.status(404).json({ error: 'Not found' });
  res.json(user);
});
// kevin: no service/repo layer. add when second caller exists.
```

Files: **1** (added to existing routes file). Lines: **5**. Tokens: **~80**.

**Result: 5 files → 0 new files. 94% fewer tokens.**

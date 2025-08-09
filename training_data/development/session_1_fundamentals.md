# Development Mode Training - Session 1: Fundamentals

## Full-Stack Development Principles

### Modern Development Architecture

#### Frontend Architecture Patterns
**Component-Based Architecture**:
- Reusable, modular components
- Clear separation of concerns
- Unidirectional data flow
- State management patterns
- Performance optimization

**React/TypeScript Best Practices**:
```typescript
// Functional component with TypeScript
interface UserCardProps {
  user: {
    id: string;
    name: string;
    email: string;
    avatar?: string;
  };
  onEdit: (userId: string) => void;
  onDelete: (userId: string) => void;
}

const UserCard: React.FC<UserCardProps> = ({ user, onEdit, onDelete }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleEdit = useCallback(() => {
    onEdit(user.id);
  }, [user.id, onEdit]);

  const handleDelete = useCallback(async () => {
    setIsLoading(true);
    try {
      await onDelete(user.id);
    } finally {
      setIsLoading(false);
    }
  }, [user.id, onDelete]);

  return (
    <div className="user-card">
      <img src={user.avatar || '/default-avatar.png'} alt={user.name} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      <div className="actions">
        <button onClick={handleEdit} disabled={isLoading}>
          Edit
        </button>
        <button onClick={handleDelete} disabled={isLoading}>
          {isLoading ? 'Deleting...' : 'Delete'}
        </button>
      </div>
    </div>
  );
};
```

#### Backend Architecture Patterns
**RESTful API Design**:
```typescript
// Express.js with TypeScript
import express, { Request, Response, NextFunction } from 'express';
import { body, validationResult } from 'express-validator';

interface CreateUserRequest {
  name: string;
  email: string;
  password: string;
}

interface AuthenticatedRequest extends Request {
  user?: { id: string; email: string; role: string };
}

// Middleware for authentication
const authenticateToken = (req: AuthenticatedRequest, res: Response, next: NextFunction) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  jwt.verify(token, process.env.JWT_SECRET!, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user as any;
    next();
  });
};

// User creation endpoint with validation
app.post('/api/users',
  [
    body('name').isLength({ min: 2 }).withMessage('Name must be at least 2 characters'),
    body('email').isEmail().withMessage('Valid email required'),
    body('password').isLength({ min: 8 }).withMessage('Password must be at least 8 characters')
  ],
  async (req: Request<{}, {}, CreateUserRequest>, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    try {
      const { name, email, password } = req.body;
      
      // Check if user already exists
      const existingUser = await User.findOne({ email });
      if (existingUser) {
        return res.status(409).json({ error: 'User already exists' });
      }

      // Hash password
      const saltRounds = 12;
      const hashedPassword = await bcrypt.hash(password, saltRounds);

      // Create user
      const user = new User({
        name,
        email,
        password: hashedPassword
      });

      await user.save();

      // Return user without password
      const { password: _, ...userResponse } = user.toObject();
      res.status(201).json(userResponse);

    } catch (error) {
      console.error('User creation error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);
```

### Database Design and Management

#### Database Schema Design
**Relational Database (PostgreSQL)**:
```sql
-- Users table with proper constraints
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'user',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Posts table with foreign key relationship
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  author_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(20) DEFAULT 'draft',
  published_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_author_id ON posts(author_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_published_at ON posts(published_at) WHERE published_at IS NOT NULL;

-- Trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**NoSQL Database (MongoDB)**:
```typescript
// Mongoose schema with TypeScript
import mongoose, { Document, Schema } from 'mongoose';

interface IUser extends Document {
  email: string;
  passwordHash: string;
  name: string;
  role: 'admin' | 'user' | 'moderator';
  profile: {
    avatar?: string;
    bio?: string;
    location?: string;
  };
  preferences: {
    theme: 'light' | 'dark';
    notifications: boolean;
    language: string;
  };
  isActive: boolean;
  lastLogin?: Date;
  createdAt: Date;
  updatedAt: Date;
}

const userSchema = new Schema<IUser>({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    validate: {
      validator: (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
      message: 'Invalid email format'
    }
  },
  passwordHash: {
    type: String,
    required: true,
    minlength: 60 // bcrypt hash length
  },
  name: {
    type: String,
    required: true,
    trim: true,
    minlength: 2,
    maxlength: 100
  },
  role: {
    type: String,
    enum: ['admin', 'user', 'moderator'],
    default: 'user'
  },
  profile: {
    avatar: String,
    bio: { type: String, maxlength: 500 },
    location: { type: String, maxlength: 100 }
  },
  preferences: {
    theme: { type: String, enum: ['light', 'dark'], default: 'light' },
    notifications: { type: Boolean, default: true },
    language: { type: String, default: 'en' }
  },
  isActive: { type: Boolean, default: true },
  lastLogin: Date
}, {
  timestamps: true,
  toJSON: {
    transform: (doc, ret) => {
      delete ret.passwordHash;
      delete ret.__v;
      return ret;
    }
  }
});

// Indexes for performance
userSchema.index({ email: 1 });
userSchema.index({ role: 1, isActive: 1 });
userSchema.index({ createdAt: -1 });

export const User = mongoose.model<IUser>('User', userSchema);
```

### API Development Best Practices

#### RESTful API Design Principles
**HTTP Methods and Status Codes**:
```typescript
// GET - Retrieve resources
app.get('/api/users', async (req, res) => {
  const { page = 1, limit = 10, search } = req.query;
  
  try {
    const query = search ? { name: { $regex: search, $options: 'i' } } : {};
    const users = await User.find(query)
      .limit(Number(limit))
      .skip((Number(page) - 1) * Number(limit))
      .sort({ createdAt: -1 });
    
    const total = await User.countDocuments(query);
    
    res.json({
      users,
      pagination: {
        page: Number(page),
        limit: Number(limit),
        total,
        pages: Math.ceil(total / Number(limit))
      }
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

// POST - Create new resource
app.post('/api/users', async (req, res) => {
  // Returns 201 Created on success
  // Returns 400 Bad Request for validation errors
  // Returns 409 Conflict if resource already exists
});

// PUT - Update entire resource
app.put('/api/users/:id', async (req, res) => {
  // Returns 200 OK on successful update
  // Returns 404 Not Found if resource doesn't exist
  // Returns 400 Bad Request for validation errors
});

// PATCH - Partial update
app.patch('/api/users/:id', async (req, res) => {
  // Returns 200 OK on successful partial update
  // Returns 404 Not Found if resource doesn't exist
});

// DELETE - Remove resource
app.delete('/api/users/:id', async (req, res) => {
  // Returns 204 No Content on successful deletion
  // Returns 404 Not Found if resource doesn't exist
});
```

#### GraphQL API Development
```typescript
import { GraphQLObjectType, GraphQLString, GraphQLSchema, GraphQLList, GraphQLNonNull } from 'graphql';

// Type definitions
const UserType = new GraphQLObjectType({
  name: 'User',
  fields: {
    id: { type: GraphQLString },
    name: { type: GraphQLString },
    email: { type: GraphQLString },
    createdAt: { type: GraphQLString }
  }
});

const PostType = new GraphQLObjectType({
  name: 'Post',
  fields: {
    id: { type: GraphQLString },
    title: { type: GraphQLString },
    content: { type: GraphQLString },
    author: {
      type: UserType,
      resolve: async (post) => {
        return await User.findById(post.authorId);
      }
    },
    createdAt: { type: GraphQLString }
  }
});

// Query resolvers
const RootQuery = new GraphQLObjectType({
  name: 'RootQueryType',
  fields: {
    users: {
      type: new GraphQLList(UserType),
      resolve: async () => {
        return await User.find();
      }
    },
    user: {
      type: UserType,
      args: { id: { type: GraphQLString } },
      resolve: async (parent, args) => {
        return await User.findById(args.id);
      }
    },
    posts: {
      type: new GraphQLList(PostType),
      resolve: async () => {
        return await Post.find();
      }
    }
  }
});

// Mutation resolvers
const Mutation = new GraphQLObjectType({
  name: 'Mutation',
  fields: {
    createUser: {
      type: UserType,
      args: {
        name: { type: new GraphQLNonNull(GraphQLString) },
        email: { type: new GraphQLNonNull(GraphQLString) }
      },
      resolve: async (parent, args) => {
        const user = new User(args);
        return await user.save();
      }
    }
  }
});

export const schema = new GraphQLSchema({
  query: RootQuery,
  mutation: Mutation
});
```

### Testing Strategies

#### Unit Testing with Jest
```typescript
// User service unit tests
import { UserService } from '../services/UserService';
import { User } from '../models/User';

jest.mock('../models/User');

describe('UserService', () => {
  let userService: UserService;
  const mockUser = {
    id: '123',
    name: 'John Doe',
    email: 'john@example.com',
    save: jest.fn(),
    toObject: jest.fn()
  };

  beforeEach(() => {
    userService = new UserService();
    jest.clearAllMocks();
  });

  describe('createUser', () => {
    it('should create a new user successfully', async () => {
      const userData = {
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      };

      (User.findOne as jest.Mock).mockResolvedValue(null);
      (User.prototype.save as jest.Mock).mockResolvedValue(mockUser);
      mockUser.toObject.mockReturnValue({ ...mockUser, password: undefined });

      const result = await userService.createUser(userData);

      expect(User.findOne).toHaveBeenCalledWith({ email: userData.email });
      expect(result).toEqual(expect.objectContaining({
        name: userData.name,
        email: userData.email
      }));
      expect(result.password).toBeUndefined();
    });

    it('should throw error if user already exists', async () => {
      const userData = {
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      };

      (User.findOne as jest.Mock).mockResolvedValue(mockUser);

      await expect(userService.createUser(userData)).rejects.toThrow('User already exists');
    });
  });
});
```

#### Integration Testing
```typescript
// API integration tests
import request from 'supertest';
import { app } from '../app';
import { connectDB, closeDB } from '../config/database';

describe('User API Integration Tests', () => {
  beforeAll(async () => {
    await connectDB();
  });

  afterAll(async () => {
    await closeDB();
  });

  describe('POST /api/users', () => {
    it('should create a new user', async () => {
      const userData = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };

      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect(201);

      expect(response.body).toMatchObject({
        name: userData.name,
        email: userData.email
      });
      expect(response.body.password).toBeUndefined();
      expect(response.body.id).toBeDefined();
    });

    it('should return validation errors for invalid data', async () => {
      const invalidData = {
        name: 'A', // Too short
        email: 'invalid-email',
        password: '123' // Too short
      };

      const response = await request(app)
        .post('/api/users')
        .send(invalidData)
        .expect(400);

      expect(response.body.errors).toHaveLength(3);
    });
  });
});
```

### DevOps and Deployment

#### Docker Configuration
```dockerfile
# Multi-stage Dockerfile for Node.js application
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY src/ ./src/

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Start application
CMD ["node", "dist/index.js"]
```

#### CI/CD Pipeline (GitHub Actions)
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linting
        run: npm run lint
      
      - name: Run type checking
        run: npm run type-check
      
      - name: Run unit tests
        run: npm run test:unit
        env:
          NODE_ENV: test
      
      - name: Run integration tests
        run: npm run test:integration
        env:
          NODE_ENV: test
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/testdb
      
      - name: Generate coverage report
        run: npm run test:coverage
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Run security scan
        run: docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image myapp:${{ github.sha }}

  deploy:
    needs: [test, build]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to production
        run: echo "Deploying to production..."
```

### Performance Optimization

#### Database Query Optimization
```typescript
// Efficient database queries
class UserRepository {
  // Use indexes and limit results
  async findUsers(filters: UserFilters, pagination: Pagination) {
    const query = User.find(filters)
      .select('name email role createdAt') // Only select needed fields
      .limit(pagination.limit)
      .skip(pagination.offset)
      .sort({ createdAt: -1 });

    // Use lean() for read-only operations
    return await query.lean().exec();
  }

  // Batch operations for better performance
  async updateMultipleUsers(userIds: string[], updateData: Partial<IUser>) {
    return await User.updateMany(
      { _id: { $in: userIds } },
      { $set: updateData }
    );
  }

  // Use aggregation for complex queries
  async getUserStats() {
    return await User.aggregate([
      {
        $group: {
          _id: '$role',
          count: { $sum: 1 },
          avgAge: { $avg: '$age' }
        }
      },
      {
        $sort: { count: -1 }
      }
    ]);
  }
}
```

#### Caching Strategies
```typescript
import Redis from 'ioredis';

class CacheService {
  private redis: Redis;

  constructor() {
    this.redis = new Redis(process.env.REDIS_URL);
  }

  // Cache with TTL
  async set(key: string, value: any, ttl: number = 3600) {
    await this.redis.setex(key, ttl, JSON.stringify(value));
  }

  async get<T>(key: string): Promise<T | null> {
    const value = await this.redis.get(key);
    return value ? JSON.parse(value) : null;
  }

  // Cache-aside pattern
  async getOrSet<T>(
    key: string,
    fetchFn: () => Promise<T>,
    ttl: number = 3600
  ): Promise<T> {
    const cached = await this.get<T>(key);
    if (cached) {
      return cached;
    }

    const fresh = await fetchFn();
    await this.set(key, fresh, ttl);
    return fresh;
  }

  // Invalidate cache patterns
  async invalidatePattern(pattern: string) {
    const keys = await this.redis.keys(pattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }
}

// Usage in service
class UserService {
  constructor(private cache: CacheService) {}

  async getUser(id: string) {
    return await this.cache.getOrSet(
      `user:${id}`,
      () => User.findById(id).lean(),
      1800 // 30 minutes
    );
  }

  async updateUser(id: string, data: Partial<IUser>) {
    const user = await User.findByIdAndUpdate(id, data, { new: true });
    
    // Invalidate cache
    await this.cache.invalidatePattern(`user:${id}*`);
    
    return user;
  }
}
```

## Training Exercises

### Exercise 1: Full-Stack Application
**Task**: Build a complete task management application
**Requirements**:
- React/TypeScript frontend with responsive design
- Node.js/Express backend with TypeScript
- PostgreSQL database with proper schema design
- JWT authentication and authorization
- RESTful API with proper error handling
- Unit and integration tests
- Docker containerization

### Exercise 2: Microservices Architecture
**Task**: Design and implement a microservices system
**Requirements**:
- Multiple services (user, order, payment, notification)
- API Gateway for request routing
- Service-to-service communication
- Database per service pattern
- Event-driven architecture with message queues
- Monitoring and logging
- CI/CD pipeline

### Exercise 3: Performance Optimization
**Task**: Optimize a slow-performing application
**Requirements**:
- Database query optimization
- Caching implementation (Redis)
- API response optimization
- Frontend performance improvements
- Load testing and monitoring
- Performance metrics and reporting

## Assessment Criteria

### Code Quality
- Clean, readable, and maintainable code
- Proper TypeScript usage and type safety
- Consistent coding standards and conventions
- Appropriate design patterns and architecture

### Technical Skills
- Proficiency in full-stack technologies
- Database design and optimization
- API development and documentation
- Testing strategies and implementation
- DevOps and deployment practices

### Problem-Solving
- Ability to break down complex problems
- Efficient algorithm and data structure usage
- Performance optimization techniques
- Debugging and troubleshooting skills

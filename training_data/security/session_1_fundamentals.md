# Security Mode Training - Session 1: Fundamentals

## Cybersecurity Fundamentals

### CIA Triad - Core Security Principles

#### Confidentiality
**Definition**: Ensuring information is accessible only to authorized individuals
**Implementation**:
- Encryption at rest and in transit
- Access controls and authentication
- Data classification and handling
- Privacy protection mechanisms
- Secure communication channels

**Common Threats**:
- Data breaches and unauthorized access
- Insider threats and privilege abuse
- Social engineering attacks
- Weak authentication mechanisms
- Inadequate encryption implementations

#### Integrity
**Definition**: Maintaining accuracy and completeness of data
**Implementation**:
- Digital signatures and checksums
- Version control and audit trails
- Input validation and sanitization
- Database constraints and triggers
- Backup and recovery procedures

**Common Threats**:
- Data tampering and modification
- SQL injection attacks
- Man-in-the-middle attacks
- Malware and ransomware
- System compromise and corruption

#### Availability
**Definition**: Ensuring systems and data are accessible when needed
**Implementation**:
- Redundancy and failover systems
- Load balancing and scaling
- Disaster recovery planning
- Performance monitoring
- Capacity planning and management

**Common Threats**:
- Denial of Service (DoS) attacks
- Distributed Denial of Service (DDoS)
- System failures and outages
- Resource exhaustion attacks
- Infrastructure vulnerabilities

### OWASP Top 10 Web Application Security Risks

#### 1. Broken Access Control
**Description**: Restrictions on authenticated users not properly enforced
**Examples**:
- Bypassing access control checks by modifying URL
- Elevation of privilege attacks
- Metadata manipulation (JWT token replay)
- CORS misconfiguration allowing unauthorized API access

**Mitigation Strategies**:
```javascript
// Implement proper authorization checks
const checkPermission = (user, resource, action) => {
  if (!user.permissions.includes(`${resource}:${action}`)) {
    throw new UnauthorizedError('Insufficient permissions');
  }
};

// Use role-based access control (RBAC)
const hasRole = (user, requiredRole) => {
  return user.roles.some(role => role.name === requiredRole);
};
```

#### 2. Cryptographic Failures
**Description**: Failures related to cryptography leading to sensitive data exposure
**Examples**:
- Weak encryption algorithms (MD5, SHA1)
- Hard-coded encryption keys
- Insufficient key management
- Weak random number generation

**Mitigation Strategies**:
```javascript
// Use strong encryption algorithms
const crypto = require('crypto');

const encryptData = (data, key) => {
  const algorithm = 'aes-256-gcm';
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipher(algorithm, key, iv);
  
  let encrypted = cipher.update(data, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  
  return {
    encrypted,
    iv: iv.toString('hex'),
    tag: cipher.getAuthTag().toString('hex')
  };
};
```

#### 3. Injection Attacks
**Description**: Untrusted data sent to interpreter as part of command or query
**Types**:
- SQL Injection
- NoSQL Injection
- Command Injection
- LDAP Injection
- XPath Injection

**SQL Injection Prevention**:
```sql
-- Vulnerable query
SELECT * FROM users WHERE username = '" + userInput + "'

-- Secure parameterized query
SELECT * FROM users WHERE username = ?
```

```javascript
// Using parameterized queries in Node.js
const getUserByUsername = async (username) => {
  const query = 'SELECT * FROM users WHERE username = ?';
  const result = await db.query(query, [username]);
  return result[0];
};
```

#### 4. Insecure Design
**Description**: Missing or ineffective control design
**Examples**:
- Lack of security requirements gathering
- Insufficient threat modeling
- Missing security architecture review
- Inadequate security testing

**Secure Design Principles**:
- Defense in depth
- Fail securely
- Least privilege principle
- Separation of duties
- Complete mediation

#### 5. Security Misconfiguration
**Description**: Missing appropriate security hardening
**Common Issues**:
- Default accounts and passwords
- Unnecessary features enabled
- Missing security headers
- Verbose error messages
- Outdated software components

**Security Headers Implementation**:
```javascript
// Express.js security headers
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  next();
});
```

### Authentication and Authorization

#### Multi-Factor Authentication (MFA)
**Factors**:
1. Something you know (password, PIN)
2. Something you have (token, phone, smart card)
3. Something you are (biometrics)

**Implementation Example**:
```javascript
const speakeasy = require('speakeasy');

// Generate TOTP secret
const generateSecret = (username) => {
  return speakeasy.generateSecret({
    name: `MyApp (${username})`,
    issuer: 'MyApp'
  });
};

// Verify TOTP token
const verifyToken = (token, secret) => {
  return speakeasy.totp.verify({
    secret: secret,
    encoding: 'base32',
    token: token,
    window: 2
  });
};
```

#### JSON Web Tokens (JWT) Security
**Best Practices**:
- Use strong signing algorithms (RS256, ES256)
- Implement proper token expiration
- Include necessary claims only
- Validate tokens on every request
- Use refresh token rotation

**Secure JWT Implementation**:
```javascript
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

// Generate JWT with proper security
const generateToken = (payload, privateKey) => {
  return jwt.sign(payload, privateKey, {
    algorithm: 'RS256',
    expiresIn: '15m',
    issuer: 'myapp.com',
    audience: 'myapp-users'
  });
};

// Verify JWT token
const verifyToken = (token, publicKey) => {
  try {
    return jwt.verify(token, publicKey, {
      algorithms: ['RS256'],
      issuer: 'myapp.com',
      audience: 'myapp-users'
    });
  } catch (error) {
    throw new Error('Invalid token');
  }
};
```

### Network Security

#### HTTPS and TLS Configuration
**TLS Best Practices**:
- Use TLS 1.2 or higher
- Implement proper certificate validation
- Use strong cipher suites
- Enable HTTP Strict Transport Security (HSTS)
- Implement certificate pinning for mobile apps

**Nginx TLS Configuration**:
```nginx
server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

#### Firewall and Network Segmentation
**Network Security Layers**:
1. Perimeter firewall (external threats)
2. Internal firewalls (network segmentation)
3. Host-based firewalls (individual systems)
4. Application-level filtering (WAF)

**Firewall Rule Example**:
```bash
# Allow HTTPS traffic
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow SSH from specific IP range
iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 22 -j ACCEPT

# Drop all other incoming traffic
iptables -A INPUT -j DROP
```

### Vulnerability Assessment

#### Common Vulnerability Types
**Input Validation Vulnerabilities**:
- Cross-Site Scripting (XSS)
- SQL Injection
- Command Injection
- Path Traversal
- XML External Entity (XXE)

**Authentication Vulnerabilities**:
- Weak password policies
- Session fixation
- Insecure password recovery
- Brute force attacks
- Credential stuffing

**Authorization Vulnerabilities**:
- Privilege escalation
- Insecure direct object references
- Missing function level access control
- Race conditions in access control

#### Vulnerability Scanning Tools
**Static Application Security Testing (SAST)**:
- SonarQube
- Checkmarx
- Veracode
- Semgrep

**Dynamic Application Security Testing (DAST)**:
- OWASP ZAP
- Burp Suite
- Nessus
- Qualys WAS

**Interactive Application Security Testing (IAST)**:
- Contrast Security
- Synopsys Seeker
- Checkmarx Interactive

### Incident Response

#### Incident Response Lifecycle
1. **Preparation**: Policies, procedures, tools, training
2. **Identification**: Detection and analysis of incidents
3. **Containment**: Short-term and long-term containment
4. **Eradication**: Remove threat from environment
5. **Recovery**: Restore systems to normal operation
6. **Lessons Learned**: Post-incident analysis and improvement

#### Incident Classification
**Severity Levels**:
- **Critical**: Complete system compromise, data breach
- **High**: Significant security impact, service disruption
- **Medium**: Limited security impact, minor service impact
- **Low**: Minimal security impact, no service disruption

**Response Time Objectives**:
- Critical: 1 hour
- High: 4 hours
- Medium: 24 hours
- Low: 72 hours

### Compliance and Frameworks

#### Security Frameworks
**NIST Cybersecurity Framework**:
1. Identify: Asset management, risk assessment
2. Protect: Access control, data security, training
3. Detect: Continuous monitoring, detection processes
4. Respond: Response planning, communications, analysis
5. Recover: Recovery planning, improvements, communications

**ISO 27001 Controls**:
- Information security policies
- Organization of information security
- Human resource security
- Asset management
- Access control
- Cryptography
- Physical and environmental security

#### Regulatory Compliance
**GDPR (General Data Protection Regulation)**:
- Data protection by design and default
- Consent management
- Data subject rights
- Breach notification requirements
- Privacy impact assessments

**PCI DSS (Payment Card Industry Data Security Standard)**:
- Build and maintain secure networks
- Protect cardholder data
- Maintain vulnerability management program
- Implement strong access control measures
- Regularly monitor and test networks

### Security Testing Methodologies

#### Penetration Testing Phases
1. **Reconnaissance**: Information gathering
2. **Scanning**: Port scanning, vulnerability identification
3. **Enumeration**: Service and system enumeration
4. **Exploitation**: Attempting to exploit vulnerabilities
5. **Post-Exploitation**: Privilege escalation, persistence
6. **Reporting**: Documentation of findings and recommendations

#### Security Code Review
**Manual Code Review Checklist**:
- Input validation and sanitization
- Authentication and session management
- Authorization and access control
- Error handling and logging
- Cryptographic implementations
- Configuration management

**Automated Code Analysis**:
```javascript
// Example of secure coding practices
const validateInput = (input, type) => {
  const validators = {
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    phone: /^\+?[\d\s\-\(\)]+$/,
    alphanumeric: /^[a-zA-Z0-9]+$/
  };
  
  if (!validators[type]) {
    throw new Error('Invalid validation type');
  }
  
  return validators[type].test(input);
};
```

## Training Exercises

### Exercise 1: Threat Modeling
**Task**: Conduct threat modeling for a web application
**Requirements**:
- Identify assets and entry points
- Create data flow diagrams
- Identify threats using STRIDE methodology
- Assess risk levels
- Recommend mitigation strategies

### Exercise 2: Vulnerability Assessment
**Task**: Perform security assessment of a sample application
**Requirements**:
- Automated vulnerability scanning
- Manual security testing
- Code review for security issues
- Risk assessment and prioritization
- Remediation recommendations

### Exercise 3: Incident Response Simulation
**Task**: Simulate security incident response
**Requirements**:
- Incident detection and analysis
- Containment and eradication procedures
- Communication and coordination
- Recovery and restoration
- Post-incident review and documentation

## Assessment Criteria

### Security Knowledge
- Understanding of security principles and concepts
- Knowledge of common vulnerabilities and threats
- Familiarity with security tools and techniques
- Awareness of compliance requirements

### Practical Skills
- Ability to identify security vulnerabilities
- Proficiency in security testing methodologies
- Experience with security tools and frameworks
- Incident response and handling capabilities

### Risk Assessment
- Threat identification and analysis
- Risk evaluation and prioritization
- Mitigation strategy development
- Business impact assessment

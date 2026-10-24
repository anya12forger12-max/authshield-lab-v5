export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export interface PasswordStrength {
  score: number;
  label: 'very-weak' | 'weak' | 'fair' | 'strong' | 'very-strong';
  feedback: string[];
}

export function validateEmail(email: string): ValidationResult {
  const errors: string[] = [];
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

  if (!email || email.trim().length === 0) {
    errors.push('Email is required');
  } else if (!emailRegex.test(email)) {
    errors.push('Please enter a valid email address');
  } else if (email.length > 254) {
    errors.push('Email address is too long');
  }

  return { valid: errors.length === 0, errors };
}

export function validatePassword(password: string): ValidationResult {
  const errors: string[] = [];

  if (!password) {
    errors.push('Password is required');
    return { valid: false, errors };
  }

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }
  if (password.length > 128) {
    errors.push('Password must be no more than 128 characters long');
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  if (!/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }

  const commonPasswords = ['password', 'password123', 'qwerty', '123456', 'admin', 'letmein', 'welcome'];
  if (commonPasswords.includes(password.toLowerCase())) {
    errors.push('This password is too common');
  }

  return { valid: errors.length === 0, errors };
}

export function validateUsername(username: string): ValidationResult {
  const errors: string[] = [];
  const usernameRegex = /^[a-zA-Z0-9_-]+$/;

  if (!username || username.trim().length === 0) {
    errors.push('Username is required');
  } else {
    if (username.length < 3) {
      errors.push('Username must be at least 3 characters long');
    }
    if (username.length > 32) {
      errors.push('Username must be no more than 32 characters long');
    }
    if (!usernameRegex.test(username)) {
      errors.push('Username can only contain letters, numbers, underscores, and hyphens');
    }
    if (/^[-_]/.test(username)) {
      errors.push('Username cannot start with a hyphen or underscore');
    }
  }

  return { valid: errors.length === 0, errors };
}

export function scorePasswordStrength(password: string): PasswordStrength {
  const feedback: string[] = [];
  let score = 0;

  if (!password) {
    return { score: 0, label: 'very-weak', feedback: ['Enter a password'] };
  }

  const length = password.length;
  if (length >= 8) score += 10;
  if (length >= 12) score += 15;
  if (length >= 16) score += 10;
  if (length >= 20) score += 5;

  if (/[a-z]/.test(password)) score += 10;
  else feedback.push('Add lowercase letters');
  if (/[A-Z]/.test(password)) score += 10;
  else feedback.push('Add uppercase letters');
  if (/\d/.test(password)) score += 10;
  else feedback.push('Add numbers');
  if (/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password)) score += 15;
  else feedback.push('Add special characters');

  const uniqueChars = new Set(password).size;
  const uniqueRatio = uniqueChars / length;
  if (uniqueRatio > 0.7) score += 10;
  else if (uniqueRatio > 0.5) score += 5;

  if (/(.)\1{2,}/.test(password)) {
    score -= 10;
    feedback.push('Avoid repeated characters');
  }

  if (/^(012|123|234|345|456|567|678|789|890)/.test(password) ||
      /^(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)/i.test(password)) {
    score -= 10;
    feedback.push('Avoid sequential characters');
  }

  const commonPatterns = ['password', 'qwerty', 'admin', 'letmein', 'welcome', 'monkey', 'dragon'];
  if (commonPatterns.some(p => password.toLowerCase().includes(p))) {
    score -= 20;
    feedback.push('Avoid common password patterns');
  }

  score = Math.max(0, Math.min(100, score));

  let label: PasswordStrength['label'] = 'very-weak';
  if (score >= 80) label = 'very-strong';
  else if (score >= 60) label = 'strong';
  else if (score >= 40) label = 'fair';
  else if (score >= 20) label = 'weak';

  return { score, label, feedback };
}

export function sanitizeInput(input: string): string {
  return input
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#x27;')
    .replace(/\//g, '&#x2F;')
    .trim();
}

export function validateRequired(value: unknown, fieldName: string): ValidationResult {
  const errors: string[] = [];
  if (value === null || value === undefined || (typeof value === 'string' && value.trim().length === 0)) {
    errors.push(`${fieldName} is required`);
  }
  return { valid: errors.length === 0, errors };
}

export function validateMinLength(value: string, min: number, fieldName: string): ValidationResult {
  const errors: string[] = [];
  if (value.length < min) {
    errors.push(`${fieldName} must be at least ${min} characters`);
  }
  return { valid: errors.length === 0, errors };
}

export function validateMaxLength(value: string, max: number, fieldName: string): ValidationResult {
  const errors: string[] = [];
  if (value.length > max) {
    errors.push(`${fieldName} must be no more than ${max} characters`);
  }
  return { valid: errors.length === 0, errors };
}

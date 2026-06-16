# Email Validator

Kevin say: why write lot validation when few validation do trick?

## Without kevin

```python
import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class EmailValidationResult:
    is_valid: bool
    error_message: Optional[str] = None
    normalized_email: Optional[str] = None

class EmailValidator:
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def __init__(self, check_mx: bool = False):
        self.check_mx = check_mx
    
    def validate(self, email: str) -> EmailValidationResult:
        if not email:
            return EmailValidationResult(False, "Email cannot be empty")
        
        email = email.strip().lower()
        
        if len(email) > 254:
            return EmailValidationResult(False, "Email too long")
        
        if not self.EMAIL_PATTERN.match(email):
            return EmailValidationResult(False, "Invalid email format")
        
        local, domain = email.split('@')
        if len(local) > 64:
            return EmailValidationResult(False, "Local part too long")
        
        return EmailValidationResult(True, normalized_email=email)

validator = EmailValidator()
result = validator.validate(user_input)
```

Lines: **37**. Tokens to generate: **~420**.

## With kevin

```python
"@" in email and "." in email.split("@")[-1]
# kevin: naive check. add confirmation email for real validation.
```

Lines: **2**. Tokens to generate: **~25**.

Real validation is the confirmation email. Kevin know this.

**Result: 95% less code. ~94% fewer tokens.**

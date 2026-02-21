class TokenManagerError(RuntimeError):
    """Base class for all token manager related errors."""
    pass

class TokenCacheError(TokenManagerError):
    """Raised when the token cache file is unreadable/corrupted."""
    pass

class RefreshTokenMissing(TokenManagerError):
    """Raised when refresh token file is missing or empty."""
    pass

class OAuthRefreshError(TokenManagerError):
    """Raised when Google OAuth refresh fails (401/400/network issues)."""
    pass

class TokenStoreError(RuntimeError): 
    """Base class for all token store related errors."""
    pass    
    
class TokenCacheCorrupted(TokenStoreError):
    """Raised when the token cache file is unreadable/corrupted.""" 
    pass
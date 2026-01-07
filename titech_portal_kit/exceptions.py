class TitechPortalLoginError(Exception):
    """Base exception for TitechPortal login errors."""
    pass

class InvalidPasswordPageHtmlError(TitechPortalLoginError):
    pass

class InvalidMatrixcodePageHtmlError(TitechPortalLoginError):
    pass

class InvalidResourceListPageHtmlError(TitechPortalLoginError):
    def __init__(self, current_matrices: list, html: str):
        self.current_matrices = current_matrices
        self.html = html
        super().__init__(f"Invalid resource list page. Matrices: {current_matrices}")

class NoMatrixcodeOptionError(TitechPortalLoginError):
    pass

class FailedCurrentMatrixParseError(TitechPortalLoginError):
    pass

class AlreadyLoggedinError(TitechPortalLoginError):
    pass

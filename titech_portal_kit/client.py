from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from .http_client import HTTPClientImpl
from .request_models import (
    BaseURL, 
    get_password_page_request, 
    get_password_submit_request,
    get_otp_select_submit_request,
    get_matrix_code_submit_request,
    get_resource_list_page_request
)
from .utils import (
    HTMLInput, HTMLSelect, TitechPortalMatrix,
    parse_html_input, parse_html_select, parse_current_matrices
)
from .exceptions import (
    InvalidPasswordPageHtmlError,
    InvalidMatrixcodePageHtmlError,
    InvalidResourceListPageHtmlError,
    NoMatrixcodeOptionError,
    FailedCurrentMatrixParseError,
    AlreadyLoggedinError
)

class TitechPortal:
    DEFAULT_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT, use_mock: bool = False):
        if use_mock:
            BaseURL.change_to_mock_server()
        self.http_client = HTTPClientImpl(user_agent=user_agent)

    def login(self, username: str, password: str, matrix_map: Optional[Dict[str, str]] = None):
        """
        matrix_map: dict mapping matrix key (e.g. "a1") to value. 
                    Can be constructed from TitechPortalMatrix enums if desired, 
                    but simple dict {"a1": "x", ...} is easier for Python users.
        """
        password_page_html = self._fetch_password_page()
        
        if not self._validate_password_page(password_page_html):
            raise InvalidPasswordPageHtmlError()
            
        password_page_inputs = parse_html_input(password_page_html)
        
        password_page_submit_html = self._submit_password(password_page_inputs, username, password)
        
        if self._validate_resource_list_page(password_page_submit_html):
             raise AlreadyLoggedinError()
             
        matrix_code_page_html = ""
        
        if self._validate_otp_page(password_page_submit_html):
             otp_inputs = parse_html_input(password_page_submit_html)
             otp_selects = parse_html_select(password_page_submit_html)
             
             has_matrix_option = False
             for sel in otp_selects:
                 if "GridAuthOption" in sel.values:
                     has_matrix_option = True
                     break
             
             if not has_matrix_option:
                 raise NoMatrixcodeOptionError()
                 
             for sel in otp_selects:
                 sel.select("GridAuthOption")
                 
             matrix_code_page_html = self._submit_otp_select(otp_inputs, otp_selects)
        else:
             matrix_code_page_html = password_page_submit_html
             
        if not self._validate_matrix_code_page(matrix_code_page_html):
            raise InvalidMatrixcodePageHtmlError()
            
        matrix_inputs = parse_html_input(matrix_code_page_html)
        current_matrices = parse_current_matrices(matrix_code_page_html)
        matrix_selects = parse_html_select(matrix_code_page_html)
        
        if not matrix_map:
             raise ValueError("Matrix authentication required but no matrix code map provided.")
        
        final_html = self._submit_matrix_code(
            matrix_inputs, matrix_selects, current_matrices, matrix_map
        )
        
        if not self._validate_resource_list_page(final_html):
            raise InvalidResourceListPageHtmlError(current_matrices, final_html)

    def check_username_password(self, username: str, password: str) -> bool:
        """
        Checks if username and password are correct. 
        Returns True if login creds are accepted (even if further auth is needed).
        """
        password_page_html = self._fetch_password_page()
        
        if not self._validate_password_page(password_page_html):
            raise InvalidPasswordPageHtmlError()
            
        password_page_inputs = parse_html_input(password_page_html)
        
        password_page_submit_html = self._submit_password(password_page_inputs, username, password)

        return self._validate_otp_page(password_page_submit_html) or \
               self._validate_matrix_code_page(password_page_submit_html)

    def fetch_current_matrix(self, username: str, password: str) -> List[TitechPortalMatrix]:
        """
        Logs in partially to fetch the required matrix cells.
        """
        password_page_html = self._fetch_password_page()
        
        if not self._validate_password_page(password_page_html):
            raise InvalidPasswordPageHtmlError()
            
        password_page_inputs = parse_html_input(password_page_html)
        
        password_page_submit_html = self._submit_password(password_page_inputs, username, password)

        if self._validate_resource_list_page(password_page_html):
             raise AlreadyLoggedinError()

        matrix_code_page_html = ""
        
        if self._validate_otp_page(password_page_submit_html):
             otp_inputs = parse_html_input(password_page_submit_html)
             otp_selects = parse_html_select(password_page_submit_html)
             
             has_matrix_option = False
             for sel in otp_selects:
                 if "GridAuthOption" in sel.values:
                     has_matrix_option = True
                     break
             
             if not has_matrix_option:
                 raise NoMatrixcodeOptionError()
                 
             for sel in otp_selects:
                 sel.select("GridAuthOption")
                 
             matrix_code_page_html = self._submit_otp_select(otp_inputs, otp_selects)
        else:
             matrix_code_page_html = password_page_submit_html
             
        if not self._validate_matrix_code_page(matrix_code_page_html):
            raise InvalidMatrixcodePageHtmlError()
            
        return parse_current_matrices(matrix_code_page_html)

    def _fetch_password_page(self) -> str:
        req = get_password_page_request()
        return self.http_client.send(req)

    def _validate_password_page(self, html: str) -> bool:
        return "Please input your account & password." in html

    def _submit_password(self, inputs: List[HTMLInput], username: str, password: str) -> str:
        injected = self._inject_user_pass(inputs, username, password)
        req = get_password_submit_request(injected)
        return self.http_client.send(req)

    def _inject_user_pass(self, inputs: List[HTMLInput], username: str, password: str) -> List[HTMLInput]:
        first_text = next((i for i in inputs if i.type == 'text'), None)
        first_pass = next((i for i in inputs if i.type == 'password'), None)
        
        if not first_text or not first_pass:
            return inputs
            
        new_inputs = []
        for inp in inputs:
            if inp is first_text:
                new_inp = HTMLInput(inp.name, inp.type, username)
                new_inputs.append(new_inp)
            elif inp is first_pass:
                new_inp = HTMLInput(inp.name, inp.type, password)
                new_inputs.append(new_inp)
            else:
                new_inputs.append(inp)
        return new_inputs

    def _validate_resource_list_page(self, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else ""
        return "リソース メニュー" in (title or "")

    def _validate_otp_page(self, html: str) -> bool:
        soup = BeautifulSoup(html, "html.parser")
        body = soup.body
        body_html = body.decode_contents() if body else ""
        return (
            "Select Label for OTP" in body_html
            or "Enter Token Dynamic Password" in body_html
        )

    def _submit_otp_select(self, inputs: List[HTMLInput], selects: List[HTMLSelect]) -> str:
        req = get_otp_select_submit_request(inputs, selects)
        return self.http_client.send(req)

    def _validate_matrix_code_page(self, html: str) -> bool:
        return "Matrix Authentication" in html

    def _submit_matrix_code(self, 
                            inputs: List[HTMLInput], 
                            selects: List[HTMLSelect], 
                            required_matrices: List[TitechPortalMatrix], 
                            matrix_map: Dict[str, str]) -> str:
        injected_inputs = self._inject_matrix(inputs, required_matrices, matrix_map)
        
        injected_selects = []
        for sel in selects:
             if "NoOtherIGAuthOption" in sel.values:
                 s = HTMLSelect(sel.name, sel.values, "NoOtherIGAuthOption")
                 injected_selects.append(s)
             else:
                 injected_selects.append(sel)
                 
        req = get_matrix_code_submit_request(injected_inputs, injected_selects)
        return self.http_client.send(req)

    def _inject_matrix(self, 
                       inputs: List[HTMLInput], 
                       required_matrices: List[TitechPortalMatrix], 
                       matrix_map: Dict[str, str]) -> List[HTMLInput]:
        if not required_matrices:
            return inputs
            
        new_inputs = []
        matrix_idx = 0
        
        for inp in inputs:
            if inp.type == 'password':
                if matrix_idx < len(required_matrices):
                    # required_matrices contains TitechPortalMatrix Enum
                    # We need the VALUE of the enum if matrix_map uses enum values as keys (e.g. "a1")
                    # TitechPortalMatrix.A1.value is "a1"
                    matrix_key = required_matrices[matrix_idx].value 
                    val = matrix_map.get(matrix_key, "")
                    new_inputs.append(HTMLInput(inp.name, inp.type, val))
                    matrix_idx += 1
                else:
                    new_inputs.append(inp)
            else:
                new_inputs.append(inp)
                
        return new_inputs

    def is_logged_in(self) -> bool:
        # Note: In Swift this is async. Here synchronous implies blocking.
        req = get_resource_list_page_request()
        try:
             code = self.http_client.status_code(req)
             return code == 200
        except:
             return False

class ElementAnalyzer:
    def __init__(self, keywords, oauth_providers):
        self.keywords = keywords
        self.oauth_providers = oauth_providers

    def analyze_element(self, element):
        """Analyze the element to determine its relevance."""
        element_str = str(element).lower()
        score = 0

        # Increase score for keyword matches
        if any(keyword in element_str for keyword in self.keywords):
            score += 1

        # Increase score for OAuth buttons or links
        if element.name in ["a", "button", "div"] and any(keyword in element_str for keyword in self.oauth_providers):
            score += 2

        # Return the element with its calculated score
        return {'element': element, 'score': score}


class FormAnalyzer:
    def __init__(self, soup):
        self.soup = soup

    def extract_forms(self):
        """Extract forms along with their input elements and buttons."""
        forms = self.soup.find_all('form')
        form_data = []
        for form in forms:
            form_inputs = form.find_all(['input', 'button', 'select', 'textarea'])
            form_details = {
                'form_html': str(form),
                'fields': [{'tag': input_.name, 'attributes': dict(input_.attrs), 'html': str(input_)} for input_ in
                           form_inputs]
            }
            form_data.append(form_details)
        return form_data

    def extract_login_form(self):
        """Heuristically identify the most likely login form based on its fields."""
        forms = self.extract_forms()
        login_form = None
        highest_score = 0
        for form in forms:
            form_score = self._calculate_form_score(form['fields'])
            if form_score > highest_score:
                highest_score = form_score
                login_form = form
        return login_form

    @staticmethod
    def _calculate_form_score(fields):
        """Calculate a heuristic score for form fields to determine if it is a login form."""
        score = 0
        for field in fields:
            if 'type' in field['attributes'] and field['attributes']['type'] == 'password':
                score += 2
            if any(keyword in field['attributes'].get('name', '').lower() for keyword in
                   ['username', 'email', 'login']):
                score += 1
        return score

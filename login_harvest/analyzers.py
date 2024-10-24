class ElementAnalyzer:
    def __init__(self, keywords, oauth_providers):
        self.keywords = keywords
        self.oauth_providers = oauth_providers

    def analyze_element(self, element):
        """Analyze the element to determine its relevance and assign a score."""
        element_str = str(element).lower()
        score = 0

        # Increase score based on keyword matches
        score += self._score_keywords(element_str)

        # Increase score for OAuth buttons or links
        score += self._score_oauth(element_str, element)

        # Return the element with its calculated score
        return {'element': element, 'score': score}

    def _score_keywords(self, element_str):
        """Calculate score based on general login keywords."""
        score = 0
        if any(keyword in element_str for keyword in self.keywords):
            score += 1
        return score

    def _score_oauth(self, element_str, element):
        """Calculate score based on the presence of OAuth providers."""
        score = 0
        if element.name in ["a", "button", "div"] and any(oauth in element_str for oauth in self.oauth_providers):
            score += 2
        return score


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
                'fields': [
                    {
                        'tag': input_.name,
                        'attributes': dict(input_.attrs),
                        'html': str(input_)
                    } for input_ in form_inputs
                ]
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
            attributes = field['attributes']
            # Increase score for password fields
            if 'type' in attributes and attributes['type'] == 'password':
                score += 3
            # Increase score for username or email fields
            if any(keyword in attributes.get('name', '').lower() for keyword in ['username', 'email', 'login']):
                score += 2
            # Increase score if the element is an input related to OAuth or has specific attributes
            if 'value' in attributes and any(word in attributes['value'].lower() for word in ['login', 'signin']):
                score += 1
        return score

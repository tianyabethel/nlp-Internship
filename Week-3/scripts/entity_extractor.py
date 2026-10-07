import re


class EntityExtractor:

    def extract_bedrooms(self, text):
        if not text:
            return None

        patterns = [
            r"(\d+)\s*(?:bed|br|bedroom)s?\b",
            r"(\d+)\s*bd\b"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.I)

            if match:
                return int(match.group(1))

        return None

    def extract_bathrooms(self, text):
        if not text:
            return None

        patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:bath|ba|bathroom)s?\b"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.I)

            if match:
                return float(match.group(1))

        return None

    def extract_price(self, text):
        if not text:
            return None

        match = re.search(r"\$?(\d{1,3}(?:,\d{3})+|\d{5,})", text)

        if match:
           return int(match.group(1).replace(",", ""))


        return None

    def extract_sqft(self, text):
        if not text:
            return None

        patterns = [
            r"(\d[\d,]*)\s*square feet",
            r"(\d[\d,]*)\s*sqft",
            r"(\d[\d,]*)\s*sq\.?\s*ft\.?",
            r"(\d[\d,]*)\s*sf"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.I)

            if match:
                return int(match.group(1).replace(",", ""))

        return None

    def extract_amenities(self, text):
        if not text:
            return []

        amenities = [
            "fireplace",
            "granite countertops",
            "garage",
            "central air",
            "walk-in closet",
            "hardwood floors",
            "pool",
            "hot tub",
            "balcony",
            "patio",
            "deck",
            "vaulted ceilings",
            "mountain views"
        ]

        found = []

        for amenity in amenities:
            if re.search(r"\b" + re.escape(amenity) + r"\b", text, re.I):
                found.append(amenity)

        return found

    def extract_all(self, text):
        return {
            "bedrooms": self.extract_bedrooms(text),
            "bathrooms": self.extract_bathrooms(text),
            "price": self.extract_price(text),
            "sqft": self.extract_sqft(text),
            "amenities": self.extract_amenities(text)
        }
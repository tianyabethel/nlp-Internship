import re


class QueryParser:
    ALLOWED_CITIES = {
        "irvine", "anaheim", "tustin", "santa ana",
        "orange", "fullerton", "costa mesa", "newport beach",
        "huntington beach", "garden grove", "mission viejo",
        "laguna niguel", "westminster", "buena park",
        "fountain valley", "yorba linda", "brea"
    }

    ALLOWED_AMENITIES = {
        "fireplace", "granite countertops", "garage",
        "central air", "walk-in closet", "hardwood floors",
        "pool", "hot tub", "balcony", "patio", "deck",
        "vaulted ceilings", "mountain views", "garden"
    }

    def parse(self, query):
        filters = {}
        text = query.lower()

        # Price range
        match = re.search(
            r"between\s+\$?([\d,.]+)\s*([km]?)\s+and\s+\$?([\d,.]+)\s*([km]?)",
            text
        )

        if match:
            filters["price_min"] = self._parse_number(
                match.group(1), match.group(2)
            )
            filters["price_max"] = self._parse_number(
                match.group(3), match.group(4)
            )
        else:
            # Minimum and maximum prices
            price_patterns = [
                (r"under\s+\$?([\d,.]+)\s*([km]?)", "price_max"),
                (r"below\s+\$?([\d,.]+)\s*([km]?)", "price_max"),
                (r"less than\s+\$?([\d,.]+)\s*([km]?)", "price_max"),
                (r"over\s+\$?([\d,.]+)\s*([km]?)", "price_min"),
                (r"above\s+\$?([\d,.]+)\s*([km]?)", "price_min"),
                (r"more than\s+\$?([\d,.]+)\s*([km]?)", "price_min"),
            ]

            for pattern, key in price_patterns:
                match = re.search(pattern, text)
                if match:
                    filters[key] = self._parse_number(
                        match.group(1), match.group(2)
                    )
                    break

        # Bedrooms
        match = re.search(
            r"(\d+)\s*\+?\s*(?:bedrooms?|beds?|br)\b", text
        )
        if match:
            filters["bedrooms"] = int(match.group(1))

        # Bathrooms
        match = re.search(
            r"(\d+)\s*(?:bathrooms?|baths?|ba)\b", text
        )
        if match:
            filters["bathrooms"] = int(match.group(1))

        # City: only recognize configured cities
        for city in sorted(self.ALLOWED_CITIES, key=len, reverse=True):
            if re.search(r"\bin\s+" + re.escape(city) + r"\b", text):
                filters["city"] = city
                break

        # Amenities and exclusions
        for amenity in sorted(self.ALLOWED_AMENITIES, key=len, reverse=True):
            escaped = re.escape(amenity)

            excluded = re.search(
                r"\b(?:without|no)\s+" + escaped + r"\b", text
            )

            if excluded:
                filters.setdefault("amenities_not", []).append(amenity)
            elif re.search(r"\b" + escaped + r"\b", text):
                filters.setdefault("amenities", []).append(amenity)

        return filters

    @staticmethod
    def _parse_number(number, suffix):
        value = float(number.replace(",", ""))

        if suffix == "k":
            value *= 1_000
        elif suffix == "m":
            value *= 1_000_000

        return int(value)

    def validate(self, filters):
        errors = []

        if "city" in filters and filters["city"] not in self.ALLOWED_CITIES:
            errors.append("Invalid city")

        for key in ("price_min", "price_max"):
            if key in filters and not 0 < filters[key] <= 100_000_000:
                errors.append(f"{key} is out of range")

        for key in ("bedrooms", "bathrooms"):
            if key in filters and not 0 <= filters[key] <= 20:
                errors.append(f"{key} is out of range")

        if (
            "price_min" in filters
            and "price_max" in filters
            and filters["price_min"] > filters["price_max"]
        ):
            errors.append("Minimum price cannot exceed maximum price")

        for key in ("amenities", "amenities_not"):
            for amenity in filters.get(key, []):
                if amenity not in self.ALLOWED_AMENITIES:
                    errors.append(f"Invalid amenity: {amenity}")

        if set(filters.get("amenities", [])) & set(
            filters.get("amenities_not", [])
        ):
            errors.append("An amenity cannot be both required and excluded")

        return errors

    def to_sql(self, filters):
        errors = self.validate(filters)

        if errors:
            raise ValueError("; ".join(errors))

        conditions = []
        params = []

        # Only fixed, trusted column names are used in SQL.
        columns = {
            "price_min": ("L_SystemPrice", ">="),
            "price_max": ("L_SystemPrice", "<="),
            "bedrooms": ("L_Keyword2", "="),
            "bathrooms": ("LM_Dec_3", "="),
            "city": ("L_City", "="),
        }

        for key, (column, operator) in columns.items():
            if key in filters:
                conditions.append(f"{column} {operator} %s")
                params.append(filters[key])

        # Amenities are searched in the listing remarks.
        for amenity in filters.get("amenities", []):
            conditions.append("L_Remarks LIKE %s")
            params.append(f"%{amenity}%")

        for amenity in filters.get("amenities_not", []):
            conditions.append("L_Remarks NOT LIKE %s")
            params.append(f"%{amenity}%")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        sql = f"SELECT * FROM rets_property WHERE {where_clause}"
        return sql, params

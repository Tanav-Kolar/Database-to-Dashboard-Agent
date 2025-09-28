#readonly-validator.py
class ReadOnlyValidator:
    """
    A simple validator to ensure that only read-only SQL queries are executed.
    This is a critical security measure to prevent the LLM from generating
    and executing destructive queries.
    """

    # A set of forbidden SQL keywords. Using a set for efficient lookup.
    # These are commands that modify or delete data or database structures.
    FORBIDDEN_KEYWORDS = {
        "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE",
        "GRANT", "REVOKE", "COMMIT", "ROLLBACK", "MERGE"
    }

    @staticmethod
    def is_readonly(sql_query: str) -> bool:
        """
        Checks if a given SQL query is read-only.

        Args:
            sql_query: The SQL query string to validate.

        Returns:
            True if the query is read-only (safe), False otherwise.
        """
        if not isinstance(sql_query, str) or not sql_query.strip():
            # Handle cases where the input is not a string or is empty.
            return False

        # Convert the query to uppercase to make the check case-insensitive.
        query_upper = sql_query.upper()

        # Check if any forbidden keyword exists in the query. We check for them as whole words to avoid false positives (e.g., a column named 'deleted').
        # We split the query by spaces and common punctuation.
        import re
        words = re.split(r'[\s;(),]+', query_upper)

        for word in words:
            if word in ReadOnlyValidator.FORBIDDEN_KEYWORDS:
                print(f"Validation failed: Found forbidden keyword '{word}' in the query.")
                return False

        # If no forbidden keywords were found, the query is considered safe.
        return True
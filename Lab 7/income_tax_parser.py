"""
Lab 7: Fuzzing for Input Validation Bugs
Module: income_tax_parser.py

Hardened against malformed, missing, unexpected, and edge-case inputs
discovered through Hypothesis property-based fuzz testing.
"""


def clean_pan(pan):
    """
    Removes whitespace from a PAN string and converts it to uppercase.
    Safely handles None, non-string types, and empty inputs without crashing.
    """
    if pan is None:
        return ""
    if not isinstance(pan, str):
        pan = str(pan)
    return "".join(pan.split()).upper()


def parse_amount(text):
    """
    Converts a currency amount string (e.g. 'Rs 12,50,000', '₹12,50,000') into an integer.
    Safely handles None, numeric types, currency prefixes ('Rs', 'Rs.', '₹', 'INR'),
    commas, malformed strings, and empty inputs without crashing.
    Returns 0 if the amount cannot be parsed.
    """
    if text is None:
        return 0
    if isinstance(text, (int, float)):
        try:
            return int(text)
        except (ValueError, OverflowError):
            return 0
    if not isinstance(text, str):
        return 0

    cleaned = text.strip()
    # Remove common Indian currency symbols and abbreviations
    cleaned = cleaned.replace("Rs.", "").replace("rs.", "")
    cleaned = cleaned.replace("Rs", "").replace("rs", "").replace("RS", "")
    cleaned = cleaned.replace("₹", "").replace("INR", "").replace("inr", "")
    cleaned = cleaned.replace(",", "").replace(" ", "")

    try:
        return int(cleaned)
    except (ValueError, TypeError, OverflowError):
        return 0


def parse_tax_slab(line):
    """
    Parses a tax slab string 'LOW-HIGH:RATE' into a (low, high, rate) tuple.
    Safely handles None, non-string, malformed, negative, and empty inputs
    without crashing. Returns (0, 0, 0) if parsing fails.
    """
    if line is None or not isinstance(line, str):
        return (0, 0, 0)

    try:
        parts = line.strip().split(":")
        if len(parts) != 2:
            return (0, 0, 0)

        limits_str, rate_str = parts[0].strip(), parts[1].strip()
        rate = int(rate_str.replace("%", "").strip())

        limit_parts = limits_str.split("-")
        if len(limit_parts) == 2:
            low = int(limit_parts[0].strip().replace(",", ""))
            high = int(limit_parts[1].strip().replace(",", ""))
        elif len(limit_parts) == 3 and limits_str.startswith("-"):
            low = -int(limit_parts[1].strip().replace(",", ""))
            high = int(limit_parts[2].strip().replace(",", ""))
        else:
            return (0, 0, 0)

        return (low, high, rate)
    except (ValueError, TypeError, OverflowError):
        return (0, 0, 0)


def main():
    print("==== Running clean_pan ====")
    value = input("Enter a PAN (e.g. abcde 1234f): ")
    print("Cleaned PAN:", clean_pan(value))

    print("\n==== Running parse_amount ====")
    value = input("Enter an amount (e.g. Rs 12,50,000): ")
    print("Amount in rupees:", parse_amount(value))

    print("\n==== Running parse_tax_slab ====")
    value = input("Enter a tax slab as LOW-HIGH:RATE (e.g. 250000-500000:5): ")
    print("Tax slab (low, high, rate):", parse_tax_slab(value))


if __name__ == "__main__":
    main()

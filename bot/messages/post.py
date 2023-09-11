from loader import _


def get_asking_for_url_buttons_text() -> str:
    """Returns asking for URL buttons message text."""
    return _(
        "Send me list of URL buttons in one message. "
        "Please, follow this format:\n\n"
        "Button text 1 - <code>https://example1.com</code>\n"
        "Button text 2 - <code>https://example2.com</code>\n\n"
        "Use separator '|' to add up to 3 buttons to one row.\n\n"
        "Example:\n\n"
        "Button text 1 - <code>https://example1.com</code> | "
        "Button text 2 - <code>https://example2.com</code>\n"
        "Button text 3 - <code>https://example3.com</code> | "
        "Button text 4 - <code>https://example4.com</code>\n\n"
        "Click the back button to cancel and return to content adding."
    )

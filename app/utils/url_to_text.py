from trafilatura import fetch_url, extract
import validators


def url_to_text(url):
    url_validation = validators.url(url)

    if not url_validation:
        raise NameError('Invalid URL provided. Cant extract text.')
        return ""

    document = fetch_url(url)
    text = extract(document)
    return text
    # Return data for use in future steps
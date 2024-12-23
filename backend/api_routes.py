from flask import Flask, jsonify, request, abort, render_template
import random
import json

api = Flask(__name__)

# Load the quotes data from the updated quotes.json with quote_size
with open('quotes.json', 'r', encoding='utf-8') as file:
    quotes = json.load(file)
    
# Load valid API keys
with open('keys.json', 'r', encoding='utf-8') as file:
    api_keys_data = json.load(file)
    # Update to use the "users" key to extract valid API keys
    VALID_API_KEYS = {key["api_key"]: key for key in api_keys_data["users"]}

def require_api_key():
    """Utility function to validate API key."""
    api_key = request.args.get('api')
    if api_key not in VALID_API_KEYS:
        abort(403, description="Invalid or missing API key")

    # Check usage limit
    key_data = VALID_API_KEYS[api_key]
    if key_data["usage_limit"] <= 0:
        abort(403, description="API key usage limit exceeded")
    key_data["usage_limit"] -= 1

    # Save updated keys data back to keys.json
    with open('keys.json', 'w', encoding='utf-8') as file:
        json.dump({"users": list(VALID_API_KEYS.values())}, file, ensure_ascii=False, indent=4)

@api.route('/quotes', methods=['GET'])
def get_quotes():
    #require_api_key()
    # Get query parameters
    api = request.args.get('api', None)  # Placeholder for an additional parameter if needed
    qn = min(int(request.args.get('qn', 1)), 10)  # Max 10 quotes at a time and Number of quotes required, default is 1
    qs = request.args.get('qs', 'small').lower()  # Quote size, default is 'small'
    tag = request.args.get('tag', None)  # Tag filter, default is None

    # Filter quotes by tag if provided
    filtered_quotes = quotes
    if tag:
        filtered_quotes = [quote for quote in filtered_quotes if tag.lower() in [t.lower() for t in quote['tags']]]

    # Filter quotes by quote_size
    filtered_quotes = [quote for quote in filtered_quotes if quote.get('quote_size', '').lower() == qs]

    # Slice the list to get the specified number of quotes
    selected_quotes = filtered_quotes[:qn]

    return jsonify(selected_quotes)

@api.route('/quotes/random', methods=['GET'])
def random_quote():
    #require_api_key()
    # Get query parameters
    tag_filter = request.args.get('tag', None)
    qs = request.args.get('qs', 'small').lower()  # Quote size, default is 'small'

    filtered_quotes = quotes

    # Filter quotes by tag if specified
    if tag_filter:
        filtered_quotes = [quote for quote in filtered_quotes if tag_filter.lower() in [tag.lower() for tag in quote["tags"]]]

    # Filter quotes by quote_size
    filtered_quotes = [quote for quote in filtered_quotes if quote.get('quote_size', '').lower() == qs]

    # Return a single random quote
    return jsonify(random.choice(filtered_quotes) if filtered_quotes else {"error": "No matching quotes found"})

@api.route('/quotes/<int:count>', methods=['GET'])
def multiple_quotes(count):
    # Get query parameters
    tag_filter = request.args.get('tag', None)
    qs = request.args.get('qs', 'small').lower()  # Quote size, default is 'small'

    filtered_quotes = quotes

    # Filter quotes by tag if specified
    if tag_filter:
        filtered_quotes = [quote for quote in filtered_quotes if tag_filter.lower() in [tag.lower() for tag in quote["tags"]]]

    # Filter quotes by quote_size
    filtered_quotes = [quote for quote in filtered_quotes if quote.get('quote_size', '').lower() == qs]

    # Return the requested number of quotes (or all if fewer than requested)
    return jsonify(random.sample(filtered_quotes, min(count, len(filtered_quotes))) if filtered_quotes else {"error": "No matching quotes found"})

if __name__ == '__main__':
    api.run()

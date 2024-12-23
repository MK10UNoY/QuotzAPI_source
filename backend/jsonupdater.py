import json

# Load the existing quotes JSON data
with open('quotes.json', 'r', encoding='utf-8') as file:
    quotes = json.load(file)

# Define the length thresholds
short_threshold = 50   # Less than 50 characters is short
medium_threshold = 100  # Less than 100 characters but more than 50 is medium
long_threshold = 100  # More than 100 characters is long

# Classify the quotes based on length and add 'quote_size'
for quote in quotes:
    quote_length = len(quote['quote'])
    
    # Determine the size category and add 'quote_size' to each quote
    if quote_length < short_threshold:
        quote['quote_size'] = 'short'
    elif short_threshold <= quote_length < medium_threshold:
        quote['quote_size'] = 'medium'
    else:
        quote['quote_size'] = 'long'

# Save the updated quotes with the new 'quote_size' attribute to the original file
with open('quotes_2.json', 'w', encoding='utf-8') as outfile:
    json.dump(quotes, outfile, ensure_ascii=False, indent=4)

# Print the number of each type of quote
short_count = sum(1 for quote in quotes if quote['quote_size'] == 'short')
medium_count = sum(1 for quote in quotes if quote['quote_size'] == 'medium')
long_count = sum(1 for quote in quotes if quote['quote_size'] == 'long')

print(f"Number of short quotes: {short_count}")
print(f"Number of medium quotes: {medium_count}")
print(f"Number of long quotes: {long_count}")

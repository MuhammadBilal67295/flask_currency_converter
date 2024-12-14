from flask import Flask, render_template, request, jsonify
import requests


class OpenExchangeRatesAPI:
    """Handles currency exchange rate fetching and supported currencies."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openexchangerates.org/api"
    
    def get_supported_currencies(self):
        """Fetch all supported currencies."""
        try:
            url = f"{self.base_url}/currencies.json"
            response = requests.get(url)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching supported currencies: {e}")
            return None
    
    def get_exchange_rate(self, base_currency, target_currency):
        """Fetch the exchange rate for the given currencies."""
        base_currency = 'USD'
        try:
            url = f"{self.base_url}/latest.json?app_id={self.api_key}&base={base_currency}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data['rates'].get(target_currency, None)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchange rate: {e}")
            return None


app = Flask(__name__)


# Initialize the API class
open_exchange_api = OpenExchangeRatesAPI("YOUR_API_KEY")  # Replace with your API key


@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')


@app.route('/currencies', methods=['GET'])
def get_currencies():
    """Return the list of supported currencies."""
    currencies = open_exchange_api.get_supported_currencies()
    if currencies:
        return jsonify({'success': True, 'currencies': currencies})
    else:
        return jsonify({'success': False, 'message': 'Unable to fetch currency list.'})


@app.route('/convert', methods=['POST'])
def convert_currency():
    """Convert the currency."""
    try:
        base_currency = request.form['base_currency'].upper()
        target_currency = request.form['target_currency'].upper()
        amount = float(request.form['amount'])
        
        if not base_currency or not target_currency or amount <= 0:
            return jsonify({'success': False, 'message': 'Invalid input data.'})
        
        exchange_rate = open_exchange_api.get_exchange_rate(base_currency, target_currency)
        if exchange_rate:
            converted_amount = amount * exchange_rate
            return jsonify({
                'success': True,
                'converted_amount': round(converted_amount, 2),
                'rate': round(exchange_rate, 4)
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid currencies or error fetching exchange rate.'})
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid amount entered. Please enter a valid number.'})
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'})


if __name__ == '__main__':
    app.run()  

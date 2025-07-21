import os
import json
from datetime import datetime
import requests
from ddgs import DDGS
import wikipedia
from datetime import datetime
from tradingview_ta import TA_Handler

EVENTS_FILE = os.path.join(os.getcwd(), "./asets/events.json")
 
def per_diff(num1: float, num2: float) -> float:
    return ((num1 - num2) / num2) * 100

def get_stock_data(symbol: str) -> dict:
    """
    Fetch technical indicators for a stock listed under NSE india along with explanations for each.

    Args:
        symbol (str): Stock symbol (e.g., "RELIANCE", "TCS")

    Returns:
        dict: {
            "success": bool,
            "data": dict | None,
            "message": str
        }
    """
    try:
        handler = TA_Handler(
            symbol=symbol,
            screener="india",
            exchange="NSE",
            interval="1d"
        )
        indicators = [
            "close", "change", "RSI", "high", "low", "open", "volume",
            "ADX", "ATR", "EMA20", "EMA50", "EMA200",
            "price_52_week_low", "price_52_week_high"
        ]
        data = handler.get_indicators(indicators=indicators)
        analysis = handler.get_analysis()
        summary = analysis.summary["RECOMMENDATION"] if analysis else None

        close = data["close"]
        technical_fields = {
            "close": "Last traded price of the stock.",
            "change": "Percentage change from the previous closing price.",
            "RSI": "Relative Strength Index (0-100). >70 = overbought, <30 = oversold.",
            "high": "Highest price traded during the day.",
            "low": "Lowest price traded during the day.",
            "open": "Opening price of the stock for the day.",
            "volume": "Total number of shares traded today.",
            "ADX": "Average Directional Index. >25 indicates a strong trend.",
            "ATR": "Average True Range. Measures daily price volatility.",
            "EMA20": "Percent difference from the 20-day EMA. Shows short-term trend.",
            "EMA50": "Percent difference from the 50-day EMA. Mid-term trend signal.",
            "EMA200": "Percent difference from the 200-day EMA. Long-term trend strength.",
            "week_low_52": "Percent difference from the 52-week low. Indicates how far the price has moved up.",
            "week_high_52": "Percent difference from the 52-week high. Indicates how close the price is to its peak.",
            "summary": "Overall technical recommendation from TradingView."
        }

        main_data = {
            "close": {"value": round(close, 2), "explanation": technical_fields["close"]},
            "change": {"value": round(data["change"], 2), "explanation": technical_fields["change"]},
            "RSI": {"value": round(data["RSI"], 2), "explanation": technical_fields["RSI"]},
            "high": {"value": round(data["high"], 2), "explanation": technical_fields["high"]},
            "low": {"value": round(data["low"], 2), "explanation": technical_fields["low"]},
            "open": {"value": round(data["open"], 2), "explanation": technical_fields["open"]},
            "volume": {"value": data["volume"], "explanation": technical_fields["volume"]},
            "ADX": {"value": round(data["ADX"], 2), "explanation": technical_fields["ADX"]},
            "ATR": {"value": round(data["ATR"], 2), "explanation": technical_fields["ATR"]},
            "EMA20": {"value": round(per_diff(close, data["EMA20"]), 2), "explanation": technical_fields["EMA20"]},
            "EMA50": {"value": round(per_diff(close, data["EMA50"]), 2), "explanation": technical_fields["EMA50"]},
            "EMA200": {"value": round(per_diff(close, data["EMA200"]), 2), "explanation": technical_fields["EMA200"]},
            "week_low_52": {"value": round(per_diff(close, data["price_52_week_low"]), 2), "explanation": technical_fields["week_low_52"]},
            "week_high_52": {"value": round(per_diff(close, data["price_52_week_high"]), 2), "explanation": technical_fields["week_high_52"]},
            "summary": {"value": summary, "explanation": technical_fields["summary"]}
        }

        return {
            "success": True,
            "data": main_data,
            "message": "Technical data fetched successfully"
        }

    except Exception as e:
        print(e)
        return {
            "success": False,
            "data": None,
            "message": "Error while fetching data: " + str(e)
        }

def get_current_time() -> str:
    """
    Returns the current time in HH:MM:SS format.

    Example:
        print(get_current_time())  # "14:35:07"
    """
    return datetime.now().strftime("%H:%M:%S")

def get_current_date() -> str:
    """
    Returns the current date in YYYY-MM-DD format.

    Example:
        print(get_current_date())  # "2025-07-20"
    """
    return datetime.now().strftime("%d:%m:%Y")

def get_current_weather(city:str)->str:
    """
    Get's the current weather and returns the response text.
    Args:
        str: The name of the city.
    Returns:
        str: The raw text content of the weather information or the error message.
    """

    url = f"https://wttr.in/{city.lower()}?format=2"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather: {e}"


def send_message_to_user(subject: str, content: str) -> str:
    """
    Send a personal notification message to yourself via ntfy.sh.

    Args:
        subject (str): The subject or title of the notification.
        content (str): The body or message content of the notification.

    Returns:
        str: A success message if the notification is sent, or an error message if it fails.

    Example:
        >>> send_message_to_user("Reminder", "Start your meeting at 10 AM")
        'ntfy notification sent successfully!'
    """
    topic = "python-notification-genai"
    message_text = f"Subject: {subject}\nContent: {content}"

    try:
        response = requests.post(f"https://ntfy.sh/{topic}", data=message_text.encode('utf-8'))
        response.raise_for_status()
        return "ntfy notification sent successfully!"
    except requests.exceptions.RequestException as e:
        return f"Error sending ntfy notification: {e}"

def search_the_internet(query: str) -> list[dict[str, str]]:
    """
    Perform a DuckDuckGo text search and return the top results.

    Args:
        query (str): The search query string.

    Returns:
        list[dict[str, str]]: A list of dictionaries, each representing a search result with keys like 'title', 'href', and 'body'.

        Example:
        [
            {
                'title': 'OpenAI - Wikipedia',
                'href': 'https://en.wikipedia.org/wiki/OpenAI',
                'body': 'OpenAI is an AI research and deployment company...'
            },
            ...
        ]

    Raises:
        Returns a string with error message if search fails.

    Example:
        >>> search_duckduckgo_text("OpenAI")
        [{'title': 'OpenAI', 'href': 'https://openai.com/', 'body': '...'}, ...]
    """
    try:
        results = DDGS().text(query, max_results=3)
        return results
    except Exception as e:
        return [{"error": str(e)}]

def get_latest_news(query: str, region: str = "in-en", max_results: int = 10) -> list[dict[str, str]]:
    """
    Fetch the latest news headlines related to a given topic using DuckDuckGo's news search.

    Args:
        query (str): The search topic for news (e.g., "ind vs eng cricket").
        region (str, optional): The locale or region for localized news (default is "in-en").
        max_results (int, optional): The maximum number of news results to fetch (default is 10).

    Returns:
        list[dict[str, str]]: A list of news result dictionaries with keys such as 'title', 'date', 'body', and 'url'.

    Example:
        >>> get_latest_news("ind vs eng cricket")
        [{'title': '...', 'date': '...', 'body': '...', 'url': '...'}, ...]
    """
    try:
        results = DDGS().news(query, region=region, max_results=max_results)
        return results
    except Exception as e:
        return [{"error": str(e)}]


def get_wikipedia_summary(topic: str, sentences: int = 3) -> str:
    """
    Fetch a summary from Wikipedia for the given topic.

    Args:
        topic (str): The topic to search on Wikipedia.
        sentences (int): Number of summary sentences to return.

    Returns:
        str: A summary of the topic from Wikipedia.

    Example:
    >>> get_wikipedia_summary("Python (programming language)")
    """

    try:
        summary = wikipedia.summary(topic, sentences=sentences, auto_suggest=True, redirect=True)
        return summary
    except wikipedia.DisambiguationError as e:
        return f"The topic '{topic}' is ambiguous. Try being more specific.\nOptions: {e.options[:5]}"
    except wikipedia.PageError:
        return f"No Wikipedia page found for '{topic}'."
    except Exception as e:
        return f"An error occurred: {str(e)}"


def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convert currency using INR as base currency.

    Parameters:
        amount (float): Amount to convert
        from_currency (str): Currency code to convert from (e.g., 'inr', 'usd')
        to_currency (str): Currency code to convert to (e.g., 'usd', 'eur')

    Returns:
        float: Converted amount

    Example Usage:
        convert_currency(100, 'inr', 'usd')  -> INR to USD
        convert_currency(10, 'usd', 'inr')   -> USD to INR
    """
    url = "https://latest.currency-api.pages.dev/v1/currencies/inr.json"

    try:
        response = requests.get(url)
        data = response.json()
        rates = data.get("inr", {})

        from_currency = from_currency.lower()
        to_currency = to_currency.lower()

        if from_currency == "inr":
            if to_currency in rates:
                return round(amount * rates[to_currency], 4)
            else:
                raise ValueError(f"Unsupported target currency: {to_currency}")

        elif to_currency == "inr":
            if from_currency in rates:
                return round(amount / rates[from_currency], 4)
            else:
                raise ValueError(f"Unsupported source currency: {from_currency}")

        else:
            # Convert via INR (e.g., USD -> INR -> EUR)
            if from_currency in rates and to_currency in rates:
                inr_amount = amount / rates[from_currency]
                return round(inr_amount * rates[to_currency], 4)
            else:
                raise ValueError(f"Unsupported currency pair: {from_currency} to {to_currency}")

    except requests.RequestException as e:
        print("Network error:", e)
        return None
    except ValueError as ve:
        print("Conversion error:", ve)
        return None



def load_events():
    if not os.path.exists(EVENTS_FILE):
        return []
    with open(EVENTS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_events(events):
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)

def cleanup_events(events):
    """Remove past events"""
    now = datetime.now()
    future_events = [
        event for event in events
        if datetime.strptime(event["date"] + " " + event["time"], "%Y-%m-%d %H:%M") >= now
    ]
    return future_events

def create_or_update_event(title: str, date: str, time: str) -> str:
    """
    Creates a new event or updates an existing one based on the title and date.
    Automatically deletes any past events before processing.

    Args:
        title (str): The name or description of the event.
        date (str): The date of the event in 'DD-MM-YYYY' format.
        time (str): The time of the event in 'HH:MM' format (24-hour clock).

    Returns:
        str: A message indicating whether the event was created or updated.

    Example:
        >>> create_or_update_event("Doctor Visit", "21-07-2025", "10:00")
        'Event created.'
    """
    events = load_events()
    events = cleanup_events(events)

    # Check if event with same title and date exists, then update it
    updated = False
    for event in events:
        if event["title"].lower() == title.lower() and event["date"] == date:
            event["time"] = time
            updated = True
            break

    if not updated:
        events.append({
            "title": title,
            "date": date,
            "time": time
        })

    save_events(events)
    return "Event updated." if updated else "Event created."

def list_events(date: str) -> str:
    """
    List all events for a specific date (format: DD-MM-YYYY)

    Example:
    >>> list_events("21-7-2025")
    """

    events = load_events()
    events = cleanup_events(events)
    save_events(events)  # Save cleaned list

    matched_events = [e for e in events if e["date"] == date]
    if not matched_events:
        return f"No events found for {date}."

    result = f"Events on {date}:\n"
    for e in matched_events:
        result += f"- {e['title']} at {e['time']}\n"
    return result.strip()

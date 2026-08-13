import os
import re
import certifi
import airportsdata
import pycountry
import requests
from dotenv import load_dotenv


load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# Default origin airport code (e.g., SGN for Tan Son Nhat International Airport)
DEFAULT_ORIGIN_DATA = os.getenv("DEFAULT_ORIGIN_IATA", "SGN")

BASE_URL = "http://api.aviationstack.com/v1/flights"


AIRPORTS = airportsdata.load("IATA")  # Load airport data with IATA codes

COUNTRY_ALIASES = {
    # United States
    "usa":                                 "United States",
    "us":                                  "United States",
    "united states":                       "United States",
    "united states of america":            "United States",
    "america":                             "United States",
    "u.s.":                                "United States",
    "u.s.a.":                              "United States",

    # United Kingdom
    "uk":                                  "United Kingdom",
    "great britain":                       "United Kingdom",
    "england":                             "United Kingdom",
    "scotland":                            "United Kingdom",
    "wales":                               "United Kingdom",
    "northern ireland":                    "United Kingdom",
    "britain":                             "United Kingdom",

    # United Arab Emirates
    "uae":                                 "United Arab Emirates",
    "united arab emirates":                "United Arab Emirates",
    "emirates":                            "United Arab Emirates",

    # Vietnam
    "viet nam":                            "Vietnam",
    "vietnam":                             "Vietnam",

    # South Korea
    "south korea":                         "Korea, Republic of",
    "republic of korea":                   "Korea, Republic of",
    "korea":                               "Korea, Republic of",

    # North Korea
    "north korea":                         "Korea, Democratic People's Republic of",
    "democratic people's republic of korea":"Korea, Democratic People's Republic of",

    # Russia
    "russia":                              "Russian Federation",
    "russian federation":                   "Russian Federation",

    # Laos
    "laos":                                "Lao People's Democratic Republic",
    "lao pdr":                             "Lao People's Democratic Republic",

    # Iran
    "iran":                                "Iran, Islamic Republic of",
    "iran (islamic republic of)":          "Iran, Islamic Republic of",
    "islamic republic of iran":            "Iran, Islamic Republic of",

    # Czech Republic
    "czechia":                             "Czech Republic",
    "czech republic":                      "Czech Republic",

    # Brunei
    "brunei":                              "Brunei Darussalam",
    "brunei darussalam":                   "Brunei Darussalam",

    # Ivory Coast / Côte d'Ivoire
    "ivory coast":                         "Côte d'Ivoire",
    "cote d'ivoire":                       "Côte d'Ivoire",

    # Taiwan
    "taiwan":                              "Taiwan, Province of China",
    "taiwan province of china":            "Taiwan, Province of China",

    # Palestine
    "palestine":                           "Palestine, State of",
    "state of palestine":                  "Palestine, State of",

    # Venezuela
    "venezuela":                           "Venezuela, Bolivarian Republic of",
    "bolivarian republic of venezuela":    "Venezuela, Bolivarian Republic of",

    # Syria
    "syria":                               "Syrian Arab Republic",
    "syrian arab republic":                "Syrian Arab Republic",

    # Moldova
    "moldova":                             "Moldova, Republic of",
    "republic of moldova":                 "Moldova, Republic of",

    # Bolivia
    "bolivia":                             "Bolivia, Plurinational State of",
    "plurinational state of bolivia":      "Bolivia, Plurinational State of",

    # Tanzania
    "tanzania":                            "Tanzania, United Republic of",
    "united republic of tanzania":         "Tanzania, United Republic of",

    # North Macedonia
    "macedonia":                           "North Macedonia",
    "north macedonia":                     "North Macedonia",
    "macedonia, the former yugoslav republic of": "North Macedonia",

    # Myanmar
    "myanmar":                             "Myanmar",
    "burma":                               "Myanmar",

    # Cabo Verde
    "cape verde":                          "Cabo Verde",
    "cabo verde":                          "Cabo Verde",
    "green cape":                          "Cabo Verde",
    "drepan":                              "Cabo Verde",  # sometimes seen in codes

    # Timor-Leste
    "east timor":                          "Timor-Leste",
    "timor-leste":                         "Timor-Leste",

    # Gambia
    "gambia":                              "Gambia",
    "the gambia":                          "Gambia",

    # Bahamas
    "bahamas":                             "Bahamas",
    "the bahamas":                         "Bahamas",

    # Congo
    "congo":                               "Congo",
    "congo-brazzaville":                   "Congo",
    "republic of the congo":               "Congo",

    # DR Congo
    "congo-kinshasa":                      "Congo, The Democratic Republic of the",
    "democratic republic of the congo":     "Congo, The Democratic Republic of the",
    "dr congo":                            "Congo, The Democratic Republic of the",
    "congo (democratic republic)":         "Congo, The Democratic Republic of the",

    # Vatican
    "vatican":                             "Holy See (Vatican City State)",
    "vatican city":                        "Holy See (Vatican City State)",
    "holy see":                            "Holy See (Vatican City State)",

    # Eswatini
    "swaziland":                           "Eswatini",
    "eswatini":                            "Eswatini",

    # Bahrain
    "bahrein":                             "Bahrain",

    # South Sudan
    "south sudan":                         "South Sudan",

    # Antigua and Barbuda
    "antigua":                             "Antigua and Barbuda",
    "barbuda":                             "Antigua and Barbuda",

    # Bosnia and Herzegovina
    "bosnia":                              "Bosnia and Herzegovina",
    "herzegovina":                         "Bosnia and Herzegovina",

    # Central African Republic
    "car":                                 "Central African Republic",
    "central african republic":             "Central African Republic",

    # Comoros
    "comoros":                             "Comoros",
    "the comoros":                         "Comoros",

    # Micronesia
    "micronesia":                          "Micronesia, Federated States of",
    "federated states of micronesia":      "Micronesia, Federated States of",

    # Saint Kitts and Nevis
    "st. kitts":                           "Saint Kitts and Nevis",
    "saint kitts and nevis":               "Saint Kitts and Nevis",

    # Saint Lucia
    "st. lucia":                           "Saint Lucia",
    "saint lucia":                         "Saint Lucia",

    # Saint Vincent and the Grenadines
    "st. vincent":                         "Saint Vincent and the Grenadines",
    "saint vincent and the grenadines":    "Saint Vincent and the Grenadines",

    # Sao Tome and Principe
    "sao tome":                            "Sao Tome and Principe",
    "sao tome and principe":               "Sao Tome and Principe",

    # Solomon Islands
    "solomon islands":                     "Solomon Islands",

    # Trinidad and Tobago
    "trinidad":                            "Trinidad and Tobago",
    "tobago":                              "Trinidad and Tobago",
    "trinidad and tobago":                 "Trinidad and Tobago",

    # Turkey
    "turkiye":                             "Turkey",
}

COUNTRY_MAIN_AIRPORTS = {
    # Danh sách các sân bay chính cho từng quốc gia (theo IATA code)
    "Vietnam":                             "SGN",   # Tan Son Nhat International Airport
    "United States":                       "JFK",   # John F. Kennedy International Airport
    "United Kingdom":                      "LHR",   # London Heathrow Airport
    "France":                              "CDG",   # Charles de Gaulle Airport
    "Germany":                             "FRA",   # Frankfurt am Main Airport
    "Japan":                               "NRT",   # Narita International Airport
    "South Korea":                         "ICN",   # Incheon International Airport
    "Singapore":                           "SIN",   # Singapore Changi Airport
    "Thailand":                            "BKK",   # Suvarnabhumi Airport (Bangkok)
    "Australia":                           "SYD",   # Sydney Kingsford Smith Airport
    "Canada":                              "YYZ",   # Toronto Pearson International Airport
    "China":                               "PEK",   # Beijing Capital International Airport
    "India":                               "DEL",   # Indira Gandhi International Airport (Delhi)
    "Indonesia":                           "CGK",   # Soekarno-Hatta International Airport (Jakarta)
    "Malaysia":                            "KUL",   # Kuala Lumpur International Airport
    "Italy":                               "FCO",   # Rome Fiumicino – Leonardo da Vinci Airport
    "Spain":                               "MAD",   # Adolfo Suárez Madrid–Barajas Airport
    "Netherlands":                         "AMS",   # Amsterdam Airport Schiphol
    "Turkey":                              "IST",   # Istanbul Airport
    "United Arab Emirates":                "DXB",   # Dubai International Airport
    "Russia":                              "SVO",   # Sheremetyevo International Airport (Moscow)
    "Brazil":                              "GRU",   # São Paulo/Guarulhos International Airport
    "Switzerland":                         "ZRH",   # Zurich Airport
    "Austria":                             "VIE",   # Vienna International Airport
    "Sweden":                              "ARN",   # Stockholm Arlanda Airport
    "Norway":                              "OSL",   # Oslo Gardermoen Airport
    "Finland":                             "HEL",   # Helsinki-Vantaa Airport
    "Denmark":                             "CPH",   # Copenhagen Airport
    "Belgium":                             "BRU",   # Brussels Airport
    "Poland":                              "WAW",   # Warsaw Chopin Airport
    "Czech Republic":                      "PRG",   # Václav Havel Airport Prague
    "Portugal":                            "LIS",   # Humberto Delgado Airport (Lisbon)
    "Greece":                              "ATH",   # Athens International Airport
    "South Africa":                        "JNB",   # O.R. Tambo International Airport (Johannesburg)
    "Saudi Arabia":                        "RUH",   # King Khalid International Airport (Riyadh)
    "Qatar":                               "DOH",   # Hamad International Airport (Doha)
    "New Zealand":                         "AKL",   # Auckland Airport
    "Philippines":                         "MNL",   # Ninoy Aquino International Airport (Manila)
    "Taiwan":                              "TPE",   # Taiwan Taoyuan International Airport
    "Hong Kong":                           "HKG",   # Hong Kong International Airport
    "Ireland":                             "DUB",   # Dublin Airport
    "Mexico":                              "MEX",   # Mexico City International Airport
    "Egypt":                               "CAI",   # Cairo International Airport
    "Argentina":                           "EZE",   # Ministro Pistarini International Airport (Buenos Aires)
    "Israel":                              "TLV",   # Ben Gurion Airport (Tel Aviv)
    "Hungary":                             "BUD",   # Budapest Ferenc Liszt International Airport
    "Romania":                             "OTP",   # Henri Coandă International Airport (Bucharest)
    "Chile":                               "SCL",   # Comodoro Arturo Merino Benítez International Airport (Santiago)
    "Myanmar":                             "RGN",   # Yangon International Airport
    "Pakistan":                            "ISB",   # Islamabad International Airport
    "Bangladesh":                          "DAC",   # Hazrat Shahjalal International Airport (Dhaka)
    "Laos":                                "VTE",   # Wattay International Airport (Vientiane)
    "Cambodia":                            "PNH",   # Phnom Penh International Airport
    "Brunei Darussalam":                   "BWN",   # Brunei International Airport
    "Sri Lanka":                           "CMB",   # Bandaranaike International Airport (Colombo)
    "Nepal":                               "KTM",   # Tribhuvan International Airport (Kathmandu)
    "Maldives":                            "MLE",   # Velana International Airport
    "Luxembourg":                          "LUX",   # Luxembourg Airport
    "Iceland":                             "KEF",   # Keflavik International Airport
    "Ukraine":                             "KBP",   # Boryspil International Airport (Kyiv)
    "Kazakhstan":                          "ALA",   # Almaty International Airport
    "Uzbekistan":                          "TAS",   # Islam Karimov Tashkent International Airport
    "Azerbaijan":                          "GYD",   # Heydar Aliyev International Airport (Baku)
    "Georgia":                             "TBS",   # Tbilisi International Airport
    "Armenia":                             "EVN",   # Zvartnots International Airport (Yerevan)
    "Iran, Islamic Republic of":            "IKA",   # Tehran Imam Khomeini International Airport
    "Iraq":                                "BGW",   # Baghdad International Airport
    "Afghanistan":                         "KBL",   # Kabul International Airport
    "Kuwait":                              "KWI",   # Kuwait International Airport
    "Oman":                                "MCT",   # Muscat International Airport
    "Jordan":                              "AMM",   # Queen Alia International Airport (Amman)
    "Morocco":                             "CMN",   # Mohammed V International Airport (Casablanca)
    "Algeria":                             "ALG",   # Houari Boumediene Airport (Algiers)
    "Tunisia":                             "TUN",   # Tunis–Carthage International Airport
    "Ethiopia":                            "ADD",   # Addis Ababa Bole International Airport
    "Kenya":                               "NBO",   # Jomo Kenyatta International Airport (Nairobi)
    "Nigeria":                             "LOS",   # Murtala Muhammed International Airport (Lagos)
    "Ivory Coast":                         "ABJ",   # Félix-Houphouët-Boigny International Airport (Abidjan)
    "Ghana":                               "ACC",   # Kotoka International Airport (Accra)
    "Tanzania":                            "DAR",   # Julius Nyerere International Airport (Dar es Salaam)
    "Senegal":                             "DSS",   # Blaise Diagne International Airport (Dakar)
}

CITY_MAIN_AIRPORTS = {
    "Ho Chi Minh City": "SGN",
    "Hanoi":           "HAN",
    "Da Nang":         "DAD",
    "Hai Phong":       "HPH",
    "Nha Trang":       "CXR",
    "Hue":             "HUI",
    "Vinh":            "VII",
    "Can Tho":         "VCA",
    "Phu Quoc":        "PQC",
}

def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    stop_words = [
        "flight", "flights", "ticket", "tickets", "trip", "travel",
        "plan", "complete", "days", "day", "including", "hotel",
        "hotels", "sightseeing", "under", "budget", "info", "information"
    ]
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words).strip()

def country_name_to_code(text: str):
    text = clean_text(text)

    if text in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[text]

    try:
        country = pycountry.countries.lookup(text)
        return country.alpha_2
    except LookupError:
        pass

    # Detect country name inside longer text
    for country in pycountry.countries:
        country_name = country.name.lower()
        if country_name in text:
            return country.alpha_2

    for alias, code in COUNTRY_ALIASES.items():
        if alias in text:
            return code

    return None



def airport_country_matches(airport: dict, country_code: str) -> bool:
    airport_country = str(airport.get("country", "")).upper().strip()

    if airport_country == country_code:
        return True

    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country and airport_country.lower() == country.name.lower():
            return True
    except Exception:
        pass

    return False




def get_best_airport_for_country(country_code: str):
    preferred = COUNTRY_MAIN_AIRPORTS.get(country_code)

    if preferred and preferred in AIRPORTS:
        return preferred

    candidates = []

    for iata, airport in AIRPORTS.items():
        if not iata:
            continue

        if airport_country_matches(airport, country_code):
            name = str(airport.get("name", "")).lower()
            city = str(airport.get("city", "")).lower()

            score = 0

            if "international" in name:
                score += 50
            if "intl" in name:
                score += 40
            if "capital" in name:
                score += 20
            if city:
                score += 5

            candidates.append((score, iata))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]




def resolve_location_to_iata(location: str):
    """
    Converts country/city/airport/IATA into IATA code.

    Examples:
    Bangladesh -> DAC
    Japan -> NRT
    Dhaka -> DAC
    Tokyo -> NRT
    DAC -> DAC
    """

    if not location:
        return None

    raw_location = location.strip()

    # Direct IATA code
    if re.fullmatch(r"[A-Za-z]{3}", raw_location):
        code = raw_location.upper()
        if code in AIRPORTS:
            return code

    location_clean = clean_text(raw_location)

    if not location_clean:
        return None

    # City preferred airport
    if location_clean in CITY_MAIN_AIRPORTS:
        return CITY_MAIN_AIRPORTS[location_clean]

    # Country preferred airport
    country_code = country_name_to_code(location_clean)
    if country_code:
        airport = get_best_airport_for_country(country_code)
        if airport:
            return airport

    # Exact city match from airport database
    city_matches = []

    for iata, airport in AIRPORTS.items():
        city = str(airport.get("city", "")).lower().strip()
        name = str(airport.get("name", "")).lower().strip()

        score = 0

        if city == location_clean:
            score += 100
        elif location_clean in city:
            score += 70

        if location_clean in name:
            score += 50

        if "international" in name:
            score += 10

        if score > 0:
            city_matches.append((score, iata))

    if city_matches:
        city_matches.sort(reverse=True)
        return city_matches[0][1]

    return None




def find_location_mentions(query: str):
    """
    Finds country or city names inside a natural language query.
    """

    q = query.lower()
    mentions = []

    # Country aliases
    for alias in COUNTRY_ALIASES:
        if re.search(rf"\b{re.escape(alias)}\b", q):
            mentions.append(alias)

    # Country names from pycountry
    for country in pycountry.countries:
        name = country.name.lower()
        if len(name) >= 4 and re.search(rf"\b{re.escape(name)}\b", q):
            mentions.append(name)

    # City names from our preferred city map
    for city in CITY_MAIN_AIRPORTS:
        if re.search(rf"\b{re.escape(city)}\b", q):
            mentions.append(city)

    # Remove duplicate while keeping order
    unique_mentions = []
    for item in mentions:
        if item not in unique_mentions:
            unique_mentions.append(item)

    return unique_mentions


def parse_route(query: str):
    """
    Returns:
    dep_iata, arr_iata

    Can return:
    None, None  -> global live flights
    DAC, NRT    -> filtered route
    DAC, None   -> all flights from DAC
    None, NRT   -> all flights to NRT
    """

    q = query.strip()
    q_lower = q.lower()

    # Global / all-country query
    global_keywords = [
        "all country",
        "all countries",
        "global flight",
        "global flights",
        "all flight",
        "all flights",
        "worldwide flight",
        "worldwide flights",
    ]

    if any(keyword in q_lower for keyword in global_keywords):
        return None, None

    # Direct IATA code route: DAC to NRT
    codes = re.findall(r"\b[A-Z]{3}\b", q)

    if len(codes) >= 2:
        dep = codes[0].upper()
        arr = codes[1].upper()
        return dep, arr

    # Pattern: from X to Y
    match = re.search(
        r"\bfrom\s+(.+?)\s+\bto\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        origin_text = match.group(1)
        dest_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: to Y from X
    match = re.search(
        r"\bto\s+(.+?)\s+\bfrom\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        dest_text = match.group(1)
        origin_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: flights from X
    match = re.search(r"\bfrom\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        origin_text = match.group(1)
        dep_iata = resolve_location_to_iata(origin_text)
        return dep_iata, None

    # Pattern: flights to X
    match = re.search(r"\bto\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        dest_text = match.group(1)
        arr_iata = resolve_location_to_iata(dest_text)
        return None, arr_iata

    # Fallback: find country/city mentions
    mentions = find_location_mentions(q)

    if len(mentions) >= 2:
        dep_iata = resolve_location_to_iata(mentions[0])
        arr_iata = resolve_location_to_iata(mentions[1])
        return dep_iata, arr_iata

    if len(mentions) == 1:
        arr_iata = resolve_location_to_iata(mentions[0])
        return DEFAULT_ORIGIN_IATA, arr_iata

    return None, None


def format_flight(flight: dict):
    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number = flight.get("flight", {}).get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    dep = flight.get("departure", {}) or {}
    arr = flight.get("arrival", {}) or {}

    dep_airport = dep.get("airport") or "Unknown departure airport"
    dep_iata = dep.get("iata") or "Unknown"
    dep_terminal = dep.get("terminal") or "N/A"
    dep_gate = dep.get("gate") or "N/A"
    dep_scheduled = dep.get("scheduled") or "Unknown"
    dep_delay = dep.get("delay")
    dep_delay_text = f"{dep_delay} minutes" if dep_delay is not None else "N/A"

    arr_airport = arr.get("airport") or "Unknown arrival airport"
    arr_iata = arr.get("iata") or "Unknown"
    arr_terminal = arr.get("terminal") or "N/A"
    arr_gate = arr.get("gate") or "N/A"
    arr_scheduled = arr.get("scheduled") or "Unknown"
    arr_delay = arr.get("delay")
    arr_delay_text = f"{arr_delay} minutes" if arr_delay is not None else "N/A"

    return f"""
Airline: {airline}
Flight: {flight_number}
Status: {status}

Departure:
- Airport: {dep_airport}
- IATA: {dep_iata}
- Terminal: {dep_terminal}
- Gate: {dep_gate}
- Scheduled: {dep_scheduled}
- Delay: {dep_delay_text}

Arrival:
- Airport: {arr_airport}
- IATA: {arr_iata}
- Terminal: {arr_terminal}
- Gate: {arr_gate}
- Scheduled: {arr_scheduled}
- Delay: {arr_delay_text}
""".strip()


def search_flights(query: str, limit: int = 10):
    if not API_KEY:
        return (
            "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
            "Please add this in your .env file:\n"
            "AVIATIONSTACK_API_KEY=your_api_key_here"
        )

    dep_iata, arr_iata = parse_route(query)

    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100),
    }

    if dep_iata:
        params["dep_iata"] = dep_iata

    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Flight API request failed: {e}"
    except ValueError:
        return "Flight API returned invalid JSON."

    if "error" in data:
        error = data["error"]
        return (
            "Flight API error:\n"
            f"Code: {error.get('code', 'Unknown')}\n"
            f"Message: {error.get('message', 'Unknown error')}"
        )

    flight_data = data.get("data", [])

    if not flight_data:
        route_text = ""

        if dep_iata and arr_iata:
            route_text = f" for route {dep_iata} to {arr_iata}"
        elif dep_iata:
            route_text = f" from {dep_iata}"
        elif arr_iata:
            route_text = f" to {arr_iata}"

        return (
            f"No live flight data found{route_text}.\n\n"
            "Note: AviationStack provides live/status flight data, not ticket prices. "
            "For actual fare prices, use a flight-pricing API such as Amadeus."
        )

    route_info = "Global live flights"

    if dep_iata and arr_iata:
        route_info = f"Live flights from {dep_iata} to {arr_iata}"
    elif dep_iata:
        route_info = f"Live flights from {dep_iata}"
    elif arr_iata:
        route_info = f"Live flights to {arr_iata}"

    formatted_flights = [format_flight(flight) for flight in flight_data[:limit]]

    return f"{route_info}\n\n" + "\n\n---\n\n".join(formatted_flights)


if __name__ == "__main__":
    print(search_flights("Plan a 7 days Japan trip from Vietnam"))
    print("\n" + "=" * 80 + "\n")
    print(search_flights("all country flight info"))
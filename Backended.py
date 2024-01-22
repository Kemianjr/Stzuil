import psycopg2
import datetime
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage, Text, Entry
print(psycopg2.__version__)
import requests

#_______________________________________________________________________________________________________________________
#FRONTEND SECTION

##stations
stations = ["Almere","Amsterdam","Groningen","Utrecht","Zwolle",]

def user_name():
    name = input("Voer hier je naam in: ")
    return name

def choose_station():
    print("Kies alstublieft een station uit de lijst:")
    for index, station in enumerate(stations, start=1):
        print(f"{index}. {station}")

    while True:
        choice = input("Voer het nummer van je keuze in: ")
        if choice.isdigit() and 0 < int(choice) <= len(stations):
            return stations[int(choice) - 1]
        else:
            print("Ongeldige keuze, voer alstublieft een geldig nummer in.")

def user_message_db():
    name = user_name()
    station = choose_station()

    print(f"Welkom {name}! Voer hier je bericht in (Max 140 tekens): ")
    while True:
        message = input()
        if len(message) > 140:
            print("Je bericht is te lang, voer alstublieft een bericht in met maximaal 140 tekens.")
        elif not message.strip():
            print("Sorry, je moet een bericht invoeren.")
        else:
            timestamp = datetime.datetime.now()
            add_message(message, name, station)
            print("Bedankt! Je bericht is opgeslagen in de database.")
            break
#_______________________________________________________________________________________________________________________
#DATABASE SECTION
dbname = "ns_project"
user = "kevin"
password = "kevinboy008!"
host = "172.167.240.147"  # Je Azure VM's publieke IP
port = "5432"  # Standaard PostgreSQL-poort

def connect_to_db():
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        print("Verbinding met de database is succesvol.")
        return conn
    except psycopg2.DatabaseError as e:
        print("Ik kon geen verbinding maken met de database: ", e)
        return None

##Database connectiegegevens
MODERATOR_NAME = "Kevin"  # naam moderator
MODERATOR_EMAIL = "Kevin.kunga@ns.nl"  # email moderator
dbname = "ns_project"
user = "kemianjr"
password = "kevinboy008"
host = "127.0.0.1"
port = "5432"

def connect_to_db():
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        return conn
    except psycopg2.DatabaseError as e:
        print("Ik kon geen verbinding maken met de database: ", e)
        return None

# Database code voor de Backended applicatie.
def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS messages (
            message_id SERIAL PRIMARY KEY,
            message_text VARCHAR(140) NOT NULL,
            message_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            sender_name VARCHAR(50) DEFAULT 'anoniem',
            station_name VARCHAR(50) NOT NULL,
            confirmed BOOLEAN NOT NULL DEFAULT FALSE,
            confirmed_timestamp TIMESTAMP WITH TIME ZONE,
            moderator_name VARCHAR(50),
            moderator_email VARCHAR(255)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS moderators (
            moderator_id SERIAL PRIMARY KEY,
            moderator_name VARCHAR(50) NOT NULL,
            moderator_email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
        """
    )
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn:
            conn.close()

# Voegt een nieuw bericht toe aan de database
def add_message(message_text, sender_name, station_name):
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO messages (message_text, sender_name, station_name) VALUES (%s, %s, %s)",
                    (message_text, sender_name, station_name))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn:
            conn.close()

def get_messages():
    conn = None
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages")
        messages = cur.fetchall()
        return messages
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return []
    finally:
        if conn:
            conn.close()

def fetch_unconfirmed_messages(): #haalt onbevestigde berichten op uit de database

    conn = connect_to_db()
    if conn is None:
        return []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM messages WHERE confirmed IS FALSE")
        messages = cursor.fetchall()
        return messages
    except Exception as e:
        print("Fout bij het ophalen van onbevestigde berichten: ", e)
        return []
    finally:
        cursor.close()
        conn.close()

def update_message_confirmation(message_id, confirmed, moderator_name, moderator_email): #update de bevestiging van berichten in de database

    conn = connect_to_db()
    if conn is None:
        return
    cursor = conn.cursor()
    confirmation_time = datetime.datetime.now()
    try:
        cursor.execute(
            "UPDATE messages SET confirmed = %s, confirmed_timestamp = %s, "
            "moderator_name = %s, moderator_email = %s WHERE message_id = %s",
            (confirmed, confirmation_time, MODERATOR_NAME, MODERATOR_EMAIL, message_id)
        )
        conn.commit()
    except Exception as error:
        print(f"Fout bij het bijwerken van bericht {message_id}: {error}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def moderate_unconfirmed_messages(): #modereert onbevestigde berichten

    unconfirmed_messages = fetch_unconfirmed_messages()
    if not unconfirmed_messages:
        print("Geen onbevestigde berichten om te modereren.")
    else:
        for message in unconfirmed_messages:
            print(format_message_for_display(message))
            while True:
                choice = input("Bevestigen (y/n)? ")
                if choice.lower() == "y":
                    update_message_confirmation(message[0], True, MODERATOR_NAME, MODERATOR_EMAIL)
                    break
                elif choice.lower() == "n":
                    update_message_confirmation(message[0], False, MODERATOR_NAME, MODERATOR_EMAIL)
                    break
                else:
                    print("Ongeldige keuze, probeer opnieuw.")

def format_message_for_display(message): #formatteert berichten voor weergave

    return (
        f"Bericht ID: {message[0]}\n"
        f"Bericht: {message[1]}\n"
        f"Van: {message[3]} (Station: {message[4]})\n"
        f"Verzonden op: {message[2].strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Bevestigd: {'Ja' if message[5] else 'Nee'}\n"
    )

def test_database_connection():
    conn = None
    try:
        conn = connect_to_db()
        if conn:
            print("Database connected.")
    except Exception as error:
        print(f"Database connection failed: {error}")
    finally:
        if conn:
            conn.close()

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def clear_screen(canvas):
    for item in canvas.find_all():
        canvas.delete(item)


def add_message_to_db(name, message, station):
    conn = connect_to_db()
    if not conn:
        print("Kon geen verbinding maken met de database.")
        return

    try:
        add_message(name, message, station, conn)
        print("Bericht toegevoegd aan de database.")
    except Exception as e:
        print(f"Fout bij het toevoegen van het bericht: {e}")
    finally:
        if conn:
            conn.close()

def moderate_messages():
    messages = Backended.get_pending_messages()  # Haal de berichten op die gemodereerd moeten worden

    for message in messages:
        print(f"Bericht van {message['name']}: {message['text']}")
        decision = input("Accepteer dit bericht? (ja/nee): ").strip().lower()
        if decision == 'ja':
            Backended.accept_message(message['id'])
            print("Bericht geaccepteerd.")
        elif decision == 'nee':
            Backended.reject_message(message['id'])
            print("Bericht afgewezen.")
        else:
            print("Ongeldige invoer, geen actie ondernomen.")

    print("Moderatie compleet!")

def get_messages_by_station(station_name):
    conn = connect_to_db()
    if conn is None:
        print("Kon geen verbinding maken met de database.")
        return []
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM messages WHERE station_name = %s AND confirmed = TRUE", (station_name,))
        messages = cursor.fetchall()
        return messages
    except Exception as error:
        print(f"Fout bij het ophalen van berichten voor station {station_name}: {error}")
        return []
    finally:
        cursor.close()
        conn.close()
def moderate_interface():
    print("Welkom bij de berichtenmoderatie.")
    moderator_name = input("Voer uw moderator naam in: ")
    moderator_email = input("Voer uw moderator e-mailadres in: ")

    unconfirmed_messages = fetch_unconfirmed_messages()
    if not unconfirmed_messages:
        print(f"\nWelkom {moderator_name}! Er zijn momenteel geen berichten om te modereren.")
        return

    print(f"\nWelkom {moderator_name}! U heeft {len(unconfirmed_messages)} berichten om te modereren.\n")

    for msg in unconfirmed_messages:
        print(
            f"\nID: {msg[0]},\nBericht: {msg[1]}\nVan: {msg[3]} ({msg[4]})\nVerzonden op: {msg[2].strftime('%Y-%m-%d %H:%M:%S')}")
        while True:
            moderator_decision = input("Keur dit bericht goed? (ja/nee/stop): ").lower()
            if moderator_decision == 'ja':
                update_message_confirmation(msg[0], True, moderator_name, moderator_email)
                print("Bericht goedgekeurd.")
                break
            elif moderator_decision == 'nee':
                update_message_confirmation(msg[0], False, moderator_name, moderator_email)
                print("Bericht afgekeurd.")
                break
            elif moderator_decision == 'stop':
                print("Moderatie gestopt.")
                return
            else:
                print("Ongeldige invoer, probeer opnieuw.")

def get_message_by_id(message_id):
    conn = connect_to_db()
    if conn is None:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM messages WHERE message_id = %s", (message_id,))
        message = cursor.fetchone()
        return message
    except Exception as e:
        print("Fout bij het ophalen van bericht: ", e)
        return None
    finally:
        cursor.close()
        conn.close()

def initialize_station_services():
    # SQL commando om de station_service tabel te maken
    create_table_command = """
    CREATE TABLE IF NOT EXISTS station_service (
        station_city VARCHAR (50) PRIMARY KEY NOT NULL,
        country VARCHAR (2) NOT NULL,
        ov_bike BOOLEAN NOT NULL,
        elevator BOOLEAN NOT NULL,
        toilet BOOLEAN NOT NULL,
        park_and_ride BOOLEAN NOT NULL
    );
    """

    # SQL commando om de gegevens in de tabel in te voegen
    insert_data_command = """
    INSERT INTO station_service (station_city, country, ov_bike, elevator, toilet, park_and_ride) VALUES
    ('Almere', 'NL', false, true, false, true),
    ('Amsterdam', 'NL', false, true, false, true),
    ('Groningen', 'NL', false, true, false, true),
    ('Utrecht', 'NL', true, false, true, false),
    ('Zwolle', 'NL', true, false, true, false)
    ON CONFLICT (station_city) DO NOTHING;  -- Voorkomt fouten als de rij al bestaat
    """

    conn = connect_to_db()
    if conn is None:
        print("Kon geen verbinding maken met de database voor het maken van station_services.")
        return

    try:
        cur = conn.cursor()
        cur.execute(create_table_command)
        cur.execute(insert_data_command)
        conn.commit()
        print("Station services tabel is succesvol en gegevens zijn ingevoerd.")
    except Exception as e:
        print(f"Fout bij het opzetten van de station_service tabel: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def update_weather():
    try:
        api_key = "40c1ca35cfc26a2dfb519d71ebcc4bc4"
        stadnaam = "Zwolle"
        url = f"http://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={stadnaam}"
        response = requests.get(url)
        weer_data = response.json()
        temperatuur = weer_data['main']['temp'] - 273.15  # Converteer van Kelvin naar Celsius
        weather_label.config(text=f"Temperatuur: {temperatuur:.2f} °C")
    finally:
        window.after(60000, update_weather)  # Update elke 60 seconden

def get_weather_info(city_name, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()

        return weather_data['weather'][0]['description'], weather_data['main']['temp']
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None, None

def get_top_headlines(api_key, country='nl'):
    url = f'https://newsapi.org/v2/top-headlines?country={country}&apiKey={api_key}'
    response = requests.get(url)
    return response.json()


api_key = '9bfe008ca34f43179b80dc6d3f770627'
headlines = get_top_headlines(api_key)

for article in headlines['articles']:
    print(article['title'])



if __name__ == "__main__":
    test_database_connection()
    test_database_connection()
    moderate_interface()



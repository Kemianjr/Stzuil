from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage, Entry, StringVar, OptionMenu
import Backended
from Backended import clear_screen, stations, get_top_headlines
import requests

# Pad naar de assets-map instellen
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"/Users/kemian/Desktop/Ns/Merge")

def update_weather():
    try:
        api_key = "40c1ca35cfc26a2dfb519d71ebcc4bc4"
        stadnaam = "Zwolle"
        url = f"http://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={stadnaam}"
        response = requests.get(url)
        weer_data = response.json()
        temperatuur = weer_data['main']['temp'] - 273.15
        weather_label.config(text=f"Temperatuur: {temperatuur:.2f} °C")
    finally:
        window.after(60000, update_weather)

def display_headlines(headlines):
    y_position = 100  # Beginpositie voor de headlines
    for headline in headlines[:5]:
        canvas.create_text(650, y_position, anchor="center", text=headline['title'], fill="#121212", font=("Helvetica", 10))
        y_position += 20


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


window = Tk()
window.geometry("1303x720")
window.configure(bg="#FFFFFF")

canvas = Canvas(window, bg="#FFFFFF", height=720, width=1303, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

clear_screen(canvas)

# Laad afbeeldingen
image_image_1 = PhotoImage(file=relative_to_assets("Startpagina.png"))
image_image_2 = PhotoImage(file=relative_to_assets("Start_trein.png"))
image_image_3 = PhotoImage(file=relative_to_assets("Kies_station.png"))
image_image_4 = PhotoImage(file=relative_to_assets("Tweede_trein.png"))
image_image5 = PhotoImage(file=relative_to_assets("Finalbg.png"))
image_image6 = PhotoImage(file=relative_to_assets("TheLastTrain.png"))
global_button = None


def show_messages_for_station(station_name):
    messages = Backended.get_messages_by_station(station_name)
    y_position = 450
    x_position = 590
    for msg in messages:
        canvas.create_text(x_position, y_position, anchor="nw", text=msg[1], fill="#121212",
                           font=("Helvetica", 22 * -1))
        y_position += 30


# homepagina
def show_home():
    global global_button
    canvas.delete("all")  # Verwijdert alle items van het canvas
    canvas.create_image(660.0, 360.0, image=image_image_1)

    # tekst op scherm
    canvas.create_text(265.0, 270.0, anchor="nw", text="Jouw verhaal kan iemand anders dag maken. Plaats het op een "
                                                       "station naar keuze.", fill="#0E0D0D", font=("Inter", 24 * -1))
    canvas.create_text(202.0, 99.0, anchor="nw", text="Verbind door Verhalen samen met NS", fill="#121212", font=
    ("Sora Bold", 64 * -1))
    # overig
    canvas.create_image(550.0, 697.0, image=image_image_2)  # Trein op homepagina

    # button
    button_image_1 = PhotoImage(file=relative_to_assets("Begin_button.png"))
    button_1 = Button(canvas, image=button_image_1, borderwidth=0, highlightthickness=0, command=berichtenpage,
                      relief="flat")
    button_1.place(x=508.0, y=356.0, width=262.0, height=59.0)
    button_1.image = button_image_1
    button_1.image = button_image_1
    global_button = button_1  # Sla de knop op in de globale variabele


def submit_message():
    global entry_1, entry_2, selected_station

    name = entry_1.get()
    message = entry_2.get()
    station = selected_station.get()

    if not name.strip():
        # Als er geen naam is ingevuld, gebruik "Anoniem"
        name = "Anoniem"

    if not message.strip():
        print("Het bericht mag niet leeg zijn.")
        return

    if len(message) > 140:
        print("Het bericht mag niet meer dan 140 tekens bevatten.")
        return

    if station == "Kies een station":
        print("Selecteer een geldig station.")
        return

    try:

        Backended.add_message(message, name, station)
        print("Bericht succesvol verzonden.")
    except Exception as e:
        print(f"Er is een fout opgetreden: {e}")


def handle_submit_and_navigate():
    submit_message()
    if global_button is not None:
        global_button.destroy()
    if button_2 is not None:
        button_2.destroy()
    entry_1.destroy()
    if entry_2 is not None:
        entry_2.destroy()
    station_menu.destroy()
    Finalpage()



# tweede pagina
def berichtenpage():
    global global_button, entry_1, entry_2, selected_station, station_menu, button_2
    if global_button:
        global_button.destroy()  # Verwijder de knop van de show_home pagina
        global_button = None
    canvas.delete("all")  # Verwijdert alle items van het canvas
    canvas.create_image(660.0, 360.0, image=image_image_3)

    # Dropdown menu voor stations
    selected_station = StringVar(window)
    selected_station.set("Kies een station")
    station_menu = OptionMenu(window, selected_station, *stations)
    station_menu.config(width=10, font=('Helvetica', 12))
    station_menu_window = canvas.create_window(548, 350.0, anchor="nw", window=station_menu, width=237, height=25)

    # tekst op scherm
    canvas.create_text(265.0, 220.0, anchor="nw", text="Jouw verhaal kan iemand anders dag maken. Plaats het op een "
                                                       "station naar keuze.", fill="#0E0D0D", font=("Inter", 24 * -1))
    canvas.create_text(300.0, 116.0, anchor="nw", text="Laat hier je bericht achter", fill="#121212", font=("Sora Bold",
                                                                                                            64 * -1))

    # OVERIG

    # trein op berichtenpagina
    canvas.create_image(696.0, 697.0, image=image_image_4)

    # button
    button_image_2 = PhotoImage(file=relative_to_assets("button_1.png"))
    button_2 = Button(canvas, image=button_image_2, borderwidth=0, highlightthickness=0,
                      command=handle_submit_and_navigate,
                      relief="flat")
    button_2.place(x=528.0, y=456.0, width=237.0, height=65.0)
    button_2.image = button_image_2
    # Tekstveld
    entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
    canvas.create_image(362.5, 360.0, image=entry_image_1)
    entry_1 = Entry(canvas, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
    entry_1.place(x=259.0, y=336.0, width=207.0, height=46.0)

    # tekstveld 2

    entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
    canvas.create_image(1030.5, 365.5, image=entry_image_2)
    entry_2 = Entry(canvas, bd=0, bg="#FFFFFF", fg="#000716", highlightthickness=0)
    entry_2.place(x=867.0, y=336.0, width=327.0, height=57.0)


    canvas.image = entry_image_1, entry_image_2, button_image_2, station_menu


def Finalpage():
    canvas.delete("all")  # Verwijdert alle items van het canvas
    canvas.create_image(650.0, 360.0, image=image_image5)

    # tekst op scherm
    canvas.create_text(312.0, 56.0, anchor="nw", text="Welkom op het station", fill="#121212", font=("Sora Bold", 64 * -1))
    canvas.create_text(12.0, 577.0, anchor="nw", text="Faciliteiten op dit station:", fill="#0E0D0D",
                       font=("Inter", 24 * -1)
                       )

    # trein
    canvas.create_image(840.0, 700.0, image=image_image6)

    selected_station = StringVar(window)
    selected_station.set("Kies een station")
    station_menu = OptionMenu(window, selected_station, *stations, command=show_messages_for_station)
    station_menu.config(width=15, font=('Helvetica', 12))
    station_menu.place(x=532.0, y=170.0)

    show_messages_for_station(selected_station.get())

    weather_description, temperature = Backended.get_weather_info("Zwolle", "40c1ca35cfc26a2dfb519d71ebcc4bc4")
    if weather_description and temperature:
        canvas.create_text(1200, 100, anchor="center",
                           text=f"Het weer momenteel:\n"
                                f" {weather_description} bij {temperature} °C", fill="#121212",
                           font=("Helvetica", 16))
    api_key = "9bfe008ca34f43179b80dc6d3f770627"
    headlines = get_top_headlines(api_key)
    print(headlines)
    display_headlines(headlines)


# canvas voor de achtergrond en inhoud
canvas = Canvas(window, bg="#FFFFFF", height=720, width=1303, bd=0, highlightthickness=0, relief="ridge")
canvas.place(x=0, y=0)

show_home()

window.mainloop()
from nicegui import app, ui, Client
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

import datetime
import jwt

app.add_middleware(SessionMiddleware, secret_key="asdasdasda")

rooms = [
    "101",
    "102",
    "103"
]

time_slots = [
    "09:00 - 10:00",
    "10:00 - 11:00",
    "11:00 - 12:00",
    "12:00 - 13:00",
    "13:00 - 14:00",
    "14:00 - 15:00",
    "15:00 - 16:00",
    "16:00 - 17:00",
    "17:00 - 18:00",
    "18:00 - 19:00",
    "19:00 - 20:00",
    "20:00 - 21:00",
    "21:00 - 22:00"
]


@ui.page("/")
async def index():
    return RedirectResponse(url="/main")


@ui.page("/main")
async def main():
    with ui.header():
        # Center name vertically
        ui.label(app.storage.user.get("name")).style('margin-left: auto; line-height: 38px;')
        ui.button("Atsijungti", on_click=lambda: ui.open("/logout")).style('margin-right: auto;')
        ui.button("Keisti rezervacijas", on_click=lambda: ui.open("/main/reservations")).style('margin-right: auto;')

    with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
        ui.label("Rezervuoti patalpą").style(
            "font-size: 30px; font-weight: bold; width: 100%; margin: auto; text-align: center;")
    with (ui.column().style("/*center div*/ margin: auto; text-align: center;") as calendar_row):
        # Calendar
        ui.label("Pasirinkite patalpą:").style("margin: auto; text-align: center;")
        for room in rooms:
            with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
                link = "/reserve?room="
                ui.button(room, on_click=lambda x: ui.open(link + x.sender.text)).style(
                    "margin: auto; text-align: center; width: 50vw;")

    with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
        ui.label("Visos rezervacijos").style(
            "font-size: 30px; font-weight: bold; width: 100%; margin: auto; text-align: center;")
    with (ui.column().style("/*center div*/ margin: auto; text-align: center;") as calendar_row):
        for room in rooms:
            with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
                ui.label("Patalpa " + room).style(
                    "font-size: 20px; font-weight: bold; width: 100%; margin: auto; text-align: center;")
                for reservation in app.storage.general.get("reservations_" + room, []):
                    with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
                        ui.label(reservation["date"] + " - " + reservation["time_slot"])
                        ui.label(reservation["band"])  # Add group name here


@ui.page("/main/reservations")
async def reservations():
    with ui.header():
        # Center name vertically
        ui.label(app.storage.user.get("name")).style('margin-left: auto; line-height: 38px;')
        ui.button("Atsijungti", on_click=lambda: ui.open("/logout")).style('margin-right: auto;')
        ui.button("Keisti rezervacijas", on_click=lambda: ui.open("/main")).style('margin-right: auto;')

    with ui.row().style("/*center div*/ margin: auto; text-align: center;") as row:
        ui.button("Grįžti", on_click=lambda: ui.open("/main")).style('margin: auto;')
        txt=ui.label("Mano rezervacijos").style(
            "font-size: 30px; font-weight: bold; width: 100%; margin: auto; text-align: center;")
        visible = False
        for room in rooms:
            for reservation in app.storage.general.get("reservations_" + room, []):
                if reservation["user"] == app.storage.user.get("name"):
                    with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
                        ui.label("Patalpa " + room + " - " + reservation["date"] + " - " + reservation["time_slot"])
                        ui.link("Atšaukti", "/cancel?room=" + room + "&date=" + reservation["date"] + "&time_slot=" + reservation["time_slot"])
                        visible = True
        if not visible:
            txt.style("display: none;")
            ui.label("Rezervacijų nėra").style(
            "font-size: 30px; font-weight: bold; width: 100%; margin: auto; text-align: center;")

    return


@ui.page("/reserve")
async def reserve(room: str):
    if room not in rooms:
        return RedirectResponse(url="/main")

    already_reserved = app.storage.general.get("reservations_" + room, [])
    today = datetime.datetime.now()
    dates = []

    def reserve_room():
        print([picker.value])
        app.storage.general["reservations_" + room] = already_reserved + [
            {"date": picker.value, "time_slot": time_slot.value, "user": app.storage.user.get("name"), "band": band_name.value}]
        ui.open("/reserved?room=" + room + "&date=" + picker.value + "&time_slot=" + time_slot.value)

    for date in range(0, 31):
        already_reserved_dates = [reservation["date"] for reservation in already_reserved]
        if (today + datetime.timedelta(days=date)).strftime("%Y-%m-%d") not in already_reserved_dates:
            dates.append((today + datetime.timedelta(days=date)))

    date_options = ":options=\"[" + ", ".join(["'" + date.strftime("%Y/%m/%d") + "'" for date in dates]) + "]\""

    with ui.header():
        # Center name vertically
        ui.label(app.storage.user.get("name")).style('margin-left: auto; line-height: 38px;')
        ui.button("Atsijungti", on_click=lambda: ui.open("/logout")).style('margin-right: auto;')

    with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
        ui.label("Rezervuoti " + room).style(
            "font-size: 30px; font-weight: bold; width: 100%; margin: auto; text-align: center;")
    with ui.column().style("/*center div*/ margin: auto; text-align: center;"):
        # Calendar
        ui.label("Pasirinkite datą:").style("margin: auto; text-align: center;")
        picker = ui.date(dates[0].strftime("%Y-%m-%d")
                         ).style("margin: auto; text-align: center;").props(date_options)

        with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
            ui.label("Pasirinkite laiko tarpą:").style("margin: auto; text-align: center;")
            available_time_slots = [slot for slot in time_slots if slot not in [reservation["time_slot"] for reservation in already_reserved if reservation["date"] == picker.value]]
            time_slot = ui.select(options=available_time_slots).style("margin: auto; text-align: center;")

        with ui.column().style("/*center div*/ margin: auto; text-align: center;"):
            ui.label("Įveskite grupės pavadinimą:").style("margin: auto; text-align: center;")
            band_name = ui.input().style("margin: auto; text-align: center;")

        with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
            ui.button("Rezervuoti", on_click=reserve_room)


@ui.page("/reserved")
async def reserved(room: str, date: str, time_slot: str):
    return RedirectResponse(url="/main")


@ui.page("/cancel")
async def cancel(room: str, date: str, time_slot: str):
    if room not in rooms:
        return RedirectResponse(url="/main")
    reservations = app.storage.general.get("reservations_" + room, [])
    for reservation in reservations:
        if reservation["date"] == date and reservation["time_slot"] == time_slot and reservation["user"] == app.storage.user.get("name"):
            reservations.remove(reservation)
            app.storage.general["reservations_" + room] = reservations

    return RedirectResponse(url="/")


@ui.page("/logout")
async def logout():
    app.storage.user.clear()
    return RedirectResponse(url="/")


ui.run()

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


@ui.page("/")
async def index():
    return RedirectResponse(url="/main")


@ui.page("/main")
async def main():
    with ui.header():
        # Center name vertically
        ui.label(app.storage.user.get("name")).style('margin-left: auto; line-height: 38px;')
        ui.button("Atsijungti", on_click=lambda: ui.open("/logout")).style('margin-right: auto;')

    with ui.row().style("/*center div*/ margin: auto; text-align: center;") as row:
        ui.label("Mano rezervacijos").style(
            "font-size: 30px; font-weight: bold; width: 100%; margin: auto; text-align: center;")
        visible = False
        for room in rooms:
            for reservation in app.storage.general.get("reservations_" + room, []):
                if reservation["user"] == app.storage.user.get("name"):
                    with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
                        ui.label("Patalpa " + room + " - " + reservation["date"])
                        ui.link("Atšaukti", "/cancel?room=" + room + "&date=" + reservation["date"])
                        visible = True
        if not visible:
            row.style("display: none;")

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
            {"date": picker.value, "user": app.storage.user.get("name")}]
        ui.open("/reserved?room=" + room + "&date=" + picker.value)

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
    with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
        # Calendar
        ui.label("Pasirinkite datą:").style("margin: auto; text-align: center;")
        picker = ui.date(dates[0].strftime("%Y-%m-%d")
                         ).style("margin: auto; text-align: center;").props(date_options)

        with ui.row().style("/*center div*/ margin: auto; text-align: center;"):
            ui.button("Rezervuoti", on_click=reserve_room)


@ui.page("/reserved")
async def reserved(room: str, date: str):
    return RedirectResponse(url="/main")


@ui.page("/cancel")
async def cancel(room: str, date: str):
    if room not in rooms:
        return RedirectResponse(url="/main")
    reservations = app.storage.general.get("reservations_" + room, [])
    for reservation in reservations:
        if reservation["date"] == date and reservation["user"] == app.storage.user.get("name"):
            reservations.remove(reservation)
            app.storage.general["reservations_" + room] = reservations

    return RedirectResponse(url="/")


@ui.page("/logout")
async def logout():
    app.storage.user.clear()
    return RedirectResponse(url="/")


ui.run()

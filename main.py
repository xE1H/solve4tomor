from nicegui import app, ui, Client
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

import datetime

# Date 30 days in advance

app.add_middleware(SessionMiddleware, secret_key="asdasdasda")


@ui.page("/")
async def index():
    if not app.storage.user.get("name"):
        return RedirectResponse(url="/login")


@ui.page("/main")
async def main():
    with ui.row():
        ui.label("Rezervavimo sistema (change me)").style(
            "font-size: 30px; font-weight: bold; /*center*/ margin: auto; text-align: center;")
    with ui.row().style("/*center div*/ margin: auto; text-align: center;") as calendar_row:
        # Calendar
        ui.label("Pasirinkite datą:").style("margin: auto; text-align: center;")
        ui.date([{"from": datetime.date.today().strftime("%Y-%m-%d"),
                  "to": (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-$d")}],
                on_change=lambda x: print(x)).style(
            "margin: auto; text-align: center;")

    with ui.row().style("/*center div*/ margin: auto; text-align: center;") as time_row:
        # Time
        ui.label("Pasirinkite laiką:").style("margin: auto; text-align: center;")
        ui.label("2023-32-32").style("margin: auto; text-align: center;")
        ui.time([{"from": "08:00", "to": "20:00"}], on_change=lambda x: print(x)).style(
            "margin: auto; text-align: center;")

    with ui.row():
        ui.button("Rezervuoti")


@ui.page("/login")
async def login():
    return RedirectResponse(url="???")


@ui.page("/logout")
async def logout():
    app.storage.user.clear()
    return RedirectResponse(url="/")


ui.run()

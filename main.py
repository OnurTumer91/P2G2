from fastapi import FastAPI, HTTPException, Query # Importerar nödvändiga moduler, Query används för att skicka query parametrar
from pydantic import BaseModel # Importerar BaseModel från pydantic för att skapa datamodeller
from typing import List, Optional # List och Optional från typing för att kunna använda dessa datatyper
from datetime import datetime 
 
app = FastAPI()
 
# Datamodeller, mallar för hur data ska se ut
class ShowTime(BaseModel):
    time: datetime
 
class Movie(BaseModel):
    id: int
    title: str
    description: str
    showtimes: List[ShowTime] = []
 
class Booking(BaseModel):
    movie_id: int
    showtime: ShowTime
    seat_number: int
    id: Optional[int] = None

# Databaser 
movies_db = [
    Movie(id=1, title="Gladiator", description="Follow Maximus on his quest for vengance and survival. ", showtimes=[ShowTime(time=datetime(2024, 11, 8, 12, 0))]),
    Movie(id=2, title="Titanic", description="Rose from first class meets Jack from the third class on board of the Titanic.", showtimes=[ShowTime(time=datetime(2024, 11, 10, 12, 0))]),
    Movie(id=3, title="Lord of the rings", description="A fellowship embarking on an epic adventure to destroy the one ring.", showtimes=[ShowTime(time=datetime(2024, 11, 11, 12, 0))])
]
 
bookings_db: List[Booking] = []
next_booking_id = 1
 
@app.get("/movies", response_model=List[Movie])
def get_movies(date: Optional[datetime] = Query(None)): 
    # Om ett datum skickas med i requestet så filtreras filmerna efter detta datum
    if date:
        available_movies = []
        for movie in movies_db:
            available_showtimes = [showtime for showtime in movie.showtimes if showtime.time.date() == date.date()]
            # Om det finns visningstider för filmen på det angivna datumet så läggs filmen till i listan
            if available_showtimes:
                available_movies.append(Movie(id=movie.id, title=movie.title, description=movie.description, showtimes=available_showtimes))
        # Returnerar en lista med filmer som har visningstider på det angivna datumet
        return available_movies
    # Om inget datum skickas med i requestet så returneras alla filmer
    return movies_db
 
# Skapar en ny bokning
@app.post("/bookings", response_model=Booking, status_code=201)
def create_booking(booking: Booking):
    global next_booking_id
 
    # Söker efter filmen som matchar bokningens movie_id i filmdatabasen
    movie = next((m for m in movies_db if m.id == booking.movie_id), None)
    if not movie: # skriver ut ett 404 meddelande om ingen film hittas
        raise HTTPException(status_code=404, detail="Movie not found")
    # kontrollerar om den valda visningstiden finns för den valda filmen
    if booking.showtime not in movie.showtimes:
        raise HTTPException(status_code=404, detail="Showtime not found")
 
    # Kontrollera om sätet är bokat för samma film med samma visningstid
    if any(b.seat_number == booking.seat_number and b.showtime == booking.showtime and b.movie_id == booking.movie_id for b in bookings_db):
        raise HTTPException(status_code=400, detail="Seat is already booked for this showtime")
 
    # Skapar ett nytt bokningsobjekt 
    booking_with_id = Booking(id=next_booking_id, movie_id=booking.movie_id, showtime=booking.showtime, seat_number=booking.seat_number)
    # lägger till det nya objektet i databasen för bokningar
    bookings_db.append(booking_with_id)
    # ökar värdet med 1 för det unika ID:t
    next_booking_id += 1
    # returnerar en lyckad bokning till klienten
    return booking_with_id
 
# Hämtar alla bokningar 
@app.get("/bookings", response_model=List[Booking])
def get_bookings():
    # Returnerar alla bokningar
    return bookings_db

# Tar bort en bokning 
@app.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(booking_id: int): # Tar emot ett boknings ID som parameter
    # Söker efter bokningen i databasen
    global bookings_db
    booking = next((b for b in bookings_db if b.id == booking_id), None)
    # Om ingen bokning hittas så skickas ett 404 meddelande
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    # Tar bort bokningen från databasen
    bookings_db = [b for b in bookings_db if b.id != booking_id]
    return {"detail": "Booking deleted"}
 
if __name__ == "__main__":
    import uvicorn # Importerar uvicorn för att kunna köra appen
    uvicorn.run(app, host="127.0.0.1", port=8000)
 


"""
Curl kommandon för att testa API:et

---------------Get movies after specific date/time--------------
curl -Method 'GET' `
  -Uri 'http://127.0.0.1:8000/bookings' `
  -Headers @{
    'accept' = 'application/json'
  }



 --------------Delete booking #1 ----------------
 curl -Method 'DELETE' `
  -Uri 'http://127.0.0.1:8000/bookings/1' `
  -Headers @{
    'accept' = 'application/json'
  }

 

--------------Create a new booking-------------
curl -Method 'POST' `
  -Uri 'http://127.0.0.1:8000/bookings' `
  -Headers @{
    'accept' = 'application/json'
    'Content-Type' = 'application/json'
  } `
  -Body '{
  "movie_id": 1,
  "showtime": {
    "time": "2024-11-08T12:00:00"
  },
  "seat_number": 1
}'


"""
import requests
 
# Base URL -> Redirect to localhost where FastAPI is running
BASE_URL = "http://127.0.0.1:8000"
 
 #____________Fetch all movies from the server via BASE_URL/movies___________________#
def list_movies():
 
    # Send a GET request to fetch all movies from the server
    response = requests.get(f"{BASE_URL}/movies")
    if response.status_code == 200:
        movies = response.json()
        #If sucesfull list all movies 
 
        # Loop through each movie and display its details
        for movie in movies:
            print(f"\nID: {movie['id']}") #The main attribute used for booking
            print(f"Title: {movie['title']}") 
            print(f"Description: {movie['description']}")
 
            print("Showtimes:")
            # Loop through each showtime, displaying it with an index number
            # Adding 1 to the index to make it 1-based for user-friendliness
            for index, showtime in enumerate(movie['showtimes']):
            #Enumerate to get the index of all the showtimes
                print(f" {index + 1}. {showtime['time']}")
        print("\n------ End of Movies List ------\n")
    else:
        print("Could not retrieve movies list.")
 
#_____________Create a booking_____________#
def create_booking():
    # First, fetch the list of movies to show to the user
    response = requests.get(f"{BASE_URL}/movies")
    if response.status_code != 200:
        print("Could not retrieve movies list.")
        return
 
    movies = response.json()
    #Present all movies to the user
 
    # Display each movie with its ID so the user can choose one by entering the ID
    for movie in movies:
        print(f"{movie['id']}: {movie['title']}")
 
    try:
        # Ask the user to enter the Movie ID they want to book
        movie_id = int(input("\nEnter the Movie ID to book: "))
        selected_movie = next((m for m in movies if m['id'] == movie_id), None)
        #Goes through the list of movies and tries to find the movie with the entered ID
 
        # If no movie is found with that ID, inform the user and return
        if not selected_movie:
            print("Invalid Movie ID.")
            return
 
        # If there are no showtimes for the selected movie, inform the user
        if not selected_movie['showtimes']:
            print("No available showtimes for this movie.")
            return
 
        #If there is a match print out the showtimes available for the selected movie
        print(f"\nShowtimes for '{selected_movie['title']}':")
        for index, showtime in enumerate(selected_movie['showtimes']):
            print(f" {index + 1}. {showtime['time']}")
            #Enumerate to present the index of the showtimes neatly
 
        #Prompt user to select an available showtime.
        showtime_index = int(input("Select a showtime by number: ")) - 1
 
        #Error hndeling if selected showtime option is bello 0 or above available showtimes
        if showtime_index < 0 or showtime_index >= len(selected_movie['showtimes']):
            print("Invalid showtime selection.")
            return
 
        # Get the selected showtime object using the index and store it in showtime for later use
        showtime = selected_movie['showtimes'][showtime_index]
 
        # Ask the user to enter a seat number for their booking and store it in seat_number
        seat_number = int(input("Enter Seat Number: "))
 
        # Prepare the booking data with the movie ID, chosen showtime, and seat number
        booking_data = {
            "movie_id": movie_id,
            "showtime": showtime,
            "seat_number": seat_number
        }
 
        # Send the booking data to the server to create a new booking
        response = requests.post(f"{BASE_URL}/bookings", json=booking_data)
        if response.status_code == 201:
            booking = response.json()
            booking = response.json()
            print(f"\nBooking created successfully! Booking ID: {booking['id']}\n")
        else:
            print(f"Failed to create booking: {response.json().get('detail', 'Unknown error')}")
 
    except ValueError:
        print("Invalid input. Please enter numbers where required.")
 
#____________Delete a booking______________#
def delete_booking(booking_id):
    url = f'{BASE_URL}/bookings/{booking_id}'
    response = requests.delete(url) 
    #DELETE /bookings/{booking_id}
 
    # Check if deletion was successful with a 204 No Content response
    if response.status_code == 204:
        print("Booking canceled successfully.")
    else:
        try:
            # Handle cases where the response might include an error message
            if response.headers.get('Content-Type') == 'application/json':
                error_message = response.json().get('detail', 'Unknown error')
            else:
                error_message = response.text
            print(f"Failed to delete booking: {error_message}")
        except requests.exceptions.JSONDecodeError:
            # Catch case where response is empty or invalid JSON
            print("Failed to delete booking: Received an invalid or empty response from the server.")
 
#___________List all current bookings______#
def list_bookings():
    # Send a GET request to fetch all bookings
    response = requests.get(f"{BASE_URL}/bookings")
    if response.status_code == 200:
        bookings = response.json()
 
        # Loop thru each booking and display its details
        for booking in bookings:
            print(f"\nBooking ID: {booking['id']}")
            print(f"Movie ID: {booking['movie_id']}")
            print(f"Showtime: {booking['showtime']['time']}")
            print(f"Seat Number: {booking['seat_number']}")
        print("\n------ End of Bookings List ------\n")
    else:
        print("Could not retrieve bookings list.")
 
#_____________Main menu loop_______________#
def main():
    #Loop through until the user chooses exit.
    while True:
        print("\n--- Movie Booking CLI ---")
        print("1. List Movies")
        print("2. Create a Booking")
        print("3. Delete a Booking")
        print("4. List All Bookings")
        print("5. Exit")
 
        # Get the users choice as input
        choice = input("Choose an option (1-5): ")
 
        # Call the relevant function based on the users choice
        if choice == "1":
            #GET /movies
            list_movies()
        elif choice == "2":
            #POST /bookings
            create_booking()
        elif choice == "3":
            # Ask user for booking_id to be able to delete correct reservation
            try:
                booking_id = int(input("Enter the Booking ID to delete: "))
                #DELETE /bookings/{booking_id}
                delete_booking(booking_id)
            except ValueError:
                print("Invalid input. Please enter a valid booking ID.")
        elif choice == "4":
            #GET /bookings
            list_bookings()
        elif choice == "5":
            print("Exiting...")
            #Break the loop
            break
        else:
            print("Invalid choice. Please select a number between 1 and 5.")
 
 
# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
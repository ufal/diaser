def get_ontology_unifier(dataset_name, domains=None):
    return {'schema': SchemaGuidedOntologyUnifier(domains),
            'multiwoz': MultiWOZOntologyUnifier(domains),
            'dstcamrest': DSTCCamRestOntologyUnifier(domains),
            }[dataset_name]


class OntologyUnifier():

    def __init__(self, domains, remove_underscores=True):
        super(OntologyUnifier, self).__init__()
        self._domains = domains
        self._domain_mapping = {}
        self._slot_mapping = {}
        self._intent_mapping = {}
        self._remove_underscores = remove_underscores

    def _init_mappings(self):

        # substitute "_" with " " in domain and slot names
        if self._remove_underscores:

            new_domain_mapping = {}
            for k in self._domain_mapping.keys():
                new_domain_mapping[k.replace("_", " ")] = self._domain_mapping[k]
            self._domain_mapping = new_domain_mapping

            new_slot_mapping = {}
            for k, v in self._slot_mapping.items():
                new_slot_mapping[k] = v.replace("_", " ")
            self._slot_mapping = new_slot_mapping

        if self._domains is not None:
            # filter out unwanted target domains
            new_mapping = {}
            for k in self._domains:
                if k in self._domain_mapping.keys():
                    new_mapping[k] = self._domain_mapping[k]
        else:
            # get list of actual target domains
            self._domains = list(self._domain_mapping.keys())

        # prepare mappings
        self._original_domains = sum(self._domain_mapping.values(), [])
        self._original_new_domain_mapping = {x: key for key, value in self._domain_mapping.items() for x in value}

    def get_domains(self):
        return self._domains

    def get_original_domains(self):
        return self._original_domains

    def map_domain(self, original_domain):
        if original_domain in self._original_new_domain_mapping:
            return self._original_new_domain_mapping[original_domain]
        else:
            return original_domain
    def is_domain(self,domain):
        if domain in self._original_new_domain_mapping:
            return True
        for dom in self._original_new_domain_mapping:
            if  self._original_new_domain_mapping[dom] == domain :
                return True
        return False
    def map_domain_reverse(self, mapped_domain):
        return self._domain_mapping[mapped_domain]

    def map_intent(self,mapped_intent,service):
        if mapped_intent in self._intent_mapping:
            return self._intent_mapping[mapped_intent]
        else:
            return mapped_intent


    def map_slot(self, original_slot,origin=""):
        if original_slot in self._slot_mapping:
            return self._slot_mapping[original_slot]
        else:
            unknown = True

            if self._remove_underscores:
                slot = original_slot.replace("_", " ")
            else:
                slot = original_slot.replace(' ', '_')
            for elem in self._slot_mapping:
                if slot == self._slot_mapping[elem] :
                    unknown = False
                    return slot


            return slot


class MultiWOZOntologyUnifier(OntologyUnifier):



    def __init__(self, domains):
        OntologyUnifier.__init__(self, domains)
        self._remove_underscores = False

        # see schema_guided_dataloader.py for a complete list of domains
        self._domain_mapping = {
            'hotel': ['Hotels_1', 'Hotels_2', 'Hotels_3', 'Hotels_4'],
            'train': ['Trains_1'],
            'attraction': ['Travel_1'],
            'restaurant': ['Restaurants_1', 'Restaurants_2'],
            'taxi': ['RideSharing_1', 'RideSharing_2'],
            'bus': ['Buses_1', 'Buses_2', 'Buses_3'],
            'flight': ['Flights_1', 'Flights_2', 'Flights_3', 'Flights_4'],
            'music': ['Music_1', 'Music_2', 'Music_3'],
            'movie': ['Media_1', 'Media_2', 'Media_3', 'Movies_1', 'Movies_2', 'Movies_3'],
            'service': ['Services_1', 'Services_2', 'Services_3', 'Services_4'],
            'bank': ['Banks_1', 'Banks_2', 'Payment_1'],
            'event': ['Events_1', 'Events_2', 'Events_3'],
            'rentalcar': ['RentalCars_1', 'RentalCars_2', 'RentalCars_3'],
            'apartment': ['Homes_1', 'Homes_2'],
            'calendar': ['Calendar_1'],
            'weather': ['Weather_1'],
            'alarm': ['Alarm_1'],
            'messaging': ['Messaging_1'],
            "hospital":["hospital"]
        }

        self._slot_mapping = {
            'star_rating': 'stars',
            'arriveby':'end_time',
            'number_of_days': 'book_stay',
            'has_wifi': 'internet',
            'check_in_date': 'check_in',  # date ?
            'street_address': 'address',
            'phone_number': 'phone',
            'price_per_night': 'price',
            'stay_length': 'book_stay',
            'where_to': 'destination',
            'check_out_date': 'check_out',
            'journey_start_time': 'start_time',
            'to': 'destination',
            'from': 'departure',
            'category': 'type',
            'number_of_riders': 'book_people',
            'from_location': 'departure',
            'to_location': 'destination',
            'leaving_time': 'start_time',
            'leaving_date': 'start_date',
            'travelers': 'book_people',
            'origin': 'departure',
            'show_type': 'genre',
            'departure_time': 'start_time',
            'group_size': 'book_people',
            'departure_date': 'start_date',
            'from_city': 'departure',
            'to_city': 'destination',
            'price_range': 'price_range',
            'cuisine': 'food',
            'track': 'song_name',
            'cast': 'starring',
            'title': 'name',
            'directed_by': 'director',
            'device': 'playback_device',
            'outbound_departure_time': 'start_time',
            'inbound_departure_time': 'start_time',
            'number_checked_bags': 'book_people',
            'actors': 'starring',
            'recipient_account_name': 'reciever',
            'transfer_amount': 'amount',
            'receiver': 'reciever',
            'city_of_event': 'city',
            'number_of_seats': 'book_people',
            'event_type': 'type',
            'car_type': 'car',
            'pickup_date': 'start_date',
            'pickup_location': 'departure',
            'total_price': 'price',
            'dropoff_location': 'destination',
            'dropoff_date': 'end_date',
            'car_name': 'car',
            "new_alarm_name": 'alarm_name',
            "new_alarm_time": "alarm_time",
            "approximate_ride_duration": "ride_duration",
            "fare": 'price',
            "fee": "price",
            'price_per_ticket': 'price',
            "flight_class": "seating_class",
            "destination_airport_name": "destination_airport",
            "origin_airport_name": "origin_airport",
            "destination_city": "destination",
            "departure_city": "departure",
            "origin_city": "departure",
            "passengers": 'book_people',
            "address_of_location": "address",
            "rent": "price",
            "number_of_tickets": "book_people",
            "price_per_day": "price",
            'pickup_time': 'start_time',
            'dropoff_time': 'end_time',
            'recipient_account_type': "reciever_account",
            "account_type": "account",
            "recipient_name": "reciever",
            "recipient": "reciever",
            "aggregate_rating": "rating",
            "return_date": "end_date",
            "party_size": "book_people",
            "subtitle_language": "subtitles",
            "average_rating": "rating",
            "pets_welcome": "pets_allowed",
            "destination_station_name": "to_station",
            "departure_station_name": "from_station",
            "origin_station_name": "from_station",
            "fare_type": "seating_class",
            "balance": "account_balance",
            "available_end_time": "end_time",
            "available_start_time": "start_time",
            "start_day":"start_day",
            "book_time":"start_time",
            "parking":"parking",
            "pricerange":"price_range",
            "book_day":"start_day",
            "area":"area",
            "leaveat":"start_time",
            "arriveby":"end_time",
            "department":"department",
            "end_time":"end_time",
            "time":"start_time",
            "year":"year",
            "ride_type":"ride_type",
            "has_vegetarian_options":"has_vegetarian_options",
            "bookday":"day",
            "booktime":"start_time",
            "bookpeople":"book_people",
            "bookstay":"book_stay"

        }
        self._intent_mapping = {
            "find_train":"train",
            "find_restaurant": "restaurant",
            "find_hotel": "hotel",
            "book_train":"train",
            "book_restaurant": "restaurant",
            "book_hotel": "hotel",
            "find_taxi":"taxi",
            "find_attraction":"attraction",
            "find_police":"police",
            "find_hospital":"hospital",
            "find_bus":"bus"
        }
        self._init_mappings()


class SchemaGuidedOntologyUnifier(OntologyUnifier):

    def __init__(self, domains):

        OntologyUnifier.__init__(self, domains)
        self._remove_underscores = False
        # see schema_guided_dataloader.py for a complete list of domains
        self._domain_mapping = {
            'hotel': ['Hotels_1', 'Hotels_2', 'Hotels_3', 'Hotels_4'],
            'train': ['Trains_1'],
            'attraction': ['Travel_1'],
            'restaurant': ['Restaurants_1', 'Restaurants_2'],
            'taxi': ['RideSharing_1', 'RideSharing_2'],
            'bus': ['Buses_1', 'Buses_2', 'Buses_3'],
            'flight': ['Flights_1', 'Flights_2', 'Flights_3', 'Flights_4'],
            'music': ['Music_1', 'Music_2', 'Music_3'],
            'movie': ['Media_1', 'Media_2', 'Media_3', 'Movies_1', 'Movies_2', 'Movies_3'],
            'service': ['Services_1', 'Services_2', 'Services_3', 'Services_4'],
            'bank': ['Banks_1', 'Banks_2', 'Payment_1'],
            'event': ['Events_1', 'Events_2', 'Events_3'],
            'rentalcar': ['RentalCars_1', 'RentalCars_2', 'RentalCars_3'],
            'apartment': ['Homes_1', 'Homes_2'],
            'calendar': ['Calendar_1'],
            'weather': ['Weather_1'],
            'alarm': ['Alarm_1'],
            'messaging': ['Messaging_1']
        }

        self._slot_mapping = {
            'star_rating': 'stars',
            'number_of_days': 'book_stay',
            'has_wifi': 'internet',
            'check_in_date': 'start_date',  # date ?
            'street_address': 'address',
            'phone_number': 'phone',
            'price_per_night': 'price',
            'stay_length': 'book_stay',
            'where_to': 'destination',
            'check_out_date': 'end_date',
            'journey_start_time': 'start_time',
            'to': 'destination',
            'from': 'departure',
            'category': 'type',
            'number_of_riders': 'book_people',
            'from_location': 'departure',
            'to_location': 'destination',
            'leaving_time': 'start_time',
            'leaving_date': 'start_date',
            'travelers': 'book_people',
            'origin': 'departure',
            'show_type': 'genre',
            'departure_time': 'start_time',
            'group_size': 'book_people',
            'departure_date': 'start_date',
            'from_city': 'departure',
            'to_city': 'destination',
            'price_range': 'price_range',
            'cuisine': 'food',
            'track': 'song_name',
            'cast': 'starring',
            'title': 'name',
            'directed_by': 'director',
            'device': 'playback_device',
            'outbound_departure_time': 'start_time',
            'inbound_departure_time': 'start_time',
            'number_checked_bags': 'book_people',
            'actors': 'starring',
            'recipient_account_name': 'reciever',
            'transfer_amount': 'amount',
            'receiver': 'reciever',
            'city_of_event': 'city',
            'number_of_seats': 'book_people',
            'event_type': 'type',
            'car_type': 'car',
            'pickup_date': 'start_date',
            'pickup_location': 'departure',
            'pickup_city': 'departure',
            "dropoff_city":"destination",
            'total_price': 'price',
            'dropoff_location': 'destination',
            'dropoff_date': 'end_date',
            'car_name': 'car',
            "new_alarm_name": 'alarm_name',
            "new_alarm_time": "alarm_time",
            "approximate_ride_duration": "ride_duration",
            "fare": 'price',
            "fee": "price",
            'price_per_ticket': 'price',
            "flight_class": "seating_class",
            "destination_airport_name": "destination_airport",
            "origin_airport_name": "origin_airport",
            "destination_city": "destination",
            "departure_city": "departure",
            "origin_city": "departure",
            "passengers": 'book_people',
            "address_of_location": "address",
            "rent": "price",
            "number_of_tickets": "book_people",
            "price_per_day": "price",
            'pickup_time': 'start_time',
            'dropoff_time': 'end_time',
            'recipient_account_type': "reciever_account",
            "account_type": "account",
            "recipient_name": "reciever",
            "recipient": "reciever",
            "aggregate_rating": "rating",
            "return_date": "end_date",
            "party_size": "book_people",
            "subtitle_language": "subtitles",
            "average_rating": "rating",
            "pets_welcome": "pets_allowed",
            "destination_station_name": "to_station",
            "departure_station_name": "from_station",
            "origin_station_name": "from_station",
            "fare_type": "seating_class",
            "balance": "account_balance",
            "available_end_time": "end_time",
            "available_start_time": "start_time",
            "time":"start_time",
            "place_name":"name",
            "number_of_rooms":"book_people",
            "smoking_allowed":"smoking_allowed",
            "check_in":"start_time",
            "year": "year",
            "artist":"artist",
            "album":"album",
            "date":"date",
            "airlines":"airlines",
            "ride_type": "ride_type",
            "add_insurance":"add_insurance",
            "has_vegetarian_options": "has_vegetarian_options",
            "has_seating_outdoors":"has_seating_outdoors",
            "num_passengers":"book_people",
            "additional_luggage":"additional_luggage",
            "new_alarm_name":"name",
            "new_alarm_time": "start_time",
            "therapist_name":"therapist_name",
            "appointment_time":"start_time",
            "appointment_date":"date",
            "is_unisex":"is_unisex",
            "stylist_name":"stylist_name",
            "number_of_baths":"number_of_baths",
            "number_of_beds":"number_of_beds",
            "intent":"operation",
            "property_name":"property_name",
            "has_garage":"has_garage",
            "visit_date":"date",
            "in_unit_laundry":"in_unit_laundry",
            "has_laundry_service":"in_unit_laundry",
            "show_date":"date",
            "show_time":"start_time",
            "show_name":"name",
            "number_of_adults":"book_people",
            "date_of_journey":"start_date",
            "trip_protection":"add_insurance",
            "class":"seating_class",
            "theater_name":"theater_name",
            "payment_method":"payment_method",
            "private_visibility":"private_visibility",
            "good_for_kids":"good_for_kids",
            "free_entry":"free_entry",
            "contact_name":"contact_name",
            "subcategory":"subcategory",
            "share_ride":"shared_ride",
            "furnished":"furnished",
            "refundable":"refundable",
            "serves_alcohol":"serves_alcohol",
            "has_live_music":"has_live_music",
            "doctor_name":"doctor_name",
            "dentist_name":"dentist_name",
            "offers_cosmetic_services":"offers_cosmetic_services",
            "event_location":"event_area",
            "bookday":"day",
            



        }


        self._intent_mapping = {
            "FindRestaurant":"restaurant",
            "FindRestaurants": "restaurant",
            "ReserveRestaurant":"restaurant",
            "SearchHotel":"hotel",
            "ReserveHotel":"hotel",
            "LookupMusic":"music",
            "PlayMedia":"music",
            "FindEvents":"event",
            "BuyEventTickets":"event",
            "SearchOnewayFlight":"flight",
            "SearchRoundtripFlights":"flight",
            "GetRide":"taxi",
            "GetCarsAvailable":"rentalcar",
            "ReserveCar":"rentalcar",
            "FindBus":"bus",
            "BuyBusTicket":"bus",
            "AddAlarm":"alarm",
            "GetAlarms":"alarm",
            "FindProvider":'service',
            "BookAppointment":"service",
            "GetWeather":"weather",
            "FindHomeByArea":"apartment",
            "ScheduleVisit":"apartment",
            "BuyMovieTickets":"movie",
            "FindTrains":"train",
            "GetTrainTickets":"train",
            "FindMovies":"movie",
            "GetTimesForMovie":"movie",
            "MakePayment":"bank",
            "SearchHouse":"hotel",
            "BookHouse": "hotel",
            "FindAttractions":'attraction',
            "RequestPayment":"bank",
            "ShareLocation":"messaging",
            "PlayMovie":"movie",
            "CheckBalance":"bank",
            "TransferMoney":"bank",
            "RentMovie":"movie",
            "FindApartment":"apartment",
            "LookupSong":"music",
            "PlaySong":"music",
            "GetEventDates":"event",
            "ReserveRoundtripFlights":"flight",
            "GetAvailableTime":"calendar",
            "ReserveOnewayFlight":"flight",
            "GetEvents":"calendar",
            "AddEvent":"calendar"



        }
        self._init_mappings()
class DSTCCamRestOntologyUnifier(OntologyUnifier):
    domains = ['restaurant']

    def __init__(self, domains):
        super(DSTCCamRestOntologyUnifier, self).__init__(domains)
        self._remove_underscores = False
        # see schema_guided_dataloader.py for a complete list of domains
        self._slot_mapping = {
            'star_rating': 'stars',
            'hotel_name': 'name',
            'number_of_days': 'book_stay',
            'number_of_adults': 'book_people',
            'post code': 'post_code',
            'postcode': 'post_code',
            'post_code': 'post_code',
            'location': 'area',
            # 'area': 'location',
            # 'type': food,
            'has_wifi': 'internet',
            'name': 'name',
            'check_in_date': 'check_in',  # date ?
            'street_address': 'address',
            'phone_number': 'phone',
            'price_per_night': 'price_range',
            'stay_length': 'stay',
            'where_to': 'destination',
            'check_out_date': 'end_date',
            'place_name': 'name',
            'journey_start_time': 'start_time',
            'to': 'destination',
            'from': 'departure',
            'category': 'type',
            'attraction_name': 'name',
            'number_of_riders': 'book_people',
            'from_location': 'departure',
            'to_location': 'destination',
            'leaving_time': 'start_time',
            'leaving_date': 'start_date',
            'travelers': 'book_people',
            'origin': 'departure',
            'departure_time': 'start_time',
            'group_size': 'book_people',
            'from_city': 'departure',
            'to_city': 'destination',
            'price_range': 'price_range',
            'cuisine': 'food',
            'restaurant_name': 'name',
            'track': 'song_name',
            'cast': 'starring',
            'title': 'name',
            'directed_by': 'director',
            'device': 'playback_device',
            'outbound_departure_time': 'start_time',
            'inbound_departure_time': 'start_time',
            'number_checked_bags': 'book_people',
            'actors': 'starring',
            'recipient_account_name': 'reciever_name',
            'transfer_amount': 'amount',
            'receiver': 'receiver_name',
            'city_of_event': 'city',
            'number_of_seats': 'book_people',
            'car_type': 'type',
            'pickup_date': 'date',
            'pickup_location': 'departure',
            'total_price': 'price',
            'dropoff_time': 'end_time',
            'dropoff_location': 'destination',
            'dropoff_date': 'end_date',
            'pickup_time': 'start_time',
            'car_name': 'car',
            'addr': 'address',
            'pricerange': 'price_range',
            'this': 'any',
            'signature': 'popular',
            'pickup_city': 'departure',
            'price_per_ticket': 'price',
            "price range":"price_range"
            
        }
        self._init_mappings()

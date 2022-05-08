from glob import glob
import sys
import json
from data_processing.ontology_unifier import get_ontology_unifier
from pprint import pprint

from word2number import w2n

cpt = 0


def preproc_slot_value(service, mapper):
    new = {}
    for slot in service:
        new_slot = mapper.map_slot(slot).replace(' ', '_')
        value = service[slot]
        value = value.lower().replace(' ', '_')
        new.update({new_slot: value})
    return new


def printing_all(ontology, domain, old_service, slot, service):
    pprint(ontology[domain])
    print(slot)
    print(old_service)
    pprint(service[slot])
    pprint(service)
    sys.exit()


def check_slot(slot, ontology, domain, service, old):
    if slot not in ontology[domain]:
        ontology[domain].update({slot: [service[old]]})
    else:
        if service[old] not in ontology[domain][slot]:
            ontology[domain][slot].append(service[old])
    if slot != old:
        service[slot] = service.pop(old)
    # print(slot)
    # print(old)


def get_info(dialog, dbs, ontology, locations, cities, areas):
    mapper = SchemaGuidedOntologyUnifier(dialog['services'])
    mapper._remove_underscores = False
    
    for turn in dialog['turns']:
        for frame in turn['frames']:
            if 'service_results' in frame:
                old_service = frame['service']
                domain = mapper.map_domain(frame['service'])
                if domain not in dbs:
                    dbs[domain] = []
                if domain not in ontology:
                    ontology[domain] = {}
                
                for service in frame['service_results']:
                    
                    service = preproc_slot_value(service, mapper)
                    tba = {}
                    if "location" in service:
                        # print(f"service location = {service['location']}")
                        service['city'] = service.pop('location')
                    if "area" in service:
                        service['city'] = service.pop('area')
                    
                    if "percent_rating" in service:
                        service["rating"] = service.pop("percent_rating")
                        slot = "rating"
                        service[slot] = str(float(service[slot]) / 10)
                    if "people" in service:
                        service["book_people"] = service.pop("people")
                    if 'Restaurants' in old_service:
                        if "time" in service:
                            service['book_time'] = service.pop('time')
                        if 'type' in service:
                            service["food"] = service.pop('type')
                    
                    if 'Services' in old_service:
                        if "city" in service:
                            service['area'] = service.pop("city")
                    elif "Events" in old_service:
                        if 'type' in service:
                            service["event_type"] = service.pop("type")
                    elif "Buses" in old_service:
                        if "type" in service:
                            service["bus_type"] = service.pop('type')
                        if "num_passengers" in service:
                            service["book_people"] = service.pop('num_passengers')
                    elif "Train" in old_service:
                        if "number_of_adults" in service:
                            service["book_people"] = service.pop('number_of_adults')
                    elif "Taxi" in old_service:
                        if "ride_fare" in service:
                            service['price'] = service.pop("ride_fare")
                    elif "Hotel" in old_service:
                        if "check_in" in service:
                            service["start_date"] = service.pop('check_in')
                        if "check_out" in service:
                            service["end_date"] = service.pop('check_out')
                        if "stay" in service:
                            service['book_stay'] = service.pop('stay')
                        
                        elif "number_of_adults" in service:
                            service["book_people"] = service.pop('number_of_adults')
                    if ontology[domain] == {}:
                        
                        for slots in service:
                            old = slots
                            check_slot(slots, ontology, domain, service, old)
                    else:
                        for slot in service:
                            old = slot
                            if slot not in ontology[domain]:
                                if old_service == 'Flights_4':
                                    if slot == 'date':
                                        slot = 'start_date'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'inbound_arrival_time' or slot == "start_date" or slot == "end_date":
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'return_date':
                                        slot = "end_date"
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "people":
                                        slot = "book_people"
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                elif old_service == 'Music_3':
                                    if slot == 'playback_device' or slot == 'artist':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                elif old_service == 'Flights_3':
                                    if slot == 'arrives_next_day' or slot == "destination" or slot == "departure" or slot == 'end_date':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "date":
                                        slot = "start_date"
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'number_of_tickets':
                                        slot = 'book_people'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'number_stops':
                                        if service[slot] == '0':
                                            tba.update({'is_nonstop': 'true'})
                                            check_slot(slot, ontology, domain, service, old)
                                        else:
                                            tba.update({'is_nonstop': 'true'})
                                            check_slot(slot, ontology, domain, service, old)
                                    # elif slot == 'type':
                                    #     slot = 'event_type'
                                    #     check_slot(slot, ontology, domain, service, old)
                                    # elif slot == 'price_per_ticket':
                                    #     slot = 'price'
                                    #     check_slot(slot, ontology, domain, service, old)
                                    
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                elif old_service == 'Flights_1':
                                    if slot == 'date':
                                        slot = "start_date"
                                        # or slot == 'start_date' or slot == 'price' or slot == 'leave_at' or slot == 'price_per_day':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "refundable" or slot == "departure":
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Flights_2':
                                    if slot == 'date':
                                        slot = "start_date"
                                        # or slot == 'start_date' or slot == 'price' or slot == 'leave_at' or slot == 'price_per_day':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "refundable" or slot == "is_redeye":
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == "Events_2":
                                    if slot == "event_name":
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Events_3':
                                    if slot == 'book_people' or slot == 'time' or slot == 'price' or slot == "event_name":
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'type':
                                        slot = 'event_type'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'price_per_ticket':
                                        slot = 'price'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Events_1':
                                    if slot == 'time' or slot == 'price' or slot == 'subcategory':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'type':
                                        slot = 'event_type'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'number_of_tickets':
                                        slot = 'book_people'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "event_location":
                                        slot = "venue"
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'address':
                                        slot = 'venue_address'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                elif old_service == 'RentalCars_3':
                                    if slot == 'add_insurance' or slot == 'start_date' or slot == 'price' or slot == 'leave_at' or slot == 'price_per_day':
                                        check_slot(slot, ontology, domain, service, old)
                                    
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'RentalCars_2':
                                    if slot == 'date':  #
                                        slot = "start_date"
                                        # or slot == 'start_date' or slot == 'price' or slot == 'leave_at' or slot == 'price_per_day':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "fee":
                                        service["fee"] = str(int(service['fee']))
                                        slot = "price"
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "leave_at":
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                elif old_service == 'RentalCars_1':
                                    # print(old_service)
                                    # print(slot)
                                    if slot == 'pickup_city' or slot == 'start_date':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'city':
                                        slot = 'pickup_city'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'type':
                                        slot = 'car_type'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'date':
                                        slot = 'start_date'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'fee':
                                        slot = 'price'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Hotels_4':
                                    if slot == 'start_date' or slot == "book_stay" or slot == 'smoking_allowed' or slot == 'has_laundry_service' or slot == 'price_range' or slot == 'price':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'name' or slot == "place_name":
                                        slot = 'hotel_name'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Hotels_1':
                                    if slot == 'check_in' or slot == 'internet' or slot == 'smoking_allowed' or slot == 'stay' or slot == 'has_laundry_service' or slot == 'price_range' or slot == 'hotel_name':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'name':
                                        slot = 'hotel_name'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Hotels_3':
                                    if slot == 'pets_allowed' or slot == 'internet' or slot == 'smoking_allowed' or slot == 'stay' or slot == 'has_laundry_service' or slot == 'price_range':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'name':
                                        slot = 'hotel_name'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                
                                elif old_service == 'Hotels_2':
                                    if slot == 'stay' or slot == 'end_date' or slot == 'has_laundry_service' or slot == 'rating' or slot == 'destination' or slot == 'book_people':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "number_of_adults":
                                        slot = "book_people"
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'fee':
                                        slot = 'price'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Media_3':
                                    if slot == 'starring' or slot == "subtitles" or slot == 'subtitle_language' or slot == 'director':
                                        
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'name':
                                        slot = 'movie_name'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Media_1':
                                    if slot == 'starring' or slot == "subtitles" or slot == 'subtitle_language' or slot == 'director':
                                        
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'name':
                                        slot = 'movie_name'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                elif old_service == 'Homes_2':
                                    if slot == 'visit_date':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "area":
                                        slot = 'city'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Homes_1':
                                    if slot == 'visit_date' or slot == 'pets_allowed' or slot == 'furnished':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "area":
                                        slot = 'city'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Services_4':
                                    if slot == 'average_rating' or slot == 'appointment_date' or slot == 'appointment_time' or slot == 'city':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                elif old_service == 'Services_2':
                                    
                                    if slot == 'dentist_name' or slot == 'offers_cosmetic_services' or slot == 'is_unisex' or slot == 'appointment_date' or slot == 'appointment_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Services_1':
                                    if slot == 'stylist_name' or slot == 'rating' or slot == 'is_unisex' or slot == 'appointment_date' or slot == 'appointment_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Services_3':
                                    if slot == 'doctor_name' or slot == 'rating' or slot == 'is_unisex' or slot == 'appointment_date' or slot == 'appointment_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                elif old_service == 'Movies_3':
                                    if slot == 'director' or slot == 'rating':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'movie_title':
                                        slot = 'movie_name'
                                        check_slot(slot, ontology, domain, service, old)
                                    
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Buses_1':
                                    if slot == 'transfers' or slot == 'leave_at' or slot == 'departure':  # or slot == 'average_rating' or slot == 'is_unisex' or slot == 'appointment_date' or slot == 'appointment_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "book_people":
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                elif 'Trains' in old_service:
                                    if slot == 'total':
                                        slot = 'price'
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                
                                elif old_service == 'Buses_2':
                                    if slot == 'transfers' or slot == "seating_class" or slot == 'leave_at' or slot == 'departure':  # or slot == 'average_rating' or slot == 'is_unisex' or slot == 'appointment_date' or slot == 'appointment_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                # elif old_service == 'Trains_1':
                                
                                elif old_service == 'Buses_3':
                                    if slot == 'additional_luggage' or slot == 'leave_at' or slot == 'departure':  # or slot == 'average_rating' or slot == 'is_unisex' or slot == 'appointment_date' or slot == 'appointment_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        check_slot(slot, ontology, domain, service, old)
                                elif old_service == 'Trains_1':
                                    if slot == 'date_of_journey':  # or slot == 'average_rating' or slot == 'is_unisex' or slot == 'appointment_date' or slot == 'appointment_time':
                                        slot = "start_date"
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Movies_1':
                                    
                                    if slot == 'book_people' or slot == 'theater_name' or slot == 'show_date' or slot == 'show_time' or slot == "city":
                                        
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'show_type':
                                        slot = 'genre'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                elif old_service == 'Movies_2':
                                    
                                    if slot == 'book_people' or slot == "rating" or slot == 'theater_name' or slot == 'show_date' or slot == 'show_time':
                                        
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'show_type':
                                        slot = 'genre'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'name':
                                        slot = "movie_name"
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Restaurants_2':
                                    if slot == 'restaurant_name' or slot == "food" or slot == 'city' or slot == 'book_people':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'name':
                                        slot = 'restaurant_name'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'type':
                                        slot = 'food'
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'book_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                elif old_service == 'Restaurants_1':
                                    if slot == 'city':
                                        check_slot(slot, ontology, domain, service, old)
                                    if slot == "serves_alcohol" or slot == "has_live_music":
                                        # or slot == 'average_rating' or slot == 'is_unisex' or slot == 'appointment_date' or slot == 'appointment_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == "time":
                                        slot = "book_time"
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                elif old_service == 'Payment_1':
                                    if slot == 'private_visibility' or slot == "reciever":  # or slot == 'average_rating' or slot == 'is_unisex' or slot == 'appointment_date' or slot == 'appointment_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        check_slot(slot, ontology, domain, service, old)
                                elif old_service == 'Banks_2':
                                    if slot == 'account_balance' or slot == 'reciever_account' or slot == "reciever" or slot == 'account' or slot == "transfer_time":  # or slot =='shared_ride' or slot =='pickup_city':
                                        check_slot(slot, ontology, domain, service, old)
                                    # elif slot == 'city':
                                    #     slot = 'pickup_city'
                                    #     check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Travel_1':
                                    if slot == 'phone' or slot == 'artist':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                elif old_service == 'Weather_1':
                                    if slot == 'wind' or slot == 'artist':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'RideSharing_2':
                                    if slot == 'artist':
                                        check_slot(slot, ontology, domain, service, old)
                                    elif slot == 'people':
                                        slot = 'book_people'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'RideSharing_1':
                                    if slot == 'ride_duration' or slot == 'shared_ride' or slot == 'pickup_city':
                                        check_slot(slot, ontology, domain, service, old)
                                    
                                    elif slot == 'people':
                                        slot = 'book_people'
                                        check_slot(slot, ontology, domain, service, old)
                                    
                                    elif slot == 'city':
                                        slot = 'pickup_city'
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                elif old_service == 'Alarm_1':
                                    if 'new' in slot:
                                        slot = slot.replace('new', '')
                                    if slot == 'alarm_name' or slot == 'alarm_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                elif old_service == 'Calendar_1':
                                    
                                    if slot == 'event_name' or slot == "start_time" or slot == "end_time" or slot == 'event_time':
                                        check_slot(slot, ontology, domain, service, old)
                                    else:
                                        printing_all(ontology, domain, old_service, slot, service)
                                
                                
                                
                                
                                ###############################"
                                else:
                                    printing_all(ontology, domain, old_service, slot, service)
                            else:
                                check_slot(slot, ontology, domain, service, old)
                    for slt in tba:
                        service.update({slt: tba[slt]})
                    if service not in dbs[domain]:
                        dbs[domain].append(service)


# def remove_minutes(value,previous):


def fill_ontology(ontology):
    for key in ontology:
        if "time" in key:
            for i in range(24):
                if i < 10:
                    hour = "0" + str(i)
                else:
                    hour = str(i)
                for j in range(60):
                    if j < 10:
                        minute = '0' + str(j)
                    else:
                        minute = str(j)
                    value = hour + ':' + minute
                    if value not in ontology[key]:
                        ontology[key].append(value)
        if "people" in key or "stay" in key:
            for j in range(50):
                if str(j) not in ontology[key]:
                    ontology[key].append(str(j))
        
        if "date" in key:
            for i in range(1, 13):
                if i < 10:
                    val = "2019-0" + str(i)
                else:
                    val = "2019-" + str(i)
                for j in range(1, 32):
                    if j < 10:
                        new = val + "-0" + str(j)
                    else:
                        new = val + "-" + str(j)
                    ontology[key].append(new)
        if "amount" in key:
            for i in range(10000):
                if str(i) not in ontology[key]:
                    ontology[key].append(str(i))
    
    json.dump(ontology, fp=open('../data/global_ontology.json', 'w'), indent=4)


def check_value(value, slot, previous, turn):
    value = value.replace('_fourty_five',':45')
    value = value.replace("o'shea","oshea")
    value = value.replace("washington_d.c.","washington")
    value = value.replace("one_o'clock_p.m","13:00")
    value = value.replace("three_forty_five_p.m","15:45")
    value = value.replace("eight_thirty","08:30")
    value = value.replace("seven_o'clock_tomorrow_evening","19:00")
    value = value.replace("half_past_one", "01:15")
    value = value.replace("half_past_1_", "01:15_")
    value = value.replace("half_past_2", "02:15")
    value = value.replace("half_past_3", "03:15")
    value = value.replace("half_past_4", "04:15")
    value = value.replace("half_past_5", "05:15")
    value = value.replace("half_past_6", "06:15")
    value = value.replace("half_past_7", "07:15")
    value = value.replace("half_past_8", "08:15")
    value = value.replace("half_past_10", "10:15")
    value = value.replace("half_past_11", "11:15")
    value = value.replace("half_past_9", "09:15")
    value = value.replace("half_past_12", "12:15")
    value = value.replace("quarter_past_1_", "01:15_")
    value = value.replace("quarter_past_2_", "02:15_")
    value = value.replace("quarter_past_3_", "03:15_")
    value = value.replace("quarter_past_4_", "04:15_")
    value = value.replace("quarter_past_5_", "05:15_")
    value = value.replace("quarter_past_6_", "06:15_")
    value = value.replace("quarter_past_7_", "07:15_")
    value = value.replace("quarter_past_8_", "08:15_")
    value = value.replace("quarter_past_9_", "09:15_")
    value = value.replace("quarter_past_10_", "10:15_")
    value = value.replace("quarter_past_11_", "11:15_")
    value = value.replace("quarter_past_12_", "12:15_")
    value = value.replace("carolina_bed_&_breakfast","carolina_bed_and_breakfast")
    value = value.replace("half_to_one", "12:45")
    value = value.replace("half_to_1_", "12:45_")
    value = value.replace("half_to_2", "01:45")
    value = value.replace("half_to_3", "02:45")
    value = value.replace("half_to_4", "03:45")
    value = value.replace("half_to_5", "04:45")
    value = value.replace("half_to_6", "05:45")
    value = value.replace("half_to_7", "06:45")
    value = value.replace("half_to_8", "07:45")
    value = value.replace("half_to_10", "09:45")
    value = value.replace("half_to_11", "10:45")
    value = value.replace("half_to_9", "08:45")
    value = value.replace("half_to_12", "11:45")
    value = value.replace("quarter_to_1_", "12:45_")
    value = value.replace("quarter_to_2_", "01:45_")
    value = value.replace("quarter_to_3_", "02:45_")
    value = value.replace("quarter_to_4_", "03:45_")
    value = value.replace("quarter_to_5_", "04:45_")
    value = value.replace("quarter_to_6_", "05:45_")
    value = value.replace("quarter_to_7_", "06:45_")
    value = value.replace("quarter_to_8_", "07:45_")
    value = value.replace("quarter_to_9_", "08:45_")
    value = value.replace("quarter_to_10_", "09:45_")
    value = value.replace("quarter_to_11_", "10:45_")
    value = value.replace("quarter_to_12_", "11:45_")
    value = value.replace("quarter_to_13", "13:45")
    value = value.replace("_o\"clock", "")
    value = value.replace("_o'clock", "")
    value = value.replace('_&_', '&')
    value = value.replace('_-_', '-')
    try:
        value = str(w2n.word_to_num(value))
    except ValueError:
        pass
    if "date" in slot:
        new = "2019-"
        if "the" in value:
            value = value.replace('the_', '')
        if "january" in value:
            new += "01-"
        
        elif "february" in value:
            new += "02-"
        
        elif "march" in value:
            new += "03-"
        
        elif "april" in value:
            new += "04-"
        
        elif "may" in value:
            new += "05-"
        
        elif "june" in value:
            new += "06-"
        
        elif "july" in value:
            new += "07-"
        
        elif "august" in value:
            new += "08-"
        
        elif "september" in value:
            new += "09-"
        
        elif "october" in value:
            new += "10-"
        
        elif "november" in value:
            new += "11-"
        
        elif "december" in value:
            new += "12-"
        else:
            new += "03-"
        if "1st" in value:
            new += "01"
            value = new
        if "2nd" in value:
            new += "02"
            value = new
        if "3rd" in value:
            new += "03"
            value = new
        minutes = ""
        for i in range(4, 32):
            
            if str(i) + "th" in value:
                if i < 10:
                    minutes = "0" + str(i)
                else:
                    minutes = str(i)
        new += minutes
        if new.endswith("-"):
            new += "10"
        
        value = new
    
    if "of_this_month" in value:
        value = value.replace("_of_this_month", '')
        if value.endswith("th"):
            if "the" not in value:
                value = "the_" + value
    if value == "nightclub":
        value = "night_club"
    if value == "swimmingpool":
        value = "swimming_pool"
    if value == "cambridge_museum_of_tech":
        value = "cambridge_museum_of_technology"
    if "fen_ditton" in value and 'express' not in value:
        value = value.replace('fen_ditton', "fenditton")
    if "lensfield" in value:
        value = "lensfield_hotel"
    if "cherry_hilton" in value:
        value = value.replace("hilton", "hinton")
    if value == "rosa's":
        value = "rosas_bed_and_breakfast"
    if value == "churchill_college":
        value = "churchills_college"
    if value == "the_huntingdon_marriott_hotel":
        value = "huntingdon_marriott_hotel"
    if value == "olds_schools":
        value = "old_schools"
    if value == "butterfly":
        value = "butterfly_restaurant"
    if value == "stazione":
        value = "stazione_restaurant_and_coffee_bar"
    
    if value == "the_alexander_bed_and_breakfast" or value =="alexander_b&b" or value == "alexander_b_&_b":
        value = "alexander_bed_and_breakfast"
    if 'taondoori' in value:
        value = value.replace('taondoori', 'tandoori')
    if value == "an_hour_earlier" or value == "one_hour_earlier":
        print(previous)
        hours = int(previous.split(':')[0]) - 1
        value = str(hours) + ':' + previous.split(':')[1]
    if "time" in slot:
        value = value.replace("one_o'clock", "01:00")
        value = value.replace("two_o'clock", "02:00")
        value = value.replace("three_o'clock", "03:00")
        value = value.replace("four_o'clock", "04:00")
        value = value.replace("five_o'clock", "05:00")
        value = value.replace("six_o'clock", "06:00")
        value = value.replace("seven_o'clock", "07:00")
        value = value.replace("eight_o'clock", "08:00")
        value = value.replace("nine_o'clock", "09:00")
        value = value.replace("ten_o'clock", "10:00")
        value = value.replace("eleven_o'clock", "11:00")
        value = value.replace("twelve_o'clock", "12:00")
        value = value.replace("one", "01")
        value = value.replace("two", "02")
        value = value.replace("three", "03")
        value = value.replace("four", "04")
        value = value.replace("five", "05")
        value = value.replace("six", "06")
        value = value.replace("seven", "07")
        value = value.replace("eight", "08")
        value = value.replace("nine", "09")
        value = value.replace("ten", "10")
        value = value.replace("eleven", "11")
        value = value.replace("twelve", "12")
        value = value.replace('?', '')
        value = value.replace('by_', '')
        
        if len(value) == 1:
            value = "0" + value + ":00"
        elif 'after' in value or 'afer':
            value = value.replace("after_", '').replace('afer_', '')
        if ',' in value:
            value = value.replace(',', '')
        if len(value) == 4:
            value = '0' + value
        elif len(value) == 2:
            value = value + ':00'
    if value == "quarter_past_5_in_the_evening":
        value = "17:15"
    if "marriot_" in value:
        value = value.replace('marriot', 'marriott')
    if value == "finches":
        value = "finches_bed_and_breakfast"
    if value == "one_o'clock_p.m":
        value = "13:00"
    if value == "three_forty_five_p.m." or value == "three_forty_five_p.m":
        value = "15:45"
    if value == "one_thirty_p.m.":
        value = "13:30"
    if (value.endswith('pm') or value.startswith('evening_') or value.startswith('night_') or value.startswith(
            'afternoon_') or value.startswith(
        "morning_") or value.endswith('am') or value.endswith('a.m') or value.endswith(
        '_in_the_afternoon') or value.endswith('_in_the_night') or value.endswith(
        '_in_the_evening') or value.endswith("_in_the_morning") or (
                value.endswith('p.m.') and value != "one_o'clock_p.m." and value !="one_o'clock_p.m")) and "time" in slot:
        if value == "fitzwilliam":
            return value
        
        if ':' in value:
            if "evening_" not in value and "afternoon_" not in value and "morning_" not in value and "night_" not in value:
                hours = value.split(':')[0]
            
            else:
                hours = value.split(':')[0].split('_')[1]
        elif '_' in value and "evening" not in value and "afternoon" not in value and "morning_" not in value and "night_" not in value:
            hours = value.split('_')[0]
        else:
            hours = value.replace('pm', '').replace('am', '').replace('p.m.', '').replace("_in_the_night", "").replace(
                'evening_', '').replace('_in_the_afternoon', "").replace("_in_the_evening", "").replace("afternoon_",
                                                                                                        "").replace(
                "morning_", "").replace("_in_the_morning", "").replace('night_', "")
        inthour = int(hours)
        if "pm" in value or 'p.m.' in value or "_in_the_night" in value or "afternoon_" in value or "_in_the_evening" in value or 'evening_' in value or "_in_the_afternoon" in value or "night_" in value:
            if inthour < 13:
                inthour += 12
        value = value.replace('pm', '')
        value = value.replace('am', '')
        value = value.replace('a.m', '')
        value = value.replace('p.m.', '')
        value = value.replace('_in_the_night', '')
        value = value.replace('_in_the_evening', '')
        value = value.replace('evening_', '')
        value = value.replace('afternoon_', '')
        value = value.replace("morning_", "")
        value = value.replace("_in_the_afternoon", "")
        value = value.replace("_in_the_morning", "")
        value = value.replace('_', '')
        value = value.replace('night_', '')
        if ':' in value:
            value = str(inthour) + ':' + value.split(':')[1]
        else:
            value = str(inthour) + ':00'
        value = value.replace("24:", "00:")
        if len(value) < 5:
            value = "0" + value
    if value.endswith('.'):
        value = value.replace('.', '')
    if value == "lunch" or value == "mid-day" or value == "around_lunch_time":
        value = "12:00"
    if value == "six_fourty_five":
        value = "18:45"
    if value == "eight_thirty":
        value = "18:30"
    
    if value == "seven_o'clock_tomorrow_evening":
        value = "19:00"
    if "s'" in value:
        value = value.replace("'", '')
    if value == "ten_o'clock_a.m":
        value = "10:00"
    if value == "an_hour_later":
        hours = int(previous.split(':')[0]) + 1
        value = str(hours) + ':' + previous.split(':')[1]
    if "fifteen_minutes_earlier" in value:
        hours = int(previous.split(':')[0])
        minutes = int(previous.split(':')[1])
        rest = minutes - 15
        if rest >= 0:
            if rest < 10:
                rest = '0' + str(0)
            else:
                rest = str(rest)
            value = str(hours) + ':' + rest
        else:
            hours -= 1
            minutes = 60 + rest
            value = str(hours) + ':' + str('minutes')
    if "30_min_earlier" in value:
        hours = int(previous.split(':')[0])
        minutes = int(previous.split(':')[1])
        rest = minutes - 30
        if rest >= 0:
            if rest < 10:
                rest = '0' + str(0)
            else:
                rest = str(rest)
            value = str(hours) + ':' + rest
        else:
            hours -= 1
            minutes = 60 + rest
            value = str(hours) + ':' + str('minutes')
    
    if value == "the_one_in_the_north" or value == "the_other_oriental_restaurant":
        value = "unknown"
    if "kymmoy" in value:
        value = "kymmoy"
    if value == "the_river_bar":
        value = "the_river_bar_steakhouse_and_grill"
    if value == "the_ghandi":
        value = "the_ghandhi"
    if value == "huntington" or value == "marriott_hotel":
        value = "huntington_marriott_hotel"
    if value == "a_and_b":
        value = "a_and_b_guesthouse"
    if value == "lovell":
        value = "lovell_lodge"
    if value == "an_hour_earlier_or_an_hour_later":
        value = previous
    if value == "alexander_b_&_b":
        value = "alexander_bed_and_breakfast"
    if value == "astropub":
        value = "gastropub"
    if value == "indiian":
        value = "indian"
    if value == "roses_bed_and_breakfast":
        value = "rosas_bed_and_breakfast"
    if value == "wagamana":
        value = "wagamama"
    if value == "academy_bar":
        value = "academy_bar_and_kitchen"
    if value == "meghan" or value == "meghana":
        value = "meghna"
    if value == "avolon":
        value = "avalon_hotel_paris_gare_du_nord"
    if value == "archyway_house":
        value = "archway_house"
    if value == "eurology":
        value = "urology"
    if value == "portugeuese":
        value = "portuguese"
    if value == "eriterean":
        value = "eritrean"
    if value == "la_tasce":
        value = "la_tasca"
    if value == "polunesian":
        value = "polynesian"
    if value == "muslim":
        value = "halal"
    if value == "grafitti":
        value = "graffiti"
    if value == "before_our_reservation_time":
        value = previous
    if value == "antolia":
        value = "anatolia"
    if value == "italian_one":
        value = "unknown"
    if value == "mi_zacatecas":
        value = "mi_zacatecas_family_restaurant"
    if value == "benissimo":
        value = "benissimo_restaurant&bar"
    if value == "pizza_hut_cherry":
        value = "pizza_hut_cherry_hinton"
    if value == "pizza_hut_in_the_city_center":
        value = "pizza_hut"
    if value == "regent":
        value = "regent_thai"
    if value == "yin_keng":
        value += "_restaurant"
    if value == "tandoori_mahal":
        value = "tandoori_mahal_indian_restaurant"
    if value == "castle_rock":
        value += "_restaurant"
    if value == "anatolian":
        value += "_kitchen"
    if value == "pearl_garden":
        value += "_restaurant"
    if value == "le_petit":
        value += "_bistro"
    if value == "b&b_kitchen":
        value += "&wine_bar"
    if value == "gios_pizza":
        value += "_and_bocce"
    if value == "genghix":
        value += "_asian_fusion"
    if value == "miramar_beach":
        value += "_restaurant"
    if value == "priya":
        value += "_indian_cuisine"
    if value == "roppongi":
        value += "_sushi"
    
    if value == "yes":
        value = "true"
    if value == "no":
        value = "false"
    value = value.replace("carolina_bed_&_breakfast", "carolina_bed_and_breakfast")
    value = value.replace("michael_house_cafe", "michaelhouse_cafe")
    if "huntingdon" in value:
        value = value.replace("huntingdon", "huntington")
        if "hotel" not in value:
            value += "_hotel"
    if value == "itermediate_deoendancy_area_department":
        value = "intermediate_dependancy_area"
    
    if "city" in slot or 'airport' in slot or "destination" in slot or "departure" in slot or "area" in slot:
        value = value.replace("_d.c.","")
        if value == "sf" or value == "san_fran" or value == "sfo":
            value = "san_francisco"
        if value == "la" or value == "lax":
            value = "los_angeles"
        if value == "olemalifornia":
            value = "olema"
        if value == "dc":
            value = "washington"
        if value == "chi-town":
            value = "chicago"
        if value == "ny" or value == "nyc" or value == "new_york_city":
            value = "new_york"
        if value == "sd":
            value = "san_diego"
        if value == "kl":
            value = "kuala_lumpur"
        if value == "torontonada":
            value = "toronto"
        if value == "rio":
            value = "rio_de_janeiro"
        if value == "philly":
            value = "philadelphia"
        if value == "ciudad_de_mexico" or value == "cdmx":
            value = "mexico_city"
        if value == "vegas":
            value = "las_" + value
        if value == "atl":
            value = "atlanta"
        value = value.replace(',_az', "")
        value = value.replace(",_uk", "")
        value = value.replace(",_bc", "")
        value = value.replace(",_or", "")
        value = value.replace(',_france', '')
        value = value.replace(',_wa', '')
        value = value.replace(',_ontario', '')
        value = value.replace(',_australia', '')
        value = value.replace(',_england', '')
        value = value.replace(',_nsw', '')
        value = value.replace(',_canada', "")
        value = value.replace('_dc', "")
        value = value.replace(',_ca', "")
        value = value.replace(',_ga', "")
        value = value.replace(',_india', "")
        value = value.replace('sydney_australia', 'sydney')
        if value == "delhi" or value == "delhi_india":
            value = "new_" + value.replace('_india', "")
        if value == "phoenix_az":
            value = "phoenix"
    value = value.replace('emmauel', 'emmanuel')
    value = value.replace('goonville', 'gonville')
    if slot == "food":
        if value == "burger" :
            value +="s"
        if value == "korean_barbeque":
            value = "korean"
        if value == "quick_meal" or value == "pick-up" or value == "snacks":
            value = "fast_food"
        if "noodle" in value :
            value = "noodles"
        if value =="tacos":
            value = "mexican"
        if value == "spicy_indian" or value == "punjabi":
            value = "indian"
        if "gastro" in value:
            value = "gastropub"
        if value == "veggie" or value == "non_meat":
            value = "vegetarian"
        if value == "pizza_and_pasta" or value == "pasta":
            value = "pizza"
        if value == "lobster" or "fish" in value:
            value = "seafood"
        if value == "szcheuan":
            value = "sichuan"
    if slot == "price_range":
        if value =="pricey" or value =="ultra_high-end":
            value = "very_expensive"
    value = value.replace("racing_in_rain", "the_art_of_racing_in_the_rain")
    value = value.replace('toy_story_4', 'toy_story_four')
    value = value.replace("movie_2", "movie_two")
    value = value.replace('madmax',"mad_max:_fury_road")
    if slot == "name":
        if value == "wild_nights":
            value = "wild_nights_with_emily"
        if value == "upside":
            value= "the_" + value
        if value == "how_to_train_your_dragon":
            value = "how_to_train_your_dragon:_the_hidden_world"
        if value == "mad_max":
            value = "mad_max:_fury_road"
        if value == "innocent":
            value= "the_" + value
        if value == "visitor":
            value= "the_" + value


        if value == "curse_of_la_llorona":
            value= "the_" + value

        if value == "poseidon_adventure":
            value= "the_" + value

        value = value.replace(':_uncaged', "")
        if value == "it_two" or value == "it2":
            value = "it_chapter_two"
        if "lord_of_the_ring" in value:
            value = "the_lord_of_the_rings"
        if value == "farewell":
            value = "the_farewell"
    elif slot == "genre":
        if "electro" in value:
            value = "electronica"
        if value == "scary" or value == "ghost":
            value = "horror"
        if value == "comic" or value == "funny":
            value = "comedy"
        if value == "cartoon":
            value = "animation"
        if value == "suspense":
            value = "thriller"
        if "rom" in value or "love" in value:
            value = "romance"
        if value == "life_history":
            value = "biographical"
        if value == "exotic" or value == "foreign_story" or "foreign" in value or value == "global":
            value = "world"
        if value == "song":
            value = "musical"
        if "myster" in value or "detect" in value or "enigm" in value or "polic" in value:
            value = "mystery"
        if "gangster" in value:
            value = "mafia"
        if value == "eccentric_story":
            value = "bizarre_story"
        if value == "combat" or value == "violent":
            value = "fight"
        if value == "army" or value == "militar":
            value = "war"
        if value == "imaginative_fiction" or value == "future_scientific_fiction" or "fiction" in value or value == "sf" or "science" in value:
            value = "sci-fi"
    if "theater_name" in slot:
        for i in range(10, 30):
            value = value.replace('_' + str(i), "")
    if value == "shattuck_cinemas":
        value = "landmarks_" + value
    if value == "vine_cinema":
        value += "&alehouse"
    if "amount" in slot:
        if "dollar" in value or "$" in value:
            value = value.replace("_dollars", "").replace("_$", "").replace('$', '')
            try:
                value = str(w2n.word_to_num(' '.join(value.split('_'))))
            except ValueError:
                value = value.replace(',', '')
        elif "bucks" in value:
            value = value.replace("_bucks", "")
            try:
                value = str(w2n.word_to_num(' '.join(value.split('_'))))
            except ValueError:
                pass
        else:
            try:
                value = str(w2n.word_to_num(' '.join(value.split('_'))))
            except ValueError:
                value = "0"
    if "rating" in slot:
        if not '.' in value :
            if value !="dontcare":
            
                value += '.00'
        
        elif len(value.split(".")[1]) == 1:
            value += "0"
    # print(value)
    # if "therapist" in slot or "doctor" in slot :
    value = value.replace(",-", '-')
    value = value.replace(",_", '_')
    value = value.replace('._', '_')
    value = value.replace('m.d', 'md')
    value = value.replace('d.r', 'dr')
    value = value.replace('d.o.', 'do')
    value = value.replace('ph.d.', 'phd')
    value = value.replace("olemalifornia","olema")
    value = value.replace("dr_thomas_stodgel","dr_thomas_o_stodgel_md")
    return value


def get_info_sgd(dialog, dbs, ontology, mapper):
    previous = ""
    for turn in dialog['turns']:
        for frame in turn['frames']:
            if "service" in frame:
                service = mapper.map_domain(frame['service'])
            if 'state' in frame:
                state = frame['state']
                if state['slot_values']:
                    to_be_changed = {}
                    for pair in state['slot_values']:
                        old = pair
                        
                        domain = state['active_intent']
                        if domain == "NONE":
                            domain = service
                        else:
                            domain = mapper.map_intent(domain, service)
                        
                        slot = pair
                        if slot == "day" and (domain == "train" or domain == "bus"):
                            slot = 'start_day'
                        # if "book" in slot:
                        #     slot = slot.replace("book", "book_")
                        
                        if (slot == "book_day" or slot == "date") and domain == "restaurant":
                            pair = domain + '-' + slot
                        elif slot == "category" and domain == "event":
                            slot = "subcategory"
                            pair = domain + '-' + slot
                        elif (slot == "type" or slot == 'category') and domain == "restaurant":
                            slot = "food"
                            pair = domain + '-' + slot
                        elif slot == 'city' and domain == "service":
                            slot = "area"
                            pair = domain + '-' + slot
                        
                        elif slot == "location":
                            if domain != "messaging":
                                slot = "city"
                            elif domain == "messaging":
                                slot = "area"
                            pair = domain + '-' + slot
                        
                        elif slot == "area" and domain == "apartment":
                            slot = "city"
                            pair = domain + '-' + slot
                        elif '_' in slot:
                            new = slot.replace('_', '-')
                            if new in ontology:
                                pair = new
                            else:
                                slot = mapper.map_slot(pair)
                                pair = domain + '-' + slot
                        else:
                            slot = mapper.map_slot(pair)
                            pair = domain + '-' + slot
                        if pair != old:
                            to_be_changed.update({old: pair})
                        if pair not in ontology:

                                print(f"slot {pair} with value {state['slot_values'][old]} and not in ontology ")
                        else:
                            # print(state['slot_values'][pair])
                            value = ""
                            value2 = ""
                            if len(state['slot_values'][old]) == 1:
                                value = state['slot_values'][old][0]
                                value = value.lower().replace(' ', '_').replace("'s", "s")
                            
                            
                            
                            else:
                                value = state['slot_values'][old][0]
                                value = value.lower().replace(' ', '_').replace("'s", "s")
                                value2 = state['slot_values'][old][1]
                                value2 = value2.lower().replace(' ', '_').replace("'s", "s")
                            
                            value = check_value(value, slot, previous, dialog['dialogue_id'])
                            
                            value2 = check_value(value2, slot, previous, dialog['dialogue_id'])
                            if 'time' in slot:
                                previous = value
                            if "name" in slot or "subcategory" in slot or "genre" in slot or "food" in slot or "area" in slot or "city" in slot or "airport" in slot or "departure" in slot or "destination" in slot:
                                inside = False
                                for elem in ontology[pair]:
                                    if elem in value:
                                        value = elem
                                        # print(f"elem {elem} in value {value}")
                                        inside = True
                                    elif value in elem:
                                        value = elem
                                        # print(f" value {value} in elem{elem}")
                                        inside = True
                                if not inside and "subcategory" not in slot and  pair != "service-doctor_name"and "contact" not in slot and "destination" not in slot and "departure" not in slot and pair != "event-name" and pair != "event-city" and pair != "restaurant-name" and pair != "hotel-name" and slot != "dentist_name" and pair !="service-area"and pair !="messaging-area" and slot != "theater_name" and pair != "service-stylist_name":
                                   print(f'value {value} not in slot {pair}')
                                else:
                                    state['slot_values'][old] = [value]
                            else:
                                if value not in ontology[pair]:
                                    
                                    if value2:
                                        if value2 not in ontology[pair]:
                                            
                                            raise AttributeError(
                                                f"value nor {value} neither {value2} not in {pair} despite value 2")
                                        else:
                                            state['slot_values'][old] = [value2]
                                    else:
                                        if ":" in value and len(value.split(':')[0]) == 1:
                                            newvalue = "0" + value
                                        else:
                                            newvalue = value
                                        if newvalue not in ontology[pair]:
                                            if pair == "taxi-destination":
                                                ontology[pair].append(newvalue)
                                            elif pair == "messaging-area":
                                                ontology[pair].append(newvalue)
                                            elif pair == "messaging-contact_name":
                                                
                                                ontology[pair].append(newvalue)
                                            elif pair == "movie-starring":
                                                ontology[pair].append(newvalue)
                                            elif pair == "event-name":
                                                ontology[pair].append(newvalue)
                                            elif pair == "event-subcategory":
                                                ontology[pair].append(newvalue)
                                            elif pair == "restaurant-name":
                                                ontology[pair].append(newvalue)
                                            elif pair == "service-dentist_name":
                                                ontology[pair].append(newvalue)
                                            elif pair == "movie-theater_name":
                                                ontology[pair].append(newvalue)
                                            elif pair == "hotel-name":
                                                ontology[pair].append(newvalue)
                                            elif pair == "service-area":
                                                ontology[pair].append(newvalue)
                                            elif pair == "service-stylist_name":
                                                ontology[pair].append(newvalue)
                                            elif pair == "service-doctor_name":
                                                ontology[pair].append(newvalue)
                                            else:
                                                
                                                raise AttributeError(f"value {newvalue} not in {pair}")
                                        else:
                                            state['slot_values'][old] = [newvalue]
                                else:
                                    state['slot_values'][old] = [value]
                    for elem in to_be_changed:
                        state['slot_values'][to_be_changed[elem]] = state['slot_values'].pop(elem)


def get_info_dstc(dialog, dbs, ontology, mapper):

    for k,turn in enumerate(dialog['dial']):
        for speaker in ['usr','sys']:
            if "slu" not in turn[speaker]:
                continue
            for j,frame in enumerate(turn[speaker]["slu"]):
                print(frame)
                if "inform" in frame["act"]:
                    service ="restaurant"
                    for i,state in enumerate(frame['slots']):
                        
                        print(state)
                        slot = state[0]
                        print(slot)
                        if slot == "slot" :
                            continue
                        old = slot
                        value = state[1]
                        if slot =="this" :
                            slot = "food"
                        slot = mapper.map_slot(slot)
                        print(slot)
                        pair = service + '-' + slot
                        if pair not in ontology:
                            
                            raise ValueError(f"slot {pair} with value {value} and not in ontology ")
                        else:
                            # print(state['slot_values'][pair])
                            value = value.lower().replace(' ', '_').replace("'s", "s")
                            # value = check_value(value, slot, previous, dialog['dialogue_id'])
                            if value not in ontology[pair]:
                                raise AttributeError(f"{value} not in {pair}")
                            else:
                                frame["slots"][i] = [slot,value]

                turn[speaker]["slu"][j] = frame
        dialog["dial"][k] = turn
        
def get_info_mwoz(dialog, dbs, ontology, mapper):
    previous = ""
    for turn in dialog['turns']:
        for frame in turn['frames']:
            if 'state' in frame:
                state = frame['state']
                if state['slot_values']:
                    to_be_changed = {}
                    for pair in state['slot_values']:
                        old = pair
                        domain, slot = pair.split('-')
                        if slot == "day" and (domain == "train" or domain == "bus"):
                            slot = 'start_day'
                        # if "book" in slot:
                        #     slot = slot.replace("book", "book_")
                        
                        if slot == "bookday":
                            if domain == "restaurant":
                                slot = "book_day"
                            else :
                                slot = "start_day"
                            
                        else:
                            slot = mapper.map_slot(slot)
                            print(slot)
                        pair = domain + '-' + slot
                        print(pair)
                        if pair != old:
                            to_be_changed.update({old: pair})
                        if pair not in ontology:
                            
                            raise ValueError(f"slot {pair} not in ontology ")
                        else:
                            # print(state['slot_values'][pair])
                            value = ""
                            value2 = ""
                            if len(state['slot_values'][old]) == 1:
                                value = state['slot_values'][old][0]
                                value = value.lower().replace(' ', '_').replace("'s", "s")
                            
                            
                            
                            else:
                                value = state['slot_values'][old][0]
                                value = value.lower().replace(' ', '_').replace("'s", "s")
                                value2 = state['slot_values'][old][1]
                                value2 = value2.lower().replace(' ', '_').replace("'s", "s")
                            value = check_value(value, slot, previous, dialog['dialogue_id'])
                            value2 = check_value(value2, slot, previous, dialog['dialogue_id'])
                            if 'time' in slot:
                                previous = value
                            if value not in ontology[pair]:
                                if value2:
                                    if value2 not in ontology[pair]:
                                        
                                        print(f"value {state['slot_values'][old]} not in {pair} despite value 2")
                                    else:
                                        state['slot_values'][old] = [value2]
                                else:
                                    if ":" in value and len(value.split(':')[0]) == 1:
                                        newvalue = "0" + value
                                    else:
                                        newvalue = value
                                    if newvalue not in ontology[pair]:
                                        print(f"value {newvalue} not in {pair}")
                                    else:
                                        state['slot_values'][old] = [newvalue]
                            else:
                                state['slot_values'][old] = [value]
                    for elem in to_be_changed:
                        state['slot_values'][to_be_changed[elem]] = state['slot_values'].pop(elem)

def parse_data(data, dsb, ontology, cpt, locations, cities, areas, mapper):
    for dialog in data:
        get_info_dstc(dialog, dsb, ontology, mapper)
        # get_info_mwoz(dialog, dsb, ontology, mapper)
        # get_info_sgd(dialog, dsb, ontology, mapper)
        cpt += 1
        print(cpt)
    return data, cpt


def parse_sgd(sgd, dbs, ontology, cpt, locations, cities, areas, mapper):
    for data in sgd:
        datas = json.load(open(data))
        dic, cpt = parse_data(datas, dbs, ontology, cpt, locations, cities, areas, mapper)
        json.dump(dic,fp=open(data,'w'),indent=4)
    return cpt


def postprodsgd(sgd_onto):
    sgd_onto = json.load(sgd_onto)
    new = {}
    for key in sgd_onto:
        for subkey in sgd_onto[key]:
            if key not in subkey:
                new.update({key + '-' + subkey: sgd_onto[key][subkey]})
            else:
                old = subkey
                subkey = subkey.replace(key, '')
                if subkey.startswith('_'):
                    subkey = subkey[1:]
                new.update({key + '-' + subkey: sgd_onto[key][old]})
    json.dump(new, fp=open('../data/sgd_mwozformat_ontology.json', 'w'), indent=4)


def compare_sgd_mwoz(sgd_onto, mwoz_onto):
    sgd_onto = json.load(sgd_onto)
    mwoz_onto = json.load(mwoz_onto)
    sgd = [key for key in sgd_onto]
    mwoz = [key for key in mwoz_onto]
    sgdomains = [key.split('-')[0] for key in sgd_onto]
    mwozdomains = [key.split('-')[0] for key in mwoz_onto]
    print("\n\n#######   SGD NOT IN MWOZ #### \n\n")
    for i, key in enumerate(sgd):
        if key not in mwoz and sgdomains[i] in mwozdomains:
            print(key)
    print("\n\n#######   MWOZ NOT IN SGD #### \n\n")
    for i, key in enumerate(mwoz):
        if key not in sgd and mwozdomains[i] in sgdomains:
            print(key)


def format_mwoz(mwoz_onto):
    mwoz = json.load(mwoz_onto)
    for key in mwoz:
        mwoz[key] = [elem.lower().replace(' ', '_') for elem in mwoz[key]]
    json.dump(mwoz, fp=open(mwoz_onto.name, 'w'), indent=4)


def main():
    dbs = {}
    # ontology = json.load(open('../data/global_ontology.json'))
    # fill_ontology(ontology)
    ontology = json.load(open('../data/mwoz_ontology.json'))
    for key in ontology:
        if "dontcare" not in ontology[key]:
            ontology[key].append("dontcare")
    locations = []
    # mapper = get_ontology_unifier("multiwoz")
    mapper = get_ontology_unifier("dstcamrest")
    mapper._remove_underscores = False
    cities = []
    areas = []
    splitter = ['test', 'dev', 'train']
    cpt = 0
    
    for splitt in splitter:
        sgd = glob('../../source_diaser_data/dscr/dstccamrest.json')
        cpt = parse_sgd(sgd, dbs, ontology, cpt, locations, cities, areas, mapper)
        json.dump(sgd, fp=open(f'../data/new_{splitt}mwoz.json', 'w'), indent=4)
    json.dump(dbs, fp=open('../data/mwoz_db.json', 'w'), indent=4)
    json.dump(ontology, fp=open('../data/mwoz_ontology.json', 'w'), indent=4)


def normalize_dstc(dstc_onto):
    dstc = json.load(dstc_onto)
    new = {}
    for key in dstc["informable"]:
        dstc['informable'][key] = [elem.lower().replace(' ', '_') for elem in dstc['informable'][key]]
        new.update({"restaurant-" + key.replace('pricerange', 'price_range'): dstc['informable'][key]})
    json.dump(new, open("../data/dstc_mwozformat_ontology.json", 'w'), indent=4)


def compare_dstc_mwoz(dstc_onto, mwoz_onto):
    dstc = json.load(dstc_onto)
    mwoz = json.load(mwoz_onto)
    print("\n\n#######   DSTC NOT IN MWOZ #### \n\n")
    for key in dstc:
        if key not in mwoz:
            print(key)
    print("\n\n#######   MWOZ NOT IN DSTC #### \n\n")
    for key in mwoz:
        if key not in dstc and "restaurant" in key:
            print(key)


def values_intersection(d1, d2, d3, d1d, d1d2, d1d3, d1d2d3):
    for key in d1:
        d1d.update({key: []})
        d1d2.update({key: []})
        d1d3.update({key: []})
        d1d2d3.update({key: []})
        if key not in d2:
            if key not in d3:
                d1d[key] = d1[key]
            else:
                for elem in d1[key]:
                    if elem not in d3[key]:
                        d1d[key].append(elem)
                    else:
                        d1d3[key].append(elem)
        else:
            if key not in d3:
                for elem in d1[key]:
                    if elem not in d2[key]:
                        d1d[key].append(elem)
                    else:
                        d1d2[key].append(elem)
            else:
                for elem in d1[key]:
                    if elem not in d2[key]:
                        
                        if elem not in d3[key]:
                            d1d[key].append(elem)
                        else:
                            d1d3[key].append(elem)
                    else:
                        if elem not in d3[key]:
                            d1d2[key].append(elem)
                        else:
                            d1d2d3[key].append(elem)


def merge_ontologies(dstc_onto, sgd_onto, mwoz_onto):
    dstc = json.load(dstc_onto)
    mwoz = json.load(mwoz_onto)
    sgd = json.load(sgd_onto)
    global_onto = {}
    dstcmwoz = {}
    sgdmwoz = {}
    dstcsgd = {}
    dstc_d = {}
    sgd_d = {}
    mwoz_d = {}
    allz = {}
    values_intersection(dstc, mwoz, sgd, dstc_d, dstcmwoz, dstcsgd, allz)
    values_intersection(mwoz, dstc, sgd, mwoz_d, dstcmwoz, sgdmwoz, allz)
    values_intersection(sgd, mwoz, dstc, sgd_d, sgdmwoz, dstcsgd, allz)
    json.dump(dstc_d, fp=open('../data/dstc_only.json', 'w'), indent=4)
    json.dump(sgdmwoz, fp=open('../data/sgdmwoz.json', 'w'), indent=4)
    json.dump(dstcsgd, fp=open('../data/dstcsgd.json', 'w'), indent=4)
    json.dump(dstcmwoz, fp=open('../data/dstcmwoz.json', 'w'), indent=4)
    json.dump(sgd_d, fp=open('../data/sgd_only.json', 'w'), indent=4)
    json.dump(mwoz_d, fp=open('../data/mwoz_only.json', 'w'), indent=4)
    json.dump(allz, fp=open('../data/allz.json', 'w'), indent=4)
    
    for sub in [dstc, mwoz, sgd]:
        for slot in sub:
            if slot not in global_onto:
                global_onto[slot] = sub[slot]
            else:
                assert type(sub[slot]) == list
                for elem in sub[slot]:
                    if elem not in global_onto[slot]:
                        global_onto[slot].append(elem)
    json.dump(global_onto, fp=open('../data/global_ontology.json', 'w'), indent=4)


def main2():
    sgd = open("../data/sgd_mwozformat_ontology.json")
    mwoz = open('../../multiwoz/data/MULTIWOZ2.3/ontology.json')
    dstc = open('../data/dstc_mwozformat_ontology.json')
    # postprodsgd(open("../data/sgd_ontology.json"))
    # compare_sgd_mwoz(sgd, mwoz)
    # format_mwoz(mwoz)
    normalize_dstc(open('../data/ontology_dstc2.json'))
    # compare_dstc_mwoz(dstc,mwoz)
    merge_ontologies(dstc, sgd, mwoz)


if __name__ == '__main__':
    main()
    # main2()

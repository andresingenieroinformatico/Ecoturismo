from service.reservas_service import get_destinations, insert_reservation

def get_data(supabase):
     return get_destinations(supabase)

def make_reservation(supabase, data):
     insert_reservation(supabase, data)
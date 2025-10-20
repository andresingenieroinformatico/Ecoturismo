def get_destinations(supabase):
     try:
          response = supabase.rpc("get_destinos_completos").execute()
          if response.data:
               return response.data
          else:
               print("Error o sin datos:", response.error)
               return []
     except Exception as e:
          print(e)
          return []

def insert_reservation(supabase, data):
     try:
          supabase.table('reservas').insert(data).execute()
     except Exception as e:
          print(e)
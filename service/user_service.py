def insert_user_service(data, supabase):
     try:
          supabase.table('usuarios').insert(data).execute()
     except Exception as e:
          print(e)
     
def check_user_exists_service(email, supabase):
     try:
          user=supabase.table('usuarios').select('*').eq('correo', email).execute()
          return user.data
     except Exception as e:
          print(e)
          return None
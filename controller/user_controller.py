from service.user_service import insert_user_service, check_user_exists_service

def insert_user(data,supabase):
     insert_user_service(data,supabase)

def is_exists(email, supabase):
     user=check_user_exists_service(email, supabase)
     if user:
          return {'exists':True,'data':user}
     return {'exists':False,'data':None}
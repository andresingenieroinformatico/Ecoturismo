def format_phone(celular):
     celular = celular.strip()
     if not celular.startswith('+57'):
          if celular.startswith('0'):
               celular = '+57' + celular[1:]
          elif celular.startswith('3'):
               celular = '+57' + celular
          else:
               celular = '+57' + celular
     return celular
from Midas import data_import

# temporary until we figure out where to store the raw csv
path = "./data/"

# from models import Identity, Transaction

def handle_uploaded_file(filefield):
  with open(path + filefield.name, 'wb+') as destination:
    for chunk in filefield.chunks():
      destination.write(chunk)
  return data_import.store_raw_data(path + filefield.name)

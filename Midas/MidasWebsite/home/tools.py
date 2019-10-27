# temporary until we figure out where to store the raw csv
path = "./data/"

def handle_uploaded_file(filefield, name):
  with open(path + filefield.name, 'wb+') as destination:
    for chunk in filefield.chunks():
      destination.write(chunk)
from django.shortcuts import render
# Create your views here.
from .models import *
from django.http import HttpResponse
import datetime

def homescreen(request):
    properties = Property.objects.all()
    cities = City.objects.all()

    return render(request, template_name="index.html", context={'properties': properties, 'cities': cities})

# pagina de la propiedad con todos los datos en display (se llega apretando el botón de 'Leer más'
# en la card de la propiedad en la homescreen)
def property_page(request):
    if request.GET["id_property"]:
        id_property = request.GET["id_property"]
        reservations_date_list = ReservationDate.objects.filter(property__id=request.GET["id_property"]).filter(
            reservation__id=None).order_by('date')
        property_aux = Property.objects.get(id=id_property)
        return render(request, template_name="property_page.html", context={'property_aux': property_aux, 'available_dates':reservations_date_list})


def success(request, property_aux):
    return render(request, template_name="success.html", context={'property_aux': property_aux})


def error(request, property_aux):
    return render(request, template_name="error.html", context={'property_aux': property_aux})


def reservation(request):
    if request.POST:
        # filtra por el id de propiedad que recibe por post, solo agarra los que no tiene id de reservacion, y ordena por fecha ascendente
        reservations_date_list = ReservationDate.objects.filter(property__id=request.POST["property_id"]).filter(
            reservation__id=None).order_by('date')
        # transformacion que nos ayuda mas adelante
        reservations_date_list = list(reservations_date_list)
        aux = []

        # copia a reser_date_list y la pasa a string para evitar problemas con datetime
        for x in reservations_date_list:
            aux.append(str(x))
        # separa en una lista al rango de fechas
        daterange_array = request.POST['daterange'].split(' - ')
        # transforma al formato de la base de datos
        initial_date = datetime.datetime.strptime(daterange_array[0], '%m/%d/%Y').strftime('%Y-%m-%d')
        final_date = datetime.datetime.strptime(daterange_array[1], '%m/%d/%Y').strftime('%Y-%m-%d')
        try:
            property_aux = Property.objects.filter(id=request.POST["property_id"])
            initial_index = aux.index(initial_date)
            final_index = aux.index(final_date)
            # si esta condicion no se cumple es porque hay "huecos" entre medio del rango de fechas
            # esta atrocidad es producto de que a python no le gusta
            if str((1 + final_index - initial_index)) == request.POST['quantity-days']:
                r = Reservation(userFirstName=request.POST['nombre'], userLastName=request.POST['apellido'],
                                email=request.POST['email'], property=property_aux[0], final_price=float(request.POST['final_price'])*1.08,
                                code=str(property_aux[0])[0:2], date_of_reservation=datetime.datetime.today().strftime('%Y-%m-%d'))
                r.save()
                cont = initial_index
                while cont <= final_index:
                    date = reservations_date_list[cont]
                    date.reservation = r
                    date.save()
                    cont = cont + 1
                return render(request, template_name="success.html", context={'property_aux': property_aux})
            return render(request, template_name="error.html", context={'property_aux': property_aux})
        except:
            return render(request, template_name="error.html", context={'property_aux': property_aux})

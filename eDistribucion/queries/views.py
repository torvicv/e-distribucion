from cgi import print_exception
from urllib.request import Request, urlopen
from django.shortcuts import render, redirect
from django.views.generic import View
from EdistribucionAPI import Edistribucion
from datetime import datetime, timedelta
import json

from django.conf import settings
from .forms import AdvancedSearchForm, ChooseCycleForm, LoginForm, ChooseForm, OnlyDateForm
from django.contrib import messages

# chartjs
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView

class LoginApp(View):
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, "index.html", {'form': form})
    
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
            else:
                messages.add_message(request, messages.ERROR, 'Los datos no son correctos.')
            request.session['user'] = {'username': username, 'password': password}
            return redirect('home')
            
class HomeApp(View):
    def get(self, request, *args, **kwargs):
        user = request.session['user']
        try:
            edis = None
            edis = Edistribucion(user['username'], user['password'])
            edis.login()
            r = edis.get_list_cups()
            if len(r) == 0:
                raise Exception()
            else:
                messages.add_message(request, messages.INFO, 'Logueado correctamente.')
        except Exception:
            messages.add_message(request, messages.ERROR, 'Vuelva a loguearse.')
            return redirect("index")
        return render(request, "home.html", {'context': r})
    
class CyclesApp(View):
    
    days = set()
    
    def get(self, request, *args, **kwargs):
        user = request.session['user']
        k = kwargs['item']
        k = k.replace("\'", "\"")
        k = json.loads(k)
        form = ChooseCycleForm()
        try:
            edis = Edistribucion(user['username'], user['password'])
            edis.login()
            try:
                f = edis.get_list_cycles(k)
                try:
                    arrayOptions = []
                    for i in f:
                        arrayOptions.append((i, i['label']))
                    form.fields['cycle'].choices = arrayOptions
                except:
                    messages.add_message(request, messages.ERROR, 'Error al mostrar datos.')
            except:
                messages.add_message(request, messages.ERROR, 'Error al conseguir los datos.')
        except:
            messages.add_message(request, messages.ERROR, 'Vuelva a loguearse.')
        return render(request, "ciclos.html", {"form": form, 'cycles': True, 'title': 'Ciclos de facturación'})

    
    def post(self, request, *args, **kwargs):
        user = request.session['user']
        p = request.POST
        k = kwargs['item']
        k = k.replace("\'", "\"")
        cont = json.loads(k)
        cycle = json.loads(p['cycle'].replace("\'", "\""))
        inicio = cycle['label'].split("-")[0].strip()
        fin = cycle['label'].split("-")[1].strip()
        try:
            edis = Edistribucion(user['username'], user['password'])
            edis.login()
            try:
                r = edis.get_meas(cont, cycle)
                valuesCycle = Utils().set_headers("https://api.esios.ree.es/indicators/1001?start_date="+inicio+"T00%3A00%3A00Z&end_date="+fin+"T23%3A55%3A00Z&geo_ids[]=8741")
                contador = 0
                sumConsumeByDay = 0
                sumTotalByDay = 0
                sumPriceDays = 0
                sumConsumeDays = 0
                for x in r:
                    contador2 = 0
                    sum = 0
                    sumConsume = 0 
                    sumTotal = 0
                    for v in x:
                        result = list(filter(lambda c: c['datetime_utc'].split("T")[0] == datetime.strftime(Utils().format_fecha2([v['date']]), "%Y-%m-%d") and c['datetime_utc'].split("T")[1][0:2] == v['hour'][0:2], valuesCycle['indicator']['values']))
                        mulValue = (r[contador][contador2]['valueDouble'] * result[0]['value']) / 1000
                        sum += mulValue
                        sumConsume += r[contador][contador2]['valueDouble']
                        sumTotal += mulValue
                        sumConsumeByDay += r[contador][contador2]['valueDouble']
                        sumTotalByDay += mulValue
                        r[contador][contador2].update({"valueEsios": result[0]['value'], "mulValue": mulValue}) 
                        contador2 += 1 
                    dic = any
                    dic = json.dumps({"hour": r[contador][0]['date'], "mulValue": sum, "value": sumConsume}, indent=4)
                    self.days.add(dic)
                    r[contador].append({"day": r[contador][0]['date'], "sumTotal": sumTotalByDay, "sumConsumeByDay": sumConsumeByDay})
                    sumConsumeByDay = 0
                    sumTotalByDay = 0
                    sumPriceDays += sum
                    sumConsumeDays += sumConsume
                    contador += 1   
            except:
                messages.add_message(request, messages.ERROR, 'Error al conseguir los datos.')
        except:
            messages.add_message(request, messages.ERROR, 'Vuelva a loguearse.')
        result = sorted(r, key=lambda d: Utils().format_fecha2([d[0]['date']]), reverse=True)
        return render(request, "ciclos.html", {"dataCycle": result, 'title': 'Ciclo '+cycle['label'], "days": len(result)-1, "avgDays": (sumPriceDays/(len(result)-1)), "sumConsumeDays": sumConsumeDays, "sumPriceDays": sumPriceDays})
        
    
class IntervalApp(View):
    
    days = set()
    
    def get(self, request, *args, **kwargs):
        form = AdvancedSearchForm()
        return render(request, "interval.html", {"interval": True, 'form': form, "title": 'Búsqueda Avanzada'})
        
    def post(self, request, *args, **kwargs):
        user = request.session['user']
        form = AdvancedSearchForm(request.POST)
        k = kwargs['item']
        k = k.replace("\'", "\"")
        k = json.loads(k)
        if form.is_valid():
            inicio = datetime.strftime(form.cleaned_data['start'], "%Y-%m-%d")
            fin = datetime.strftime(form.cleaned_data['end'], "%Y-%m-%d")
            firstDate = datetime.strftime(form.cleaned_data['start'], "%d-%m-%Y")
            lastDate = datetime.strftime(form.cleaned_data['end'], "%d-%m-%Y")
        try:
            edis = Edistribucion(user['username'], user['password'])
            edis.login()
            try:
                i = edis.get_meas_interval(k, inicio, fin)
                valuesLastInterval = Utils().set_headers("https://api.esios.ree.es/indicators/1001?start_date="+inicio+"T00%3A00%3A00Z&end_date="+fin+"T23%3A55%3A00Z&geo_ids[]=8741")
                mapDates = i['lstData']
                contador1 = 0
                sumPriceDays = 0
                sumConsumeDays = 0
                for hourlyPoints in mapDates:
                    contador2 = 0
                    sumPrice = 0
                    sumConsume = 0
                    for x in hourlyPoints:          
                        result2 = list(filter(lambda c: c['datetime_utc'].split("T")[0] == datetime.strftime(Utils().format_fecha2([x['date']]), "%Y-%m-%d") and c['datetime_utc'].split("T")[1][0:2] == x['hour'][0:2], valuesLastInterval['indicator']['values']))
                        mulValue = (i['lstData'][contador1][contador2]['valueDouble'] * result2[0]['value']) / 1000
                        sumPrice += (i['lstData'][contador1][contador2]['valueDouble'] * result2[0]['value']) / 1000
                        sumConsume += i['lstData'][contador1][contador2]['valueDouble']
                        i['lstData'][contador1][contador2].update({"valueEsios": result2[0]['value'], "mulValue": mulValue})  
                        day = x['date']
                        contador2 += 1
                    sumPriceDays += sumPrice
                    sumConsumeDays += sumConsume
                    i['lstData'][contador1].append({"sumPriceDay": sumPrice, "sumConsumeDay": sumConsume, "day": day})
                    dic = any
                    dic = json.dumps({"hour": day, "mulValue": sumPrice, "value": sumConsume}, indent=4)
                    self.days.add(dic)
                    contador1 += 1
                i['lstData'].append({"sumPriceDays": sumPriceDays, "sumConsumeDays": sumConsumeDays})
            except:
                messages.add_message(request, messages.ERROR, 'Error al conseguir los datos.')
        except:
            messages.add_message(request, messages.ERROR, 'Vuelva a loguearse.')
        return render(request, "interval.html", {"meas": zip(i['lstMonthlyPoints'], i['lstData']), "days": len(i['lstData'])-1, "avgDays": (sumPriceDays/(len(i['lstData'])-1)), "sumConsumeDays": sumConsumeDays, "sumPriceDays": sumPriceDays, 'intervalo': 'Del '+firstDate+' al '+lastDate, "title": 'Búsqueda Avanzada'})

    
class ChooseApp(View):
    
    days = set()
    
    def get(self, request, *args, **kwargs):
        user = request.session['user']
        f = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        fDict1 = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")
        k = kwargs['item']
        k = k.replace("\'", "\"")
        k = json.loads(k)
        edis = Edistribucion(user['username'], user['password'])
        edis.login()
        print('choose app: ', kwargs)
        g = request.GET
        if g and len(g['fecha']) > 0:
            form = ChooseForm(g)
        else:
            form = ChooseForm()
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            avg = 0
            sum = 0
            sumTotal = 0
            sumConsume = 0
            if fecha == '1':
                i = edis.get_last_day(k, f)
                valuesLastDay = Utils().set_headers("https://api.esios.ree.es/indicators/1001?start_date="+f+"T00%3A00%3A00Z&end_date="+f+"T23%3A55%3A00Z&geo_ids[]=8741") 
                contador = 0;
                try:
                    if 'mapHourlyPoints' in i:
                        for x in i['mapHourlyPoints'].get(fDict1):
                            result = list(filter(lambda c: c['datetime_utc'].split("T")[1][0:2] == x['hour'][0:2], valuesLastDay['indicator']['values']))
                            mulValue = (i['mapHourlyPoints'].get(fDict1)[contador]['value'] * result[0]['value']) / 1000
                            i['mapHourlyPoints'].get(fDict1)[contador].update({"valueEsios": result[0]['value'], "mulValue": mulValue})
                            dic = any
                            dic = json.dumps({"hour": x['hour'], "mulValue": mulValue, "value": x['value']}, indent=4)
                            sum += mulValue
                            sumConsume += i['mapHourlyPoints'].get(fDict1)[contador]['value']
                            self.days.add(dic)
                            contador += 1
                        i['mapHourlyPoints'][fDict1].append({"day": fDict1, "sum": sum, "sumConsume": sumConsume})
                        return render(request, "elegir.html", {"chosenDay": True, "item":  i['mapHourlyPoints'].get(fDict1)})
                    else:
                        raise Exception()
                except Exception as e:
                    messages.add_message(request, messages.ERROR, 'No hay datos del último día.')
                    return render(request, "elegir.html", {"chosenDay": True})
                
            elif fecha == '2':
                i = edis.get_last_week(k, f)
                fEnd = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
                valuesLastWeek = Utils().set_headers("https://api.esios.ree.es/indicators/1001?start_date="+fEnd+"T00%3A00%3A00Z&end_date="+f+"T23%3A55%3A00Z&geo_ids[]=8741") 
                result = []
                sumConsumeByDay = 0
                sumTotalByDay = 0
                mapDates = i['mapHourlyPoints']
                for hourlyPoints in mapDates:
                    contador = 0
                    for x in i['mapHourlyPoints'].get(hourlyPoints):
                        result2 = list(filter(lambda c: c['datetime_utc'].split("T")[0] == datetime.strftime(Utils().format_fecha([hourlyPoints]), "%Y-%m-%d") and c['datetime_utc'].split("T")[1][0:2] == x['hour'][0:2], valuesLastWeek['indicator']['values']))
                        for v in result2:
                            mulValue = (i['mapHourlyPoints'].get(hourlyPoints)[contador]['value'] * v['value']) / 1000
                            sum += mulValue
                            sumConsume += i['mapHourlyPoints'].get(hourlyPoints)[contador]['value']
                            sumTotal += mulValue
                            sumConsumeByDay += i['mapHourlyPoints'].get(hourlyPoints)[contador]['value']
                            sumTotalByDay += mulValue
                            i['mapHourlyPoints'].get(hourlyPoints)[contador].update({"valueEsios": v['value'], "mulValue": mulValue})
                        contador += 1
                    dic = any
                    dic = json.dumps({"hour": hourlyPoints, "mulValue": sum, "value": sumConsume}, indent=4)
                    self.days.add(dic)
                    sum = 0
                    sumConsume = 0 
                    i['mapHourlyPoints'][hourlyPoints].append({"day": hourlyPoints, "sumTotal": sumTotalByDay, "sumConsumeByDay": sumConsumeByDay})
                    sumConsumeByDay = 0
                    sumTotalByDay = 0
                    result.append({hourlyPoints: i['mapHourlyPoints'].get(hourlyPoints)})
                result = sorted(result, key=lambda d: Utils().format_fecha([list(d.keys())[0]]), reverse=True)
                avg = sumTotal / len(result)
                return render(request, "elegir.html", {"chooseWeek": True, "item": list(result), "sum": sumTotal, "avg": avg, "days": len(result), "total": self.days})
            elif fecha == '3':
                i = edis.get_last_month(k, f)
                fEnd = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
                valuesLastMonth = Utils().set_headers("https://api.esios.ree.es/indicators/1001?start_date="+fEnd+"T00%3A00%3A00Z&end_date="+f+"T23%3A55%3A00Z&geo_ids[]=8741")
                result = []
                sumConsumeByDay = 0
                sumTotalByDay = 0
                mapDates = i['mapHourlyPoints']
                for hourlyPoints in mapDates:
                    contador = 0
                    for x in i['mapHourlyPoints'].get(hourlyPoints):
                        result2 = list(filter(lambda c: c['datetime_utc'].split("T")[0] == datetime.strftime(Utils().format_fecha([hourlyPoints]), "%Y-%m-%d") and c['datetime_utc'].split("T")[1][0:2] == x['hour'][0:2], valuesLastMonth['indicator']['values']))
                        for v in result2:
                            mulValue = (i['mapHourlyPoints'].get(hourlyPoints)[contador]['value'] * v['value']) / 1000
                            sum += mulValue
                            sumConsume += i['mapHourlyPoints'].get(hourlyPoints)[contador]['value']
                            sumTotal += mulValue
                            sumConsumeByDay += i['mapHourlyPoints'].get(hourlyPoints)[contador]['value']
                            sumTotalByDay += mulValue
                            i['mapHourlyPoints'].get(hourlyPoints)[contador].update({"valueEsios": v['value'], "mulValue": mulValue})
                        contador += 1
                    dic = any
                    dic = json.dumps({"hour": hourlyPoints, "mulValue": sum, "value": sumConsume}, indent=4)
                    self.days.add(dic)
                    sum = 0
                    sumConsume = 0 
                    i['mapHourlyPoints'][hourlyPoints].append({"day": hourlyPoints, "sumTotal": sumTotalByDay, "sumConsumeByDay": sumConsumeByDay})
                    sumConsumeByDay = 0
                    sumTotalByDay = 0
                    result.append({hourlyPoints: i['mapHourlyPoints'].get(hourlyPoints)})
                result = sorted(result, key=lambda d: Utils().format_fecha([list(d.keys())[0]]), reverse=True)
                avg = sumTotal / len(result)             
                return render(request, "elegir.html", {"chooseMonth": True, "result": list(result), "sum": sumTotal, "avg": avg, "days": len(result), "total": self.days})
            elif  fecha == '4':
                form = OnlyDateForm()
                return render(request, "elegir.html", {"chooseDay": True, 'form': form})
        else:
            return render(request, "elegir.html", {"chooseDate": True, 'form': form})
        
    def post(self, request, *args, **kwargs):
        user = request.session['user']
        # f = request.POST
        form = OnlyDateForm(request.POST)
        if form.is_valid():
            f = datetime.strftime(form.cleaned_data['day'], "%Y-%m-%d")
        k = kwargs['item']
        k = k.replace("\'", "\"")
        k = json.loads(k)
        sum = 0
        sumConsume = 0
        try:
            edis = Edistribucion(user['username'], user['password'])
            edis.login()
            try:
                i = edis.get_choose_day(k, f)
                valuesLastDay = Utils().set_headers("https://api.esios.ree.es/indicators/1001?start_date="+f+"T00%3A00%3A00Z&end_date="+f+"T23%3A55%3A00Z&geo_ids[]=8741")
                contador = 0
                for x in i['lstData'][0]:
                    result = list(filter(lambda c: c['datetime_utc'].split("T")[1][0:2] == x['hour'][0:2], valuesLastDay['indicator']['values']))
                    mulValue = (x['valueDouble'] * result[0]['value']) / 1000
                    i['lstData'][0][contador].update({"valueEsios": result[0]['value'], "mulValue": mulValue})
                    sumConsume += mulValue
                    sum += x['valueDouble']
                    contador += 1
                    dic = any
                    dic = json.dumps({"hour": x['hour'], "mulValue": mulValue, "value": x['valueDouble']}, indent=4)
                    self.days.add(dic)
            except:
                messages.add_message(request, messages.ERROR, 'Error al conseguir los datos.')
        except:
            messages.add_message(request, messages.ERROR, 'Vuelva a loguearse.')
        try:
            lst = i['lstData']
            lst[0].append({"day": form.cleaned_data['day'], "sum": sum, "sumConsume": sumConsume})
            return render(request, "elegir.html", {"measDay": i})
        except:
            messages.add_message(request, messages.ERROR, 'No hay datos de la fecha '+form.cleaned_data['day'].strftime('%d-%m-%Y')+'.')
            return render(request, "elegir.html")
    
    def get_date(self, json):
        return json
    
    def getDays(self, result):
        a = result
        return a
                    
    
# Clase para los charts
class LineChartJSONView(BaseLineChartView):
    
    days = []
    
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        days = []
        l = []
        if len(ChooseApp.days) > 0:
            for day in list(ChooseApp.days):
                l.append(json.loads(day))
            if len(l) > 0 and l[0]['hour'].find(" - ") != -1:
                self.days = sorted(list(l), key=lambda d: d['hour'], reverse=False)
            else:
                self.days = sorted(list(l), key=lambda d: Utils().format_fecha([d['hour']]), reverse=False)
        if len(IntervalApp.days) > 0:
            for day in list(IntervalApp.days):
                l.append(json.loads(day))
            if len(l) > 0 and l[0]['hour'].find(" - ") != -1:
                self.days = sorted(list(l), key=lambda d: d['hour'], reverse=False)
            else:
                self.days = sorted(list(l), key=lambda d: Utils().format_fecha2([d['hour']]), reverse=False)
        if len(CyclesApp.days) > 0:
            for day in list(CyclesApp.days):
                l.append(json.loads(day))
            if len(l) > 0 and l[0]['hour'].find(" - ") != -1:
                self.days = sorted(list(l), key=lambda d: d['hour'], reverse=False)
            else:
                self.days = sorted(list(l), key=lambda d: Utils().format_fecha2([d['hour']]), reverse=False)
        
        for i in self.days:
            days.append(i['hour'])
        return days

    def get_providers(self):
        """Return names of datasets."""
        return ["Precio Total", "Consumido Por Día", "Precio Por Día", "Consumido"]

    def get_data(self):
        """Return 3 datasets to plot."""
        prices = []
        consumes = []
        sum = 0
        sumConsumes = 0
        total = []
        totalConsumes = []
        for t in self.days:
            total.append(t['mulValue'])
            sum += t['mulValue']
            prices.append(sum)
            sumConsumes += t['value']
            totalConsumes.append(sumConsumes)
            consumes.append(t['value'])
        return [prices, consumes, total, totalConsumes]

    
# Clase para métodos comunes.
class Utils:
    def set_headers(self, url):
        r = Request(url, method='GET')
        r.add_header('Accept', "application/json; application/vnd.esios-api-v1+json")
        r.add_header('Content-Type', "application/json")
        r.add_header('host', "api.esios.ree.es")
        r.add_header('Authorization', "Token token="+settings.TOKEN_API_ESIOS)
        response = urlopen(r)
        json_string = response.read().decode('utf-8')
        values = dict(json.loads(json_string))
        return values
    
    def format_fecha(self, fecha):
        original_date = datetime.strptime(fecha[0], "%d-%m-%Y").strftime("%Y-%m-%d")
        return datetime.strptime(original_date, "%Y-%m-%d")
    
    def format_fecha2(self, fecha):
        original_date = datetime.strptime(fecha[0], "%d/%m/%Y").strftime("%Y-%m-%d")
        return datetime.strptime(original_date, "%Y-%m-%d")
    
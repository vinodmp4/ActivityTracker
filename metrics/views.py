from django.shortcuts import render, redirect
from django.utils.html import format_html
from .models import blockchain

def site_metrics(request):
    ulink = '/login';utitle = 'Login'
    if request.user.is_authenticated:
        ulink = '/logout';utitle = 'Logout'
        if request.method == "POST":
            pass
        # End of updation --------------------
    output = "</table>"
    rawdata = blockchain.objects.all()
    for data in rawdata:
        output = "<tr><td>"+str(data.date)+"</td><td>"+data.hashcode+"</td><td>"+data.data+"</td></tr>" + output
    output = "<table>"+output
    return render(request, 'metrics/metrics_home.html', {"utitle":utitle, "ulink":ulink, 'data':format_html(output)})

# Create your views here.

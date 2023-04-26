import urllib.request
from flask import Flask, request, send_file, redirect, send_from_directory, render_template, make_response
from urllib.parse import urlparse
import requests
import geoip2.database
from geopy.distance import geodesic
import socket
import paramiko
import datetime
import time
import os
from flask import send_file

from flask import Flask, make_response

app = Flask(__name__)




reader = geoip2.database.Reader('GeoLite2-City.mmdb')

server1_ip = {'IP': '185.156.41.156', 'username': 'root', 'password': 'password', 'city': 'Kyiv', 'name': 'VPS1'}
server2_ip = {'IP': '185.67.0.21', 'username': 'root', 'password': 'password', 'city': 'Dronten', 'name': 'VPS2'}
server3_ip = {'IP': '208.167.238.108', 'username': 'root', 'password': 'password', 'city': 'New Jersey', 'name': 'VPS3'}
list_ip = [server1_ip, server2_ip, server3_ip]


def replicant(server, filename):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server['IP'], username=server["username"], password=server['password'])

    # Відпвка файлу на ервер
    sftp = ssh.open_sftp()
    start_time = time.time()
    sftp.put(f'/home/uploads/{filename}', f'/home/uploads/{filename}')
    dt = datetime.datetime.now()
    end_time = time.time()
    duration = end_time - start_time
    sftp.close()

    # Закритя з'єднання
    ssh.close()
    return duration, dt

def get_distance(my_ip):
    server1_location = reader.city("185.156.41.156").location
    server2_location = reader.city(server2_ip['IP']).location
    server3_location = reader.city(server3_ip['IP']).location

    my_location = reader.city(my_ip).location
    distance1 = geodesic((my_location.latitude, my_location.longitude),
                         (server1_location.latitude, server1_location.longitude)).km
    distance2 = geodesic((my_location.latitude, my_location.longitude),
                         (server2_location.latitude, server2_location.longitude)).km
    distance3 = geodesic((my_location.latitude, my_location.longitude),
                         (server3_location.latitude, server3_location.longitude)).km
    return distance1, distance2, distance3





@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        ip_address = socket.gethostbyname(domain)
        d1, d2, d3 = get_distance(ip_address)
        url_upload = url
        external_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

        if d1 < d2 and d1 < d3:
            ip_replicant = server1_ip['IP']

            data = {'url_upload': url_upload, 'ip_replicant': ip_replicant, 'url': url, "external_ip": external_ip}
            url = 'http://185.156.41.156:5000/upload'
            response = requests.post(url, data=data)
            try:
                return response.content
                # обробка відповіді сервера
            except requests.exceptions.ConnectionError as e:
                return ("Connection error:", e)
                # додаткові дії в разі виникнення помилки з'єднання
            except requests.exceptions.RequestException as e:
                return ("Some error:", e)

        elif d2 < d1 and d2 < d3:
            ip_replicant = server2_ip['IP']
            data = {'url_upload': url_upload, 'ip_replicant': ip_replicant, 'url': url, "external_ip": external_ip}
            url = 'http://185.67.0.21/upload'
            response = requests.post(url, data=data)
            try:
                return response.content
                # обробка відповіді сервера
            except requests.exceptions.ConnectionError as e:
                return ("Connection error:", e)
                # додаткові дії в разі виникнення помилки з'єднання
            except requests.exceptions.RequestException as e:
                return ("Some error:", e)
        elif d3 < d1 and d3 < d2:
            ip_replicant = server3_ip['IP']
            data = {'url_upload': url_upload, 'ip_replicant': ip_replicant, 'url': url, "external_ip": external_ip}
            url = 'http://208.167.238.108/upload'
            response = requests.post(url, data=data)
            try:
                return response.content
                # обробка відповіді сервера
            except requests.exceptions.ConnectionError as e:
                return ("Connection error:", e)
                # додаткові дії в разі виникнення помилки з'єднання
            except requests.exceptions.RequestException as e:
                return ("Some error:", e)
    else:

        return '''
                    <script>
                    function displayGif() {
                        var gifDiv = document.getElementById("gifDiv");
                        gifDiv.innerHTML = '<img src="https://i.gifer.com/7h4F.gif">';
                        var form = document.getElementById("form");
                        form.style.display = "none";
                    }
                    </script>
                    <form id="form" method="post" action="/">
                        <label for="url">Enter file URL:</label>
                        <input type="text" id="url" name="url"><br><br>
                        <button type="submit" onclick="displayGif()">Submit</button>
                    </form>
                    <div id="gifDiv"></div>
                '''

@app.route('/upload', methods=['POST'])
def upload():
    url_upload = request.form['url_upload']
    ip_replicant = request.form['ip_replicant']
    external_ip = request.form['external_ip']

    start_time = time.time()
    filename = os.path.basename(url_upload)
    urllib.request.urlretrieve(url_upload, f"/home/uploads/{filename}")
    dt = datetime.datetime.now()
    end_time = time.time()
    duration = end_time - start_time

    name_replicate = []
    for server1 in list_ip:

        if ip_replicant == server1['IP']:
            domain_name = server1
            if domain_name['IP'] == "185.156.41.156":
                domain_name['IP'] = "185.156.41.156:5000"
        elif ip_replicant != server1['IP']:

            duration_rep, dt_rep = replicant(server1, filename)
            if server1['IP'] == '185.156.41.156':
                server_ip_change = f"{server1['IP']}:5000"
            else:
                server_ip_change = server1['IP']
            vps_rep = {'server': server1, 'duration': round(duration_rep, 0),
                       'dt': dt_rep.strftime("%Y-%m-%d %H:%M:%S"),
                       'domain_name': server_ip_change}
            name_replicate.append(vps_rep)

    d1, d2, d3 = get_distance(external_ip)
    if d1 < d2 and d1 < d3:
        host_name = '185.156.41.156:5000'
        uploaded_host_name = server1_ip
    elif d2 < d1 and d2 < d3:
        uploaded_host_name = server2_ip
        host_name = '185.67.0.21'
    else:
        uploaded_host_name = server3_ip
        host_name = '208.167.238.108'

    return render_template('download.html', domain_name_name=domain_name["name"], domain_name_city=domain_name["city"], domain_name_ip=domain_name["IP"], duration_first=round(duration, 0), dt_first=dt.strftime("%Y-%m-%d %H:%M:%S"), filename=filename,
                           name_replicate_name_1=name_replicate[-2]["server"]["name"], name_replicate_city_1=name_replicate[-2]["server"]["city"], name_replicate_ip_1=name_replicate[-2]["server"]["IP"], name_replicate_duration_1=name_replicate[-2]["duration"], name_replicate_dt_1=name_replicate[-2]["dt"], name_replicate_domain_name_1=name_replicate[-2]["domain_name"],
                           name_replicate_name_2=name_replicate[-1]["server"]["name"], name_replicate_city_2=name_replicate[-1]["server"]["city"], name_replicate_ip_2=name_replicate[-1]["server"]["IP"], name_replicate_duration_2=name_replicate[-1]["duration"], name_replicate_dt_2=name_replicate[-1]["dt"], name_replicate_domain_name_2=name_replicate[-1]["domain_name"],
                           host_name=host_name, link_url=f'http://{host_name}/download/{filename}',
                           uploaded_host_name=uploaded_host_name['name'], uploaded_host_city=uploaded_host_name['city'], uploaded_host_ip=uploaded_host_name['IP'])


# @app.after_request
# def add_headers(response):
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Content-Security-Policy'] = 'upgrade-insecure-requests;'
#     return response


@app.route('/download/<filename>')
def download(filename):
    resp = make_response(send_file(f"/home/uploads/{filename}", as_attachment=True))
    resp.headers['Access-Control-Allow-Origin'] = '*'

    # set Content-Security-Policy header
    resp.headers['Content-Security-Policy'] = 'upgrade-insecure-requests;'
    return resp



if __name__ == '__main__':
    app.run(debug=True , host="0.0.0.0", port=80 )

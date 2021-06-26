import json
from bs4 import BeautifulSoup
import requests
import flask
from flask import request,jsonify

def scrapping(url,tienda):
        tagPrecio=" "; ruta=" ";idPrecio=" ";idNombre=" ";tagNombre=" ";entradaPrecio=""
        fp = requests.get(url)    
        if fp.status_code == 404:
            return 0
        html = BeautifulSoup(fp.text, 'html.parser')    
        if "vans" in tienda:
            tagPrecio="span";tagNombre="span"
            entradaImg="class";entradaPrecio="class";entradasNombre="class"
            idPrecio="vansmx-custom-price-0-x-priceShelfNormal";idNombre="vtex-store-components-3-x-productBrand"
        elif "nike" in tienda:
            tagPrecio="div";tagNombre="h1"
            entradaPrecio="data-test";entradasNombre="id"
            ruta="https://www.nike.com/mx/"
            idPrecio="product-price";idNombre="pdp_product_title"
        elif "coppel" in tienda:
            tagPrecio="span";tagNombre="h1"
            entradaPrecio="itemprop";entradasNombre="class"
            ruta="https://www.coppel.com"
            idPrecio="price";idNombre="main_header"    
        try:        
            precio = ((html.find(tagPrecio, {entradaPrecio: idPrecio}).text).split())
            nombre = (html.find(tagNombre, {entradasNombre: idNombre}).text)
            return {
                "url":url,
                "nombre":' '.join(nombre.split()),
                "precio":precio[0]
            }
        except NameError:
            print(NameError)
            return 0
app = flask.Flask(__name__)
@app.route('/',methods=['GET'])
def home(): 
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
    calzado = request.args['calzado']
#estos son los datos de acceso al api de bing
    subscriptionKey = "5e0ddbf7e50c43ec9609c3d5a1311478"
    customConfigId = "9f8b2731-9e63-40b6-8e3f-0341d2429efa"

    #la palabra que busca el usuario
    searchTerm = calzado
    #acá armamos la solicitud al api con los datos
    url = 'https://api.bing.microsoft.com/v7.0/custom/search?' + 'q=' + searchTerm + '&' + 'customconfig=' + customConfigId + "&mkt=en-MX&count=12"
    #aquí ya hacemos el request
    r = requests.get(url, headers={'Ocp-Apim-Subscription-Key': subscriptionKey})
    tenis = r.json()#lo paso a Json para manejarlo más facil
    #acá recorremos el json y así tomamos el snippet de cada objeto
    tienda =""
    imagen= ""
    data= []
    for item in tenis["webPages"]["value"]:
        url = "";tienda = "";imagen= "" #filtramos para no pasar páginas basura
        #esto podría ser opcional si el usuario no busca algo exacto, pero eso aún estoy pensando como implementarlo en el front
        if "vans" in item['url'] and "/p" in item['url']:
            tienda="vans"
        elif "nike" in item['url'] and "/t/" in item['url']:
            tienda="nike"
        elif "coppel" in item['url'] and "-pr-" in item['url']:
            tienda="coppel"

        url=item['url']
        if not (tienda == " " or tienda ==""):        
            scrap= scrapping(url,tienda)
            if not type(scrap) is int:
                if not (tienda == " " or  "amazon" in tienda):
                    if 'openGraphImage' in item:                
                        imagen= item['openGraphImage']['contentUrl']
                        scrap['imagen'] = imagen
                scrap['tienda']= tienda
                data.append(scrap)
            else:
                continue
    #print(type(data))
    resultado = json.dumps(data,indent = 4)
    return jsonify(data) 
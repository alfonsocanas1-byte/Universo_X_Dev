from flask import Flask, render_template_string, request, redirect
import json
import os

app = Flask(__name__)
DATA_FILE = 'datos_inventario.json'

def cargar_datos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"productos": {}, "historial": []}

def guardar_datos(datos):
    with open(DATA_FILE, 'w') as f:
        json.dump(datos, f, indent=4)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sistema de Control - Aion</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: #d1d1d1; padding: 20px; }
        .container { max-width: 900px; margin: auto; }
        h1 { border-bottom: 2px solid #0056b3; padding-bottom: 10px; color: #fff; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .card { background: #151515; padding: 20px; border-radius: 8px; border: 1px solid #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #111; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #222; }
        th { color: #007bff; text-transform: uppercase; font-size: 0.8em; }
        input, select, button { width: 90%; padding: 10px; margin: 8px 0; background: #222; border: 1px solid #444; color: white; border-radius: 4px; }
        button { background: #0056b3; border: none; font-weight: bold; cursor: pointer; width: 100%; }
        button:hover { background: #007bff; }
        .btn-sacar { background: #b30000; }
        .btn-sacar:hover { background: #ff0000; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 Centro de Mando: Inventario</h1>
        
        <div class="card">
            <h3>Estado Actual del Mercado</h3>
            <table>
                <thead>
                    <tr><th>Producto</th><th>Cant.</th><th>Unidad</th><th>Ubicación</th></tr>
                </thead>
                <tbody>
                    {% for nombre, info in datos.productos.items() %}
                    <tr>
                        <td><strong>{{ nombre }}</strong></td>
                        <td>{{ info.cantidad }}</td>
                        <td>{{ info.unidad }}</td>
                        <td>{{ info.lugar }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📥 Ingresar / Abastecer</h3>
                <form action="/agregar" method="post">
                    <input type="text" name="nombre" placeholder="Nombre del producto" required>
                    <input type="number" step="0.1" name="cantidad" placeholder="Cantidad" required>
                    <input type="text" name="unidad" placeholder="Unidad (kg, litros, etc.)" required>
                    <input type="text" name="lugar" placeholder="Lugar de guardado (Alacena, Nevera...)" required>
                    <button type="submit">Cargar al Inventario</button>
                </form>
            </div>

            <div class="card">
                <h3>📤 Sacar Producto</h3>
                <form action="/sacar" method="post">
                    <select name="nombre">
                        {% for nombre in datos.productos.keys() %}
                        <option value="{{ nombre }}">{{ nombre }}</option>
                        {% endfor %}
                    </select>
                    <input type="number" step="0.1" name="cantidad" placeholder="Cantidad a sacar" required>
                    <button type="submit" class="btn-sacar">Confirmar Salida</button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    datos = cargar_datos()
    return render_template_string(HTML_TEMPLATE, datos=datos)

@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form.get('nombre').capitalize()
    cantidad = float(request.form.get('cantidad'))
    unidad = request.form.get('unidad')
    lugar = request.form.get('lugar')
    
    datos = cargar_datos()
    
    if nombre in datos['productos']:
        # Si coincide el nombre, sumamos la cantidad
        datos['productos'][nombre]['cantidad'] += cantidad
        # Opcional: Actualizar el lugar si se desea
        datos['productos'][nombre]['lugar'] = lugar 
    else:
        # Si es nuevo, lo creamos
        datos['productos'][nombre] = {
            "cantidad": cantidad,
            "unidad": unidad,
            "lugar": lugar
        }
    
    guardar_datos(datos)
    return redirect('/')

@app.route('/sacar', methods=['POST'])
def sacar():
    nombre = request.form.get('nombre')
    cantidad_a_sacar = float(request.form.get('cantidad'))
    
    datos = cargar_datos()
    if nombre in datos['productos']:
        if datos['productos'][nombre]['cantidad'] >= cantidad_a_sacar:
            datos['productos'][nombre]['cantidad'] = round(datos['productos'][nombre]['cantidad'] - cantidad_a_sacar, 2)
            # Si el stock llega a 0, podrías elegir borrarlo o dejarlo en 0. Aquí se queda en 0.
            guardar_datos(datos)
            
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
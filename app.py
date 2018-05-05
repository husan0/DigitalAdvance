from flask import Flask,render_template,request,redirect,flash,session
from flaskext.mysql import MySQL
from werkzeug.utils import secure_filename
import os

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'mi clave es secreta'

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'bd_proyecto'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = 'static/Uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

mysql.init_app(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# VIEWS -----------------------------------------------------------------

@app.route('/')
def main():
    if session.get('username'):
        return render_template('index.html')
    else:
        return render_template('login.html')


@app.route('/index')
def inicio():
    if session.get('username'):
        return render_template('index.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')


# -------------------------------PRODUCTOS-------------------------------
@app.route('/irBuscar')
def irBuscar():
    if session.get('username'):
        return render_template('producto/buscar.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')


@app.route('/irAgregar')
def irAgregar():
    if session.get('username'):
        return render_template('producto/agregar.html', lista=getTipoProducto(), listaC=getCategoria(),listaTP=getTipoPrecio())
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')


@app.route('/irEliminar')
def irEliminar():
    if session.get('username'):
        return render_template('producto/eliminar.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')



@app.route('/irListar')
def irListar():
    if session.get('username'):
        return render_template('producto/listar.html',productos=listarProducto(), stock=getStockProducto(),
        detalle=getDetalle(),tipoPrecio=getTipoPrecio(),categoria=getCategoria(),tipoProducto=getTipoProducto())
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')


@app.route('/irModificar')
def irModificar():
    if session.get('username'):
        return render_template('producto/modificar.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')


# -------------------------------USUARIOS-------------------------------

# ----------------------------------------------------------------------
@app.route('/volver')
def volver():
    if session.get('username'):
        return render_template('index.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')


@app.route('/respuesta')
def respuesta():
    if session.get('username'):
        return render_template('respuesta.html')
    else:
        flash('ACCESO NO AUTORIZADO')
        return render_template('login.html')


@app.route('/desconectar')
def desconectar():
    session.pop('username', None)
    flash('Desconectado :(')
    return redirect('/')


# ------------------------FUNCIONES PRODUCTO------------------------------

@app.route('/buscar', methods=['POST'])
def webBuscar():
    nombre_producto = request.form['nombre']
    data = buscarProducto(nombre_producto)
    if len(data) is 0:
        flash('no existen registros')
        return render_template('producto/buscar.html')
    else:
        return render_template('producto/buscar.html', id=data[0][0], codigo=data[0][1], nombre=data[0][2],
                               stock=data[0][3], precio=data[0][4],tipoPrecio=data[0][5], categoria=data[0][6],
                               tipo=data[0][7], detalle=data[0][9],
                               imagen=os.path.join(app.config['UPLOAD_FOLDER'], data[0][8]))


@app.route('/buscarModificar', methods=['POST'])
def buscarModificar():
    nombre_producto = request.form['nombre']
    data = buscarProductoModificar(nombre_producto)
    if len(data) is 0:
        flash('no existen registros')
        return render_template('producto/modificar.html')
    else:
        session["id_producto"] = data[0][0]
        session["img_producto"] = os.path.join(app.config['UPLOAD_FOLDER'], data[0][7])
        return render_template('producto/modificar.html', nombre=data[0][1], stock=data[0][2], precio=data[0][3],
                               tipo=data[0][5], categoria=data[0][4], detalle=data[0][6],
                               imagen=os.path.join(app.config['UPLOAD_FOLDER'], data[0][7]),
                               activo=data[0][8],
                               tipo_producto=getTipoProducto(), categoria_producto=getCategoria())



@app.route('/agregar', methods=['POST'])
def webAgregar():
    codigo_de_barras = request.form['codigoBarras']
    nombre_producto = request.form['nombreProducto']
    detalle = request.form['detalle']
    categoria = request.form.get('categoria')
    tipo = request.form.get('tipoProducto')
    file = request.files['file']
    cantidad = request.form['cantidad']
    precio = request.form['price']
    tipo_precio = request.form.get('tipoPrecio')
    data = agregarProducto(codigo_de_barras,nombre_producto, detalle, categoria, tipo, file, cantidad, precio,tipo_precio)
    if len(data) is 0:
        flash('Agregado correctamente')
        return render_template('index.html')
    else:
        flash('No se puede agregar')
        return render_template('index.html')

@app.route('/eliminarProducto', methods=['POST'])
def WebEliminarProducto():
    nombre_producto = request.form['nombre_producto']
    data = eliminarProducto(nombre_producto)
    if data ==  1:
        flash('Eliminado correctamente')
        return render_template('index.html')
    else:
        flash('No se puede Eliminar')
        return render_template('index.html')


@app.route('/modificarProductos', methods=['POST', 'GET'])
def WebModificarProducto():
    id_producto=session["id_producto"]
    nombre_producto = request.form['nombre']
    stock_producto = request.form['stock']
    precio_producto = request.form['precio']
    id_tipo_categoria= request.form['categoria_producto']
    id_tipo_producto= request.form['tipo_producto']
    detalle_producto= request.form['detalle_producto']

    activo = request.form['activo']
    if request.files['file']:
        file = request.files['file']
    else:
        file = session["img_producto"]
    data = modificar_producto(id_producto, nombre_producto, stock_producto, precio_producto, id_tipo_categoria, id_tipo_producto, detalle_producto, file, activo)
    if data==1:
        flash('Modificado correctamente')
        return render_template('index.html')
    else:
        flash('No se puede modificar')
        return render_template('index.html')

@app.route('/login', methods=['POST'])
def webLogin():
    try:
        user_email = request.form['email']
        user_pass = request.form['password']
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM `usuario` WHERE `correo_usuario`= %(user)s and `contrasenia_usuario`= %(pass)s ',
                       {'user': user_email, 'pass': user_pass})
        data = cursor.fetchall()
        if len(data) is 1:
            session['username'] = data[0][1]
            flash('Bienvenido')
            return render_template('index.html')
        else:
            flash('Error usuario o contraseña incorrecto')
            return render_template('login.html')
    except Exception as e:
        return render_template('respuesta.html', respuesta=str(e))
    finally:
        cursor.close()
        con.close()


def buscarProducto(nombre_producto):
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute(
            'SELECT p.id_producto,p.codigo_de_barras,p.nombre_producto,sp.cantidad_stock ,dp.precio,tp.nombre_tipo_precio,cp.nombre_categoria,tpo.nombre_tipo,p.direccion_foto_producto,p.detalle_producto,p.activo FROM producto p JOIN stock_producto sp on p.id_stock_producto=sp.id_stock_producto JOIN detalle_producto dp on p.id_detalle_producto=dp.id_detalle_producto JOIN tipo_precio tp on dp.id_tipo_precio=tp.id_tipo_precio JOIN categoria_producto cp ON p.id_categoria=cp.id_categoria JOIN tipo_producto tpo on p.id_tipo_producto=tpo.id_tipo_producto WHERE nombre_producto= %(id)s',
            {'id': nombre_producto})
        data = cursor.fetchall()
        return data
    except Exception as e:
        return render_template('respuesta.html', respuesta=str(e))
    finally:
        cursor.close()
        con.close()

def buscarProductoModificar(nombre_producto):
        try:
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM producto WHERE nombre_producto= %(nombre_producto)s ',
                           {'nombre_producto': nombre_producto})
            data = cursor.fetchall()
            return data
        except Exception as e:
            return render_template('respuesta.html', respuesta=str(e))
        finally:
            cursor.close()
            con.close()

def agregarProducto(codigo_de_barras,nombre_producto, detalle, categoria, tipo, file, cantidad, precio,tipo_precio):
    try:
        con = mysql.connect()
        cursor = con.cursor()
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if len(buscarProducto(nombre_producto)) is 0:
                cursor.callproc('AgregarProducto',(codigo_de_barras,nombre_producto, detalle, categoria, tipo, filename, cantidad, precio,tipo_precio))
                data = cursor.fetchall()
                if len(data) is 0:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    con.commit()
                    return data
                else:
                    return data
            else:
                return data
        else:
            return data
    except Exception as e:
        return render_template('respuesta.html', respuesta=str(e))
    finally:
        cursor.close()
        con.close()


def getTipoProducto():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM `tipo_producto`')
        data = cursor.fetchall()
        return data
    except Exception as e:
        return render_template('respuesta.html', respuesta=str(e))
    finally:
        cursor.close()
        con.close()


def getCategoria():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM `categoria_producto`')
        data = cursor.fetchall()
        return data
    except Exception as e:
        return render_template('respuesta.html', respuesta=str(e))
    finally:
        cursor.close()
        con.close()

def getDetalle():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM `detalle_producto` ')
        data = cursor.fetchall()
        return data
    except Exception as e:
        return render_template('respuesta.html', respuesta=str(e))
    finally:
        cursor.close()
        con.close()

def getTipoPrecio():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM `tipo_precio` ')
        data = cursor.fetchall()
        return data
    except Exception as e:
        return render_template('respuesta.html', respuesta=str(e))
    finally:
        cursor.close()
        con.close()

def getStockProducto():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute('SELECT * FROM `stock_producto`')
        data = cursor.fetchall()
        return data
    except Exception as e:
        return render_template('respuesta.html', respuesta=str(e))
    finally:
        cursor.close()
        con.close()


#SELECT p.id_producto,p.codigo_de_barras,p.nombre_producto,sp.cantidad_stock ,dp.precio,tp.nombre_tipo_precio,cp.nombre_categoria,tpo.nombre_tipo,p.direccion_foto_producto,p.activo FROM producto p JOIN stock_producto sp on p.id_stock_producto=sp.id_stock_producto JOIN detalle_producto dp on p.id_detalle_producto=dp.id_detalle_producto JOIN tipo_precio tp on dp.id_tipo_precio=tp.id_tipo_precio JOIN categoria_producto cp ON p.id_categoria=cp.id_categoria JOIN tipo_producto tpo on p.id_tipo_producto=tpo.id_tipo_producto 

def listarProducto():
    try:
        con = mysql.connect()
        cursor = con.cursor()   
        cursor.execute('SELECT * FROM `producto` WHERE `activo` = 1')
        data = cursor.fetchall()
        return data
    except Exception as e:
         return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()


def eliminarProducto(nombre_producto):
    con = mysql.connect()
    try:
        with con.cursor() as cursor:
            cursor.execute('UPDATE `producto` SET `activo`= 0 WHERE `nombre_producto` = %(name)s', {'name': nombre_producto})
            data = cursor.rowcount
            if data == 1:
                con.commit()
                return data
            else:
                return data
    except Exception as e:
        return render_template('respuesta.html', respuesta=str(e))
    finally:
        cursor.close()
        con.close()

def modificar_producto(id_producto, nombre_producto, stock_producto, precio_producto, categoria, id_tipo_producto, detalle_producto, file, activo):
    con = mysql.connect()
    try:
        with con.cursor() as cursor:
            filename = secure_filename(file.filename)
            sql = "UPDATE `producto` SET `nombre_producto`= %s,`stock_producto`= %s, `precio_producto`= %s, `id_categoria`=%s,`id_tipo_producto`= %s, `detalle_producto`= %s, `direccion_foto_producto`= %s, `activo`= %s WHERE id_producto= %s"
            cursor.execute(sql, (nombre_producto, stock_producto, precio_producto, categoria, id_tipo_producto, detalle_producto, filename, activo, id_producto))
            data=cursor.rowcount
            if data==1:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                con.commit()
                return data
            else:
                return data
    except Exception as e:
        return render_template('respuesta.html',respuesta = str(e))
    finally:
        cursor.close()
        con.close()

# ejecucion de la aplicacion
if __name__ == "__main__":
    app.run(debug=True)


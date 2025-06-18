import hashlib
import os

ARCHIVO_USUARIOS = "USUARIOS.TXT"

def simular_hash(contraseña):
    return hashlib.sha256(contraseña.encode()).hexdigest()

def usuario_existe(nombre_usuario):
    if not os.path.exists(ARCHIVO_USUARIOS):
        return False
    with open(ARCHIVO_USUARIOS, "r") as f:
        lineas = f.readlines()
    for i in range(0, len(lineas), 14):
        if len(lineas[i:i+14]) < 14:
            continue
        nombre_usuario_arch = lineas[i+4].strip().split(":", 1)[1].strip()
        if nombre_usuario == nombre_usuario_arch:
            return True
    return False

def registrar_usuario(nombre, nombre_usuario, contraseña, rol, correo, fecha_nac,
                      mascota, escuela, ciudad, amor):
    if usuario_existe(nombre_usuario):
        return False  # Usuario ya existe

    contraseña_hash = simular_hash(contraseña)

    try:
        with open(ARCHIVO_USUARIOS, "a") as f:
            f.write("---- Usuarios registrados:----\n")
            f.write("\n\n")
            f.write(f"Nombre: {nombre}\n")
            f.write(f"Nombre de usuario: {nombre_usuario}\n")
            f.write(f"Contraseña (hash): {contraseña_hash}\n")
            f.write(f"Rol: {rol.lower()}\n")
            f.write(f"Correo: {correo}\n")
            f.write(f"Fecha de nacimiento: {fecha_nac}\n")
            f.write(f"Pregunta 1 - Mascota: {mascota}\n")
            f.write(f"Pregunta 2 - Escuela: {escuela}\n")
            f.write(f"Pregunta 3 - Ciudad natal: {ciudad}\n")
            f.write(f"Pregunta 4 - Primer amor: {amor}\n")
            f.write("-" * 40 + "\n")
        return True
    except:
        return False

def iniciar_sesion(nombre_usuario_input, contraseña_input):
    contraseña_hash_input = simular_hash(contraseña_input)

    if not os.path.exists(ARCHIVO_USUARIOS):
        return None  # No hay archivo aún

    with open(ARCHIVO_USUARIOS, "r") as f:
        lineas = f.readlines()

    for i in range(0, len(lineas), 14):
        bloque = lineas[i:i+14]
        if len(bloque) < 14:
            continue
        try:
            nombre_arch           = bloque[3].strip().split(":", 1)[1].strip()
            nombre_usuario_arch   = bloque[4].strip().split(":", 1)[1].strip()
            hash_arch             = bloque[5].strip().split(":", 1)[1].strip()
            rol                   = bloque[6].strip().split(":", 1)[1].strip()
            correo                = bloque[7].strip().split(":", 1)[1].strip()
            fecha_nac             = bloque[8].strip().split(":", 1)[1].strip()
            # preguntas omitidas aquí

            if nombre_usuario_input == nombre_usuario_arch:
                if contraseña_hash_input == hash_arch:
                    return rol  # Login correcto
                else:
                    return None  # Contraseña incorrecta
        except:
            continue

    return None  # Usuario no encontrado

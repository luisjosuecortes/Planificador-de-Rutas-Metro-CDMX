import cv2
import csv

# Configuración inicial
estaciones = []
relacion_escala = 1.0
offset_x, offset_y = 0, 0
max_ancho_ventana = 1280
max_alto_ventana = 720

# Función para redimensionamiento de alta calidad
def redimensionar_alta_calidad(imagen, escala):
    if escala < 1.0:
        return cv2.resize(imagen, None, fx=escala, fy=escala, 
                        interpolation=cv2.INTER_LANCZOS4)
    else:
        return cv2.resize(imagen, None, fx=escala, fy=escala, 
                        interpolation=cv2.INTER_CUBIC)

# Función para actualizar la visualización
def actualizar_visualizacion():
    global img_mostrar, relacion_escala, offset_x, offset_y
    
    img_escalada = redimensionar_alta_calidad(img_original, relacion_escala)
    h, w = img_escalada.shape[:2]
    
    offset_x = (max_ancho_ventana - w) // 2
    offset_y = (max_alto_ventana - h) // 2
    
    img_mostrar = cv2.copyMakeBorder(img_escalada, 
                                   offset_y, 
                                   max_alto_ventana - h - offset_y,
                                   offset_x,
                                   max_ancho_ventana - w - offset_x,
                                   cv2.BORDER_CONSTANT, 
                                   value=[0,0,0])
    
    cv2.imshow('Mapa del Metro', img_mostrar)

# Callback para eventos del mouse
def click_event(event, x, y, flags, param):
    global relacion_escala, offset_x, offset_y
    
    if event == cv2.EVENT_LBUTTONDOWN:
        x_original = int((x - offset_x) / relacion_escala)
        y_original = int((y - offset_y) / relacion_escala)
        
        if 0 <= x_original < width and 0 <= y_original < height:
            print(f"\nCoordenadas seleccionadas: ({x_original}, {y_original})")
            nombre = input("Ingrese el nombre de la estación: ").strip()
            linea = input("Ingrese el número de línea: ").strip()
            
            estaciones.append({
                'coordenadas': (x_original, y_original),
                'nombre': nombre,
                'linea': linea
            })
            
            # Dibujar en la imagen original
            cv2.circle(img_original, (x_original, y_original), 5, (0, 0, 255), -1)
            actualizar_visualizacion()

# Cargar imagen
img_original = cv2.imread('metro.jpg')
if img_original is None:
    print("Error: No se pudo cargar la imagen. Verifica:")
    print("- Que el archivo exista y tenga extensión .png")
    print("- Que esté en el mismo directorio que este script")
    exit()

height, width = img_original.shape[:2]

# Configurar ventana
cv2.namedWindow('Mapa del Metro', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Mapa del Metro', max_ancho_ventana, max_alto_ventana)
cv2.setMouseCallback('Mapa del Metro', click_event)

# Escala inicial
relacion_escala = min(max_ancho_ventana/width, max_alto_ventana/height)
actualizar_visualizacion()

# Instrucciones
print("\n[ Dimensiones originales ]")
print(f"Ancho: {width}px | Alto: {height}px")
print("\n[ Controles ]")
print("+ : Acercar (Zoom in)")
print("- : Alejar (Zoom out)")
print("ESC: Guardar y salir")
print("\n[ Registro de estaciones ]")
print("Haz clic en cada estación y sigue las indicaciones en la terminal")

# Bucle principal
while True:
    key = cv2.waitKey(0) & 0xFF
    
    # Control de zoom
    if key == 43:  # Tecla '+'
        relacion_escala *= 1.1
        actualizar_visualizacion()
    elif key == 45:  # Tecla '-'
        relacion_escala *= 0.9
        actualizar_visualizacion()
    elif key == 27:  # ESC
        break

# Guardar datos en CSV
if estaciones:
    with open('estaciones_metro.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Encabezado con dimensiones
        writer.writerow(['METADATOS'])
        writer.writerow(['Ancho_original', width])
        writer.writerow(['Alto_original', height])
        writer.writerow([])
        
        # Datos de estaciones
        writer.writerow(['LINEA', 'ESTACION', 'COORD_X', 'COORD_Y'])
        for estacion in estaciones:
            writer.writerow([
                estacion['linea'],
                estacion['nombre'],
                estacion['coordenadas'][0],
                estacion['coordenadas'][1]
            ])
    
    # Resumen en terminal
    print("\n[ Resumen final ]")
    print(f"Total de estaciones registradas: {len(estaciones)}")
    print("Detalles:")
    for idx, estacion in enumerate(estaciones, 1):
        print(f"{idx}. Línea {estacion['linea']} - {estacion['nombre']}: {estacion['coordenadas']}")
    
    print(f"\nArchivo generado: 'estaciones_metro.csv'")
else:
    print("\nNo se registraron estaciones")

cv2.destroyAllWindows()
print("\nPrograma finalizado exitosamente")
# Libreta del Entrenador

Web para un entrenador de gimnasio: alumnos, rutinas de funcional (AMRAP, EMOM…), calendario de clases y entrenamientos.

- Se usa desde el iPhone: abrir la web en Safari → Compartir → **Añadir a pantalla de inicio**, y usarla siempre desde ese icono.
- Los datos se guardan **solo en el móvil** (IndexedDB). Nada se sube a ningún servidor ni a este repositorio.
- Para cambiar de móvil: Ajustes → **Guardar copia de seguridad** y, en el móvil nuevo, **Recuperar una copia**.

`index.html` se genera con `python3 tools/build_standalone.py` a partir de `tools/gym.html`.

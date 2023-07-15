import unicodedata
import pickle
import string
import os

# Mapeo de teclas T9 a letras, considerando letras acentuadas
t9 = {
    '2': 'abcáàäâãç',
    '3': 'deféèëê',
    '4': 'ghiíìïî',
    '5': 'jkl',
    '6': 'mnoóòöôõñ',
    '7': 'pqrs',
    '8': 'tuvúùüû',
    '9': 'wxyz',
}

# Crear grupos de letras para el mapeo T9
letter_groups = ['ABCÁÄ', 'DEFÉË', 'GHIÍÏ', 'JKL', 'MNOÑÓÖ', 'PQRS', 'TUVÚÜ', 'WXYZÇ']
punctuation = string.punctuation
space = ' '

# Crear el diccionario de mapeo T9
t9_dict = {char: str(i + 2) for i, group in enumerate(letter_groups) for char in group}
for char in punctuation:
    t9_dict[char] = '1'
t9_dict[space] = '0'


class Node:
    def __init__(self):
        self.children = {}
        self.is_word = False


class Trie:
    def __init__(self):
        self.root = Node()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = Node()
            node = node.children[char]
        node.is_word = True

    def search(self, node, number, prefix):
        if number == "":
            if node.is_word:
                return [prefix]
            else:
                return []

        if number[0] not in t9:
            return []

        words = []
        for char in set(t9[number[0]]):  # use set for faster lookups
            if char in node.children:
                words.extend(self.search(node.children[char], number[1:], prefix + char))
        return words

    def search_one_edit(self, node, number, prefix):
        words = []
        for i in range(len(number)):
            for key in t9:
                if key != number[i]:
                    for char in set(t9[key]):  # use set for faster lookups
                        if char in node.children:
                            words.extend(self.search(node.children[char], number[i + 1:], prefix + char))
        words = [word for word in words if
                 len(number) - extra_char_limit <= len(word) <= len(number) + extra_char_limit]
        return words


# Función para normalizar texto (eliminar tildes y diéresis)
def normalize_text(text):
    normalized_text = ""
    for char in text:
        if char in ('ñ', 'ç'):
            normalized_text += char
        else:
            normalized_char = unicodedata.normalize('NFD', char)
            normalized_text += ''.join(
                c for c in normalized_char
                if unicodedata.category(c) != 'Mn'
            )
    return normalized_text


# Load trie from file if it exists
trie = None

# Autocorrect settings
correction_char_limit = 2
extra_char_limit = 2
use_correction_on_dictionary_words = False

if os.path.exists('trie.pkl'):
    with open('trie.pkl', 'rb') as f:
        trie = pickle.load(f)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    while True:
        print("Por favor, selecciona una de las siguientes opciones:")
        print("1) T9 a Español")
        print("2) Español a T9.")
        print("3) Generar Trie desde diccionario.txt.")
        print("4) Salir.",
        print("5) Configurar autocorrección."),
        )

        option = input("Introduce el número de la opción que deseas seleccionar: ")

        if option == "1":
            handle_option_1()
        elif option == "2":
            handle_option_2()
        elif option == "3":
            handle_option_3()
        elif option == "5":
            handle_option_5()
        elif option == "4":
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")


def handle_option_5():
    global correction_char_limit
    global extra_char_limit
    global use_correction_on_dictionary_words

    print("-== Configurar autocorrección ==-")
    try:
        print(
            "(1/3) Introduce cuantos caracteres se pueden modificar para la corrección.")

        #El valor de correction_char_limit determina cuántos caracteres se pueden corregir en la entrada original.
        # Si correction_char_limit es 1, entonces la función buscará palabras que se puedan obtener cambiando
        # un solo carácter en la entrada original. Si correction_char_limit es 2, la función buscará palabras que
        # se puedan obtener cambiando dos caracteres en la entrada original, y así sucesivamente.
        correction_char_limit = int(input("Límite de caracteres para corrección: "))
        print(
            "(2/3) Numero de caracteres ± que puede tener la palabra corregida respecto a la original")
        # Esta línea de código filtra la lista de palabras generadas para incluir sólo las palabras cuya longitud
        # está dentro del rango definido por la longitud de la entrada original (len(number)) más o menos el valor
        # de extra_char_limit.
        #
        # Por ejemplo, si la entrada original es 3 caracteres y extra_char_limit es 1, la función devolverá palabras
        # de longitud 2 a 4. Si extra_char_limit es 0, entonces la función devolverá solo palabras que tengan exactamente
        # la misma longitud que la entrada original
        extra_char_limit = int(input("Límite de caracteres extra: "))
        print("¿Quieres generar resultados de palabras corregidas para respuestas que sí están en el diccionario?")

        use_correction_on_dictionary_words = input(
            # La variable use_correction_on_dictionary_words determina si el programa debe intentar buscar posibles
            # correcciones para palabras que ya se encuentran en el diccionario.
            #
            # Si use_correction_on_dictionary_words es True, entonces incluso cuando se encuentra una palabra exacta
            # en el diccionario, el programa aún buscará y devolverá palabras "corregidas" que están a una distancia
            # de edición de la entrada original. Esto puede ser útil si se sospecha que la entrada original podría
            # contener errores de tipeo, incluso si resulta en una palabra válida.
            #
            # Por otro lado, si use_correction_on_dictionary_words es False, entonces cuando se encuentra una palabra
            # exacta en el diccionario, el programa asume que esta es la palabra correcta y no busca ni devuelve palabras "corregidas".

            "(3/3) Generar palabras corregidas para respuestas en el diccionario (s/n): ").lower() == 's'
    except ValueError:
        print("Entrada no válida. Por favor, intenta de nuevo.")

    input("Presiona enter para continuar.")
    clear_screen()


def handle_option_1():
    global trie  # Agregar esta línea para acceder a la variable global trie
    print("-== T9 a Español ==-")
    if trie is None:
        print("No se encontró el archivo Trie. Por favor, genera un Trie primero usando la opción 3.")
        return
    codigo = input("Por favor, introduce los números T9 a traducir, separa las palabras con 0: ")
    palabras_por_seccion = generar_palabras(codigo)
    for i, palabras in enumerate(palabras_por_seccion):
        print(f"Las palabras generadas para la sección {i + 1} son: {', '.join(palabras)}")
    input("Presiona enter para continuar.")
    clear_screen()


def handle_option_2():
    print("-== Español a T9. ==-")
    text = input("Introduce el texto que quieres convertir: ")
    t9_text = translate_to_t9(text)
    print("Texto en formato T9: ", t9_text)

    try:
        import pyperclip
        if input("Presionar 1 para copiar en el portapapeles: ") == "1":
            pyperclip.copy(t9_text)
            print("Texto copiado al portapapeles.")
    except ModuleNotFoundError:
        print("El módulo 'pyperclip' no está instalado. Copia el texto manualmente.")

    input("Presiona enter para continuar.")
    clear_screen()


def handle_option_3():
    print("-== Generar Trie desde diccionario.txt. ==-")
    trie = Trie()
    with open('diccionario.txt', 'r', encoding='utf-8') as f:
        for linea in f:
            trie.insert(normalize_text(linea.strip()))
    with open('trie.pkl', 'wb') as f:
        pickle.dump(trie, f)
    input("Presiona enter para continuar.")
    clear_screen()


def generar_palabras(codigo):
    secciones = codigo.split('0')
    palabras_por_seccion = []
    for seccion in secciones:
        palabras = trie.search(trie.root, seccion, "")
        if not palabras or use_correction_on_dictionary_words:
            palabras_corregidas = trie.search_one_edit(trie.root, seccion, "")
            if palabras_corregidas:
                palabras = ["(corregida) "] + palabras_corregidas
        palabras_por_seccion.append(palabras)
    return palabras_por_seccion


def translate_to_t9(text):
    text = text.upper()
    t9_text = "".join(t9_dict.get(char, char) for char in text)
    return t9_text


if __name__ == "__main__":
    main()
    clear_screen()

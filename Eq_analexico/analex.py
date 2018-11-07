#!/usr/bin/env python

import componentes
#import errores
import flujo
import string
import sys

from sys import argv
from sets import ImmutableSet


class Analex:
    #############################################################################
    # Conjunto de palabras reservadas para comprobar si un identificador es PR
    #############################################################################
    PR = ImmutableSet(["PROGRAMA", "VAR", "VECTOR", "DE", "ENTERO", "REAL", "BOOLEANO", "PROC", "FUNCION", "INICIO",
                       "FIN", "SI", "ENTONCES", "SINO", "MIENTRAS", "HACER", "LEE", "ESCRIBE", "Y", "O", "NO", "CIERTO", "FALSO"])

    ############################################################################
    #
    #  Funcion: __init__
    #  Tarea:  Constructor de la clase
    #  Prametros:  flujo:  flujo de caracteres de entrada
    #  Devuelve: --
    #
    ############################################################################
    def __init__(self, flujo):
        # Debe completarse con  los campos de la clase que se consideren necesarios

        self.nlinea = 1  # contador de lineas para identificar errores
        self.flujo = flujo
    ############################################################################
    #
    #  Funcion: Analiza
    #  Tarea:  Identifica los diferentes componentes lexicos
    #  Prametros:  --
    #  Devuelve: Devuelve un componente lexico
    #
    ############################################################################

    def Analiza(self):

        ch = self.flujo.siguiente()

        if ch == " ":
            # quitar todos los caracteres blancos
            return self.Analiza()
            # buscar el siguiente componente lexico que sera devuelto )
        elif ch == "+":
            return componentes.OpAdd("SimSum", self.nlinea)

        elif ch == "-":
            return componentes.OpAdd("SimRest", self.nlinea)
         # debe crearse un objeto de la clasee OpAdd que sera devuelto

        elif ch == "*":
            return componentes.OpMult("SimMult", self.nlinea)

        elif ch == "/":
            return componentes.OpMult("SimDiv", self.nlinea)

        elif ch == "[":
            return componentes.CorAp()

        elif ch == "]":  # asi con todos los simbolos y operadores del lenguaje
            return componentes.CorCi()

        elif ch == "{":
            # Saltar todos los caracteres del comentario
            while(ch != "}"):
                ch = self.flujo.siguiente()

            # Comprobamos que hemos cerrado el comentario
            if ch != "}":
                print "ERROR: Comentario no cerrado"  # tenemos un comentario no cerrado

            # y encontrar el siguiente componente lexico
            return self.Analiza()

        elif ch == "}":
            print "ERROR: Comentario no abierto"  # tenemos un comentario no abierto
            return self.Analiza()

        elif ch == ":":
            # Comprobar con el siguiente caracter si es una definicion de la declaracion o el operador de asignacion
            ch = self.flujo.siguiente()

            if ch == '=':
                return componentes.OpAsigna()

            else:
                self.flujo.devuelve(ch)
                return componentes.DosPtos()

        elif ch == '(':
            return componentes.ParentAp()

        elif ch == ')':
            return componentes.ParentCi()

        elif ch == '.':
            return componentes.Punto()

        elif ch == ',':
            return componentes.Coma()

        elif ch == ';':
            return componentes.PtoComa()

        elif ch == ':':
            return componentes.DosPtos()

        elif ch == "=":
            return componentes.OpRel("SimIgual", self.nlinea)

        elif ch == "<":
            ch = self.flujo.siguiente()

            if ch == ">":
                return componentes.OpRel("SimDist", self.nlinea)
            elif ch == "=":
                return componentes.OpRel("SimMenIgual", self.nlinea)
            else:
                self.flujo.devuelve(ch)
                return componentes.OpRel("SimMenor", self.nlinea)

        elif ch == ">":
            ch = self.flujo.siguiente()
            if ch == "=":
                return componentes.OpRel("SimMayIgual", self.nlinea)
            else:
                self.flujo.devuelve(ch)
                return componentes.OpRel("SimMayor", self.nlinea)

        elif ch.isalpha():
            # leer entrada hasta que no sea un caracter valido de un identificador
            cadena = "" + ch

            ch = self.flujo.siguiente()

            while ch.isalnum():
                cadena = cadena + ch
                ch = self.flujo.siguiente()

            # devolver el ultimo caracter a la entrada
            self.flujo.devuelve(ch)

            # Comprobar si es un identificador o PR y devolver el objeto correspondiente
            if(cadena in Analex.PR):
                return componentes.PR(cadena, self.nlinea)
            else:
                return componentes.Identif(cadena, self.nlinea)

        elif ch.isdigit():
            # Leer todos los elementos que forman el numero
            numero = "" + ch
            puntoDetectado = 0

            ch = self.flujo.siguiente()

            while ch.isdigit():

                numero = numero + ch
                ch = self.flujo.siguiente()

            # Es un entero
            if ch != ".":
                self.flujo.devuelve(ch)
                return componentes.Numero(numero, self.nlinea, int)

            # Puede ser un real
            else:

                real = numero + ch
                ch = self.flujo.siguiente()

                #Guardamos el numero de digitos decimales
                digitosDecimales = 0

                # Comprobamos que lo siguiente del punto sea un digito
                while ch.isdigit():
                    digitosDecimales += 1

                    real = real + ch
                    ch = self.flujo.siguiente()

                # devolver el ultimo caracter que ya no pertenece al numero a la entrada
                self.flujo.devuelve(ch)

                # No es un valor de tipo de real. Devolvemos el tipo entero
                if digitosDecimales == 0:
                    self.flujo.devuelve(ch) #Devolvemos el caracter decimal al flujo de entrada
                    return componentes.Numero(numero, self.nlinea, int)

                # Es un valor real. Devolvemos el tipo real
                else:
                    return componentes.Numero(real, self.nlinea, float)

        elif ch == "\n":
            # incrementa el numero de linea ya que acabamos de saltar a otra
            self.nlinea += 1
            # devolver el siguiente componente encontrado
            return self.Analiza()

        elif len(ch) == 0:
            return

        else:
            return self.Analiza()


############################################################################
#
#  Funcion: __main__
#  Tarea:  Programa principal de prueba del analizador lexico
#  Prametros:  --
#  Devuelve: --
#
############################################################################
if __name__ == "__main__":
    script, filename = argv
    txt = open(filename)
    print "Este es tu fichero %r" % filename
    i = 0
    fl = flujo.Flujo(txt)
    analex = Analex(fl)
    try:
        c = analex.Analiza()
        while c:
            print c
            c = analex.Analiza()
        i = i+1

    # except errores.Error, err:
       #sys.stderr.write("%s\n" % err)
       # analex.muestraError(sys.stderr)
    except Exception as e:
        print(e)

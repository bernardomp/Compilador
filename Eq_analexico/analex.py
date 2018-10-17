#!/usr/bin/env python

import componentes
import errores
import flujo
import string
import sys

from sys import argv
from sets import ImmutableSet

class Analex:
#############################################################################
##  Conjunto de palabras reservadas para comprobar si un identificador es PR
#############################################################################
 PR = ImmutableSet(["PROGRAMA", "VAR", "VECTOR","DE", "ENTERO", "REAL", "BOOLEANO", "PROC", "FUNCION", "INICIO", "FIN", "SI", "ENTONCES", "SINO", "MIENTRAS", "HACER", "LEE", "ESCRIBE", "Y", "O", "NO", "CIERTO","FALSO"])

 ############################################################################
 #
 #  Funcion: __init__
 #  Tarea:  Constructor de la clase
 #  Prametros:  flujo:  flujo de caracteres de entrada
 #  Devuelve: --
 #
 ############################################################################
 def __init__(self):
    #Debe completarse con  los campos de la clase que se consideren necesarios

    self.nlinea=1 #contador de lineas para identificar errores

 ############################################################################
 #
 #  Funcion: Analiza
 #  Tarea:  Identifica los diferentes componentes lexicos
 #  Prametros:  --
 #  Devuelve: Devuelve un componente lexico
 #
 ############################################################################
 def Analiza(self):
  
  ch=leerCaracter
  if ch==" ":
       # quitar todos los caracteres blancos 
       #buscar el siguiente componente lexico que sera devuelto )
  elif ch== "+":
   # debe crearse un objeto de la clasee OpAdd que sera devuelto
  elif  #asi con todos los simbolos y operadores del lenguaje
   return componentes.CorCi()
  elif ch == "{":
   #Saltar todos los caracteres del comentario 
   # y encontrar el siguiente componente lexico
  elif ch == "}":
   print "ERROR: Comentario no abierto" # tenemos un comentario no abierto
   return self.Analiza()
  elif ch==":":
    #Comprobar con el siguiente caracter si es una definicion de la declaracion o el operador de asignacion
  elif  
    #Completar los operadores y categorias lexicas que faltan
  elif ch es un caracter
    #leer entrada hasta que no sea un caracter valido de un identificador
    #devolver el ultimo caracter a la entrada
    # Comprobar si es un identificador o PR y devolver el objeto correspondiente
  elif ch es numero:
    #Leer todos los elementos que forman el numero 
    # devolver el ultimo caracter que ya no pertenece al numero a la entrada
    # Devolver un objeto de la categoria correspondiente 
  elif ch== "\n":
   #incrementa el numero de linea ya que acabamos de saltar a otra
   # devolver el siguiente componente encontrado


############################################################################
#
#  Funcion: __main__
#  Tarea:  Programa principal de prueba del analizador lexico
#  Prametros:  --
#  Devuelve: --
#
############################################################################
if __name__=="__main__":
    script, filename=argv
    txt=open(filename)
    print "Este es tu fichero %r" % filename
    i=0
    fl = flujo.Flujo(txt)
    analex=Analex(fl)
    try:
      c=analex.Analiza()
      while c :
       print c
       c=analex.Analiza()
      i=i+1
    except errores.Error, err:
     sys.stderr.write("%s\n" % err)
     analex.muestraError(sys.stderr)


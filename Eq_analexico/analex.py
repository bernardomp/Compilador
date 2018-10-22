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
    self.flujo = flujo
    self.esCaracter = lambda ch: (ord(ch) >= 65 and ord(ch) <= 90) or (ord(ch) >= 97 and ord(ch) <= 122)
    self.esNumero = lambda ch: ord(ch) >= 48 and ord(ch) <= 57
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
       return self.Analiza()
       #buscar el siguiente componente lexico que sera devuelto )
  elif ch == "+" or ch == "-":
   # debe crearse un objeto de la clasee OpAdd que sera devuelto
      return Componente.OpAdd(ch)
  elif ch== "*" or ch== "/":
      return Componente.OpMult(ch)

  elif ch == "[": 
      return Componente.CorAp()
  elif ch== "]":   #asi con todos los simbolos y operadores del lenguaje
   return componentes.CorCi()
  elif ch == "{":
   #Saltar todos los caracteres del comentario 
    while(ch != "}"):
        ch=self.flujo.siguiente()
   # y encontrar el siguiente componente lexico
   return self.Analiza()
  elif ch == "}":
   print "ERROR: Comentario no abierto" # tenemos un comentario no abierto
   return self.Analiza()
  elif ch==":":
    #Comprobar con el siguiente caracter si es una definicion de la declaracion o el operador de asignacion
     ch=self.flujo.siguiente()

     if ch  == '=':
        return Componente.OpAsigna()
      
      else:
        self.flujo.devuelve(ch)
        return self.Analiza()
  elif  ch == '(':
    return componentes.ParentAp()

  elif  ch == ')':
    return componentes.ParentCi()
  
  elif  ch == '.':
    return componentes.Punto()

  elif  ch == ',':
    return componentes.Coma()
  
  elif  ch == ';':
    return componentes.PtoComa()

  elif  ch == ':':
    return componentes.DosPto()
    #Completar los operadores y categorias lexicas que faltan

  elif self.esCaracter(ch):
    #leer entrada hasta que no sea un caracter valido de un identificador
    cadena = "" + ch

    ch = self.flujo.siguiente()
    
    while(self.esCaracter(ch) or self.esNumero(ch)):
      cadena = cadena + ch
      ch = self.flujo.siguiente()
    #devolver el ultimo caracter a la entrada
    self.flujo.devuelve(ch)
    # Comprobar si es un identificador o PR y devolver el objeto correspondiente
    if(cadena in PR):
      return componentes.PR(cadena,self.nlinea)
    else:
      return componentes.identif(cadena,self.nlinea)
  elif self.esNumero(ch):
    #Leer todos los elementos que forman el numero 
    numero = "" + ch
    puntoDetectado = False

    ch = self.flujo.siguiente()
      
    while(self.esNumero(ch) and puntoDetectado == False):

      if ch == ".":
        puntoDetectado = True

        numero = numero + ch
        ch = self.flujo.siguiente()
    # devolver el ultimo caracter que ya no pertenece al numero a la entrada
    self.flujo.devuelve(ch)

    # Devolver un objeto de la categoria correspondiente
    if puntoDetectado:
      return componentes.Numero(numero,"REAL")
      
    else:
      return componentes.Numero(numero,"ENTERO")

  elif ch== "\n":
   #incrementa el numero de linea ya que acabamos de saltar a otra
    self.nlinea+=1
   # devolver el siguiente componente encontrado
    return self.Analiza()


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


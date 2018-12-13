# -*- coding: latin-1 -*-
import sys

"""
import tipos
import Rossi
import errores
import etiquetas
import memoria
import BancoRegistros
registros = BancoRegistros.BancoRegistros()

R = Rossi
"""

class AST:
    def __str__(self):
        return self.arbol()


class NodoAsignacion(AST):
    def __init__(self, izda, exp, linea):
        self.izda = izda
        self.exp = exp
        self.linea = linea

    def compsemanticas(self):
       
        self.izda.compsemanticas()
        self.exp.compsemanticas()

        #Comprobacion semantica 3: Conversión implicita de enteros en reales
        if self.izda.tipo == "ENTERO" and self.exp.tipo in ["REAL","ENTERO"]:
            self.izda.tipo = self.exp.tipo

        elif self.izda.tipo == "REAL" and self.exp.tipo in ["REAL","ENTERO"]:
            self.izda.tipo = "REAL"

        elif self.izda.tipo == "BOOLEANO" and self.exp.tipo == "BOOLEANO":
            self.izda.tipo = "BOOLEANO"

        else:
            print("Tipos incompatibles en asignacion (%s y %s)." % (self.izda.tipo, self.exp.tipo), self.linea)

    def arbol(self):
        return '( "Asignacion"\n  "linea: %d" \n%s\n%s\n)' % (self.linea, self.izda, self.exp)



class NodoSi(AST):
    def __init__(self, cond, si, sino, linea):
        self.cond = cond
        self.si = si
        self.sino = sino
        self.linea = linea

    def compsemanticas(self):
        self.cond.compsemanticas()
        self.si.compsemanticas()
        self.sino.compsemanticas()

        if self.cond.tipo != "BOOLEANO":
    
            print("La condicion del si debe ser de tipo logico.", self.linea)


    def arbol(self):
        return '( "Si" "linea: %d" %s\n %s\n %s\n )' % (self.linea, self.cond, self.si, self.sino)

class NodoMientras(AST):

    def __init__(self, cond, cuerpo, linea):
        self.cond = cond
        self.cuerpo = cuerpo
        self.linea = linea
    
    def compsemanticas(self):
        self.cond.compsemanticas()
        self.cuerpo.compsemanticas()
    
        if self.cond.tipo != "BOOLEANO":
    
            print("La condicion debe ser de tipo logico.", self.linea)


    def arbol(self):
        return '( "Mientras" "linea: %d" %s\n %s\n %s\n )' % (self.linea, self.cond, self.cuerpo)

class NodoEscribe(AST):
    def __init__(self, exp, linea):
        self.exp = exp
        self.linea = linea

    def compsemanticas(self):
        self.exp.compsemanticas()
       
        if self.exp.tipo not in ["ENTERO","REAL","BOOLEANO"]:
            print("Solo se pueden escribir tipos ENTERO, REAL Y BOOLEANO",self.linea)


    def arbol(self):
        return '( "Escribe" "linea: %d" %s )' % (self.linea, self.exp)

class NodoLee(AST):
    def __init__(self, exp, linea):
        self.exp = exp
        self.linea = linea

    def compsemanticas(self):
        self.exp.compsemanticas()
       
        if self.exp.tipo not in ["ENTERO","REAL"]:
            print("Solo se pueden lee tipos ENTERO y REAL",self.linea)


    def arbol(self):
        return '( "Escribe" "linea: %d" %s )' % (self.linea, self.exp)


class NodoCompuesta(AST):
    def __init__(self, sentencias, linea):
        self.sentencias = sentencias
        self.linea = linea

    def compsemanticas(self):
        for sent in self.sentencias:
            sent.compsemanticas()

    def arbol(self):
        r = ""
        for sent in self.sentencias:
            r += sent.arbol()+"\n"
        return '( "Compuesta"\n %s)' % r


class NodoComparacion(AST):
    def __init__(self, op, izdo, dcho, linea):
        self.op = op
        self.izdo = izdo
        self.dcho = dcho
        self.linea = linea
        self.tipo = None

    def compsemanticas(self):
        self.izdo.compsemanticas()
        self.dcho.compsemanticas()

        #Comprobacion semantica 3: Conversión implicita de enteros en reales
        if self.izdo.tipo == "ENTERO" and self.dcho.tipo in ["REAL","ENTERO"]:
            self.tipo = self.dcho.tipo

        elif self.izdo.tipo == "REAL" and self.dcho.tipo in ["REAL","ENTERO"]:
            self.tipo = "REAL"

        elif self.izdo.tipo == "BOOLEANO" and self.dcho.tipo == "BOOLEANO":
            self.tipo = "BOOLEANO"

        else:
            print("Tipos incompatibles en asignacion (%s y %s)." % (self.izdo.tipo, self.dcho.tipo), self.linea)

    def arbol(self):
        return '( "Comparacion" "op: %s" "tipo: %s" "linea: %d" \n %s\n %s\n)' % \
               (self.op, self.tipo, self.linea, self.izdo, self.dcho)


class NodoAritmetica(AST):
    def __init__(self, op, izdo, dcho, linea):
        self.op = op
        self.izdo = izdo
        self.dcho = dcho
        self.linea = linea
        self.tipo = None

    def compsemanticas(self):
        self.izdo.compsemanticas()
        self.dcho.compsemanticas()
       
       #Comprobacion semantica 3: Conversión implicita de enteros en reales
        if self.izdo.tipo == "ENTERO" and self.dcho.tipo in ["REAL","ENTERO"]:
            self.tipo = self.dcho.tipo

        elif self.izdo.tipo == "REAL" and self.dcho.tipo in ["REAL","ENTERO"]:
            self.tipo = "REAL"

        elif self.izdo.tipo == "BOOLEANO" and self.dcho.tipo == "BOOLEANO":
            self.tipo = "BOOLEANO"

        else:
            print("Tipos incompatibles en asignacion (%s y %s)." % (self.izdo.tipo, self.dcho.tipo), self.linea)

    def arbol(self):
        return '( "Aritmetica" "op: %s" "tipo: %s" "linea: %d" \n %s\n %s\n)' % \
               (self.op, self.tipo, self.linea, self.izdo, self.dcho)


class NodoEntero(AST):
    def __init__(self, valor, linea):
        self.valor = valor
        self.linea = linea

    def compsemanticas(self):
        self.tipo = "ENTERO"

    def arbol(self):
        return '( "Entero" "valor: %d" "tipo: %s" "linea: %d" )' % (self.valor, self.tipo, self.linea)

class NodoReal(AST):
    def __init__(self, valor, linea):
        self.valor = valor
        self.linea = linea

    def compsemanticas(self):
        self.tipo = "REAL"

    def arbol(self):
        return '( "Real" "valor: %d" "tipo: %s" "linea: %d" )' % (self.valor, self.tipo, self.linea)

class NodoBooleano(AST):
    def __init__(self, valor, linea):
        self.valor = valor
        self.linea = linea

    def compsemanticas(self):
        self.tipo = "BOOLEANO"

    def arbol(self):
        return '( "BOOLEANO" "valor: %d" "tipo: %s" "linea: %d" )' % (self.valor, self.tipo, self.linea)


class NodoAccesoVariable(AST):
    def __init__(self, var, linea,tipo):
        self.var = var
        self.linea = linea
        self.tipo = tipo

    def compsemanticas(self):
        pass


    def arbol(self):
        return '( "AccesoVariable" "v: %s" "linea: %d" )' % (self.var, self.linea)


class NodoAccesoVector(AST):
    def __init__(self, izda, exp, linea):
        self.izda = izda
        self.exp = exp
        self.linea = linea

    def compsemanticas(self):
        self.izda.compsemanticas()
        self.exp.compsemanticas()

        self.tipo = "VECTOR"

        if self.izda.tipo != "VECTOR":
            print("Estas accediendo a una expresion de tipo %s como si fuera un vector." %
            self.izda.tipo, self.linea)
        
        if self.exp.tipo != "ENTERO":
            print("El tipo de la expresion de acceso al vector debe ser entero.",
                              self.linea)


    def arbol(self):
        return '( "AccesoVector" "tipo: %s" "linea: %d" %s\n %s\n)' % (self.tipo, self.linea, self.izda, self.exp)


class NodoVacio(AST):
    def __init__(self, linea):
        self.linea = linea

    def compsemanticas(self):
        self.tipo = "ERROR"

    def arbol(self):
        return '( "NodoVacio" "linea: %d" )' % self.linea


    
# Añadir nodo programa o lista de de arboles

class NodoPrograma(AST):
    def __init__(self, id,decVar,inst,linea):
        self.linea = linea
        self.id = id
        self.decVar = decVar
        self.inst = inst

    def compsemanticas(self):
        self.tipo = "PROGRAMA"

    def arbol(self):
        return '( "PROGRAMA" "linea: %d " )' % (self.linea,sel)


# -*- coding: latin-1 -*-
import sys
import tipos
import Rossi
import errores
import etiquetas
import memoria
import BancoRegistros
registros = BancoRegistros.BancoRegistros()

R = Rossi


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
        if not tipos.igualOError(self.izda.tipo, self.exp.tipo):
            errores.semantico("Tipos incompatibles en asignacion (%s y %s)." %
                              (self.izda.tipo, self.exp.tipo), self.linea)
        else:
            if not self.izda.tipo.elemental() or not self.exp.tipo.elemental():
                errores.semantico(
                    "Solo puedo asignar objetos de tipos elementales.", self.linea)

    def generaCodigo(self, c):
        c.append(R.Comentario("Asignacion en linea %d" % self.linea))
        rexp = self.exp.generaCodigo(c)
        rizda = self.izda.generaDir(c)
        c.append(R.sw(rexp, 0, rizda))
        registros.libera(rizda)
        registros.libera(rexp)

    def arbol(self):
        return '( "Asignacion"\n  "linea: %d" \n%s\n%s\n)' % (self.linea, self.izda, self.exp)


class NodoDevuelve(AST):
    def __init__(self, exp, f, linea):
        self.exp = exp
        self.f = f
        self.linea = linea

    def compsemanticas(self):
        self.exp.compsemanticas()
        if not tipos.igualOError(self.exp.tipo, self.f.tipoDevuelto):
            errores.semantico(
                "El tipo de la expresion del devuelve debe coincidir con el de la funcion.", self.linea)

    def generaCodigo(self, c):
        c.append(R.Comentario("Devuelve en linea %d" % self.linea))
        r = self.exp.generaCodigo(c)
        c.append(R.add("a0", r, "zero"))
        registros.libera(r)
        c.append(R.j(self.f.salida))

    def arbol(self):
        return '( "Devuelve" "linea: %d" %s)' % (self.linea, self.exp)


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
        if not tipos.igualOError(self.cond.tipo, tipos.Logico):
            errores.semantico(
                "La condicion del si debe ser de tipo logico.", self.linea)

    def generaCodigo(self, c):
        c.append(R.Comentario("Condicional en linea: %d" % self.linea))
        siguiente = etiquetas.nueva()
        falso = etiquetas.nueva()
        self.cond.codigoControl(c, None, falso)
        self.si.generaCodigo(c)
        c.append(R.j(siguiente))
        c.append(R.Etiqueta(falso))
        self.sino.generaCodigo(c)
        c.append(R.Etiqueta(siguiente))

    def arbol(self):
        return '( "Si" "linea: %d" %s\n %s\n %s\n )' % (self.linea, self.cond, self.si, self.sino)


class NodoEscribe(AST):
    def __init__(self, exp, linea):
        self.exp = exp
        self.linea = linea

    def compsemanticas(self):
        self.exp.compsemanticas()
        if self.exp.tipo != tipos.Error:
            if self.exp.tipo != tipos.Entero and self.exp.tipo != tipos.Cadena:
                errores.semantico(
                    "Solo se escribir enteros y cadenas.", self.linea)

    def generaCodigo(self, c):
        c.append(R.Comentario("Escribe, linea %d" % self.linea))
        r = self.exp.generaCodigo(c)
        c.append(R.add("a0", r, "zero"))
        if self.exp.tipo == tipos.Entero:
            c.append(R.addi("sc", "zero", 0, "Escribe entero"))
        elif self.exp.tipo == tipos.Cadena:
            c.append(R.addi("sc", "zero", 2, "Escribe cadena"))
        c.append(R.syscall())
        registros.libera(r)

    def arbol(self):
        return '( "Escribe" "linea: %d" %s )' % (self.linea, self.exp)


class NodoCompuesta(AST):
    def __init__(self, sentencias, linea):
        self.sentencias = sentencias
        self.linea = linea

    def compsemanticas(self):
        for sent in self.sentencias:
            sent.compsemanticas()

    def generaCodigo(self, c):
        for sent in self.sentencias:
            sent.generaCodigo(c)

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

    def compsemanticas(self):
        self.izdo.compsemanticas()
        self.dcho.compsemanticas()
        if not tipos.igualOError(self.izdo.tipo, tipos.Entero) or \
           not tipos.igualOError(self.dcho.tipo, tipos.Entero):
            errores.semantico(
                "Las operaciones de comparacion solo pueden operar con enteros.", self.linea)
            self.tipo = tipos.Error
        else:
            self.tipo = tipos.Logico

    def codigoControl(self, c, cierto, falso):
        iz = self.izdo.generaCodigo(c)
        de = self.dcho.generaCodigo(c)
        if cierto != None:
            op = {"=": R.beq, "!=": R.bne, "<": R.blt,
                  "<=": R.ble, ">": R.bgt, ">=": R.bge}[self.op]
            c.append(op(iz, de, cierto))
        else:
            op = {"=": R.bne, "!=": R.beq, "<": R.bge,
                  "<=": R.bgt, ">": R.ble, ">=": R.blt}[self.op]
            c.append(op(iz, de, falso))
        if cierto != None and falso != None:
            c.append(R.j(falso))
        registros.libera(de)
        registros.libera(iz)

    def arbol(self):
        return '( "Comparacion" "op: %s" "tipo: %s" "linea: %d" \n %s\n %s\n)' % \
               (self.op, self.tipo, self.linea, self.izdo, self.dcho)


class NodoAritmetica(AST):
    def __init__(self, op, izdo, dcho, linea):
        self.op = op
        self.izdo = izdo
        self.dcho = dcho
        self.linea = linea

    def compsemanticas(self):
        self.izdo.compsemanticas()
        self.dcho.compsemanticas()
        if not tipos.igualOError(self.izdo.tipo, tipos.Entero) or \
           not tipos.igualOError(self.dcho.tipo, tipos.Entero):
            errores.semantico(
                "Las operaciones aritmeticas solo pueden operar con enteros.", self.linea)
            self.tipo = tipos.Error
        else:
            self.tipo = tipos.Entero

    def generaCodigo(self, c):
        iz = self.izdo.generaCodigo(c)
        de = self.dcho.generaCodigo(c)
        if self.op == "+":
            c.append(R.add(iz, iz, de))
        elif self.op == "-":
            c.append(R.sub(iz, iz, de))
        elif self.op == "*":
            c.append(R.mult(iz, iz, de))
        elif self.op == "/":
            c.append(R.div(iz, iz, de))
        elif self.op == "%":
            c.append(R.mod(iz, iz, de))
        registros.libera(de)
        return iz

    def arbol(self):
        return '( "Aritmetica" "op: %s" "tipo: %s" "linea: %d" \n %s\n %s\n)' % \
               (self.op, self.tipo, self.linea, self.izdo, self.dcho)


class NodoEntero(AST):
    def __init__(self, valor, linea):
        self.valor = valor
        self.linea = linea

    def compsemanticas(self):
        self.tipo = tipos.Entero

    def generaCodigo(self, c):
        r = registros.reserva()
        c.append(R.addi(r, "zero", self.valor, "Valor entero"))
        return r

    def arbol(self):
        return '( "Entero" "valor: %d" "tipo: %s" "linea: %d" )' % (self.valor, self.tipo, self.linea)


class NodoCadena(AST):
    def __init__(self, cad, linea):
        self.cad = cad
        self.linea = linea

    def compsemanticas(self):
        self.tipo = tipos.Cadena

    def generaCodigo(self, c):
        r = registros.reserva()
        c.append(R.addi(r, "zero", self.cad.dir, str(self.cad)))
        return r

    def arbol(self):
        return '( "Cadena" "valor: %s" "tipo: %s" "linea: %d" )' % (str(self.cad)[1:-1], self.tipo, self.linea)

# Posiblemente no haga falta


class NodoLlamada(AST):
    def __init__(self, f, args, linea):
        self.f = f
        self.args = args
        self.linea = linea

    def compsemanticas(self):
        for arg in self.args:
            arg.compsemanticas()
        if not self.f.tipo == tipos.Funcion:
            errores.semantico("Estas intentando llamar a algo que no es una funcion.",
                              self.linea)
            self.tipo = tipos.Error
            return
        self.tipo = self.f.tipoDevuelto
        if self.f.tipoDevuelto == tipos.Error:
            return
        if len(self.args) != len(self.f.parametros):
            errores.semantico("La llamada a %s deberia tener %d parametros en lugar de %d." %
                              (self.f.id, len(self.f.parametros), len(self.args)), self.linea)
        else:
            for i in range(len(self.args)):
                arg = self.args[i]
                pf = self.f.parametros[i]
                if not tipos.igualOError(arg.tipo, pf.tipo):
                    errores.semantico("No coincide el tipo del parametro %d (deberia ser %s)." %
                                      (i+1, pf.tipo), self.linea)

    def generaCodigo(self, c):
        c.append(R.Comentario("Llamada a %s en linea %d" %
                              (self.f.id, self.linea)))
        act = registros.activos()
        if act:
            c.append(R.Comentario("Guardamos los registros activos:"))
            for i, ra in enumerate(act):
                c.append(R.save(ra, i, "sp"))
            c.append(R.addi("sp", "sp", len(act)))
        for i in range(len(self.args)):
            r = self.args[i].generaCodigo(c)
            c.append(R.sw(r, 0, "sp", "Parametro %s" %
                          self.f.parametros[i].id))
            c.append(R.addi("sp", "sp", 1))
            registros.libera(r)
        c.append(R.jal(self.f.etiqueta, "Salto a la funcion"))
        r = registros.reserva()
        c.append(R.add(r, "a0", "zero"))
        if act:
            c.append(R.Comentario("Recuperamos los registros activos:"))
            c.append(R.subi("sp", "sp", len(act)))
            for i, ra in enumerate(act):
                c.append(R.rest(ra, i, "sp"))
        return r

    def arbol(self):
        l = []
        for p in self.args:
            l.append(p.arbol())
        return '("Llamada" "f: %s" "tipo: %s" "linea: %d" %s )' % (self.f, self.tipo, self.linea, "\n".join(l))


class NodoAccesoVariable(AST):
    def __init__(self, var, linea):
        self.var = var
        self.linea = linea

    def compsemanticas(self):
        self.tipo = self.var.tipo

    def generaCodigo(self, c):
        r = registros.reserva()
        c.append(R.lw(r, self.var.dir, self.var.base,
                      "Acceso a %s" % self.var.id))
        return r

    def generaDir(self, c):
        r = registros.reserva()
        c.append(R.addi(r, self.var.base, self.var.dir,
                        "Direccion de %s" % self.var.id))
        return r

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
        if self.izda.tipo != tipos.Error:
            if self.izda.tipo.elemental():
                errores.semantico("Estas accediendo a una expresion de tipo %s como si fuera un vector." %
                                  self.izda.tipo, self.linea)
                self.tipo = tipos.Error
            elif self.izda.tipo == tipos.Funcion:
                errores.semantico("Estas accediendo a la funcion %s como si fuera un vector." %
                                  self.izda.var.id, self.linea)
                self.tipo = tipos.Error
            else:
                self.tipo = self.izda.tipo.base
        else:
            self.tipo = tipos.Error
        if not tipos.igualOError(self.exp.tipo, tipos.Entero):
            errores.semantico("El tipo de la expresion de acceso al vector debe ser entero.",
                              self.linea)

    def generaCodigo(self, c):
        r = self.generaDir(c)
        c.append(R.lw(r, 0, r))
        return r

    def generaDir(self, c):
        base = self.izda.generaDir(c)
        desp = self.exp.generaCodigo(c)
        if self.tipo.talla() > 1:
            c.append(R.multi(desp, desp, self.tipo.talla(),
                             "Tama�o del %s" % self.tipo))
        c.append(R.add(base, base, desp))
        registros.libera(desp)
        return base

    def arbol(self):
        return '( "AccesoVector" "tipo: %s" "linea: %d" %s\n %s\n)' % (self.tipo, self.linea, self.izda, self.exp)


class NodoVacio(AST):
    def __init__(self, linea):
        self.linea = linea

    def compsemanticas(self):
        self.tipo = tipos.Error

    def arbol(self):
        return '( "NodoVacio" "linea: %d" )' % self.linea


# Añadir nodo programa o lista de de arboles
# -*- coding: utf-8 -*-
import flujo
import string
import sys
import componentes
from sys import argv
from analex import Analex
from AST import *

class Atributos:
    pass

class Anasint:

    def __init__(self, lexico):

        self.lexico= lexico
        self.tabla = {}

        self.avanza()
        self.NodoPrograma = self.analizaPrograma()
        
        if not self.comprueba("EOF"):
            self.error("Se esperaba EOF")
            self.sincroniza()
    
    def avanza(self):
        self.componente = self.lexico.siguiente()

    def comprueba(self, cat):
        
        #Verificamos que estamos ante una palabra reservada
        if self.componente.cat == "PR":

            if self.componente.valor == cat:
                self.avanza()
                return True
            else:
                return False
        
        #No es una palabra reservada
        else:

            if self.componente.cat == cat:
                self.avanza()
                return True
            else:
                return False
    
    def error(self,msg=""):
        
        print "Error en linea " + str(self.lexico.nlinea) + ": " + msg


    #Permite obtener el punto de sincronización
    def sincroniza(self, sinc = []):

        if "EOF" not in sinc:
            sinc.append("EOF")

        while True :
            
            if self.componente.cat == "PR" and self.componente.valor in sinc:
                break
            
            if self.componente.cat in sinc:
                break
           
            self.avanza()


    def analizaPrograma(self):

        siguiente = ["EOF"]


        if self.componente.cat == "PR" and self.componente.valor == "PROGRAMA":
            #<Programa> -> PROGRAMA id; <decl_var> <instrucciones>.
            self.avanza()

            identifProg = self.componente.valor

            if not self.comprueba("Identif"):
                self.error("Se esperaba Identif")
                self.sincroniza(siguiente)
                return NodoVacio(self.lexico.nlinea)

            #Especificacion semantica 1
            #Comprobamos que no existe el identificador del programa
            if (not self.tabla.has_key(identifProg)) and (identifProg not in Analex.PR):
                self.tabla[identifProg] = {}

            elif identifProg in Analex.PR:
                self.error("No se puede utilizar palabra reservada como indentificador")

            else:
                self.error("Variable definida")

            if not self.comprueba("PtoComa"):
                self.error("Se esperaba ;")
                self.sincroniza(siguiente)
                return NodoVacio(self.lexico.nlinea)
            

            self.analizaDeclVar()
            instrucciones = self.analizaInstrucciones()

            if not self.comprueba("Punto"):
                self.error("Se esperaba .")
                self.sincroniza(siguiente)
    
            return NodoPrograma(identifProg,instrucciones,self.lexico.nlinea)
        
        else:
            self.error("Se experaba la palabra reservada PROGRAMA")
            self.sincroniza(siguiente)
            return NodoVacio(self.lexico.nlinea)
    

    def analizaDeclVar(self):
        
        siguiente = ["INICIO"]

        tipo = None
        tam = None
        subtipo = None

        if self.componente.cat == "PR" and self.componente.valor == "VAR":
            #<decl_var> -> VAR <lista_id> : <tipo> ; <decl_v> 
            self.avanza()
            
            identificadores = self.analizaListaid()

            if not self.comprueba("DosPtos"):
                self.error("Se esperaba :")
                self.sincroniza(siguiente)
                return NodoVacio(self.lexico.nlinea)

            (tipo,tam,subtipo) = self.analizaTipo()
    
            if identificadores != None:

                for id in identificadores:
                    self.tabla[id]["tipo"] = tipo
                    self.tabla[id]["tam"] = tam
                    self.tabla[id]["subtipo"] = subtipo

            
            if not self.comprueba("PtoComa"):
                self.error("Se esperaba ;")
                self.sincroniza(siguiente)
                return NodoVacio(self.lexico.nlinea)

            self.analizaDeclV()
        
        elif self.componente == "PR" and self.componente.valor == "INICIO":
            #<decl_var> -> lambda
            pass
        
        else:

            self.error("Se esperaba palabra reservada VAR o INICIO")
            self.sincroniza(siguiente)
            return NodoVacio(self.lexico.nlinea)
    

    def analizaInstrucciones(self):
        
        siguiente = ["Punto"]

        conjuntoInst = []

        if self.componente.cat == "PR" and self.componente.valor == "INICIO":
            #<instrucciones> -> INICIO <lista_inst> FIN
            self.avanza()

            listaInst = self.analizaListainst()

            if(listaInst!=None):
                conjuntoInst.extend(listaInst)

            if not self.comprueba("FIN"):
                self.error("Se esperaba palabra reservada FIN")
                self.sincroniza(siguiente)
                return conjuntoInst
           
            return conjuntoInst

        else:
            self.error("Se esperaba palabra reservada INICIO")
            self.sincroniza(siguiente)
            return conjuntoInst


    def analizaListaid(self):
        
        siguiente = ["DosPtos"]

        listaids = []

        if self.componente.cat == "Identif":
            #<lista_id> -> id <resto_listaid>

            listaids.append(self.componente.valor)

            #Especificacion semantica 1
            #Comprobamos que no existe el identificador del programa
            if (not self.tabla.has_key(self.componente.valor)) and (self.componente.valor not in Analex.PR):
                self.tabla[self.componente.valor] = {}

            elif self.componente.valor in Analex.PR:
                self.error("No se puede utilizar palabra reservada como indentificador")

            else:
                self.error("Variable definida")
            
            self.avanza()

            restoid = self.analizaRestolistaid()

            if restoid != None:
                listaids.extend(restoid)

            return listaids

        else:
            self.error("Se esperada Identif")
            self.sincroniza(siguiente)


    def analizaTipo(self):

        siguiente = ["PtoComa"]

        tipo = None
        tam = None
        subtipo = None

        if self.componente.cat == "PR" and self.componente.valor in ["ENTERO","REAL","BOOLEANO"]:
            #<Tipo> -> <tipo_std>
            tipo = self.analizaTipostd()
            
            return (tipo,tam,subtipo)
        
        elif self.componente.cat == "PR" and self.componente.valor == "VECTOR":
            #<Tipo> -> VECTOR [num] de <tipo_std>
            self.avanza()
        
            tipo = "VECTOR"

            if not self.comprueba("CorAp"):
                self.error("Se esperaba [")
                self.sincroniza(siguiente)
                return (tipo,tam,subtipo)

            tam = self.componente.valor

            if not self.comprueba("Numero"):
                self.error("Se esperaba Numero")
                self.sincroniza(siguiente)
                return (tipo,tam,subtipo)

            if not self.comprueba("CorCi"):
                self.error("Se esperaba ]")
                self.sincroniza(siguiente)
                return (tipo,tam,subtipo)

            if not self.comprueba("DE"):
                self.error("Se esperada palabra reservada DE")
                self.sincroniza(siguiente)
                return (tipo,tam,subtipo)
            
            subtipo = self.analizaTipostd()

            return (tipo,tam,subtipo)
        
        else:
            self.error("Se esperaba ENTERO, REAL, BOOLEANO o VECTOR")
            self.sincroniza(siguiente)
            return (tipo,tam,subtipo)


    def analizaDeclV(self):

        siguiente = ["INICIO"]

        if self.componente.cat == "Identif":
            #<decl_v> -> <lista_id> : <tipo> ; <decl_v>
            listaid = self.analizaListaid()
            
            if not self.comprueba("DosPtos"):
                self.error("Se esperada :")
                self.sincroniza(siguiente)
                return 

            (tipo,tam,subtipo) = self.analizaTipo()

            if listaid != None:

                for id in listaid:

                    self.tabla[id]["tipo"] = tipo
                    self.tabla[id]["tam"] = tam
                    self.tabla[id]["subtipo"] = subtipo    


            if not self.comprueba("PtoComa"):
                self.error("Se esperada ;")
                self.sincroniza(siguiente)
                return

            self.analizaDeclV()
        
        elif self.componente.cat == "PR" and self.componente.valor == "INICIO":
            #<decl_v> -> lambda
            pass

        else:
            self.error("se esperaba Identif o palabra reservada INICIO")
            self.sincroniza(siguiente)


    def analizaRestolistaid(self):

        siguiente = ["DosPtos"]

        if self.componente.cat == "Coma":
            #<resto_listaid> -> ,<lista_id>
            self.avanza()

            return self.analizaListaid()

        elif self.componente.cat == "DosPtos":
            #<resto_listaid> -> lambda
            pass
        
        else:
            self.error("Se esperaba , o :")
            self.sincroniza(siguiente)


    def analizaTipostd(self):

        siguiente = ["PtoComa"]
        tipo = None

        if self.componente.cat == "PR" and self.componente.valor == "ENTERO":
            #<tipo_std> -> ENTERO
            tipo = self.componente.valor
            self.avanza()

        elif self.componente.cat == "PR" and self.componente.valor == "REAL":
            #<tipo_std> -> REAL
            tipo = self.componente.valor
            self.avanza()

        elif self.componente.cat == "PR" and self.componente.valor == "BOOLEANO":
            #<tipo_std> -> BOOLEANO
            tipo = self.componente.valor
            self.avanza()

        else:
            self.error("Se esperaba tipo ENTERO, REAL o BOOLEANO")
            self.sincroniza(siguiente)
            return 
        
        return tipo


    def analizaListainst(self):
       
        siguiente = ["FIN"]

        conjuntoInst = []

        if (self.componente.cat == "PR" and self.componente.valor in ["INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]) or self.componente.cat == "Identif":
            #<lista_inst> -> <instruccion>;<lista_inst>
            inst = self.analizaInstruccion()

            if inst !=None:
                conjuntoInst.append(inst)

            if not self.comprueba("PtoComa"):
                self.error("Se esperada ;")
                self.sincroniza(siguiente)
                return conjuntoInst
            
            listaInst = self.analizaListainst()
            
            if listaInst != None:
                conjuntoInst = conjuntoInst + listaInst

            return conjuntoInst
        
        elif self.componente.cat == "PR" and self.componente.valor == "FIN":
            #<lista_inst> -> lambda
            return 
        
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)
            return 



    def analizaInstruccion(self):

        siguiente = ["PtoComa","SINO"]

        if self.componente.cat == "PR" and self.componente.valor == "INICIO":
            #<instruccion> -> INICIO <lista_inst> FIN 
            self.avanza()
            
            lista = self.analizaListainst()

            if not self.comprueba("FIN"):
                self.error("Se esperada palabra reservada FIN")
                self.sincroniza(siguiente)
                return 
            
            if lista == None:
                lista = [NodoVacio(self.lexico.nlinea)]
        
            return NodoCompuesta(lista,self.lexico.nlinea)
        
        elif self.componente.cat == "Identif":
            #<instruccion> -> <inst_simple>
            return self.analizaInstruccionSimple()
        
        elif self.componente.cat == "PR" and self.componente.valor in ["LEE","ESCRIBE"]:
            #<instruccion> -> <inst_e/s>
            return self.analizaInstruccionES()

        elif self.componente.cat == "PR" and self.componente.valor == "SI":
            #<instruccion> -> SI <expresion> ENTONCES <instruccion> SINO <instruccion>
            self.avanza()

            cond = self.analizaExpresion()

            if cond == None:
                cond = NodoVacio(self.lexico.nlinea)

            if not self.comprueba("ENTONCES"):
                self.error("Se esperaba palabra reservada ENTONCES")
                self.sincroniza(siguiente)
                return

            si = self.analizaInstruccion()

            if si == None:
                si = NodoVacio(self.lexico.nlinea)
            
            if not self.comprueba("SINO"):
                self.error("Se esperaba palabra reservada SINO")
                self.sincroniza(siguiente)
                return NodoVacio(self.lexico.nlinea)

            no = self.analizaInstruccion()

            if no == None:
                no = NodoVacio(self.lexico.nlinea)

            return NodoSi(cond,si,no,self.lexico.nlinea)
        
        elif self.componente.cat == "PR" and self.componente.valor == "MIENTRAS":
            #<instruccion> -> MIENTRAS <expresion> HACER <instruccion>
            linea = self.componente.linea
            self.avanza()

            exp = self.analizaExpresion()
            if exp == None:
                exp = NodoVacio(linea)

            if not self.comprueba("HACER"):
                self.error("Se esperaba palabra reservada HACER")
                self.sincroniza(siguiente)
                return NodoVacio(linea)

            cuerpo = self.analizaInstruccion()

            if cuerpo == None:
                cuerpo =  NodoVacio(linea)

            return NodoMientras(exp,cuerpo,linea)
        
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)
            return 
            


    def analizaInstruccionSimple(self):

        siguiente = ["PtoComa","SINO"]

        if self.componente.cat =="Identif":
            #<inst_simple> -> id <resto_instsimple>

            #Atributo heredado con valor, linea, tipo y subtipo(solo para vectores)
            ISimple = Atributos()
            ISimple.v = self.componente.valor
            ISimple.l = self.componente.linea
            ISimple.t = None
            ISimple.st = None

            #Verificamos que la variable se haya definido
            if not self.tabla.has_key(self.componente.valor):
                self.error("Variable no definida")
            else:
                ISimple.t = self.tabla[self.componente.valor]["tipo"]
                ISimple.st = self.tabla[self.componente.valor]["subtipo"]

    
            self.avanza()
          
            return self.analizaRestoInstSimple(ISimple)
        
        else:
            self.error("Elemento esperado Identif")
            self.sincroniza(siguiente)


    def analizaInstruccionES(self):

        siguiente = ["PtoComa","SINO"]

        if self.componente.cat == "PR" and self.componente.valor == "LEE":
            #<inst_e/s> -> LEE (id) 
            self.avanza()

            if not self.comprueba("ParentAp"):
                self.error("Elemento  esperado (")
                self.sincroniza(siguiente)
                return 

            nombrevar = self.componente.valor

            #Especificacion semantica 1
            #Verificamos que la variable se haya definido
            if not self.tabla.has_key(nombrevar):
                self.error("Variable no definida")
                tipo = None
            
            elif self.tabla[nombrevar]["tipo"] not in ["ENTERO","REAL"]:
                self.error("Solo podemos leer variable de tipo ENTERO o REAL") 

            else:
                tipo = self.tabla[nombrevar]["tipo"]

            if not self.comprueba("Identif"):
                self.error("Elemento esperado Identif")
                self.sincroniza(siguiente)
                return


            if not self.comprueba("ParentCi"):
                self.error("Elemento esperado )")
                self.sincroniza(siguiente)
                return

            accesoVar = NodoAccesoVariable(nombrevar,self.lexico.nlinea,tipo)
            return NodoLee(accesoVar,self.lexico.nlinea)
                    
            
        elif self.componente.cat == "PR" and self.componente.valor == "ESCRIBE":
            #<inst_e/s> -> ESCRIBE (<expr_simple>)
            self.avanza()
            
            if not self.comprueba("ParentAp"):
                self.error("Elemento  esperado (")
                self.sincroniza(siguiente)

                return NodoVacio(self.lexico.nlinea)

            exp_simple = self.analizaExpresionSimple()
        
            if not self.comprueba("ParentCi"):
                self.error("Elemento esperado )")
                self.sincroniza(siguiente)

                return NodoVacio(self.lexico.nlinea)

            return NodoEscribe(exp_simple,self.lexico.nlinea)
        
        else:
            self.error("Se esperaba palabra reservada LEE o ESCRIBE " + str(self.componente))
            self.sincroniza(siguiente)

    

    def analizaExpresion(self):
        
        siguiente = ["ENTONCES","HACER","SINO" ,"PtoComa","ParentCi"] 

        if (self.componente.cat == "PR" and self.componente.valor in ["FALSO", "CIERTO", "NO"]) or  self.componente.cat in ["OpAdd","Numero","ParentAp","Identif"]:
            #<expresion> -> <expr_simple> <expresion'>
            exp1 = self.analizaExpresionSimple()
            exp_prim = self.analizaExpresionPrima()

            if exp_prim != None:
                op = exp_prim[0]
                exp2 = exp_prim[1]
                return NodoComparacion(op,exp1,exp2,self.lexico.nlinea)
            
            return exp1   

        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)
    

    def analizaRestoInstSimple(self,ISimple):

        siguiente = ["PtoComa", "SINO"]

        if self.componente.cat == "OpAsigna":
            #<resto_instsimple> -> opasigna <expresion> 
            self.avanza()

            expr =  self.analizaExpresion()

            if expr == None:
                expr = NodoVacio(self.lexico.nlinea)

            accesoVar = NodoAccesoVariable(ISimple.v,ISimple.l,ISimple.t)

            return NodoAsignacion(accesoVar,expr,self.lexico.nlinea)


        elif self.componente.cat == "CorAp":
            #<resto_instsimple> -> [<expr_simple>] opasigna <expresion>
            self.avanza()

            exp_simple = self.analizaExpresionSimple()
          
            if not self.comprueba("CorCi"):
                self.error("Elemento esperado ]")
                self.sincroniza(siguiente)

                return

            if not self.comprueba("OpAsigna"):
                self.error("Elemento esperado :=")
                self.sincroniza(siguiente)

                return

            exp = self.analizaExpresion()

            if exp == None:
                exp = NodoVacio(self.lexico.nlinea)
       
            accesoVar = NodoAccesoVariable(ISimple.v,self.lexico.nlinea,ISimple.t,ISimple.st)
            accesoVec = NodoAccesoVector(accesoVar,exp_simple,self.lexico.nlinea)
           
            return NodoAsignacion(accesoVec,exp,self.lexico.nlinea)

        elif (self.componente.cat == "PR" and self.componente.valor == "SINO") or self.componente.cat == "PtoComa":
            #<resto_exsimple> -> lambda
            pass

        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)


    def analizaExpresionSimple(self):

        siguiente = ["CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

        if self.componente.cat == "OpAdd":
            #<expr_simple> -> <signo> <termino> <resto_exsimple>
            op = self.componente.valor
            self.analizaSigno()

            term = self.analizaTermino()
            resto_exp = self.analizaRestoExpSimple(term)
           
            return NodoAritmetica(op,term,None,self.lexico.nlinea)

        elif (self.componente.cat == "PR" and self.componente.valor in ["FALSO", "CIERTO", "NO"]) or self.componente.cat in ["Numero", "ParentAp", "Identif"]:
           #<expr_simple> -> <termino> <resto_exsimple> 
           term = self.analizaTermino()
      
           return self.analizaRestoExpSimple(term)
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)
    

    def analizaVariable(self):
        
        siguiente = ["OpMult","Y","OpAdd","O","CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

        if self.componente.cat == "Identif":
            #<variable> -> id <resto_var>

            identificador = self.componente.valor
            tipo = None
            nodo = None

            #Especificacion semantica 1
            #Verificamos que la variable se haya definido
            if not self.tabla.has_key(self.componente.valor):
                self.error("Variable no definida")
                nodo = NodoVacio(self.lexico.nlinea)
              
            else:
                tipo = self.tabla[identificador]["tipo"]
                subtipo = self.tabla[identificador]["subtipo"]

            self.avanza()
            resto_var = self.analizaRestoVar()

            if nodo != None:
                return nodo
            
            elif resto_var == None:
                return NodoAccesoVariable(identificador,self.lexico.nlinea,tipo)
            
            else:
                acceso_var = NodoAccesoVariable(identificador,self.lexico.nlinea,tipo,subtipo)
                return NodoAccesoVector(acceso_var,resto_var,self.lexico.nlinea)
        
        else:
            self.error("Elemento esperado Identif")
            self.sincroniza(siguiente)
    


    def analizaRestoVar(self):

        siguiente = ["OpMult","Y","OpAdd","O","CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

        if self.componente.cat == "CorAp":
            #<resto_var> -> [<expr_simple>]
            self.avanza()
            exp = self.analizaExpresionSimple()
            
            if not self.comprueba("CorCi"):
                self.error("Elemento esperado )")
                self.sincroniza(siguiente)
                return
    
        
        elif (self.componente.cat == "PR" and self.componente.valor in ["Y","O","ENTONCES","HACER","SINO"]) or self.componente.cat in ["OpMult","OpAdd","OpRel","CorCi","ParentCi", "PtoComa"]:
            #<resto_var> -> lambda
            return None
        
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)


    
    def analizaExpresionPrima(self):

        siguiente = ["ENTONCES","HACER","PtoComa","SINO","CorCi"]
        
        if self.componente.cat == "OpRel":
            #<expresion'> -> oprel <expr_simple>

            op = self.componente.valor
            self.avanza()
            exp_simple = self.analizaExpresionSimple()

            return (op,exp_simple)

                
        elif self.componente.cat in ["PtoComa", "ParentCi"] or (self.componente.cat == "PR" and self.componente.valor in ["ENTONCES","HACER","SINO"]):
            #<expresion'> -> lambda
            return None

        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)
            return


    def analizaTermino(self):

        siguiente = ["OpAdd","O","CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

        if (self.componente.cat == "PR" and self.componente.valor in ["FALSO", "CIERTO", "NO"]) or self.componente.cat in ["Numero","ParentAp","Identif"]:
            #<termino> -> <factor> <resto_term>
            factor = self.analizaFactor()

            return self.analizaRestoTerm(factor)
        
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)


    def analizaRestoExpSimple(self,atributo):

        siguiente = ["CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

        if self.componente.cat == "OpAdd":
            #<resto_exsimple> -> opsuma <termino> <resto_exsimple>
            op = self.componente.valor
            self.avanza()
            term = self.analizaTermino()

            nodoArit = NodoAritmetica(op,atributo,term,self.lexico.nlinea)

            return self.analizaRestoExpSimple(nodoArit)

        elif self.componente.cat == "PR" and self.componente.valor == "O":
            #<resto_exsimple> -> O <termino> <resto_exsimple>
            op = self.componente.valor
            self.avanza()
            term = self.analizaTermino()
            
            nodoComp = NodoComparacion(op,atributo,term,self.lexico.nlinea)

            return  self.analizaRestoExpSimple(nodoComp)

        elif self.componente.cat in ["CorCi","ParentCi","OpRel", "PtoComa"] or (self.componente.cat == "PR" and self.componente.valor in ["ENTONCES", "HACER", "SINO"]):
            #<resto_exsimple> -> lambda
            return atributo

        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)


    def analizaSigno(self):

        siguiente = ["Identif","Numero","ParentAp","NO","CIERTO","FALSO"]

        if self.componente.cat == "OpAdd":
            #<signo> -> + 
            #<signo> -> -
            self.avanza()
        
        else:
            self.error("Elemento esperado + o -")
            self.sincroniza(siguiente)


    def analizaRestoTerm(self,atributo):

        siguiente = ["OpAdd","O","CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

        if self.componente.cat == "PR" and self.componente.valor == "Y":
            #<resto_term> -> Y <factor> <resto_term>
            op = self.componente.valor
            self.avanza()
          
            factor = self.analizaFactor()
            resto_term = self.analizaRestoTerm(factor)
          
            return NodoComparacion(op,atributo,resto_term,self.lexico.nlinea)

        elif self.componente.cat == "OpMult":
            #<resto_term> -> opmult <factor> <resto_term>
            op = self.componente.valor
            
            self.avanza()
            
            factor = self.analizaFactor()
            resto_term = self.analizaRestoTerm(factor)

            return NodoAritmetica(op,atributo,resto_term,self.lexico.nlinea)

        elif self.componente.cat in [ "OpAdd", "OpRel","CorCi","ParentCi","PtoComa"] or (self.componente.cat == "PR" and self.componente.valor in ["O", "ENTONCES","HACER","SINO"]):
            #<resto_term> -> lambda
            return atributo

        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)

    
    def analizaFactor(self):

        siguiente = ["OpMult","Y","OpAdd","O","CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

        if self.componente.cat == "PR" and self.componente.valor == "FALSO":
            #<factor> -> FALSO

            booleano =  NodoBooleano(0,self.componente.linea)
            self.avanza()

            return booleano
        
        elif self.componente.cat == "PR" and self.componente.valor == "CIERTO":
            #<factor> -> CIERTO
            booleano =  NodoBooleano(1,self.componente.linea)
            self.avanza()

            return booleano
        
        elif self.componente.cat == "PR" and self.componente.valor == "NO":
            #<factor> -> NO <factor>

            op = self.componente.valor
            self.avanza()
            factor = self.analizaFactor()

            return NodoComparacion(op,factor,None,self.lexico.nlinea)

        elif self.componente.cat == "Numero":
            #<factor> -> num
            
            valor = self.componente.valor
            tipo = self.componente.tipo
            nodo = None

            if tipo == "REAL":
                nodo = NodoReal(self.componente.valor,self.componente.linea)

            elif tipo == "ENTERO":
                nodo = NodoEntero(self.componente.valor,self.componente.linea)

            self.avanza()
    
            return nodo
            

        elif self.componente.cat == "ParentAp":
            #<factor> -> (<expresion>)
            self.avanza()
            
            exp = self.analizaExpresion()
            
            if not self.comprueba("ParentCi"):
                self.error("Se esperaba )")
                self.sincroniza(siguiente)
                return
            
            return exp

        elif self.componente.cat == "Identif":
            #<factor> -> <variable>
            return self.analizaVariable()

        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)


if __name__ == "__main__":

    script, filename = argv
    txt = open(filename)
    print "Este es tu fichero %r" % filename
    print "###################\n"
    print "Analisis lexico"
    fl = flujo.Flujo(txt)
    analex = Analex(fl)
  
    print "\n###################"
    print "Analisis sintactico/semantico"
    anasint = Anasint(analex)

    print "\n###################"
    print "AST"
    print(anasint.NodoPrograma)
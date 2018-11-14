import flujo
import string
import sys
import componentes
from sys import argv
from analex import Analex

class Anasint:

    def __init__(self, lexico):

        self.lexico= lexico
        self.avanza()
        self.analizaPrograma()
        self.comprueba("EOF")
    
    def avanza(self):
        self.componente= self.lexico.siguiente()

    def comprueba(self, cat):
        
        if self.componente.cat == cat:
            self.avanza()
        else:
            self.error()

    def compruebaPR(self, cat):
        
        if self.componente.valor == cat:
            self.avanza()
        else:
            self.error()
    
    def error(self):
        print "Error:",self.componente


    def sincroniza(self, sinc):
        #sinc |= \{ "eof" \} 
        sinc = None
        while self.componente.cat not in sinc:
            self.avanza()

    def analizaPrograma(self):

        if self.componente.cat == "PR" and self.componente.valor == "PROGRAMA":
            #<Programa> -> PROGRAMA id; <decl_var> <instrucciones>.
            self.avanza()
            self.comprueba("Identif")
            self.comprueba("PtoComa")
            self.analizaDeclVar()
            self.analizaInstrucciones()
            self.comprueba("Punto")
        
        else:
            self.error()
    
    def analizaDeclVar(self):
        
        if self.componente.cat == "PR" and self.componente.valor == "VAR":
            #<decl_var> -> VAR <lista_id> : <tipo> ; <decl_v> 
            self.avanza()
            self.analizaListaid()
            self.comprueba("DosPtos")
            self.analizaTipo()
            self.comprueba("PtoComa")
            self.analizaDeclV()
        
        elif self.componente == "PR" and self.componente.valor == "INICIO":
            #<decl_var> -> lambda
            pass
        
        else:
            self.error()
    

    def analizaInstrucciones(self):
        
        if self.componente.cat == "PR" and self.componente.valor == "INICIO":
            #<instrucciones> -> INICIO <lista_inst> FIN
            self.avanza()
            self.analizaListainst()
            self.compruebaPR("FIN")

        else:
            self.error()


    def analizaListaid(self):
        
        if self.componente.cat == "Identif":
            #<lista_id> -> id <resto_listaid>
            self.avanza()
            self.analizaRestolistaid()

        else:
            self.error()


    def analizaTipo(self):

        if self.componente.cat == "PR" and self.componente.valor in ["ENTERO","REAL","BOOLEAN"]:
            #<Tipo> -> <tipo_std>
            self.analizaTipostd()
        
        elif self.componente.cat == "PR" and self.componente.valor == "VECTOR":
            #<Tipo> -> VECTOR [num] de <tipo_std>
            self.avanza()
            self.comprueba("CorAp")
            self.comprueba("Numero")
            self.comprueba("CorCi")
            self.compruebaPR("DE")
            self.analizaTipostd()
        
        else:
            self.error()


    def analizaDeclV(self):

        if self.componente.cat == "Identif":
            #<decl_v> -> <lista_id> : <tipo> ; <decl_v>
            self.analizaListaid()
            self.comprueba("DosPtos")
            self.analizaTipo()
            self.comprueba("PtoComa")
            self.analizaDeclV()
        
        elif self.componente.cat == "PR" and self.componente.valor == "INICIO":
            #<decl_v> -> lambda
            pass

        else:
            self.error()



    def analizaRestolistaid(self):

        if self.componente.cat == "Coma":
            #<resto_listaid> -> ,<lista_id>
            self.avanza()
            self.analizaListaid()

        elif self.componente.cat == "DosPtos":
            #<resto_listaid> -> lambda
            pass
        
        else:
            self.error()


    def analizaTipostd(self):

        if self.componente.cat == "PR" and self.componente.valor == "ENTERO":
            #<tipo_std> -> ENTERO
            self.avanza()

        elif self.componente.cat == "PR" and self.componente.valor == "REAL":
            #<tipo_std> -> REAL
            self.avanza()

        elif self.componente.cat == "PR" and self.componente.valor == "BOOLEANO":
            #<tipo_std> -> BOOLEANO
            self.avanza()

        else:
            self.error()


    def analizaListainst(self):
       
        if (self.componente.cat == "PR" and self.componente.valor in ["INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]) or self.componente.cat == "Identif":
            #<lista_inst> -> <instruccion>;<lista_inst>
            self.analizaInstruccion()
            self.comprueba("PtoComa")
            self.analizaListainst()
        
        elif self.componente.cat == "PR" and self.componente.valor == "FIN":
            #<lista_inst> -> lambda
            pass
        
        else:
            self.error()


    def analizaInstruccion(self):

        if self.componente.cat == "PR" and self.componente.valor == "INICIO":
            #<instruccion> -> INICIO <lista_inst> FIN 
            self.avanza()
            self.analizaListainst()
            self.compruebaPR("FIN")
        
        elif self.componente.cat == "Identif":
            #<instruccion> -> <inst_simple>
            self.analizaInstruccionSimple()
        
        elif self.componente.cat == "PR" and self.componente.valor in ["LEE","ESCRIBE"]:
            #<instruccion> -> <inst_e/s>
            self.analizaInstruccionES()

        elif self.componente.cat == "PR" and self.componente.valor == "SI":
            #<instruccion> -> SI <expresion> ENTONCES <instruccion> SINO <instruccion>
            self.avanza()
            self.analizaExpresion()
            self.compruebaPR("ENTONCES")
            self.analizaInstruccion()
            self.compruebaPR("SINO")
            self.analizaInstruccion()
        
        elif self.componente.cat == "PR" and self.componente.valor == "MIENTRAS":
            #<instruccion> -> MIENTRAS <expresion> HACER <instruccion>
            self.avanza()
            print "dsds",self.componente
            self.analizaExpresion()
            self.compruebaPR("HACER")
            self.analizaInstruccion()
        
        else:
            self.error()


    def analizaInstruccionSimple(self):

        if self.componente.cat =="Identif":
            #<inst_simple> -> id <resto_instsimple>
            self.avanza()
            self.analizaRestoInstSimple()
        
        else:
            self.error()


    def analizaInstruccionES(self):

        if self.componente.cat == "PR" and self.componente.valor == "LEE":
            #<inst_e/s> -> LEE (id) 
            self.avanza()
            self.comprueba("ParentAp")
            self.comprueba("Identif")
            self.comprueba("ParentCi")

        elif self.componente.cat == "PR" and self.componente.valor == "ESCRIBE":
            #<inst_e/s> -> ESCRIBE (<expr_simple>)
            self.avanza()
            self.comprueba("ParentAp")
            print "Estoy aqui1",self.componente
            self.analizaExpresionSimple()
            print "Estoy aquissss2",self.componente
            self.comprueba("ParentCi")
            print "Estoy aquissss3",self.componente
        
        else:
            self.error()
    

    def analizaExpresion(self):
        
        if (self.componente.cat == "PR" and self.componente.valor in ["FALSO", "CIERTO", "NO"]) or  self.componente.cat in ["OpAdd","Numero","ParentAp","Identif"]:
            #<expresion> -> <expr_simple> <expresion'>
            print "12",self.componente
            self.analizaExpresionSimple()
            print "32",self.componente
            self.analizaExpresionPrima()
        else:
            self.error()
    

    def analizaRestoInstSimple(self):

        if self.componente.cat == "OpAsigna":
            #<resto_instsimple> -> opasigna <expresion> 
            self.avanza()
            self.analizaExpresion()

        elif self.componente.cat == "CorAp":
            #<resto_instsimple> -> [<expr_simple>] opasigna <expresion>
            self.avanza()
            self.analizaExpresionSimple()
            self.comprueba("]")
            self.comprueba("OpAsigna")
            self.analizaExpresion()
        
        elif (self.componente.cat == "PR" and self.componente.valor == "SINO") or self.componente.cat == "PtoComa":
            #<resto_exsimple> -> lambda
            pass

        else:
            self.error()


    def analizaExpresionSimple(self):

        if self.componente.cat == "OpAdd":
            #<expr_simple> -> <signo> <termino> <resto_exsimple>
            self.analizaSigno()
            self.analizaTermino()
            self.analizaRestoExpSimple()

        elif (self.componente.cat == "PR" and self.componente.valor in ["FALSO", "CIERTO", "NO"]) or self.componente.cat in ["Numero", "ParentAp", "Identif"]:
           #<expr_simple> -> <termino> <resto_exsimple> 
            self.analizaTermino()
            print "Entramos expr_simpl",self.componente
            self.analizaRestoExpSimple()
    
        else:
            self.error()
    

    def analizaVariable(self):
        
        if self.componente.cat == "Identif":
            #<variable> -> id <resto_var>
            self.avanza()
            self.analizaRestoVar()
        
        else:
            self.error()


    def analizaRestoVar(self):

        if self.componente.cat == "CorAp":
            #<resto_var> -> [<expr_simple>]
            self.avanza()
            self.analizaExpresionSimple()
            self.comprueba("CorCi")
        
        elif (self.componente.cat == "PR" and self.componente.valor in ["Y","O","ENTONCES","HACER","SINO"]) or self.componente.cat in ["OpMult","OpAdd","OpRel","CorCi","ParentCi", "PtoComa"]:
            #<resto_var> -> lambda
            pass
        
        else:
            self.error()

    
    def analizaExpresionPrima(self):

        if self.componente.cat == "OpRel":
            #<expresion'> -> oprel <expr_simple>
            self.avanza()
            self.analizaExpresionSimple()
        
        elif self.componente.cat == "PtoComa" or (self.componente.cat == "PR" and self.componente.valor == ["ENTONCES", "HACER", "SINO"]):
            pass

        else:
            self.error()


    def analizaTermino(self):

        if (self.componente.cat == "PR" and self.componente.valor in ["FALSO", "CIERTO", "NO"]) or self.componente.cat in ["Numero","ParentAp","Identif"]:
            #<termino> -> <factor> <resto_term>
            self.analizaFactor()
            print "Derech o Izquierda"
            self.analizaRestoTerm()
        
        else:
            self.error()

    def analizaRestoExpSimple(self):

        if self.componente.cat == "OpAdd":
            #<resto_exsimple> -> opsuma <termino> <resto_exsimple>
            self.avanza()
            self.analizaTermino()
            self.analizaRestoExpSimple()

        elif self.componente.cat == "PR" and self.componente.valor == "O":
            #<resto_exsimple> -> O <termino> <resto_exsimple>
            self.avanza()
            self.analizaTermino()
            self.analizaRestoExpSimple()

        elif self.componente.cat in ["CorCi","ParentCi","OpRel", "PtoComa"] or (self.componente.cat == "PR" and self.componente.valor in ["ENTONCES", "HACER", "SINO"]):
            #<resto_exsimple> -> lambda
            pass

        else:
            self.error()


    def analizaSigno(self):

        if self.componente.cat == "OpAdd":
            #<signo> -> + 
            #<signo> -> -
            self.avanza()
        
        else:
            self.error()


    def analizaRestoTerm(self):

        if self.componente.cat == "PR" and self.componente.valor == "Y":
            #<resto_term> -> Y <factor> <resto_term>
            self.avanza()
            self.analizaFactor()
            self.analizaRestoTerm()

        elif self.componente.cat == "OpMult":
            #<resto_term> -> opmult <factor> <resto_term>
            self.avanza()
            self.analizaFactor()
            self.analizaRestoTerm()

        elif self.componente.cat in [ "OpAdd", "OpRel","CorCi","ParentCi","PtoComa"] or (self.componente.cat == "PR" and self.componente.valor in ["O", "ENTONCES","HACER","SINO"]):
            #<resto_term> -> lambda
            print "Entrando resto_term",self.componente
            pass

        else:
            self.error()

    
    def analizaFactor(self):

        print "Factor",self.componente

        if self.componente.cat == "PR" and self.componente.valor == "FALSO":
            #<factor> -> FALSO
            self.avanza()
        
        elif self.componente.cat == "PR" and self.componente.valor == "CIERTO":
            #<factor> -> CIERTO
            self.avanza()
        
        elif self.componente.cat == "PR" and self.componente.valor == "NO":
            #<factor> -> NO <factor>
            self.avanza()
            self.analizaFactor()

        elif self.componente.cat == "Numero":
            #<factor> -> num
            self.avanza()
            

        elif self.componente.cat == "ParentAp":
            #<factor> -> (<expresion>)
            self.avanza()
            self.analizaExpresion()
            print "4,",self.componente
            self.comprueba("ParentCi")

        elif self.componente.cat == "Identif":
            #<factor> -> <variable>
            print "AntesVar",self.componente
            self.analizaVariable()
            print "DesVar",self.componente


        else:
            self.error()


if __name__ == "__main__":

    script, filename = argv
    txt = open(filename)
    print "Este es tu fichero %r" % filename
    fl = flujo.Flujo(txt)
    analex = Analex(fl)
  
    anasint = Anasint(analex)
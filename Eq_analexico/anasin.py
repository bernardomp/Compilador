from sys import argv
import flujo

class Anasint:

    def __init__(self, lexico):

        self.lexico= lexico
        self.avanza()
        self.analizaPrograma()
        self.comprueba("eof")
    
    def avanza(self):
        self.componente= self.lexico.siguiente()

    def comprueba(self, cat):
        if self.componente == cat:
            self.avanza()
        else:
            self.error()

    def sincroniza(self, sinc):
        #sinc |= \{ "eof" \} 
        sinc = None
        while self.componente.cat not in sinc:
            self.avanza()

    def analizaPrograma(self):

        if self.componente.cat == "PROGRAMA":
            #<Programa> -> PROGRAMA id; <decl_var> <instrucciones>.
            self.avanza()
            self.comprueba("id")
            self.analizaDeclVar()
            self.analizaInstrucciones()
            self.comprueba(".")
        
        else:
            self.error()
    
    def analizaDeclVar(self):

        #ERROR HAY QUE TRATAR CON PALABRAS RESERVADAS
        if self.componente.cat == "VAR":
            #<decl_var> -> VAR <lista_id> : <tipo> ; <decl_v> 
            self.avanza()
            self.analizaListaid()
            self.comprueba(":")
            self.analizaTipo()
            self.comprueba(";")
            self.analizaDeclV()
        
        elif self.componente.cat in ["INICIO"]:
            #<decl_var> -> lambda
            pass
        
        else:
            self.error()
    

    def analizaInstrucciones(self):
        
        if self.componente.cat == "INICIO":
            #<instrucciones> -> INICIO <lista_inst> FIN
            self.avanza()
            self.analizaListainst()
            self.comprueba("FIN")

        else:
            self.error()

    def analizaListaid(self):
        
        if self.componente.cat == "id":
            #<lista_id> -> id <resto_listaid>
            self.avanza()
            self.analizaListaid()

        else:
            self.error()

    def analizaTipo(self):

        if self.componente.cat in ["ENTERO","REAL","BOOLEAN"]:
            #<Tipo> -> <tipo_std>
            self.avanza()
            self.analizaTipostd()
        
        elif self.componente.cat == "VECTOR":
            #<Tipo> -> VECTOR [num] de <tipo_std>
            self.avanza()
            self.comprueba("[")
            self.comprueba("num")
            self.comprueba("]")
            self.comprueba("de")
            self.analizaTipostd()
        
        else:
            self.error()

    def analizaDeclV(self):

        if self.componente.cat == "id":
            #<decl_v> -> <lista_id> : <tipo> ; <decl_v>
            self.avanza()
            self.analizaListaid()
            self.comprueba(":")
            self.analizaTipo()
            self.comprueba(";")
            self.analizaDeclV()
        
        elif self.componente.cat in ["INICIO"]:
            #<decl_v> -> lambda
            pass

        else:
            self.error()

    def analizaRestolistaid(self):

        if self.componente.cat == ",":
            #<resto_listaid> -> ,<lista_id>
            self.avanza()
            self.analizaListaid()

        elif self.componente.cat in [":"]:
            #<resto_listaid> -> lambda
            pass
        
        else:
            self.error()

    def analizaTipostd(self):

        if self.componente.cat == "ENTERO":
            #<tipo_std> -> ENTERO
            pass

        elif self.componente.cat == "REAL":
            #<tipo_std> -> REAL
            pass

        elif self.componente.cat == "BOOLEANO":
            #<tipo_std> -> BOOLEANO
            pass

        else:
            self.error()


    def analizaListainst(self):
       
        if self.componente.cat in ["INICIO", "id", "LEE", "ESCRIBE", "SI", "MIENTRAS"]:
            #<lista_inst> -> <instruccion>;<lista_inst>
            self.avanza()
            self.analizaInstruccion()
            self.comprueba(";")
            self.analizaListainst()
        
        elif self.comprueba == "FIN":
            #<lista_inst> -> lambda
            pass
        
        else:
            self.error()


    def analizaInstruccion(self):

        if self.componente.cat == "INICIO":
            #<instruccion> -> INICIO <lista_inst> FIN 
            self.avanza()
            self.analizaInstrucciones()
            self.comprueba("FIN")
        
        elif self.componente.cat == "id":
            #<instruccion> -> <inst_simple>
            self.avanza()
            self.analizaInstruccionSimple()
        
        elif self.componente.cat in ["LEE","ESCRIBE"]:
            #<instruccion> -> <inst_e/s>
            self.analizaInstruccionES()

        elif self.categoria.cat == "SI":
            #<instruccion> -> SI <expresion> ENTONCES <instruccion> SINO <instruccion>
            self.avanza()
            self.analizaExpresion()
            self.comprueba("ENTONCES")
            self.analizaInstruccion()
            self.comprueba("SINO")
            self.analizaInstruccion()
        
        elif self.comprueba.cat == "MIENTRAS":
            #<instruccion> -> MIENTRAS <expresion> HACER <instruccion>
            self.avanza()
            self.analizaExpresion()
            self.comprueba("HACER")
            self.analizaInstruccion()
        
        else:
            self.error()


    def analizaInstruccionSimple(self):

        if self.comprueba.cat =="id":
            #<inst_simple> -> id <resto_instsimple>
            self.avanza()
            self.analizaRestoInstSimple()
        
        else:
            self.error()


    def analizaInstruccionES(self):

        if self.comprueba.cat == "LEE":
            #<inst_e/s> -> LEE (id) 
            self.avanza()
            self.comprueba("(")
            self.comprueba("id")
            self.comprueba(")")

        elif self.comprueba.cat == "ESCRIBE":
            #<inst_e/s> -> ESCRIBE (<expr_simple>)
            self.avanza()
            self.comprueba("(")
            self.analizaExpresionSimple()
            self.comprueba(")")
        
        else:
            self.error()
    

    def analizaExpresion(self):

        if self.comprueba.cat in ["+", "-", "FALSO", "CIERTO", "NO", "num", "(", "id"]:
            #<expresion> -> <expr_simple> <expresion'>
            self.analizaExpresionSimple()
        
        else:
            self.error()
    

    def analizaRestoInstSimple(self):

        if self.comprueba.cat == "opsum":
            #<resto_exsimple> -> opsuma <termino> <resto_exsimple>
            self.avanza()
            self.analizaTermino()
            self.analizaRestoExpSimple()

        elif self.comprueba.cat == "O":
            #<resto_exsimple> -> O <termino> <resto_exsimple>
            self.avanza()
            self.analizaTermino()
            self.analizaRestoExpSimple()
        
        elif self.comprueba.cat in [";", "SINO"]:
            #<resto_exsimple> -> lambda
            pass

        else:
            self.error()


    def analizaExpresionSimple(self):

        if self.comprueba.cat in ["+","-"]:
            #<expr_simple> -> <termino> <resto_exsimple> 
            self.analizaTermino()
            self.analizaRestoExpSimple()

        elif self.comprueba.cat in ["FALSO", "CIERTO", "NO", "num", "(", "id"]:
            #<expr_simple> -> <signo> <termino> <resto_exsimple>
            self.analizaSigno()
    
        else:
            self.error()
    

    def analizaVariable(self):
        
        if self.comprueba.cat == "id":
            #<variable> -> id <resto_var>
            self.avanza()
            self.analizaRestoVar()
        
        else:
            self.error()


    def analizaRestoVar(self):

        if self.comprueba.cat == "[":
            #<resto_var> -> [<expr_simple>]
            self.avanza()
            self.analizaExpresionSimple()
            self.comprueba("]")
        
        elif self.comprueba.cat in ["Y", "opmult"]:
            pass
        
        else:
            self.error()
    
    def analizaExpresionPrima(self):

        if self.comprueba.cat == "oprel":
            #<expresion'> -> oprel <expr_simple>
            self.avanza()
            self.analizaExpresionSimple()
        
        elif self.comprueba.cat in ["ENTONCES", "HACER", ";", "SINO"]:
            pass

        else:
            self.error()

    def analizaTermino(self):

        if self.comprueba.cat in ["FALSO", "CIERTO", "NO", "num", "(", "id"]:
            #<termino> -> <factor> <resto_term>
            self.analizaFactor()
            self.analizaRestoTerm()
        
        else:
            self.error()

    def analizaRestoExpSimple(self):

        if self.comprueba.cat == "opsuma":
            #<resto_exsimple> -> opsuma <termino> <resto_exsimple>
            self.avanza()
            self.analizaTermino()
            self.analizaRestoExpSimple()

        elif self.comprueba.cat == "O":
            #<resto_exsimple> -> O <termino> <resto_exsimple>
            self.avanza()
            self.analizaTermino()
            self.analizaRestoExpSimple()

        elif self.comprueba.cat in ["]", ")", "oprel", "ENTONCES", "HACER", ";" , "SINO"]:
            pass

        else:
            self.error()


    def analizaSigno(self):

        if self.comprueba.cat == "+":
            #<signo> -> + 
            pass
        
        elif self.comprueba.cat == "+":
            #<signo> -> -
            pass
        
        else:
            self.error()


    def analizaRestoTerm(self):

        if self.comprueba.cat == "Y":
            #<resto_term> -> Y <factor> <resto_term>
            self.avanza()
            self.analizaFactor()
            self.analizaRestoTerm()

        elif self.comprueba.cat == "opmult":
            #<resto_term> -> opmult <factor> <resto_term>
            self.avanza()
            self.analizaFactor()
            self.analizaRestoTerm()

        elif self.comprueba.cat in ["opsuma", "O"]:
            #<resto_term> -> lambda
            pass

        else:
            self.error()

    
    def analizaFactor(self):

        if self.comprueba.cat == "FALSO":
            #<factor> -> FALSO
            pass
        
        elif self.comprueba.cat == "CIERTO":
            #<factor> -> CIERTO
            pass
        
        elif self.comprueba.cat == "NO":
            #<factor> -> NO <factor>
            self.avanza()
            self.analizaFactor()

        elif self.comprueba.cat == "num":
            #<factor> -> num
            pass

        elif self.comprueba.cat == "(":
            #<factor> -> (<expresion>)
            self.avanza()
            self.analizaExpresion()
            self.comprueba(")")

        elif self.comprueba.cat == "id":
            #<factor> -> <variable>
            self.analizaVariable()

        else:
            self.error()


if __name__ == "__main__":

    script, filename = argv
    txt = open(filename)
    print "Este es tu fichero %r" % filename
    fl = flujo.Flujo(txt)
    analex = Analex(fl)
  
    anasint = Anasint(analex)
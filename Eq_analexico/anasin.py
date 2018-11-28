import flujo
import string
import sys
import componentes
from sys import argv
from analex import Analex

class Anasint:

    def __init__(self, lexico):

        self.lexico= lexico
        self.tabla = {}

        self.avanza()
        self.analizaPrograma()
        
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

            identifPrograma = self.componente.valor

            if not self.comprueba("Identif"):
                self.error("Se esperaba Identif")
                self.sincroniza(siguiente)
                return

            #Comprobamos que no existe el identificador del programa
            if (not self.tabla.has_key(identifPrograma)) and (identifPrograma not in Analex.PR):
                self.tabla[identifPrograma] = True

            elif identifPrograma in Analex.PR:
                self.error("No se puede utilizar palabra reservada como indentificador")

            else:
                self.error("Variable definida")

            if not self.comprueba("PtoComa"):
                self.error("Se esperaba ;")
                self.sincroniza(siguiente)
                return
            

            self.analizaDeclVar()
            self.analizaInstrucciones()

            if not self.comprueba("Punto"):
                self.error("Se esperaba .")
                self.sincroniza(siguiente)
                return
        
        else:
            self.error("Se experaba la palabra reservada PROGRAMA")
            self.sincroniza(siguiente)
    

    def analizaDeclVar(self):
        
        siguiente = ["INICIO"]

        if self.componente.cat == "PR" and self.componente.valor == "VAR":
            #<decl_var> -> VAR <lista_id> : <tipo> ; <decl_v> 
            self.avanza()
            self.analizaListaid()

            if not self.comprueba("DosPtos"):
                self.error("Se esperaba :")
                self.sincroniza(siguiente)
                return 

            self.analizaTipo()
    
            
            if not self.comprueba("PtoComa"):
                self.error("Se esperaba ;")
                self.sincroniza(siguiente)
                return

            self.analizaDeclV()
        
        elif self.componente == "PR" and self.componente.valor == "INICIO":
            #<decl_var> -> lambda
            pass
        
        else:

            self.error("Se esperaba palabra reservada VAR o INICIO")
            self.sincroniza(siguiente)
    

    def analizaInstrucciones(self):
        
        siguiente = ["Punto"]

        if self.componente.cat == "PR" and self.componente.valor == "INICIO":
            #<instrucciones> -> INICIO <lista_inst> FIN
            self.avanza()
            self.analizaListainst()

            if not self.comprueba("FIN"):
                self.error("Se esperaba palabra reservada FIN")
                self.sincroniza(siguiente)
                return

        else:
            self.error("Se esperaba palabra reservada INICIO")
            self.sincroniza(siguiente)
            return


    def analizaListaid(self):
        
        siguiente = ["DosPtos"]

        if self.componente.cat == "Identif":
            #<lista_id> -> id <resto_listaid>

             #Comprobamos que no existe el identificador del programa
            if (not self.tabla.has_key(self.componente.valor)) and (self.componente.valor not in Analex.PR):
                self.tabla[self.componente.valor] = True

            elif self.componente.valor in Analex.PR:
                self.error("No se puede utilizar palabra reservada como indentificador")

            else:
                self.error("Variable definida")
            
            self.avanza()
            self.analizaRestolistaid()

        else:
            self.error("Se esperada Identif")
            self.sincroniza(siguiente)


    def analizaTipo(self):

        siguiente = ["PtoComa"]

        if self.componente.cat == "PR" and self.componente.valor in ["ENTERO","REAL","BOOLEANO"]:
            #<Tipo> -> <tipo_std>
            self.analizaTipostd()
        
        elif self.componente.cat == "PR" and self.componente.valor == "VECTOR":
            #<Tipo> -> VECTOR [num] de <tipo_std>
            self.avanza()

            if not self.comprueba("CorAp"):
                self.error("Se esperada [")
                self.sincroniza(siguiente)
                return

            if not self.comprueba("Numero"):
                self.error("Se esperada Numero")
                self.sincroniza(siguiente)
                return

            if not self.comprueba("CorCi"):
                self.error("Se esperada ]")
                self.sincroniza(siguiente)
                return

            if not self.comprueba("DE"):
                self.error("Se esperada palabra reservada DE")
                self.sincroniza(siguiente)
                return

            self.analizaTipostd()
        
        else:
            self.error("Se esperaba ENTERO, REAL, BOOLEANO o VECTOR")
            self.sincroniza(siguiente)


    def analizaDeclV(self):

        siguiente = ["INICIO"]

        if self.componente.cat == "Identif":
            #<decl_v> -> <lista_id> : <tipo> ; <decl_v>
            self.analizaListaid()
            
            if not self.comprueba("DosPtos"):
                self.error("Se esperada :")
                self.sincroniza(siguiente)
                return 

            self.analizaTipo()

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
            self.analizaListaid()

        elif self.componente.cat == "DosPtos":
            #<resto_listaid> -> lambda
            pass
        
        else:
            self.error("Se esperaba , o :")
            self.sincroniza(siguiente)


    def analizaTipostd(self):

        siguiente = ["PtoComa"]

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
            self.error("Se esperaba tipo ENTERO, REAL o BOOLEANO")
            self.sincroniza(siguiente)


    def analizaListainst(self):
       
        siguiente = ["FIN"]

        if (self.componente.cat == "PR" and self.componente.valor in ["INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]) or self.componente.cat == "Identif":
            #<lista_inst> -> <instruccion>;<lista_inst>
            self.analizaInstruccion()

            if not self.comprueba("PtoComa"):
                self.error("Se esperada ;")
                self.sincroniza(siguiente)
                return
            
            self.analizaListainst()
        
        elif self.componente.cat == "PR" and self.componente.valor == "FIN":
            #<lista_inst> -> lambda
            pass
        
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)



    def analizaInstruccion(self):

        siguiente = ["PtoComa","SINO"]

        if self.componente.cat == "PR" and self.componente.valor == "INICIO":
            #<instruccion> -> INICIO <lista_inst> FIN 
            self.avanza()
            self.analizaListainst()

            if not self.comprueba("FIN"):
                self.error("Se esperada palabra reservada FIN")
                self.sincroniza(siguiente)
                return
        
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

            if not self.comprueba("ENTONCES"):
                self.error("Se esperaba palabra reservada ENTONCES")
                self.sincroniza(siguiente)
                return

            self.analizaInstruccion()
            
            if not self.comprueba("SINO"):
                self.error("Se esperaba palabra reservada SINO")
                self.sincroniza(siguiente)
                return

            self.analizaInstruccion()
        
        elif self.componente.cat == "PR" and self.componente.valor == "MIENTRAS":
            #<instruccion> -> MIENTRAS <expresion> HACER <instruccion>
            self.avanza()
            self.analizaExpresion()

            if not self.comprueba("HACER"):
                self.error("Se esperaba palabra reservada HACER")
                self.sincroniza(siguiente)
                return

            self.analizaInstruccion()
        
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)


    def analizaInstruccionSimple(self):

        siguiente = ["PtoComa","SINO"]

        if self.componente.cat =="Identif":

            #Verificamos que la variable se haya definido
            if not self.tabla.has_key(self.componente.valor):
                self.error("Variable no definida")
            
            #<inst_simple> -> id <resto_instsimple>
            self.avanza()
            self.analizaRestoInstSimple()
        
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

            if not self.comprueba("Identif"):
                self.error("Elemento esperado Identif")
                self.sincroniza(siguiente)
                return

            #Verificamos que la variable se haya definido
            if not self.tabla.has_key(nombrevar):
                self.error("Variable no definida")

            if not self.comprueba("ParentCi"):
                self.error("Elemento esperado )")
                self.sincroniza(siguiente)
                return

        elif self.componente.cat == "PR" and self.componente.valor == "ESCRIBE":
            #<inst_e/s> -> ESCRIBE (<expr_simple>)
            self.avanza()
            
            if not self.comprueba("ParentAp"):
                self.error("Elemento  esperado (")
                self.sincroniza(siguiente)
                return

            self.analizaExpresionSimple()
            
            if not self.comprueba("ParentCi"):
                self.error("Elemento esperado )")
                self.sincroniza(siguiente)
                return
        
        else:
            self.error("Se esperaba palabra reservada LEE o ESCRIBE " + str(self.componente))
            self.sincroniza(siguiente)

    

    def analizaExpresion(self):
        
        siguiente = ["ENTONCES","HACER","SINO" ,"PtoComa","ParentCi"]

        if (self.componente.cat == "PR" and self.componente.valor in ["FALSO", "CIERTO", "NO"]) or  self.componente.cat in ["OpAdd","Numero","ParentAp","Identif"]:
            #<expresion> -> <expr_simple> <expresion'>
            self.analizaExpresionSimple()
            self.analizaExpresionPrima()
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)
    

    def analizaRestoInstSimple(self):

        siguiente = ["PtoComa", "SINO"]

        if self.componente.cat == "OpAsigna":
            #<resto_instsimple> -> opasigna <expresion> 
            self.avanza()
            self.analizaExpresion()

        elif self.componente.cat == "CorAp":
            #<resto_instsimple> -> [<expr_simple>] opasigna <expresion>
            self.avanza()
            self.analizaExpresionSimple()

            if not self.comprueba("]"):
                self.error("Elemento esperado ]")
                self.sincroniza(siguiente)
                return

            if not self.comprueba("OpAsigna"):
                self.error("Elemento esperado :=")
                self.sincroniza(siguiente)
                return

            self.analizaExpresion()
        
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
            self.analizaSigno()
            self.analizaTermino()
            self.analizaRestoExpSimple()

        elif (self.componente.cat == "PR" and self.componente.valor in ["FALSO", "CIERTO", "NO"]) or self.componente.cat in ["Numero", "ParentAp", "Identif"]:
           #<expr_simple> -> <termino> <resto_exsimple> 
            self.analizaTermino()
            self.analizaRestoExpSimple()    
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)
    

    def analizaVariable(self):
        
        siguiente = ["OpMult","Y","OpAdd","O","CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

        if self.componente.cat == "Identif":
            #<variable> -> id <resto_var>

            #Verificamos que la variable se haya definido
            if not self.tabla.has_key(self.componente.valor):
                self.error("Variable no definida")


            self.avanza()
            self.analizaRestoVar()
        
        else:
            self.error("Elemento esperado Identif")
            self.sincroniza(siguiente)
    


    def analizaRestoVar(self):

        siguiente = ["OpMult","Y","OpAdd","O","CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

        if self.componente.cat == "CorAp":
            #<resto_var> -> [<expr_simple>]
            self.avanza()
            self.analizaExpresionSimple()
            
            if not self.comprueba("CorCi"):
                self.error("Elemento esperado )")
                self.sincroniza(siguiente)
                return
    
        
        elif (self.componente.cat == "PR" and self.componente.valor in ["Y","O","ENTONCES","HACER","SINO"]) or self.componente.cat in ["OpMult","OpAdd","OpRel","CorCi","ParentCi", "PtoComa"]:
            #<resto_var> -> lambda
            pass
        
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)


    
    def analizaExpresionPrima(self):

        siguiente = ["ENTONCES","HACER","PtoComa","SINO","CorCi"]
        
        if self.componente.cat == "OpRel":
            #<expresion'> -> oprel <expr_simple>
            self.avanza()
            self.analizaExpresionSimple()
        
        elif self.componente.cat in ["PtoComa", "ParentCi"] or (self.componente.cat == "PR" and self.componente.valor in ["ENTONCES","HACER","SINO"]):
            #<expresion'> -> lambda
            pass

        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)


    def analizaTermino(self):

        siguiente = ["OpAdd","O","CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

        if (self.componente.cat == "PR" and self.componente.valor in ["FALSO", "CIERTO", "NO"]) or self.componente.cat in ["Numero","ParentAp","Identif"]:
            #<termino> -> <factor> <resto_term>
            self.analizaFactor()
            self.analizaRestoTerm()
        
        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)


    def analizaRestoExpSimple(self):

        siguiente = ["CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

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


    def analizaRestoTerm(self):

        siguiente = ["OpAdd","O","CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

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
            pass

        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)

    
    def analizaFactor(self):

        siguiente = ["OpMult","Y","OpAdd","O","CorCi","ParentCi","ENTONCES","HACER","PtoComa","SINO","OpRel"]

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
            
            if not self.comprueba("ParentCi"):
                self.error("Se esperaba )")
                self.sincroniza(siguiente)
                return

        elif self.componente.cat == "Identif":
            #<factor> -> <variable>
            self.analizaVariable()

        else:
            self.error("Elemento inesperado " + str(self.componente))
            self.sincroniza(siguiente)


if __name__ == "__main__":

    script, filename = argv
    txt = open(filename)
    print "Este es tu fichero %r" % filename
    fl = flujo.Flujo(txt)
    analex = Analex(fl)
  
    anasint = Anasint(analex)
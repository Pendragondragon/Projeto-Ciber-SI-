class Cofre:
    MAX_UTILIZADORES = 3

    def __init__(self, id, codigo_autenticacao, assinatura_digital, tipo_de_cifra, mensagem, metadado):
        self.id = id
        self.codigo_autenticacao = codigo_autenticacao  # HMAC
        self.assinatura_digital = assinatura_digital
        self.tipo_de_cifra = tipo_de_cifra
        self.utilizadores = []  # lista de users com acesso
        self.mensagem = mensagem
        self.metadado = metadado  # ex: cofre_id

    def adicionar_utilizador(self, user):
        if len(self.utilizadores) >= Cofre.MAX_UTILIZADORES:
            raise Exception("Limite de utilizadores atingido (máx. 3).")
        
        if user in self.utilizadores:
            print("Utilizador já tem acesso ao cofre.")
            return
        
        self.utilizadores.append(user)

    def remover_utilizador(self, user):
        if user in self.utilizadores:
            self.utilizadores.remove(user)

    def __str__(self):
        return (
            f"Cofre(id={self.id}, tipo_de_cifra='{self.tipo_de_cifra}', "
            f"num_utilizadores={len(self.utilizadores)})"
        )